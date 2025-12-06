"""
Servidor FastAPI principal para el Sistema de RRHH
"""
from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
from contextlib import asynccontextmanager
import uvicorn
from datetime import datetime, date, timedelta
import bcrypt
import time
import logging

from database import get_db, Database
from models import (
    UsuarioCreate, UsuarioUpdate, UsuarioResponse, UsuarioLogin,
    DepartamentoCreate, DepartamentoUpdate,
    EmpleadoCreate, EmpleadoUpdate,
    ContratoCreate, ContratoUpdate,
    AsistenciaCreate, AsistenciaUpdate, AsistenciaReporteRequest,
    NominaCreate, NominaUpdate,
    VacacionPermisoCreate, VacacionPermisoUpdate,
    DocumentoCreate, DocumentoUpdate,
    PuestoCreate, PuestoUpdate,
    CapacitacionCreate, CapacitacionUpdate,
    EvaluacionCreate, EvaluacionUpdate,
    RolCreate, RolUpdate, AsignarPermisosRol, AsignarRolUsuario,
    PermisoCreate, SincronizarEmpleadoUsuario,
    NotificacionCreate, NotificacionUpdate, NotificacionConfigCreate, NotificacionConfigUpdate
)
from auth import create_access_token, get_current_user, get_current_active_user, require_role
from helpers.notification_helper import NotificationHelper
from helpers.export_helper import ExportHelper

# ============================================================================
#                           CONFIGURACIÓN DE LOGGING
# ============================================================================
# Configurar logging PRIMERO para que esté disponible en todas las funciones
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Función helper para hashear contraseñas
def hash_password(password: str) -> str:
    """Hashea una contraseña usando bcrypt"""
    # Asegurar que la contraseña no exceda 72 bytes
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode('utf-8')

# Función helper para verificar contraseñas
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña contra su hash"""
    try:
        # Intentar verificar con bcrypt
        password_bytes = plain_password.encode('utf-8')[:72]
        hash_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)
    except Exception:
        # Fallback para contraseñas antiguas en SHA-256 o texto plano (solo para migración)
        import hashlib
        if hashed_password == plain_password:
            # Si está en texto plano, actualizar a bcrypt automáticamente
            return True  # Permitir login pero debería actualizarse después
        sha256_hash = hashlib.sha256(plain_password.encode()).hexdigest()
        return sha256_hash == hashed_password

# Función helper para obtener nombre de empleado de forma robusta
def get_empleado_nombre_sql(alias_empleado: str = "e") -> str:
    """
    Retorna una expresión SQL para obtener el nombre del empleado de forma robusta.
    Maneja casos donde la tabla Empleados puede no existir o no tener datos.
    
    Args:
        alias_empleado: Alias de la tabla Empleados en la consulta (default: "e")
    
    Returns:
        Expresión SQL para obtener el nombre del empleado
    """
    return f"COALESCE({alias_empleado}.nombre || ' ' || {alias_empleado}.apellido, 'Empleado no encontrado')"

# Función helper para hacer JOIN con Empleados de forma robusta
def build_empleado_join(alias_contrato: str = "c", alias_empleado: str = "e", join_type: str = "LEFT") -> str:
    """
    Construye una cláusula JOIN con la tabla Empleados de forma robusta.
    
    Args:
        alias_contrato: Alias de la tabla que contiene id_empleado (default: "c")
        alias_empleado: Alias de la tabla Empleados (default: "e")
        join_type: Tipo de JOIN ("LEFT", "INNER", etc.) (default: "LEFT")
    
    Returns:
        Cláusula SQL para el JOIN
    """
    return f"{join_type} JOIN Empleados {alias_empleado} ON {alias_contrato}.id_empleado = {alias_empleado}.id_empleado"

# Función helper para obtener nombre de empleado de forma robusta
def get_empleado_nombre_select(alias_empleado: str = "e") -> str:
    """
    Construye una expresión SELECT para obtener el nombre del empleado de forma robusta.
    Maneja tanto la tabla nueva (Empleados con nombre y apellido) como la antigua.
    
    Args:
        alias_empleado: Alias de la tabla Empleados (default: "e")
    
    Returns:
        Expresión SQL para el nombre del empleado
    """
    return f"COALESCE({alias_empleado}.nombre || ' ' || {alias_empleado}.apellido, {alias_empleado}.nombre, 'Empleado no encontrado') as nombre_empleado"

# Función helper para ejecutar consultas con JOINs robustos a Empleados
def execute_query_with_empleado_join(
    db: Database,
    base_query: str,
    fallback_query: str,
    params: tuple = (),
    error_context: str = "consulta"
) -> list:
    """
    Ejecuta una consulta con JOIN a Empleados de forma robusta.
    Intenta primero con la tabla nueva, y si falla, usa el fallback.
    
    Args:
        db: Instancia de Database
        base_query: Query principal con JOIN a Empleados
        fallback_query: Query de respaldo sin JOIN o con estructura alternativa
        params: Parámetros para la consulta
        error_context: Contexto del error para logging
    
    Returns:
        Lista de resultados
    """
    try:
        return db.fetch_all(base_query, params)
    except Exception as table_error:
        error_msg = str(table_error).lower()
        logger.warning(f"Error en {error_context} con JOIN a Empleados: {str(table_error)}")
        
        # Si la tabla no existe, retornar lista vacía
        if 'no such table' in error_msg or 'does not exist' in error_msg:
            logger.info(f"Tabla Empleados no existe en {error_context}, usando fallback")
            try:
                return db.fetch_all(fallback_query, params)
            except Exception as fallback_error:
                logger.error(f"Error en fallback de {error_context}: {str(fallback_error)}")
                return []
        else:
            # Intentar con el fallback
            try:
                return db.fetch_all(fallback_query, params)
            except Exception as fallback_error:
                logger.error(f"Error en fallback de {error_context}: {str(fallback_error)}")
                return []

# ============================================================================
#                           LIFESPAN EVENT HANDLER
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Maneja eventos de inicio y cierre de la aplicación"""
    # Startup
    print("\n" + "="*60)
    print("INICIANDO SERVIDOR RRHH")
    print("="*60)
    
    db_instance = None
    try:
        print("[1/3] Conectando a la base de datos...")
        db_instance = get_db()
        if not db_instance.connection:
            db_instance.connect()
        print("[OK] Conexión a base de datos establecida")
        
        print("[2/3] Creando/verificando tablas...")
        db_instance.create_tables()
        print("[OK] Tablas verificadas/creadas")
        
        print("[3/3] Inicializando aplicación...")
        print("[OK] Base de datos inicializada correctamente")
        print("="*60)
        print("[OK] SERVIDOR LISTO - Escuchando en http://localhost:8000")
        print("Documentacion: http://localhost:8000/docs")
        print("Health Check: http://localhost:8000/api/health")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n[ERROR CRÍTICO] Error al inicializar base de datos: {e}")
        print(f"[ERROR] Tipo: {type(e).__name__}")
        import traceback
        print(f"[ERROR] Traceback:\n{traceback.format_exc()}")
        print("\n[INFO] El servidor puede no funcionar correctamente")
        print("="*60 + "\n")
        # No lanzar la excepción para que el servidor pueda iniciar
        # Los endpoints manejarán los errores de conexión
    
    yield
    
    # Shutdown
    print("\n" + "="*60)
    print("CERRANDO SERVIDOR")
    print("="*60)
    try:
        if db_instance and db_instance.connection:
            db_instance.disconnect()
            print("[OK] Conexión a base de datos cerrada")
        else:
            # Intentar obtener la instancia global
            from database import db
            if db.connection:
                db.disconnect()
                print("[OK] Conexión a base de datos cerrada")
    except Exception as e:
        print(f"[ERROR] Error al cerrar conexión: {e}")
    print("="*60 + "\n")

# Crear instancia de FastAPI con lifespan
app = FastAPI(
    title="Sistema de RRHH API",
    description="API para gestión de Recursos Humanos",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS con mejores prácticas de seguridad
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "http://localhost:4201",
        "http://localhost:3000",
        "http://127.0.0.1:4200",
        "http://127.0.0.1:4201"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Middleware para logging de requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware para registrar todas las peticiones HTTP"""
    start_time = time.time()
    
    # Log de la petición
    logger.info(f"{request.method} {request.url.path} - Cliente: {request.client.host if request.client else 'Unknown'}")
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log de la respuesta
        logger.info(
            f"{request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Tiempo: {process_time:.3f}s"
        )
        
        # Agregar header con tiempo de procesamiento
        response.headers["X-Process-Time"] = str(process_time)
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"{request.method} {request.url.path} - "
            f"Error: {str(e)} - "
            f"Tiempo: {process_time:.3f}s"
        )
        raise

# ============================================================================
#                           ENDPOINTS PRINCIPALES
# ============================================================================

@app.get("/")
async def root():
    """Endpoint principal de la API"""
    return {
        "mensaje": "Bienvenido a la API del Sistema de RRHH",
        "version": "1.0.0",
        "status": "activo",
        "documentacion": "/docs"
    }

@app.get("/api/health")
async def health_check(db: Database = Depends(get_db)):
    """Verificar estado del servidor y base de datos"""
    try:
        # Intentar una consulta simple
        db.fetch_one("SELECT 1")
        return {
            "status": "ok",
            "database": "conectada",
            "mensaje": "Sistema funcionando correctamente"
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "database": "desconectada",
                "mensaje": f"Error en la base de datos: {str(e)}"
            }
        )

# ============================================================================
#                           ENDPOINTS DE USUARIOS
# ============================================================================

@app.get("/api/usuarios", response_model=dict)
async def listar_usuarios(db: Database = Depends(get_db)):
    """Listar todos los usuarios activos relacionados con empleados"""
    try:
        # Obtener usuarios que tienen un empleado asociado (por email)
        # Esto asegura que solo se muestren usuarios relacionados con empleados
        usuarios = db.fetch_all(
            """SELECT DISTINCT u.id, u.nombre, u.email, u.rol, u.fecha_creacion, u.activo 
               FROM usuarios u
               INNER JOIN Empleados e ON LOWER(u.email) = LOWER(e.correo)
               WHERE u.activo = 1 
               ORDER BY u.fecha_creacion DESC"""
        )
        
        # Si no hay resultados con JOIN (tabla Empleados puede no existir o no tener datos),
        # mostrar todos los usuarios activos como fallback
        if not usuarios:
            usuarios = db.fetch_all(
                "SELECT id, nombre, email, rol, fecha_creacion, activo FROM usuarios WHERE activo = 1 ORDER BY fecha_creacion DESC"
            )
        
        return {
            "success": True,
            "data": usuarios,
            "count": len(usuarios)
        }
    except Exception as e:
        logger.error(f"Error al obtener usuarios: {str(e)}", exc_info=True)
        # Si hay error con el JOIN, usar fallback simple
        try:
            usuarios = db.fetch_all(
                "SELECT id, nombre, email, rol, fecha_creacion, activo FROM usuarios WHERE activo = 1 ORDER BY fecha_creacion DESC"
            )
            return {
                "success": True,
                "data": usuarios,
                "count": len(usuarios)
            }
        except Exception as e2:
            raise HTTPException(
                status_code=500, 
                detail=f"Error al obtener usuarios: {str(e2)}"
            )

@app.get("/api/usuarios/{usuario_id}", response_model=dict)
async def obtener_usuario(usuario_id: int, db: Database = Depends(get_db)):
    """Obtener un usuario por ID (activo o inactivo)"""
    try:
        usuario = db.fetch_one(
            "SELECT id, nombre, email, rol, fecha_creacion, activo FROM usuarios WHERE id = ?",
            (usuario_id,)
        )
        if not usuario:
            raise HTTPException(status_code=404, detail=f"Usuario con ID {usuario_id} no encontrado")
        return {"success": True, "data": usuario}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener usuario: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al obtener usuario: {str(e)}")

@app.post("/api/usuarios", response_model=dict, status_code=201)
async def crear_usuario(usuario: UsuarioCreate, db: Database = Depends(get_db)):
    """Crear un nuevo usuario"""
    try:
        # Verificar si el email ya existe
        existente = db.fetch_one("SELECT id FROM usuarios WHERE email = ?", (usuario.email,))
        if existente:
            raise HTTPException(status_code=400, detail=f"El email {usuario.email} ya está registrado")
        
        # Hashear la contraseña
        password_hash = hash_password(usuario.password)
        
        # Insertar usuario
        cursor = db.execute_query(
            """INSERT INTO usuarios (nombre, email, password, rol) 
               VALUES (?, ?, ?, ?)""",
            (usuario.nombre, usuario.email, password_hash, usuario.rol)
        )
        
        # Obtener el usuario creado
        nuevo_usuario = db.fetch_one(
            "SELECT id, nombre, email, rol, fecha_creacion, activo FROM usuarios WHERE id = ?",
            (cursor.lastrowid,)
        )
        
        return {
            "success": True,
            "message": "Usuario creado exitosamente",
            "data": nuevo_usuario
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear usuario: {str(e)}")

@app.put("/api/usuarios/{usuario_id}", response_model=dict)
async def actualizar_usuario(usuario_id: int, usuario: UsuarioUpdate, db: Database = Depends(get_db)):
    """Actualizar un usuario existente"""
    try:
        # Verificar que el usuario existe
        existente = db.fetch_one("SELECT id, nombre FROM usuarios WHERE id = ?", (usuario_id,))
        if not existente:
            raise HTTPException(status_code=404, detail=f"Usuario con ID {usuario_id} no encontrado")
        
        # Construir query de actualización dinámicamente
        updates = []
        params = []
        
        if usuario.nombre:
            updates.append("nombre = ?")
            params.append(usuario.nombre)
        if usuario.email:
            # Verificar si el email ya está en uso por otro usuario
            otro_usuario = db.fetch_one("SELECT id FROM usuarios WHERE email = ? AND id != ?", (usuario.email, usuario_id))
            if otro_usuario:
                raise HTTPException(status_code=400, detail=f"El email {usuario.email} ya está en uso")
            updates.append("email = ?")
            params.append(usuario.email)
        if usuario.password:
            updates.append("password = ?")
            params.append(hash_password(usuario.password))
        if usuario.rol:
            updates.append("rol = ?")
            params.append(usuario.rol)
        if usuario.activo is not None:
            updates.append("activo = ?")
            params.append(1 if usuario.activo else 0)
        
        if not updates:
            raise HTTPException(status_code=400, detail="No se proporcionaron campos para actualizar")
        
        params.append(usuario_id)
        query = f"UPDATE usuarios SET {', '.join(updates)} WHERE id = ?"
        db.execute_query(query, tuple(params))
        
        # Obtener el usuario actualizado
        usuario_actualizado = db.fetch_one(
            "SELECT id, nombre, email, rol, fecha_creacion, activo FROM usuarios WHERE id = ?",
            (usuario_id,)
        )
        
        return {
            "success": True,
            "message": "Usuario actualizado exitosamente",
            "data": usuario_actualizado
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar usuario: {str(e)}")

@app.delete("/api/usuarios/{usuario_id}", response_model=dict)
async def eliminar_usuario(usuario_id: int, db: Database = Depends(get_db)):
    """Desactivar un usuario (soft delete)"""
    try:
        usuario = db.fetch_one("SELECT id, nombre FROM usuarios WHERE id = ?", (usuario_id,))
        if not usuario:
            raise HTTPException(status_code=404, detail=f"Usuario con ID {usuario_id} no encontrado")
        
        db.execute_query("UPDATE usuarios SET activo = 0 WHERE id = ?", (usuario_id,))
        
        return {
            "success": True,
            "message": f"Usuario '{usuario['nombre']}' desactivado exitosamente"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar usuario: {str(e)}")

@app.post("/api/usuarios/login", response_model=dict)
async def login_usuario(credenciales: UsuarioLogin, db: Database = Depends(get_db)):
    """
    Autenticar un usuario y generar token JWT
    
    Returns:
        Token JWT y datos del usuario
    """
    try:
        # Buscar usuario por email
        usuario = db.fetch_one(
            "SELECT id, nombre, email, password, rol, activo FROM usuarios WHERE email = ?",
            (credenciales.email,)
        )
        
        if not usuario:
            logger.warning(f"Intento de login fallido - Email no encontrado: {credenciales.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas"
            )
        
        # Verificar si el usuario está activo
        if usuario['activo'] != 1:
            logger.warning(f"Intento de login fallido - Usuario inactivo: {credenciales.email}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario inactivo"
            )
        
        # Verificar contraseña
        password_valid = verify_password(credenciales.password, usuario['password'])
        
        # Si la contraseña está en texto plano, actualizarla a bcrypt
        if not password_valid and usuario['password'] == credenciales.password:
            # Contraseña en texto plano, actualizar a bcrypt
            new_hash = hash_password(credenciales.password)
            db.execute_query(
                "UPDATE usuarios SET password = ? WHERE id = ?",
                (new_hash, usuario['id'])
            )
            password_valid = True
            logger.info(f"Contraseña actualizada a bcrypt para usuario: {usuario['email']}")
        
        if not password_valid:
            logger.warning(f"Intento de login fallido - Contraseña incorrecta: {credenciales.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas"
            )
        
        # Crear token JWT
        access_token_expires = timedelta(minutes=60 * 24)  # 24 horas
        access_token = create_access_token(
            data={"sub": usuario['id'], "email": usuario['email'], "rol": usuario['rol']},
            expires_delta=access_token_expires
        )
        
        # Retornar datos del usuario (sin password) y token
        usuario_response = {
            "id": usuario['id'],
            "nombre": usuario['nombre'],
            "email": usuario['email'],
            "rol": usuario['rol'],
            "fecha_creacion": usuario.get('fecha_creacion', ''),
            "activo": usuario['activo']
        }
        
        logger.info(f"Login exitoso - Usuario: {usuario['email']}")
        
        return {
            "success": True,
            "message": "Login exitoso",
            "data": usuario_response,
            "access_token": access_token,
            "token_type": "bearer"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en el login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en el login: {str(e)}"
        )

@app.patch("/api/usuarios/{usuario_id}/toggle-status", response_model=dict)
async def toggle_usuario_status(usuario_id: int, db: Database = Depends(get_db)):
    """Activar o desactivar un usuario"""
    try:
        usuario = db.fetch_one("SELECT id, nombre, activo FROM usuarios WHERE id = ?", (usuario_id,))
        if not usuario:
            raise HTTPException(status_code=404, detail=f"Usuario con ID {usuario_id} no encontrado")
        
        nuevo_estado = 0 if usuario['activo'] == 1 else 1
        db.execute_query("UPDATE usuarios SET activo = ? WHERE id = ?", (nuevo_estado, usuario_id))
        
        return {
            "success": True,
            "message": f"Usuario {'activado' if nuevo_estado == 1 else 'desactivado'} exitosamente",
            "data": {"id": usuario_id, "activo": nuevo_estado}
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al cambiar estado de usuario: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al cambiar estado de usuario: {str(e)}")

# ============================================================================
#                           ENDPOINTS DE ROLES (SISTEMA COMPLETO)
# ============================================================================

@app.get("/api/roles", response_model=dict)
async def listar_roles(
    incluir_permisos: bool = False,
    activo: Optional[bool] = None,
    db: Database = Depends(get_db)
):
    """Listar todos los roles del sistema con opción de incluir permisos"""
    try:
        # Verificar conexión
        if not db.connection:
            db.connect()
        
        # Construir query
        query = """
            SELECT r.*, 
                   p.nombre_puesto as puesto_nombre,
                   (SELECT COUNT(*) FROM Usuarios_Roles ur WHERE ur.id_rol = r.id_rol AND ur.activo = 1) as usuarios_count
            FROM Roles r
            LEFT JOIN Puestos p ON r.id_puesto = p.id_puesto
            WHERE 1=1
        """
        params = []
        
        if activo is not None:
            query += " AND r.activo = ?"
            params.append(1 if activo else 0)
        
        query += " ORDER BY r.nivel_acceso DESC, r.nombre"
        
        roles = db.fetch_all(query, tuple(params))
        
        # Incluir permisos si se solicita
        if incluir_permisos:
            for rol in roles:
                permisos = db.fetch_all("""
                    SELECT p.*, rp.concedido
                    FROM Roles_Permisos rp
                    JOIN Permisos p ON rp.id_permiso = p.id_permiso
                    WHERE rp.id_rol = ? AND p.activo = 1
                    ORDER BY p.modulo, p.accion
                """, (rol['id_rol'],))
                rol['permisos'] = permisos
                rol['permisos_count'] = len(permisos)
        
        return {
            "success": True,
            "data": roles,
            "count": len(roles)
        }
    except Exception as e:
        logger.error(f"Error al obtener roles: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al obtener roles: {str(e)}")

@app.get("/api/roles/{rol_id}", response_model=dict)
async def obtener_rol(rol_id: int, db: Database = Depends(get_db)):
    """Obtener un rol específico con sus permisos"""
    try:
        if not db.connection:
            db.connect()
        
        # Obtener rol
        rol = db.fetch_one("""
            SELECT r.*, 
                   p.nombre_puesto as puesto_nombre,
                   (SELECT COUNT(*) FROM Usuarios_Roles ur WHERE ur.id_rol = r.id_rol AND ur.activo = 1) as usuarios_count
            FROM Roles r
            LEFT JOIN Puestos p ON r.id_puesto = p.id_puesto
            WHERE r.id_rol = ?
        """, (rol_id,))
        
        if not rol:
            raise HTTPException(status_code=404, detail=f"Rol con ID {rol_id} no encontrado")
        
        # Obtener permisos del rol
        permisos = db.fetch_all("""
            SELECT p.*, rp.concedido
            FROM Roles_Permisos rp
            JOIN Permisos p ON rp.id_permiso = p.id_permiso
            WHERE rp.id_rol = ?
            ORDER BY p.modulo, p.accion
        """, (rol_id,))
        
        rol['permisos'] = permisos
        rol['permisos_count'] = len(permisos)
        
        return {
            "success": True,
            "data": rol
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener rol: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al obtener rol: {str(e)}")

@app.post("/api/roles", response_model=dict, status_code=201)
async def crear_rol(rol: RolCreate, db: Database = Depends(get_db)):
    """Crear un nuevo rol en el sistema"""
    try:
        if not db.connection:
            db.connect()
        
        # Verificar que no exista un rol con el mismo nombre
        rol_existente = db.fetch_one("SELECT id_rol FROM Roles WHERE nombre = ?", (rol.nombre.lower(),))
        if rol_existente:
            raise HTTPException(status_code=400, detail=f"Ya existe un rol con el nombre '{rol.nombre}'")
        
        # Verificar que el puesto existe si se proporcionó
        if rol.id_puesto:
            puesto = db.fetch_one("SELECT id_puesto FROM Puestos WHERE id_puesto = ?", (rol.id_puesto,))
            if not puesto:
                raise HTTPException(status_code=404, detail=f"Puesto con ID {rol.id_puesto} no encontrado")
        
        # Crear el rol
        cursor = db.execute_query("""
            INSERT INTO Roles (nombre, descripcion, id_puesto, nivel_acceso, es_sistema)
            VALUES (?, ?, ?, ?, 0)
        """, (rol.nombre.lower(), rol.descripcion, rol.id_puesto, rol.nivel_acceso))
        
        rol_id = cursor.lastrowid
        
        # Asignar permisos si se proporcionaron
        if rol.permisos:
            for permiso_id in rol.permisos:
                try:
                    db.execute_query("""
                        INSERT INTO Roles_Permisos (id_rol, id_permiso)
                        VALUES (?, ?)
                    """, (rol_id, permiso_id))
                except Exception as e:
                    logger.warning(f"Error al asignar permiso {permiso_id}: {str(e)}")
        
        # Obtener el rol creado
        nuevo_rol = db.fetch_one("""
            SELECT r.*, p.nombre_puesto as puesto_nombre
            FROM Roles r
            LEFT JOIN Puestos p ON r.id_puesto = p.id_puesto
            WHERE r.id_rol = ?
        """, (rol_id,))
        
        return {
            "success": True,
            "message": "Rol creado exitosamente",
            "data": nuevo_rol
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al crear rol: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al crear rol: {str(e)}")

@app.put("/api/roles/{rol_id}", response_model=dict)
async def actualizar_rol(rol_id: int, rol: RolUpdate, db: Database = Depends(get_db)):
    """Actualizar un rol existente"""
    try:
        if not db.connection:
            db.connect()
        
        # Verificar que el rol existe
        rol_existente = db.fetch_one("SELECT id_rol, es_sistema FROM Roles WHERE id_rol = ?", (rol_id,))
        if not rol_existente:
            raise HTTPException(status_code=404, detail=f"Rol con ID {rol_id} no encontrado")
        
        # No permitir modificar roles del sistema protegidos
        if rol_existente['es_sistema'] and rol.nombre:
            raise HTTPException(status_code=403, detail="No se puede modificar el nombre de un rol del sistema")
        
        # Construir actualización dinámica
        campos_actualizar = []
        valores = []
        
        if rol.nombre is not None:
            # Verificar que no exista otro rol con el mismo nombre
            otro_rol = db.fetch_one(
                "SELECT id_rol FROM Roles WHERE nombre = ? AND id_rol != ?",
                (rol.nombre.lower(), rol_id)
            )
            if otro_rol:
                raise HTTPException(status_code=400, detail=f"Ya existe otro rol con el nombre '{rol.nombre}'")
            campos_actualizar.append("nombre = ?")
            valores.append(rol.nombre.lower())
        
        if rol.descripcion is not None:
            campos_actualizar.append("descripcion = ?")
            valores.append(rol.descripcion)
        
        if rol.id_puesto is not None:
            if rol.id_puesto > 0:
                puesto = db.fetch_one("SELECT id_puesto FROM Puestos WHERE id_puesto = ?", (rol.id_puesto,))
                if not puesto:
                    raise HTTPException(status_code=404, detail=f"Puesto con ID {rol.id_puesto} no encontrado")
            campos_actualizar.append("id_puesto = ?")
            valores.append(rol.id_puesto if rol.id_puesto > 0 else None)
        
        if rol.nivel_acceso is not None:
            campos_actualizar.append("nivel_acceso = ?")
            valores.append(rol.nivel_acceso)
        
        if rol.activo is not None:
            campos_actualizar.append("activo = ?")
            valores.append(1 if rol.activo else 0)
        
        if not campos_actualizar:
            # Sin cambios, retornar el rol actual
            rol_actual = db.fetch_one("""
                SELECT r.*, p.nombre_puesto as puesto_nombre
                FROM Roles r
                LEFT JOIN Puestos p ON r.id_puesto = p.id_puesto
                WHERE r.id_rol = ?
            """, (rol_id,))
            return {
                "success": True,
                "message": "No hay cambios para aplicar",
                "data": rol_actual
            }
        
        # Agregar fecha de modificación
        campos_actualizar.append("fecha_modificacion = CURRENT_TIMESTAMP")
        valores.append(rol_id)
        
        # Ejecutar actualización
        query = f"UPDATE Roles SET {', '.join(campos_actualizar)} WHERE id_rol = ?"
        db.execute_query(query, tuple(valores))
        
        # Obtener rol actualizado
        rol_actualizado = db.fetch_one("""
            SELECT r.*, p.nombre_puesto as puesto_nombre
            FROM Roles r
            LEFT JOIN Puestos p ON r.id_puesto = p.id_puesto
            WHERE r.id_rol = ?
        """, (rol_id,))
        
        return {
            "success": True,
            "message": "Rol actualizado exitosamente",
            "data": rol_actualizado
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar rol: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al actualizar rol: {str(e)}")

@app.delete("/api/roles/{rol_id}", response_model=dict)
async def eliminar_rol(rol_id: int, db: Database = Depends(get_db)):
    """Eliminar (desactivar) un rol"""
    try:
        if not db.connection:
            db.connect()
        
        # Verificar que el rol existe
        rol = db.fetch_one("SELECT id_rol, nombre, es_sistema FROM Roles WHERE id_rol = ?", (rol_id,))
        if not rol:
            raise HTTPException(status_code=404, detail=f"Rol con ID {rol_id} no encontrado")
        
        # No permitir eliminar roles del sistema
        if rol['es_sistema']:
            raise HTTPException(status_code=403, detail="No se puede eliminar un rol del sistema")
        
        # Verificar si hay usuarios con este rol
        usuarios_count = db.fetch_one(
            "SELECT COUNT(*) as count FROM Usuarios_Roles WHERE id_rol = ? AND activo = 1",
            (rol_id,)
        )
        
        if usuarios_count and usuarios_count['count'] > 0:
            raise HTTPException(
                status_code=400,
                detail=f"No se puede eliminar el rol '{rol['nombre']}' porque tiene {usuarios_count['count']} usuario(s) asignado(s)"
            )
        
        # Desactivar el rol (soft delete)
        db.execute_query("UPDATE Roles SET activo = 0 WHERE id_rol = ?", (rol_id,))
        
        return {
            "success": True,
            "message": f"Rol '{rol['nombre']}' desactivado exitosamente"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar rol: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al eliminar rol: {str(e)}")

@app.post("/api/roles/{rol_id}/permisos", response_model=dict)
async def asignar_permisos_rol(rol_id: int, asignacion: AsignarPermisosRol, db: Database = Depends(get_db)):
    """Asignar permisos a un rol"""
    try:
        if not db.connection:
            db.connect()
        
        # Verificar que el rol existe
        rol = db.fetch_one("SELECT id_rol, nombre FROM Roles WHERE id_rol = ?", (rol_id,))
        if not rol:
            raise HTTPException(status_code=404, detail=f"Rol con ID {rol_id} no encontrado")
        
        # Si se debe reemplazar, eliminar permisos existentes
        if asignacion.reemplazar:
            db.execute_query("DELETE FROM Roles_Permisos WHERE id_rol = ?", (rol_id,))
        
        # Asignar nuevos permisos
        permisos_asignados = 0
        for permiso_id in asignacion.permisos:
            try:
                # Verificar que el permiso existe
                permiso = db.fetch_one("SELECT id_permiso FROM Permisos WHERE id_permiso = ?", (permiso_id,))
                if permiso:
                    db.execute_query("""
                        INSERT OR REPLACE INTO Roles_Permisos (id_rol, id_permiso)
                        VALUES (?, ?)
                    """, (rol_id, permiso_id))
                    permisos_asignados += 1
            except Exception as e:
                logger.warning(f"Error al asignar permiso {permiso_id}: {str(e)}")
        
        return {
            "success": True,
            "message": f"{permisos_asignados} permiso(s) asignado(s) al rol '{rol['nombre']}'",
            "data": {
                "rol_id": rol_id,
                "permisos_asignados": permisos_asignados
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al asignar permisos: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al asignar permisos: {str(e)}")

# ============================================================================
#                           ENDPOINTS DE AUDITORÍA
# ============================================================================

@app.get("/api/usuarios/auditoria", response_model=dict)
async def listar_auditoria(
    usuario_id: Optional[int] = None,
    modulo: Optional[str] = None,
    accion: Optional[str] = None,
    fecha_desde: Optional[str] = None,
    fecha_hasta: Optional[str] = None,
    db: Database = Depends(get_db)
):
    """Listar registros de auditoría con filtros opcionales"""
    try:
        # Verificar que la conexión a la base de datos esté activa
        if not db.connection:
            db.connect()
        
        query = """
            SELECT 
                a.id_auditoria as id,
                a.usuario_id,
                u.nombre as nombre_usuario,
                a.accion,
                a.modulo,
                a.detalles,
                a.ip_address,
                a.fecha_accion as timestamp,
                CASE 
                    WHEN a.accion LIKE '%exitos%' OR a.accion LIKE '%crear%' OR a.accion LIKE '%actualizar%' THEN 'exitoso'
                    WHEN a.accion LIKE '%fallido%' OR a.accion LIKE '%error%' THEN 'fallido'
                    ELSE 'info'
                END as resultado
            FROM Usuarios_Auditoria a
            LEFT JOIN usuarios u ON a.usuario_id = u.id
            WHERE 1=1
        """
        params = []
        
        if usuario_id:
            query += " AND a.usuario_id = ?"
            params.append(usuario_id)
        if modulo:
            query += " AND a.modulo = ?"
            params.append(modulo)
        if accion:
            query += " AND a.accion = ?"
            params.append(accion)
        if fecha_desde:
            query += " AND DATE(a.fecha_accion) >= ?"
            params.append(fecha_desde)
        if fecha_hasta:
            query += " AND DATE(a.fecha_accion) <= ?"
            params.append(fecha_hasta)
        
        query += " ORDER BY a.fecha_accion DESC"
        
        try:
            logs = db.fetch_all(query, tuple(params))
        except Exception as e:
            # Si la tabla no existe, retornar lista vacía
            logger.warning(f"Error al consultar auditoría: {str(e)}")
            logs = []
        
        return {
            "success": True,
            "data": logs,
            "count": len(logs)
        }
    except Exception as e:
        logger.error(f"Error al obtener auditoría: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al obtener auditoría: {str(e)}")

@app.post("/api/usuarios/auditoria", response_model=dict)
async def crear_log_auditoria(log_data: dict, db: Database = Depends(get_db)):
    """Crear un nuevo registro de auditoría"""
    try:
        # Verificar que la conexión a la base de datos esté activa
        if not db.connection:
            db.connect()
        
        cursor = db.execute_query("""
            INSERT INTO Usuarios_Auditoria (usuario_id, accion, modulo, detalles, ip_address)
            VALUES (?, ?, ?, ?, ?)
        """, (
            log_data.get('usuario_id'),
            log_data.get('accion', 'Acción no especificada'),
            log_data.get('modulo'),
            log_data.get('detalles'),
            log_data.get('ip_address')
        ))
        
        return {
            "success": True,
            "message": "Log de auditoría creado exitosamente",
            "data": {"id": cursor.lastrowid}
        }
    except Exception as e:
        logger.error(f"Error al crear log de auditoría: {str(e)}")
        # No lanzar error si la tabla no existe, solo loguear
        return {
            "success": False,
            "message": f"Error al crear log de auditoría: {str(e)}"
        }

# ============================================================================
#                           ENDPOINTS DE PERMISOS
# ============================================================================

@app.get("/api/permisos", response_model=dict)
async def listar_permisos(
    modulo: Optional[str] = None,
    activo: Optional[bool] = None,
    db: Database = Depends(get_db)
):
    """Listar todos los permisos del sistema"""
    try:
        if not db.connection:
            db.connect()
        
        query = "SELECT * FROM Permisos WHERE 1=1"
        params = []
        
        if modulo:
            query += " AND modulo = ?"
            params.append(modulo)
        
        if activo is not None:
            query += " AND activo = ?"
            params.append(1 if activo else 0)
        
        query += " ORDER BY modulo, accion"
        
        permisos = db.fetch_all(query, tuple(params))
        
        # Agrupar por módulo
        permisos_por_modulo = {}
        for permiso in permisos:
            mod = permiso['modulo']
            if mod not in permisos_por_modulo:
                permisos_por_modulo[mod] = []
            permisos_por_modulo[mod].append(permiso)
        
        return {
            "success": True,
            "data": permisos,
            "por_modulo": permisos_por_modulo,
            "count": len(permisos)
        }
    except Exception as e:
        logger.error(f"Error al obtener permisos: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al obtener permisos: {str(e)}")

@app.post("/api/permisos", response_model=dict, status_code=201)
async def crear_permiso(permiso: PermisoCreate, db: Database = Depends(get_db)):
    """Crear un nuevo permiso personalizado"""
    try:
        if not db.connection:
            db.connect()
        
        # Verificar que no exista el código
        existente = db.fetch_one("SELECT id_permiso FROM Permisos WHERE codigo = ?", (permiso.codigo,))
        if existente:
            raise HTTPException(status_code=400, detail=f"Ya existe un permiso con el código '{permiso.codigo}'")
        
        # Crear permiso
        cursor = db.execute_query("""
            INSERT INTO Permisos (nombre, descripcion, modulo, accion, codigo)
            VALUES (?, ?, ?, ?, ?)
        """, (permiso.nombre, permiso.descripcion, permiso.modulo, permiso.accion, permiso.codigo))
        
        # Obtener permiso creado
        nuevo_permiso = db.fetch_one(
            "SELECT * FROM Permisos WHERE id_permiso = ?",
            (cursor.lastrowid,)
        )
        
        return {
            "success": True,
            "message": "Permiso creado exitosamente",
            "data": nuevo_permiso
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al crear permiso: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al crear permiso: {str(e)}")

@app.get("/api/usuarios/{usuario_id}/permisos", response_model=dict)
async def obtener_permisos_usuario(usuario_id: int, db: Database = Depends(get_db)):
    """Obtener todos los permisos de un usuario (heredados de roles + permisos especiales)"""
    try:
        if not db.connection:
            db.connect()
        
        # Verificar que el usuario existe
        usuario = db.fetch_one(
            "SELECT id, nombre, email, rol FROM usuarios WHERE id = ?",
            (usuario_id,)
        )
        if not usuario:
            raise HTTPException(status_code=404, detail=f"Usuario con ID {usuario_id} no encontrado")
        
        # Obtener roles del usuario
        roles = db.fetch_all("""
            SELECT r.*, ur.es_principal, ur.fecha_asignacion
            FROM Usuarios_Roles ur
            JOIN Roles r ON ur.id_rol = r.id_rol
            WHERE ur.usuario_id = ? AND ur.activo = 1 AND r.activo = 1
            ORDER BY ur.es_principal DESC, r.nivel_acceso DESC
        """, (usuario_id,))
        
        # Obtener permisos de los roles
        permisos_rol = []
        permisos_codigos = set()
        
        for rol in roles:
            permisos = db.fetch_all("""
                SELECT p.*, rp.concedido
                FROM Roles_Permisos rp
                JOIN Permisos p ON rp.id_permiso = p.id_permiso
                WHERE rp.id_rol = ? AND p.activo = 1 AND rp.concedido = 1
            """, (rol['id_rol'],))
            
            for permiso in permisos:
                if permiso['codigo'] not in permisos_codigos:
                    permiso['origen'] = f"Rol: {rol['nombre']}"
                    permisos_rol.append(permiso)
                    permisos_codigos.add(permiso['codigo'])
        
        # Obtener permisos especiales del usuario
        permisos_especiales = db.fetch_all("""
            SELECT p.*, up.concedido, up.razon, up.fecha_asignacion
            FROM Usuarios_Permisos up
            JOIN Permisos p ON up.id_permiso = p.id_permiso
            WHERE up.usuario_id = ? AND p.activo = 1
              AND (up.fecha_expiracion IS NULL OR up.fecha_expiracion > CURRENT_TIMESTAMP)
        """, (usuario_id,))
        
        for permiso_esp in permisos_especiales:
            permiso_esp['origen'] = 'Permiso especial'
            if permiso_esp['concedido']:
                permisos_codigos.add(permiso_esp['codigo'])
        
        # Lista final de códigos de permisos
        permisos_totales = list(permisos_codigos)
        
        return {
            "success": True,
            "data": {
                "usuario_id": usuario_id,
                "nombre_usuario": usuario['nombre'],
                "email": usuario['email'],
                "rol_legacy": usuario['rol'],
                "roles": roles,
                "permisos_rol": permisos_rol,
                "permisos_especiales": permisos_especiales,
                "permisos_totales": permisos_totales,
                "count_roles": len(roles),
                "count_permisos": len(permisos_totales)
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener permisos del usuario: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al obtener permisos del usuario: {str(e)}")

@app.post("/api/usuarios/{usuario_id}/roles", response_model=dict)
async def asignar_rol_usuario(usuario_id: int, asignacion: AsignarRolUsuario, db: Database = Depends(get_db)):
    """Asignar un rol a un usuario"""
    try:
        if not db.connection:
            db.connect()
        
        # Verificar que el usuario existe
        usuario = db.fetch_one("SELECT id, nombre FROM usuarios WHERE id = ?", (usuario_id,))
        if not usuario:
            raise HTTPException(status_code=404, detail=f"Usuario con ID {usuario_id} no encontrado")
        
        # Verificar que el rol existe
        rol = db.fetch_one("SELECT id_rol, nombre FROM Roles WHERE id_rol = ?", (asignacion.id_rol,))
        if not rol:
            raise HTTPException(status_code=404, detail=f"Rol con ID {asignacion.id_rol} no encontrado")
        
        # Si es rol principal, quitar principal de otros roles
        if asignacion.es_principal:
            db.execute_query(
                "UPDATE Usuarios_Roles SET es_principal = 0 WHERE usuario_id = ?",
                (usuario_id,)
            )
        
        # Asignar rol
        try:
            db.execute_query("""
                INSERT INTO Usuarios_Roles (usuario_id, id_rol, es_principal, fecha_expiracion)
                VALUES (?, ?, ?, ?)
            """, (usuario_id, asignacion.id_rol, 1 if asignacion.es_principal else 0, asignacion.fecha_expiracion))
        except Exception as e:
            # Si ya existe, actualizar
            db.execute_query("""
                UPDATE Usuarios_Roles 
                SET es_principal = ?, fecha_expiracion = ?, activo = 1
                WHERE usuario_id = ? AND id_rol = ?
            """, (1 if asignacion.es_principal else 0, asignacion.fecha_expiracion, usuario_id, asignacion.id_rol))
        
        # Actualizar rol en tabla usuarios (compatibilidad)
        if asignacion.es_principal:
            db.execute_query(
                "UPDATE usuarios SET rol = ? WHERE id = ?",
                (rol['nombre'], usuario_id)
            )
        
        # Registrar en historial
        db.execute_query("""
            INSERT INTO Historial_Roles (usuario_id, id_rol_nuevo, motivo)
            VALUES (?, ?, ?)
        """, (usuario_id, asignacion.id_rol, "Asignación de rol"))
        
        return {
            "success": True,
            "message": f"Rol '{rol['nombre']}' asignado a '{usuario['nombre']}' exitosamente"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al asignar rol: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al asignar rol: {str(e)}")

# ============================================================================
#               ENDPOINT DE SINCRONIZACIÓN EMPLEADO-USUARIO
# ============================================================================

@app.post("/api/empleados/{empleado_id}/sincronizar-usuario", response_model=dict)
async def sincronizar_empleado_usuario(empleado_id: int, sincronizacion: SincronizarEmpleadoUsuario, db: Database = Depends(get_db)):
    """Sincronizar un empleado con un usuario del sistema, asignando rol basado en su puesto"""
    try:
        if not db.connection:
            db.connect()
        
        # Obtener información del empleado
        empleado = db.fetch_one("""
            SELECT e.*, p.nombre_puesto, p.id_puesto
            FROM Empleados e
            LEFT JOIN Puestos p ON e.id_puesto = p.id_puesto
            WHERE e.id_empleado = ?
        """, (empleado_id,))
        
        if not empleado:
            raise HTTPException(status_code=404, detail=f"Empleado con ID {empleado_id} no encontrado")
        
        # Buscar si ya existe un usuario con ese correo
        usuario_existente = db.fetch_one(
            "SELECT id, nombre, rol FROM usuarios WHERE email = ?",
            (empleado['correo'],)
        )
        
        usuario_id = None
        mensaje = ""
        
        if usuario_existente:
            usuario_id = usuario_existente['id']
            mensaje = f"Usuario existente vinculado: {usuario_existente['nombre']}"
        elif sincronizacion.crear_usuario:
            # Crear nuevo usuario
            password = sincronizacion.password_temporal or "Temporal123!"
            password_hash = hash_password(password)
            
            # Determinar rol por defecto
            rol_default = "empleado"
            
            cursor = db.execute_query("""
                INSERT INTO usuarios (nombre, email, password, rol)
                VALUES (?, ?, ?, ?)
            """, (
                f"{empleado['nombre']} {empleado['apellido']}",
                empleado['correo'],
                password_hash,
                rol_default
            ))
            
            usuario_id = cursor.lastrowid
            mensaje = f"Usuario creado exitosamente con contraseña temporal"
        else:
            raise HTTPException(
                status_code=404,
                detail=f"No existe usuario con el email {empleado['correo']}. Active 'crear_usuario' para crearlo."
            )
        
        # Asignar rol basado en el puesto si se solicita
        if sincronizacion.asignar_rol_automatico and empleado['id_puesto']:
            # Buscar rol vinculado al puesto
            rol_puesto = db.fetch_one(
                "SELECT id_rol, nombre FROM Roles WHERE id_puesto = ? AND activo = 1",
                (empleado['id_puesto'],)
            )
            
            if rol_puesto:
                # Asignar rol
                try:
                    db.execute_query("""
                        INSERT OR REPLACE INTO Usuarios_Roles (usuario_id, id_rol, es_principal)
                        VALUES (?, ?, 1)
                    """, (usuario_id, rol_puesto['id_rol']))
                    
                    # Actualizar rol en tabla usuarios
                    db.execute_query(
                        "UPDATE usuarios SET rol = ? WHERE id = ?",
                        (rol_puesto['nombre'], usuario_id)
                    )
                    
                    mensaje += f" | Rol asignado: {rol_puesto['nombre']} (basado en puesto: {empleado['nombre_puesto']})"
                except Exception as e:
                    logger.warning(f"Error al asignar rol automático: {str(e)}")
        
        # Obtener datos finales del usuario
        usuario_final = db.fetch_one("""
            SELECT u.id, u.nombre, u.email, u.rol,
                   (SELECT COUNT(*) FROM Usuarios_Roles WHERE usuario_id = u.id AND activo = 1) as roles_count
            FROM usuarios u
            WHERE u.id = ?
        """, (usuario_id,))
        
        return {
            "success": True,
            "message": mensaje,
            "data": {
                "empleado": {
                    "id": empleado['id_empleado'],
                    "nombre": f"{empleado['nombre']} {empleado['apellido']}",
                    "puesto": empleado['nombre_puesto']
                },
                "usuario": usuario_final
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al sincronizar empleado-usuario: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al sincronizar empleado-usuario: {str(e)}")

# ============================================================================
#                           ENDPOINTS DE PUESTOS
# ============================================================================

@app.get("/api/puestos", response_model=dict)
async def listar_puestos(db: Database = Depends(get_db)):
    """Listar todos los puestos"""
    try:
        # Verificar que la conexión a la base de datos esté activa
        if not db.connection:
            db.connect()
        
        puestos = []
        
        try:
            puestos = db.fetch_all(
                "SELECT id_puesto, nombre_puesto, nivel, salario_base FROM Puestos ORDER BY nombre_puesto"
            )
        except Exception as e:
            error_msg = str(e).lower()
            logger.warning(f"Error al consultar puestos: {str(e)}")
            
            # Si la tabla no existe, retornar lista vacía
            if 'no such table' in error_msg or 'does not exist' in error_msg:
                logger.info("Tabla Puestos no existe, retornando lista vacía")
                puestos = []
            else:
                puestos = []
        
        return {
            "success": True,
            "data": puestos,
            "count": len(puestos)
        }
    except Exception as e:
        logger.error(f"Error inesperado al obtener puestos: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener puestos: {str(e)}"
        )

@app.get("/api/puestos/nombres", response_model=dict)
async def listar_nombres_puestos(db: Database = Depends(get_db)):
    """Listar solo los nombres de los puestos disponibles"""
    try:
        # Verificar que la conexión a la base de datos esté activa
        if not db.connection:
            db.connect()
        
        nombres_puestos = []
        
        try:
            puestos = db.fetch_all(
                "SELECT DISTINCT nombre_puesto FROM Puestos WHERE nombre_puesto IS NOT NULL ORDER BY nombre_puesto"
            )
            nombres_puestos = [p['nombre_puesto'] for p in puestos]
        except Exception as e:
            error_msg = str(e).lower()
            logger.warning(f"Error al consultar nombres de puestos: {str(e)}")
            
            # Si la tabla no existe, retornar lista vacía
            if 'no such table' in error_msg or 'does not exist' in error_msg:
                logger.info("Tabla Puestos no existe, retornando lista vacía")
                nombres_puestos = []
            else:
                nombres_puestos = []
        
        return {
            "success": True,
            "data": nombres_puestos,
            "count": len(nombres_puestos)
        }
    except Exception as e:
        logger.error(f"Error inesperado al obtener nombres de puestos: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener nombres de puestos: {str(e)}"
        )

@app.get("/api/puestos/{puesto_id}", response_model=dict)
async def obtener_puesto(puesto_id: int, db: Database = Depends(get_db)):
    """Obtener un puesto por ID"""
    try:
        # Verificar que la conexión a la base de datos esté activa
        if not db.connection:
            db.connect()
        
        puesto = db.fetch_one(
            "SELECT id_puesto, nombre_puesto, nivel, salario_base FROM Puestos WHERE id_puesto = ?",
            (puesto_id,)
        )
        
        if not puesto:
            raise HTTPException(
                status_code=404,
                detail=f"Puesto con ID {puesto_id} no encontrado"
            )
        
        return {
            "success": True,
            "data": puesto
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener puesto: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener puesto: {str(e)}"
        )

@app.post("/api/puestos", response_model=dict, status_code=201)
async def crear_puesto(puesto: PuestoCreate, db: Database = Depends(get_db)):
    """Crear un nuevo puesto"""
    try:
        # Verificar que la conexión a la base de datos esté activa
        if not db.connection:
            db.connect()
        
        # Verificar si ya existe un puesto con el mismo nombre
        puesto_existente = db.fetch_one(
            "SELECT id_puesto FROM Puestos WHERE nombre_puesto = ?",
            (puesto.nombre_puesto,)
        )
        
        if puesto_existente:
            raise HTTPException(
                status_code=400,
                detail=f"Ya existe un puesto con el nombre '{puesto.nombre_puesto}'"
            )
        
        # Insertar el nuevo puesto
        cursor = db.execute_query(
            """
            INSERT INTO Puestos (nombre_puesto, nivel, salario_base)
            VALUES (?, ?, ?)
            """,
            (puesto.nombre_puesto, puesto.nivel, puesto.salario_base)
        )
        
        # Obtener el puesto recién creado
        nuevo_puesto = db.fetch_one(
            "SELECT id_puesto, nombre_puesto, nivel, salario_base FROM Puestos WHERE id_puesto = ?",
            (cursor.lastrowid,)
        )
        
        return {
            "success": True,
            "message": "Puesto creado exitosamente",
            "data": nuevo_puesto
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al crear puesto: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear puesto: {str(e)}"
        )

@app.put("/api/puestos/{puesto_id}", response_model=dict)
async def actualizar_puesto(puesto_id: int, puesto: PuestoUpdate, db: Database = Depends(get_db)):
    """Actualizar un puesto existente"""
    try:
        # Verificar que la conexión a la base de datos esté activa
        if not db.connection:
            db.connect()
        
        # Verificar que el puesto existe
        puesto_existente = db.fetch_one(
            "SELECT id_puesto FROM Puestos WHERE id_puesto = ?",
            (puesto_id,)
        )
        
        if not puesto_existente:
            raise HTTPException(
                status_code=404,
                detail=f"Puesto con ID {puesto_id} no encontrado"
            )
        
        # Construir la consulta de actualización dinámicamente
        campos_actualizar = []
        valores = []
        
        if puesto.nombre_puesto is not None:
            # Verificar que no exista otro puesto con el mismo nombre
            otro_puesto = db.fetch_one(
                "SELECT id_puesto FROM Puestos WHERE nombre_puesto = ? AND id_puesto != ?",
                (puesto.nombre_puesto, puesto_id)
            )
            if otro_puesto:
                raise HTTPException(
                    status_code=400,
                    detail=f"Ya existe otro puesto con el nombre '{puesto.nombre_puesto}'"
                )
            campos_actualizar.append("nombre_puesto = ?")
            valores.append(puesto.nombre_puesto)
        
        if puesto.nivel is not None:
            campos_actualizar.append("nivel = ?")
            valores.append(puesto.nivel)
        
        if puesto.salario_base is not None:
            campos_actualizar.append("salario_base = ?")
            valores.append(puesto.salario_base)
        
        # Si no hay campos para actualizar, retornar el puesto sin cambios
        if not campos_actualizar:
            puesto_actual = db.fetch_one(
                "SELECT id_puesto, nombre_puesto, nivel, salario_base FROM Puestos WHERE id_puesto = ?",
                (puesto_id,)
            )
            return {
                "success": True,
                "message": "No hay cambios para aplicar",
                "data": puesto_actual
            }
        
        # Agregar el ID al final de los valores
        valores.append(puesto_id)
        
        # Ejecutar la actualización
        query = f"UPDATE Puestos SET {', '.join(campos_actualizar)} WHERE id_puesto = ?"
        db.execute_query(query, tuple(valores))
        
        # Obtener el puesto actualizado
        puesto_actualizado = db.fetch_one(
            "SELECT id_puesto, nombre_puesto, nivel, salario_base FROM Puestos WHERE id_puesto = ?",
            (puesto_id,)
        )
        
        return {
            "success": True,
            "message": "Puesto actualizado exitosamente",
            "data": puesto_actualizado
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar puesto: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar puesto: {str(e)}"
        )

@app.delete("/api/puestos/{puesto_id}", response_model=dict)
async def eliminar_puesto(puesto_id: int, db: Database = Depends(get_db)):
    """Eliminar un puesto (solo si no está asignado a empleados)"""
    try:
        # Verificar que la conexión a la base de datos esté activa
        if not db.connection:
            db.connect()
        
        # Verificar que el puesto existe
        puesto = db.fetch_one(
            "SELECT id_puesto, nombre_puesto FROM Puestos WHERE id_puesto = ?",
            (puesto_id,)
        )
        
        if not puesto:
            raise HTTPException(
                status_code=404,
                detail=f"Puesto con ID {puesto_id} no encontrado"
            )
        
        # Verificar que no hay empleados asignados a este puesto
        empleados_asignados = db.fetch_one(
            "SELECT COUNT(*) as count FROM Empleados WHERE id_puesto = ?",
            (puesto_id,)
        )
        
        if empleados_asignados and empleados_asignados['count'] > 0:
            raise HTTPException(
                status_code=400,
                detail=f"No se puede eliminar el puesto '{puesto['nombre_puesto']}' porque tiene {empleados_asignados['count']} empleado(s) asignado(s)"
            )
        
        # Eliminar el puesto
        db.execute_query(
            "DELETE FROM Puestos WHERE id_puesto = ?",
            (puesto_id,)
        )
        
        return {
            "success": True,
            "message": f"Puesto '{puesto['nombre_puesto']}' eliminado exitosamente"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar puesto: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al eliminar puesto: {str(e)}"
        )

# ============================================================================
#                           ENDPOINTS DE DEPARTAMENTOS
# ============================================================================

@app.get("/api/departamentos", response_model=dict)
async def listar_departamentos(db: Database = Depends(get_db)):
    """Listar todos los departamentos"""
    try:
        # Verificar que la conexión a la base de datos esté activa
        if not db.connection:
            db.connect()
        
        departamentos = []
        
        # Intentar obtener de la tabla nueva primero (Departamentos con mayúscula)
        try:
            departamentos = db.fetch_all(
                "SELECT id_departamento as id, nombre_departamento as nombre, descripcion FROM Departamentos"
            )
        except Exception as table_error:
            error_msg = str(table_error).lower()
            logger.warning(f"Error al consultar tabla Departamentos: {str(table_error)}")
            
            # Si la tabla no existe, intentar con la tabla antigua
            if 'no such table' in error_msg or 'does not exist' in error_msg:
                logger.info("Tabla Departamentos no existe, intentando con tabla antigua 'departamentos'")
                try:
                    departamentos = db.fetch_all(
                        "SELECT id, nombre, descripcion, fecha_creacion, activo FROM departamentos WHERE activo = 1"
                    )
                except Exception as old_table_error:
                    logger.error(f"Error al consultar tabla antigua departamentos: {str(old_table_error)}")
                    # Si ambas fallan, retornar lista vacía en lugar de error
                    departamentos = []
            else:
                # Si es otro tipo de error, intentar con la tabla antigua como fallback
                try:
                    departamentos = db.fetch_all(
                        "SELECT id, nombre, descripcion, fecha_creacion, activo FROM departamentos WHERE activo = 1"
                    )
                except Exception as fallback_error:
                    logger.error(f"Error en fallback al consultar departamentos: {str(fallback_error)}")
                    departamentos = []
        
        return {
            "status": "success",
            "data": departamentos,
            "count": len(departamentos)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado al obtener departamentos: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error al obtener departamentos: {str(e)}")

@app.get("/api/departamentos/{departamento_id}", response_model=dict)
async def obtener_departamento(departamento_id: int, db: Database = Depends(get_db)):
    """Obtener un departamento por ID"""
    try:
        # Verificar que la conexión a la base de datos esté activa
        if not db.connection:
            db.connect()
        
        departamento = None
        
        # Intentar tabla nueva primero
        try:
            departamento = db.fetch_one(
                "SELECT id_departamento as id, nombre_departamento as nombre, descripcion FROM Departamentos WHERE id_departamento = ?",
                (departamento_id,)
            )
        except Exception as table_error:
            error_msg = str(table_error).lower()
            logger.warning(f"Error al consultar tabla Departamentos: {str(table_error)}")
            
            # Si la tabla no existe, intentar con la tabla antigua
            if 'no such table' in error_msg or 'does not exist' in error_msg:
                logger.info("Tabla Departamentos no existe, intentando con tabla antigua 'departamentos'")
                try:
                    departamento = db.fetch_one(
                        "SELECT id, nombre, descripcion, fecha_creacion, activo FROM departamentos WHERE id = ? AND activo = 1",
                        (departamento_id,)
                    )
                except Exception as old_table_error:
                    logger.error(f"Error al consultar tabla antigua departamentos: {str(old_table_error)}")
                    departamento = None
        
        # Si no se encontró en la tabla nueva, buscar en tabla antigua
        if not departamento:
            try:
                departamento = db.fetch_one(
                    "SELECT id, nombre, descripcion, fecha_creacion, activo FROM departamentos WHERE id = ? AND activo = 1",
                    (departamento_id,)
                )
            except Exception as fallback_error:
                logger.warning(f"Error en fallback al consultar departamento: {str(fallback_error)}")
                departamento = None
        
        if not departamento:
            raise HTTPException(status_code=404, detail=f"Departamento con ID {departamento_id} no encontrado")
        
        return {"status": "success", "data": departamento}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado al obtener departamento: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error al obtener departamento: {str(e)}")

@app.post("/api/departamentos", response_model=dict, status_code=201)
async def crear_departamento(departamento: DepartamentoCreate, db: Database = Depends(get_db)):
    """Crear un nuevo departamento"""
    try:
        cursor = db.execute_query(
            "INSERT INTO Departamentos (nombre_departamento, descripcion) VALUES (?, ?)",
            (departamento.nombre, departamento.descripcion)
        )
        
        nuevo_departamento = db.fetch_one(
            "SELECT id_departamento as id, nombre_departamento as nombre, descripcion FROM Departamentos WHERE id_departamento = ?",
            (cursor.lastrowid,)
        )
        
        return {
            "status": "success",
            "message": "Departamento creado exitosamente",
            "data": nuevo_departamento
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear departamento: {str(e)}")

# ============================================================================
#                           ENDPOINTS DE EMPLEADOS
# ============================================================================

@app.get("/api/empleados", response_model=dict)
async def listar_empleados(db: Database = Depends(get_db)):
    """Listar todos los empleados con información de departamento"""
    try:
        # Verificar que la conexión a la base de datos esté activa
        if not db.connection:
            db.connect()
        
        empleados = []
        
        # Intentar obtener de la tabla nueva (Empleados) primero
        try:
            empleados = db.fetch_all("""
                SELECT 
                    e.id_empleado as id,
                    e.id_empleado,
                    e.nombre,
                    e.apellido,
                    e.correo as email,
                    e.correo,
                    e.telefono,
                    e.direccion,
                    e.fecha_nacimiento,
                    e.genero,
                    e.estado_civil,
                    e.fecha_ingreso,
                    e.estado,
                    e.id_departamento,
                    e.id_puesto,
                    COALESCE(
                        (SELECT salario FROM Contratos 
                         WHERE id_empleado = e.id_empleado 
                         ORDER BY fecha_inicio DESC LIMIT 1),
                        0
                    ) as salario,
                    d.nombre_departamento as departamento_nombre,
                    p.nombre_puesto as puesto_nombre
                FROM Empleados e
                LEFT JOIN Departamentos d ON e.id_departamento = d.id_departamento
                LEFT JOIN Puestos p ON e.id_puesto = p.id_puesto
                ORDER BY e.id_empleado
                LIMIT 40
            """)
        except Exception as table_error:
            # Si falla la tabla nueva, intentar tabla antigua
            logger.warning(f"Error al consultar tabla Empleados, intentando tabla antigua: {str(table_error)}")
            try:
                empleados = db.fetch_all("""
                    SELECT 
                        e.id,
                        e.id as id_empleado,
                        e.nombre,
                        e.apellido,
                        e.email,
                        e.email as correo,
                        e.telefono,
                        e.departamento_id as id_departamento,
                        e.puesto as id_puesto,
                        e.fecha_ingreso,
                        COALESCE(e.salario, 0) as salario,
                        e.activo,
                        CASE WHEN e.activo = 1 THEN 'Activo' ELSE 'Retirado' END as estado,
                        d.nombre as departamento_nombre,
                        COALESCE(p.nombre_puesto, e.puesto, 'Sin puesto asignado') as puesto_nombre,
                        COALESCE(p.nombre_puesto, e.puesto, 'Sin puesto asignado') as cargo,
                        p.nivel as nivel_puesto
                    FROM empleados e
                    LEFT JOIN departamentos d ON e.departamento_id = d.id
                    LEFT JOIN Puestos p ON CAST(e.puesto AS INTEGER) = p.id_puesto
                    WHERE e.activo = 1
                    ORDER BY e.id
                    LIMIT 40
                """)
            except Exception as old_table_error:
                logger.error(f"Error al consultar tabla antigua empleados: {str(old_table_error)}")
                # Si ambas fallan, retornar lista vacía en lugar de error
                empleados = []
        
        return {
            "status": "success",
            "data": empleados,
            "count": len(empleados)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado al obtener empleados: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error al obtener empleados: {str(e)}"
        )

@app.get("/api/empleados/{empleado_id}", response_model=dict)
async def obtener_empleado(empleado_id: int, db: Database = Depends(get_db)):
    """Obtener un empleado por ID"""
    try:
        # Intentar tabla nueva
        empleado = db.fetch_one("""
            SELECT 
                e.id_empleado as id,
                e.id_empleado,
                e.nombre,
                e.apellido,
                e.correo as email,
                e.correo,
                e.telefono,
                e.direccion,
                e.fecha_nacimiento,
                e.genero,
                e.estado_civil,
                e.fecha_ingreso,
                e.estado,
                e.id_departamento,
                e.id_puesto,
                COALESCE(
                    (SELECT salario FROM Contratos 
                     WHERE id_empleado = e.id_empleado 
                     ORDER BY fecha_inicio DESC LIMIT 1),
                    0
                ) as salario,
                d.nombre_departamento as departamento_nombre,
                p.nombre_puesto as puesto_nombre
            FROM Empleados e
            LEFT JOIN Departamentos d ON e.id_departamento = d.id_departamento
            LEFT JOIN Puestos p ON e.id_puesto = p.id_puesto
            WHERE e.id_empleado = ?
        """, (empleado_id,))
        
        # Si no existe, buscar en tabla antigua
        if not empleado:
            empleado = db.fetch_one("""
                SELECT 
                    e.id,
                    e.id as id_empleado,
                    e.nombre,
                    e.apellido,
                    e.email,
                    e.email as correo,
                    e.telefono,
                    e.departamento_id as id_departamento,
                    e.puesto as id_puesto,
                    e.fecha_ingreso,
                    COALESCE(e.salario, 0) as salario,
                    e.activo,
                    CASE WHEN e.activo = 1 THEN 'Activo' ELSE 'Retirado' END as estado,
                    d.nombre as departamento_nombre,
                    COALESCE(p.nombre_puesto, e.puesto) as puesto_nombre,
                    COALESCE(p.nombre_puesto, e.puesto) as cargo,
                    p.nivel as nivel_puesto
                FROM empleados e
                LEFT JOIN departamentos d ON e.departamento_id = d.id
                LEFT JOIN Puestos p ON CAST(e.puesto AS INTEGER) = p.id_puesto
                WHERE e.id = ? AND e.activo = 1
            """, (empleado_id,))
        
        if not empleado:
            raise HTTPException(status_code=404, detail=f"Empleado con ID {empleado_id} no encontrado")
        
        return {"status": "success", "data": empleado}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener empleado {empleado_id}: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error al obtener empleado: {str(e)}")

@app.post("/api/empleados", response_model=dict, status_code=201)
async def crear_empleado(empleado: EmpleadoCreate, db: Database = Depends(get_db)):
    """Crear un nuevo empleado"""
    try:
        # Verificar que el departamento existe
        depto = db.fetch_one("SELECT id_departamento FROM Departamentos WHERE id_departamento = ?", (empleado.departamento_id,))
        if not depto:
            # Intentar tabla antigua
            depto = db.fetch_one("SELECT id FROM departamentos WHERE id = ? AND activo = 1", (empleado.departamento_id,))
            if not depto:
                raise HTTPException(status_code=400, detail=f"Departamento con ID {empleado.departamento_id} no encontrado")
        
        cursor = db.execute_query("""
            INSERT INTO Empleados 
            (nombre, apellido, correo, telefono, fecha_ingreso, estado, id_departamento, puesto)
            VALUES (?, ?, ?, ?, ?, 'Activo', ?, ?)
        """, (
            empleado.nombre,
            empleado.apellido,
            empleado.email,
            empleado.telefono,
            empleado.fecha_ingreso,
            empleado.departamento_id,
            empleado.puesto
        ))
        
        nuevo_empleado = db.fetch_one("""
            SELECT 
                e.id_empleado as id,
                e.id_empleado,
                e.nombre,
                e.apellido,
                e.correo as email,
                e.correo,
                e.telefono,
                e.fecha_ingreso,
                e.estado,
                e.id_departamento,
                e.id_puesto,
                COALESCE(
                    (SELECT salario FROM Contratos 
                     WHERE id_empleado = e.id_empleado 
                     ORDER BY fecha_inicio DESC LIMIT 1),
                    0
                ) as salario,
                d.nombre_departamento as departamento_nombre,
                p.nombre_puesto as puesto_nombre
            FROM Empleados e
            LEFT JOIN Departamentos d ON e.id_departamento = d.id_departamento
            LEFT JOIN Puestos p ON e.id_puesto = p.id_puesto
            WHERE e.id_empleado = ?
        """, (cursor.lastrowid,))
        
        # Crear notificación automática para administradores
        try:
            # Obtener usuarios administradores
            admins = db.fetch_all("SELECT id FROM usuarios WHERE rol = 'administrador'")
            nombre_completo = f"{empleado.nombre} {empleado.apellido}"
            for admin in admins:
                NotificationHelper.notificar_empleado_creado(
                    db, admin['id'], nombre_completo, cursor.lastrowid
                )
        except Exception as notif_error:
            logger.warning(f"No se pudo crear notificación: {str(notif_error)}")
        
        return {
            "status": "success",
            "message": "Empleado creado exitosamente",
            "data": nuevo_empleado
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear empleado: {str(e)}")

@app.put("/api/empleados/{empleado_id}", response_model=dict)
async def actualizar_empleado(empleado_id: int, empleado: EmpleadoUpdate, db: Database = Depends(get_db)):
    """Actualizar un empleado existente"""
    try:
        # Verificar que el empleado existe
        existente = db.fetch_one("SELECT id_empleado FROM Empleados WHERE id_empleado = ?", (empleado_id,))
        if not existente:
            raise HTTPException(status_code=404, detail=f"Empleado con ID {empleado_id} no encontrado")
        
        updates = []
        params = []
        
        if empleado.nombre:
            updates.append("nombre = ?")
            params.append(empleado.nombre)
        if empleado.apellido:
            updates.append("apellido = ?")
            params.append(empleado.apellido)
        if empleado.email:
            updates.append("correo = ?")
            params.append(empleado.email)
        if empleado.telefono:
            updates.append("telefono = ?")
            params.append(empleado.telefono)
        if empleado.departamento_id:
            updates.append("id_departamento = ?")
            params.append(empleado.departamento_id)
        if empleado.puesto:
            updates.append("puesto = ?")
            params.append(empleado.puesto)
        if empleado.fecha_ingreso:
            updates.append("fecha_ingreso = ?")
            params.append(empleado.fecha_ingreso)
        if empleado.activo is not None:
            updates.append("estado = ?")
            params.append("Activo" if empleado.activo else "Retirado")
        
        if not updates:
            raise HTTPException(status_code=400, detail="No se proporcionaron campos para actualizar")
        
        params.append(empleado_id)
        query = f"UPDATE Empleados SET {', '.join(updates)} WHERE id_empleado = ?"
        db.execute_query(query, tuple(params))
        
        empleado_actualizado = db.fetch_one("""
            SELECT 
                e.id_empleado as id,
                e.id_empleado,
                e.nombre,
                e.apellido,
                e.correo as email,
                e.correo,
                e.telefono,
                e.fecha_ingreso,
                e.estado,
                e.id_departamento,
                e.id_puesto,
                COALESCE(
                    (SELECT salario FROM Contratos 
                     WHERE id_empleado = e.id_empleado 
                     ORDER BY fecha_inicio DESC LIMIT 1),
                    0
                ) as salario,
                d.nombre_departamento as departamento_nombre,
                p.nombre_puesto as puesto_nombre
            FROM Empleados e
            LEFT JOIN Departamentos d ON e.id_departamento = d.id_departamento
            LEFT JOIN Puestos p ON e.id_puesto = p.id_puesto
            WHERE e.id_empleado = ?
        """, (empleado_id,))
        
        return {
            "status": "success",
            "message": "Empleado actualizado exitosamente",
            "data": empleado_actualizado
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar empleado: {str(e)}")

@app.delete("/api/empleados/{empleado_id}", response_model=dict)
async def eliminar_empleado(empleado_id: int, db: Database = Depends(get_db)):
    """Eliminar (desactivar) un empleado"""
    try:
        empleado = db.fetch_one("SELECT id_empleado, nombre FROM Empleados WHERE id_empleado = ?", (empleado_id,))
        if not empleado:
            raise HTTPException(status_code=404, detail=f"Empleado con ID {empleado_id} no encontrado")
        
        db.execute_query("UPDATE Empleados SET estado = 'Retirado' WHERE id_empleado = ?", (empleado_id,))
        
        return {
            "status": "success",
            "message": f"Empleado '{empleado['nombre']}' eliminado exitosamente"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar empleado: {str(e)}")

# ============================================================================
#                           ENDPOINTS DE NOTIFICACIONES
# ============================================================================

@app.get("/api/notificaciones/{usuario_id}", response_model=dict)
async def obtener_notificaciones(usuario_id: int, db: Database = Depends(get_db)):
    """Obtener notificaciones de un usuario"""
    try:
        notificaciones = db.fetch_all(
            """SELECT id, usuario_id, titulo, mensaje, tipo, is_read as leido, created_at as fecha_creacion 
               FROM notificaciones 
               WHERE usuario_id = ? 
               ORDER BY fecha_creacion DESC""",
            (usuario_id,)
        )
        
        return {
            "status": "success",
            "data": notificaciones,
            "count": len(notificaciones)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener notificaciones: {str(e)}")

# ============================================================================
#                           ENDPOINTS DE CONTRATOS
# ============================================================================

@app.get("/api/contratos", response_model=dict)
async def listar_contratos(id_empleado: Optional[int] = None, db: Database = Depends(get_db)):
    """Listar contratos, opcionalmente filtrados por empleado"""
    try:
        # Verificar que la conexión a la base de datos esté activa
        if not db.connection:
            db.connect()
        
        contratos = []
        
        # Verificar si la tabla Contratos existe
        try:
            # Intentar obtener de la tabla nueva (Contratos con Empleados)
            if id_empleado:
                contratos = db.fetch_all("""
                    SELECT c.*, 
                           COALESCE(e.nombre || ' ' || e.apellido, 'Empleado no encontrado') as empleado_nombre
                    FROM Contratos c
                    LEFT JOIN Empleados e ON c.id_empleado = e.id_empleado
                    WHERE c.id_empleado = ?
                    ORDER BY c.fecha_inicio DESC
                """, (id_empleado,))
            else:
                contratos = db.fetch_all("""
                    SELECT c.*, 
                           COALESCE(e.nombre || ' ' || e.apellido, 'Empleado no encontrado') as empleado_nombre
                    FROM Contratos c
                    LEFT JOIN Empleados e ON c.id_empleado = e.id_empleado
                    ORDER BY c.fecha_inicio DESC
                    LIMIT 40
                """)
        except Exception as table_error:
            # Si falla la tabla nueva, intentar sin JOIN o retornar solo contratos
            error_msg = str(table_error).lower()
            logger.warning(f"Error al consultar tabla Contratos: {str(table_error)}")
            
            # Si la tabla no existe, retornar lista vacía
            if 'no such table' in error_msg or 'does not exist' in error_msg:
                logger.info("Tabla Contratos no existe, retornando lista vacía")
                contratos = []
            else:
                # Intentar sin JOIN
                try:
                    if id_empleado:
                        contratos = db.fetch_all("""
                            SELECT c.*, 'Empleado ID: ' || c.id_empleado as empleado_nombre
                            FROM Contratos c
                            WHERE c.id_empleado = ?
                            ORDER BY c.fecha_inicio DESC
                        """, (id_empleado,))
                    else:
                        contratos = db.fetch_all("""
                            SELECT c.*, 'Empleado ID: ' || c.id_empleado as empleado_nombre
                            FROM Contratos c
                            ORDER BY c.fecha_inicio DESC
                            LIMIT 40
                        """)
                except Exception as fallback_error:
                    logger.error(f"Error al consultar tabla Contratos sin JOIN: {str(fallback_error)}")
                    contratos = []
        
        return {"status": "success", "data": contratos, "count": len(contratos)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado al obtener contratos: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error al obtener contratos: {str(e)}"
        )

@app.get("/api/contratos/{contrato_id}", response_model=dict)
async def obtener_contrato(contrato_id: int, db: Database = Depends(get_db)):
    """Obtener un contrato por ID"""
    try:
        # Validar parámetro de entrada
        if contrato_id < 1:
            raise HTTPException(status_code=400, detail="ID de contrato inválido")
        
        # Verificar que la conexión a la base de datos esté activa
        if not db.connection:
            db.connect()
        
        contrato = None
        
        # Intentar obtener de la tabla nueva (Contratos con Empleados)
        try:
            contrato = db.fetch_one("""
                SELECT c.*, 
                       COALESCE(e.nombre || ' ' || e.apellido, 'Empleado no encontrado') as empleado_nombre
                FROM Contratos c
                LEFT JOIN Empleados e ON c.id_empleado = e.id_empleado
                WHERE c.id_contrato = ?
            """, (contrato_id,))
        except Exception as table_error:
            # Si falla la tabla nueva, intentar sin JOIN
            logger.warning(f"Error al consultar contrato con JOIN, intentando sin JOIN: {str(table_error)}")
            try:
                contrato = db.fetch_one("""
                    SELECT c.*, 'Empleado ID: ' || c.id_empleado as empleado_nombre
                    FROM Contratos c
                    WHERE c.id_contrato = ?
                """, (contrato_id,))
            except Exception as fallback_error:
                logger.error(f"Error al consultar contrato: {str(fallback_error)}")
                contrato = None
        
        if not contrato:
            raise HTTPException(status_code=404, detail=f"Contrato con ID {contrato_id} no encontrado")
        
        return {"status": "success", "data": contrato}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado al obtener contrato {contrato_id}: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error al obtener contrato: {str(e)}"
        )

@app.post("/api/contratos", response_model=dict, status_code=201)
async def crear_contrato(contrato: ContratoCreate, db: Database = Depends(get_db)):
    """Crear un nuevo contrato completo con todos los datos requeridos"""
    try:
        # Obtener datos del empleado si no se proporcionaron
        empleado = None
        if contrato.id_empleado:
            empleado = db.fetch_one("""
                SELECT e.*, d.nombre_departamento 
                FROM Empleados e
                LEFT JOIN Departamentos d ON e.id_departamento = d.id_departamento
                WHERE e.id_empleado = ?
            """, (contrato.id_empleado,))
        
        # Usar salario_base si salario no está definido
        salario_final = contrato.salario_base if contrato.salario_base else (contrato.salario if contrato.salario else 0)
        
        # Preparar datos del trabajador desde el empleado si no se proporcionaron
        trabajador_nombre = contrato.trabajador_nombre_completo or (f"{empleado['nombre']} {empleado['apellido']}" if empleado else None)
        trabajador_email = contrato.trabajador_email or (empleado['correo'] if empleado else None)
        trabajador_telefono = contrato.trabajador_telefono or (empleado['telefono'] if empleado else None)
        trabajador_direccion = contrato.trabajador_direccion or (empleado.get('direccion') if empleado else None)
        
        # Preparar datos del puesto desde el empleado si no se proporcionaron
        nombre_puesto_final = contrato.nombre_puesto or (empleado.get('puesto') if empleado else None)
        id_departamento_final = contrato.id_departamento or (empleado['id_departamento'] if empleado else None)
        
        cursor = db.execute_query("""
            INSERT INTO Contratos (
                id_empleado,
                empresa_nombre, empresa_representante_legal, empresa_rtn, empresa_direccion, empresa_telefono, empresa_email,
                trabajador_nombre_completo, trabajador_dni, trabajador_nacionalidad, trabajador_estado_civil,
                trabajador_direccion, trabajador_telefono, trabajador_email,
                nombre_puesto, descripcion_puesto, id_departamento, jefe_inmediato,
                tipo_contrato, jornada_laboral_dias, horario_entrada, horario_salida, tiempo_descanso, lugar_trabajo,
                salario_base, forma_pago, metodo_pago, bonificaciones, comisiones, incentivos, deducciones,
                fecha_inicio, fecha_fin, periodo_prueba_dias,
                derechos_empleado, obligaciones_empleado, derechos_empleador, obligaciones_empleador,
                vacaciones_anuales, aguinaldo, prestaciones_sociales, dias_feriados, permisos_ley,
                clausula_confidencialidad, politica_datos, no_competencia,
                causas_terminacion, tiempo_preaviso, pago_prestaciones,
                politica_uniformes, uso_vehiculos, trabajo_remoto, politica_horas_extras, uso_sistemas,
                condiciones, estado
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            contrato.id_empleado,
            contrato.empresa_nombre, contrato.empresa_representante_legal, contrato.empresa_rtn,
            contrato.empresa_direccion, contrato.empresa_telefono, contrato.empresa_email,
            trabajador_nombre, contrato.trabajador_dni, contrato.trabajador_nacionalidad, contrato.trabajador_estado_civil,
            trabajador_direccion, trabajador_telefono, trabajador_email,
            nombre_puesto_final, contrato.descripcion_puesto, id_departamento_final, contrato.jefe_inmediato,
            contrato.tipo_contrato, contrato.jornada_laboral_dias, contrato.horario_entrada, contrato.horario_salida,
            contrato.tiempo_descanso, contrato.lugar_trabajo,
            salario_final, contrato.forma_pago, contrato.metodo_pago, contrato.bonificaciones, contrato.comisiones,
            contrato.incentivos, contrato.deducciones,
            contrato.fecha_inicio, contrato.fecha_fin, contrato.periodo_prueba_dias,
            contrato.derechos_empleado, contrato.obligaciones_empleado, contrato.derechos_empleador, contrato.obligaciones_empleador,
            contrato.vacaciones_anuales, 1 if contrato.aguinaldo else 0, contrato.prestaciones_sociales,
            contrato.dias_feriados, contrato.permisos_ley,
            contrato.clausula_confidencialidad, contrato.politica_datos, contrato.no_competencia,
            contrato.causas_terminacion, contrato.tiempo_preaviso, contrato.pago_prestaciones,
            contrato.politica_uniformes, contrato.uso_vehiculos, contrato.trabajo_remoto,
            contrato.politica_horas_extras, contrato.uso_sistemas,
            contrato.condiciones, 'activo'
        ))
        
        # Obtener el contrato creado con información del empleado
        try:
            nuevo_contrato = db.fetch_one("""
                SELECT c.*, 
                       COALESCE(e.nombre || ' ' || e.apellido, 'Empleado no encontrado') as empleado_nombre
                FROM Contratos c
                LEFT JOIN Empleados e ON c.id_empleado = e.id_empleado
                WHERE c.id_contrato = ?
            """, (cursor.lastrowid,))
        except Exception:
            # Si falla el JOIN, obtener solo el contrato
            nuevo_contrato = db.fetch_one("""
                SELECT c.*, 'Empleado ID: ' || c.id_empleado as empleado_nombre
                FROM Contratos c
                WHERE c.id_contrato = ?
            """, (cursor.lastrowid,))
        
        return {"status": "success", "message": "Contrato creado exitosamente", "data": nuevo_contrato}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear contrato: {str(e)}")

@app.put("/api/contratos/{contrato_id}", response_model=dict)
async def actualizar_contrato(contrato_id: int, contrato: ContratoUpdate, db: Database = Depends(get_db)):
    """Actualizar un contrato"""
    try:
        existente = db.fetch_one("SELECT id_contrato FROM Contratos WHERE id_contrato = ?", (contrato_id,))
        if not existente:
            raise HTTPException(status_code=404, detail=f"Contrato con ID {contrato_id} no encontrado")
        
        updates = []
        params = []
        
        # Datos del Empleador
        if contrato.empresa_nombre is not None:
            updates.append("empresa_nombre = ?")
            params.append(contrato.empresa_nombre)
        if contrato.empresa_representante_legal is not None:
            updates.append("empresa_representante_legal = ?")
            params.append(contrato.empresa_representante_legal)
        if contrato.empresa_rtn is not None:
            updates.append("empresa_rtn = ?")
            params.append(contrato.empresa_rtn)
        if contrato.empresa_direccion is not None:
            updates.append("empresa_direccion = ?")
            params.append(contrato.empresa_direccion)
        if contrato.empresa_telefono is not None:
            updates.append("empresa_telefono = ?")
            params.append(contrato.empresa_telefono)
        if contrato.empresa_email is not None:
            updates.append("empresa_email = ?")
            params.append(contrato.empresa_email)
        
        # Datos del Trabajador
        if contrato.trabajador_nombre_completo is not None:
            updates.append("trabajador_nombre_completo = ?")
            params.append(contrato.trabajador_nombre_completo)
        if contrato.trabajador_dni is not None:
            updates.append("trabajador_dni = ?")
            params.append(contrato.trabajador_dni)
        if contrato.trabajador_nacionalidad is not None:
            updates.append("trabajador_nacionalidad = ?")
            params.append(contrato.trabajador_nacionalidad)
        if contrato.trabajador_estado_civil is not None:
            updates.append("trabajador_estado_civil = ?")
            params.append(contrato.trabajador_estado_civil)
        if contrato.trabajador_direccion is not None:
            updates.append("trabajador_direccion = ?")
            params.append(contrato.trabajador_direccion)
        if contrato.trabajador_telefono is not None:
            updates.append("trabajador_telefono = ?")
            params.append(contrato.trabajador_telefono)
        if contrato.trabajador_email is not None:
            updates.append("trabajador_email = ?")
            params.append(contrato.trabajador_email)
        
        # Datos del Puesto
        if contrato.nombre_puesto is not None:
            updates.append("nombre_puesto = ?")
            params.append(contrato.nombre_puesto)
        if contrato.descripcion_puesto is not None:
            updates.append("descripcion_puesto = ?")
            params.append(contrato.descripcion_puesto)
        if contrato.id_departamento is not None:
            updates.append("id_departamento = ?")
            params.append(contrato.id_departamento)
        if contrato.jefe_inmediato is not None:
            updates.append("jefe_inmediato = ?")
            params.append(contrato.jefe_inmediato)
        
        # Condiciones de Trabajo
        if contrato.tipo_contrato:
            updates.append("tipo_contrato = ?")
            params.append(contrato.tipo_contrato)
        if contrato.jornada_laboral_dias is not None:
            updates.append("jornada_laboral_dias = ?")
            params.append(contrato.jornada_laboral_dias)
        if contrato.horario_entrada is not None:
            updates.append("horario_entrada = ?")
            params.append(contrato.horario_entrada)
        if contrato.horario_salida is not None:
            updates.append("horario_salida = ?")
            params.append(contrato.horario_salida)
        if contrato.tiempo_descanso is not None:
            updates.append("tiempo_descanso = ?")
            params.append(contrato.tiempo_descanso)
        if contrato.lugar_trabajo is not None:
            updates.append("lugar_trabajo = ?")
            params.append(contrato.lugar_trabajo)
        
        # Remuneración
        if contrato.salario_base is not None:
            updates.append("salario_base = ?")
            params.append(contrato.salario_base)
        elif contrato.salario is not None:
            updates.append("salario_base = ?")
            params.append(contrato.salario)
        if contrato.forma_pago is not None:
            updates.append("forma_pago = ?")
            params.append(contrato.forma_pago)
        if contrato.metodo_pago is not None:
            updates.append("metodo_pago = ?")
            params.append(contrato.metodo_pago)
        if contrato.bonificaciones is not None:
            updates.append("bonificaciones = ?")
            params.append(contrato.bonificaciones)
        if contrato.comisiones is not None:
            updates.append("comisiones = ?")
            params.append(contrato.comisiones)
        if contrato.incentivos is not None:
            updates.append("incentivos = ?")
            params.append(contrato.incentivos)
        if contrato.deducciones is not None:
            updates.append("deducciones = ?")
            params.append(contrato.deducciones)
        
        # Duración
        if contrato.fecha_inicio:
            updates.append("fecha_inicio = ?")
            params.append(contrato.fecha_inicio)
        if contrato.fecha_fin is not None:
            updates.append("fecha_fin = ?")
            params.append(contrato.fecha_fin)
        if contrato.periodo_prueba_dias is not None:
            updates.append("periodo_prueba_dias = ?")
            params.append(contrato.periodo_prueba_dias)
        
        # Derechos y Obligaciones
        if contrato.derechos_empleado is not None:
            updates.append("derechos_empleado = ?")
            params.append(contrato.derechos_empleado)
        if contrato.obligaciones_empleado is not None:
            updates.append("obligaciones_empleado = ?")
            params.append(contrato.obligaciones_empleado)
        if contrato.derechos_empleador is not None:
            updates.append("derechos_empleador = ?")
            params.append(contrato.derechos_empleador)
        if contrato.obligaciones_empleador is not None:
            updates.append("obligaciones_empleador = ?")
            params.append(contrato.obligaciones_empleador)
        
        # Beneficios Legales
        if contrato.vacaciones_anuales is not None:
            updates.append("vacaciones_anuales = ?")
            params.append(contrato.vacaciones_anuales)
        if contrato.aguinaldo is not None:
            updates.append("aguinaldo = ?")
            params.append(1 if contrato.aguinaldo else 0)
        if contrato.prestaciones_sociales is not None:
            updates.append("prestaciones_sociales = ?")
            params.append(contrato.prestaciones_sociales)
        if contrato.dias_feriados is not None:
            updates.append("dias_feriados = ?")
            params.append(contrato.dias_feriados)
        if contrato.permisos_ley is not None:
            updates.append("permisos_ley = ?")
            params.append(contrato.permisos_ley)
        
        # Confidencialidad
        if contrato.clausula_confidencialidad is not None:
            updates.append("clausula_confidencialidad = ?")
            params.append(contrato.clausula_confidencialidad)
        if contrato.politica_datos is not None:
            updates.append("politica_datos = ?")
            params.append(contrato.politica_datos)
        if contrato.no_competencia is not None:
            updates.append("no_competencia = ?")
            params.append(contrato.no_competencia)
        
        # Terminación
        if contrato.causas_terminacion is not None:
            updates.append("causas_terminacion = ?")
            params.append(contrato.causas_terminacion)
        if contrato.tiempo_preaviso is not None:
            updates.append("tiempo_preaviso = ?")
            params.append(contrato.tiempo_preaviso)
        if contrato.pago_prestaciones is not None:
            updates.append("pago_prestaciones = ?")
            params.append(contrato.pago_prestaciones)
        
        # Cláusulas Adicionales
        if contrato.politica_uniformes is not None:
            updates.append("politica_uniformes = ?")
            params.append(contrato.politica_uniformes)
        if contrato.uso_vehiculos is not None:
            updates.append("uso_vehiculos = ?")
            params.append(contrato.uso_vehiculos)
        if contrato.trabajo_remoto is not None:
            updates.append("trabajo_remoto = ?")
            params.append(contrato.trabajo_remoto)
        if contrato.politica_horas_extras is not None:
            updates.append("politica_horas_extras = ?")
            params.append(contrato.politica_horas_extras)
        if contrato.uso_sistemas is not None:
            updates.append("uso_sistemas = ?")
            params.append(contrato.uso_sistemas)
        
        # Campos adicionales
        if contrato.condiciones:
            updates.append("condiciones = ?")
            params.append(contrato.condiciones)
        if contrato.estado:
            updates.append("estado = ?")
            params.append(contrato.estado)
        
        # Actualizar fecha de modificación
        updates.append("fecha_modificacion = CURRENT_TIMESTAMP")
        
        if not updates:
            raise HTTPException(status_code=400, detail="No se proporcionaron campos para actualizar")
        
        params.append(contrato_id)
        query = f"UPDATE Contratos SET {', '.join(updates)} WHERE id_contrato = ?"
        db.execute_query(query, tuple(params))
        
        # Obtener el contrato actualizado con información del empleado
        try:
            contrato_actualizado = db.fetch_one("""
                SELECT c.*, 
                       COALESCE(e.nombre || ' ' || e.apellido, 'Empleado no encontrado') as empleado_nombre
                FROM Contratos c
                LEFT JOIN Empleados e ON c.id_empleado = e.id_empleado
                WHERE c.id_contrato = ?
            """, (contrato_id,))
        except Exception:
            # Si falla el JOIN, obtener solo el contrato
            contrato_actualizado = db.fetch_one("""
                SELECT c.*, 'Empleado ID: ' || c.id_empleado as empleado_nombre
                FROM Contratos c
                WHERE c.id_contrato = ?
            """, (contrato_id,))
        
        return {"status": "success", "message": "Contrato actualizado exitosamente", "data": contrato_actualizado}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar contrato: {str(e)}")

@app.delete("/api/contratos/{contrato_id}", response_model=dict)
async def eliminar_contrato(contrato_id: int, db: Database = Depends(get_db)):
    """Eliminar un contrato"""
    try:
        contrato = db.fetch_one("SELECT id_contrato FROM Contratos WHERE id_contrato = ?", (contrato_id,))
        if not contrato:
            raise HTTPException(status_code=404, detail=f"Contrato con ID {contrato_id} no encontrado")
        
        db.execute_query("DELETE FROM Contratos WHERE id_contrato = ?", (contrato_id,))
        
        return {"status": "success", "message": "Contrato eliminado exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar contrato: {str(e)}")

@app.get("/api/contratos/alertas/vencimiento", response_model=dict)
async def alertas_vencimiento_contratos(dias: int = 30, db: Database = Depends(get_db)):
    """Obtener contratos próximos a vencer"""
    try:
        # Validar parámetro de entrada
        if dias < 1 or dias > 365:
            raise HTTPException(
                status_code=400, 
                detail="El número de días debe estar entre 1 y 365"
            )
        
        # Verificar que la conexión a la base de datos esté activa
        if not db.connection:
            db.connect()
        
        fecha_limite = (datetime.now() + timedelta(days=dias)).date()
        contratos = []
        
        # Intentar obtener de la tabla nueva (Contratos con Empleados)
        try:
            contratos = db.fetch_all("""
                SELECT c.*, 
                       COALESCE(e.nombre || ' ' || e.apellido, 'Empleado no encontrado') as empleado_nombre,
                       CAST(julianday(c.fecha_fin) - julianday('now') AS INTEGER) as dias_restantes
                FROM Contratos c
                LEFT JOIN Empleados e ON c.id_empleado = e.id_empleado
                WHERE c.fecha_fin IS NOT NULL 
                AND c.fecha_fin <= ? 
                AND c.fecha_fin >= date('now')
                ORDER BY c.fecha_fin ASC
            """, (fecha_limite,))
        except Exception as table_error:
            # Si falla la tabla nueva, intentar sin JOIN
            error_msg = str(table_error).lower()
            logger.warning(f"Error al consultar alertas: {str(table_error)}")
            
            # Si la tabla no existe, retornar lista vacía
            if 'no such table' in error_msg or 'does not exist' in error_msg:
                logger.info("Tabla Contratos no existe, retornando lista vacía")
                contratos = []
            else:
                try:
                    contratos = db.fetch_all("""
                        SELECT c.*, 
                               'Empleado ID: ' || c.id_empleado as empleado_nombre,
                               CAST(julianday(c.fecha_fin) - julianday('now') AS INTEGER) as dias_restantes
                        FROM Contratos c
                        WHERE c.fecha_fin IS NOT NULL 
                        AND c.fecha_fin <= ? 
                        AND c.fecha_fin >= date('now')
                        ORDER BY c.fecha_fin ASC
                    """, (fecha_limite,))
                except Exception as fallback_error:
                    logger.error(f"Error al consultar alertas de contratos sin JOIN: {str(fallback_error)}")
                    contratos = []
        
        return {
            "status": "success", 
            "data": contratos, 
            "count": len(contratos), 
            "dias_consulta": dias
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado al obtener alertas: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error al obtener alertas: {str(e)}"
        )

# ============================================================================
#                           ENDPOINTS DE ASISTENCIAS
# ============================================================================

@app.get("/api/asistencias", response_model=dict)
async def listar_asistencias(
    id_empleado: Optional[int] = None,
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None,
    db: Database = Depends(get_db)
):
    """Listar asistencias con filtros opcionales"""
    try:
        # Verificar que la conexión a la base de datos esté activa
        if not db.connection:
            db.connect()
        
        asistencias = []
        
        # Intentar obtener de la tabla nueva (Asistencias con Empleados)
        try:
            query = """
                SELECT a.*, 
                       COALESCE(e.nombre || ' ' || e.apellido, 'Empleado no encontrado') as empleado_nombre
                FROM Asistencias a
                LEFT JOIN Empleados e ON a.id_empleado = e.id_empleado
                WHERE 1=1
            """
            params = []
            
            if id_empleado:
                query += " AND a.id_empleado = ?"
                params.append(id_empleado)
            if fecha_inicio:
                query += " AND a.fecha >= ?"
                params.append(fecha_inicio)
            if fecha_fin:
                query += " AND a.fecha <= ?"
                params.append(fecha_fin)
            
            query += " ORDER BY a.fecha DESC, a.hora_entrada DESC"
            
            asistencias = db.fetch_all(query, tuple(params))
        except Exception as table_error:
            # Si falla la tabla nueva, intentar sin JOIN
            error_msg = str(table_error).lower()
            logger.warning(f"Error al consultar asistencias: {str(table_error)}")
            
            # Si la tabla no existe, retornar lista vacía
            if 'no such table' in error_msg or 'does not exist' in error_msg:
                logger.info("Tabla Asistencias no existe, retornando lista vacía")
                asistencias = []
            else:
                try:
                    query = """
                        SELECT a.*, 'Empleado ID: ' || a.id_empleado as empleado_nombre
                        FROM Asistencias a
                        WHERE 1=1
                    """
                    params = []
                    
                    if id_empleado:
                        query += " AND a.id_empleado = ?"
                        params.append(id_empleado)
                    if fecha_inicio:
                        query += " AND a.fecha >= ?"
                        params.append(fecha_inicio)
                    if fecha_fin:
                        query += " AND a.fecha <= ?"
                        params.append(fecha_fin)
                    
                    query += " ORDER BY a.fecha DESC, a.hora_entrada DESC"
                    
                    asistencias = db.fetch_all(query, tuple(params))
                except Exception as fallback_error:
                    logger.error(f"Error al consultar asistencias sin JOIN: {str(fallback_error)}")
                    asistencias = []
        
        return {"status": "success", "data": asistencias, "count": len(asistencias)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado al obtener asistencias: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error al obtener asistencias: {str(e)}"
        )

@app.get("/api/asistencias/{asistencia_id}", response_model=dict)
async def obtener_asistencia(asistencia_id: int, db: Database = Depends(get_db)):
    """Obtener una asistencia por ID con manejo robusto"""
    try:
        asistencia = None
        
        # Intentar con JOIN primero
        try:
            asistencia = db.fetch_one("""
                SELECT a.*, 
                       COALESCE(e.nombre || ' ' || e.apellido, 'Empleado no encontrado') as empleado_nombre
                FROM Asistencias a
                LEFT JOIN Empleados e ON a.id_empleado = e.id_empleado
                WHERE a.id_asistencia = ?
            """, (asistencia_id,))
        except Exception:
            # Si falla, intentar sin JOIN
            try:
                asistencia = db.fetch_one("""
                    SELECT a.*, 'Empleado ID: ' || a.id_empleado as empleado_nombre
                    FROM Asistencias a
                    WHERE a.id_asistencia = ?
                """, (asistencia_id,))
            except Exception:
                asistencia = None
        
        if not asistencia:
            raise HTTPException(status_code=404, detail=f"Asistencia con ID {asistencia_id} no encontrada")
        
        return {"status": "success", "data": asistencia}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener asistencia: {str(e)}")

@app.post("/api/asistencias", response_model=dict, status_code=201)
async def crear_asistencia(asistencia: AsistenciaCreate, db: Database = Depends(get_db)):
    """Crear un nuevo registro de asistencia"""
    try:
        cursor = db.execute_query("""
            INSERT INTO Asistencias (id_empleado, fecha, hora_entrada, hora_salida, observaciones)
            VALUES (?, ?, ?, ?, ?)
        """, (
            asistencia.id_empleado,
            asistencia.fecha,
            asistencia.hora_entrada,
            asistencia.hora_salida,
            asistencia.observaciones
        ))
        
        nueva_asistencia = db.fetch_one("""
            SELECT a.*, e.nombre || ' ' || e.apellido as empleado_nombre
            FROM Asistencias a
            JOIN Empleados e ON a.id_empleado = e.id_empleado
            WHERE a.id_asistencia = ?
        """, (cursor.lastrowid,))
        
        return {"status": "success", "message": "Asistencia registrada exitosamente", "data": nueva_asistencia}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear asistencia: {str(e)}")

@app.put("/api/asistencias/{asistencia_id}", response_model=dict)
async def actualizar_asistencia(asistencia_id: int, asistencia: AsistenciaUpdate, db: Database = Depends(get_db)):
    """Actualizar una asistencia"""
    try:
        existente = db.fetch_one("SELECT id_asistencia FROM Asistencias WHERE id_asistencia = ?", (asistencia_id,))
        if not existente:
            raise HTTPException(status_code=404, detail=f"Asistencia con ID {asistencia_id} no encontrada")
        
        updates = []
        params = []
        
        if asistencia.hora_entrada:
            updates.append("hora_entrada = ?")
            params.append(asistencia.hora_entrada)
        if asistencia.hora_salida:
            updates.append("hora_salida = ?")
            params.append(asistencia.hora_salida)
        if asistencia.observaciones:
            updates.append("observaciones = ?")
            params.append(asistencia.observaciones)
        
        if not updates:
            raise HTTPException(status_code=400, detail="No se proporcionaron campos para actualizar")
        
        params.append(asistencia_id)
        query = f"UPDATE Asistencias SET {', '.join(updates)} WHERE id_asistencia = ?"
        db.execute_query(query, tuple(params))
        
        asistencia_actualizada = db.fetch_one("""
            SELECT a.*, e.nombre || ' ' || e.apellido as empleado_nombre
            FROM Asistencias a
            JOIN Empleados e ON a.id_empleado = e.id_empleado
            WHERE a.id_asistencia = ?
        """, (asistencia_id,))
        
        return {"status": "success", "message": "Asistencia actualizada exitosamente", "data": asistencia_actualizada}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar asistencia: {str(e)}")

@app.delete("/api/asistencias/{asistencia_id}", response_model=dict)
async def eliminar_asistencia(asistencia_id: int, db: Database = Depends(get_db)):
    """Eliminar una asistencia"""
    try:
        asistencia = db.fetch_one("SELECT id_asistencia FROM Asistencias WHERE id_asistencia = ?", (asistencia_id,))
        if not asistencia:
            raise HTTPException(status_code=404, detail=f"Asistencia con ID {asistencia_id} no encontrada")
        
        db.execute_query("DELETE FROM Asistencias WHERE id_asistencia = ?", (asistencia_id,))
        
        return {"status": "success", "message": "Asistencia eliminada exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar asistencia: {str(e)}")

@app.post("/api/asistencias/reporte", response_model=dict)
async def generar_reporte_asistencias(reporte: AsistenciaReporteRequest, db: Database = Depends(get_db)):
    """Generar reporte de asistencias por rango de fechas con estadísticas por empleado"""
    try:
        # Query para obtener estadísticas agrupadas por empleado
        query = """
            SELECT 
                e.id as id_empleado,
                COALESCE(e.nombre || ' ' || e.apellido, 'Desconocido') as empleado,
                COALESCE(d.nombre, 'Sin departamento') as departamento,
                COUNT(CASE WHEN a.hora_entrada IS NOT NULL THEN 1 END) as presente,
                COUNT(CASE WHEN a.hora_entrada IS NULL THEN 1 END) as ausente,
                COUNT(CASE WHEN TIME(a.hora_entrada) > '08:30:00' THEN 1 END) as tardanzas,
                ROUND(
                    CAST(COUNT(CASE WHEN a.hora_entrada IS NOT NULL THEN 1 END) AS FLOAT) * 100.0 / 
                    NULLIF(COUNT(*), 0), 1
                ) as porcentaje_asistencia
            FROM empleados e
            LEFT JOIN departamentos d ON e.departamento_id = d.id
            LEFT JOIN asistencias a ON e.id = a.empleado_id AND a.fecha BETWEEN ? AND ?
            WHERE e.activo = 1
        """
        
        params = [reporte.fecha_inicio, reporte.fecha_fin]
        
        if reporte.id_empleado:
            query += " AND e.id = ?"
            params.append(reporte.id_empleado)
        
        query += " GROUP BY e.id, e.nombre, e.apellido, d.nombre HAVING COUNT(a.id) > 0 ORDER BY e.nombre, e.apellido"
        
        asistencias = db.fetch_all(query, tuple(params))
        
        return {
            "success": True,
            "data": asistencias,
            "count": len(asistencias)
        }
    except Exception as e:
        logger.error(f"Error al generar reporte: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al generar reporte: {str(e)}")

# ============================================================================
#                           ENDPOINTS DE NÓMINA
# ============================================================================

@app.get("/api/nomina", response_model=dict)
async def listar_nominas(
    id_empleado: Optional[int] = None,
    mes: Optional[int] = None,
    anio: Optional[int] = None,
    db: Database = Depends(get_db)
):
    """Listar nóminas con filtros opcionales y manejo robusto"""
    try:
        # Verificar que la conexión a la base de datos esté activa
        if not db.connection:
            db.connect()
        
        nominas = []
        params = []
        
        # Intentar obtener de la tabla nueva (Nomina con Empleados) primero
        try:
            query = """
                SELECT n.*, 
                       COALESCE(e.nombre || ' ' || e.apellido, 'Empleado no encontrado') as nombre_empleado
                FROM Nomina n
                LEFT JOIN Empleados e ON n.id_empleado = e.id_empleado
                WHERE 1=1
            """
            
            if id_empleado:
                query += " AND n.id_empleado = ?"
                params.append(id_empleado)
            if mes:
                query += " AND n.mes = ?"
                params.append(mes)
            if anio:
                query += " AND n.anio = ?"
                params.append(anio)
            
            query += " ORDER BY n.anio DESC, n.mes DESC, n.fecha_creacion DESC"
            
            nominas = db.fetch_all(query, tuple(params))
        except Exception as table_error:
            # Si falla el JOIN, intentar sin JOIN
            error_msg = str(table_error).lower()
            logger.warning(f"Error al consultar nóminas: {str(table_error)}")
            
            try:
                query = """
                    SELECT n.*, 'Empleado ID: ' || n.id_empleado as nombre_empleado
                    FROM Nomina n
                    WHERE 1=1
                """
                
                if id_empleado:
                    query += " AND n.id_empleado = ?"
                    params.append(id_empleado)
                if mes:
                    query += " AND n.mes = ?"
                    params.append(mes)
                if anio:
                    query += " AND n.anio = ?"
                    params.append(anio)
                
                query += " ORDER BY n.anio DESC, n.mes DESC, n.fecha_creacion DESC"
                
                nominas = db.fetch_all(query, tuple(params))
            except Exception as fallback_error:
                logger.error(f"Error al consultar nóminas sin JOIN: {str(fallback_error)}")
                # Si la tabla no existe, retornar lista vacía
                if 'no such table' in error_msg or 'does not exist' in error_msg:
                    logger.info("Tabla Nomina no existe, retornando lista vacía")
                    nominas = []
                else:
                    nominas = []
        
        # Obtener detalles de bonificaciones y deducciones
        for nomina in nominas:
            bonificaciones = db.fetch_all(
                "SELECT * FROM Nomina_Bonificaciones WHERE id_nomina = ?",
                (nomina['id_nomina'],)
            )
            deducciones = db.fetch_all(
                "SELECT * FROM Nomina_Deducciones WHERE id_nomina = ?",
                (nomina['id_nomina'],)
            )
            nomina['bonificaciones_detalle'] = bonificaciones
            nomina['deducciones_detalle'] = deducciones
        
        return {"success": True, "data": nominas, "count": len(nominas)}
    except Exception as e:
        logger.error(f"Error al obtener nóminas: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al obtener nóminas: {str(e)}")

@app.get("/api/nomina/{nomina_id}", response_model=dict)
async def obtener_nomina(nomina_id: int, db: Database = Depends(get_db)):
    """Obtener una nómina por ID"""
    try:
        nomina = db.fetch_one("""
            SELECT n.*, e.nombre || ' ' || e.apellido as nombre_empleado
            FROM Nomina n
            JOIN Empleados e ON n.id_empleado = e.id_empleado
            WHERE n.id_nomina = ?
        """, (nomina_id,))
        
        if not nomina:
            raise HTTPException(status_code=404, detail=f"Nómina con ID {nomina_id} no encontrada")
        
        # Obtener detalles
        bonificaciones = db.fetch_all(
            "SELECT * FROM Nomina_Bonificaciones WHERE id_nomina = ?",
            (nomina_id,)
        )
        deducciones = db.fetch_all(
            "SELECT * FROM Nomina_Deducciones WHERE id_nomina = ?",
            (nomina_id,)
        )
        nomina['bonificaciones_detalle'] = bonificaciones
        nomina['deducciones_detalle'] = deducciones
        
        return {"success": True, "data": nomina}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener nómina: {str(e)}")

@app.post("/api/nomina", response_model=dict, status_code=201)
async def crear_nomina(nomina: NominaCreate, db: Database = Depends(get_db)):
    """Crear una nueva nómina"""
    try:
        # Verificar que el empleado existe
        empleado = db.fetch_one("SELECT id_empleado FROM Empleados WHERE id_empleado = ?", (nomina.id_empleado,))
        if not empleado:
            raise HTTPException(status_code=400, detail=f"Empleado con ID {nomina.id_empleado} no encontrado")
        
        # Calcular periodo
        periodo = f"{nomina.mes:02d}/{nomina.anio}"
        
        # Calcular totales
        total_bonificaciones = sum(b.get('monto', 0) for b in (nomina.bonificaciones or []))
        total_deducciones = sum(d.get('monto', 0) for d in (nomina.deducciones or []))
        salario_neto = nomina.salario_base + total_bonificaciones - total_deducciones
        
        # Insertar nómina
        cursor = db.execute_query("""
            INSERT INTO Nomina (id_empleado, mes, anio, periodo, salario_base, total_bonificaciones, 
                              total_deducciones, salario_neto, fecha_pago, estado, observaciones)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            nomina.id_empleado, nomina.mes, nomina.anio, periodo,
            nomina.salario_base, total_bonificaciones, total_deducciones,
            salario_neto, nomina.fecha_pago, 'pendiente', nomina.observaciones
        ))
        
        nomina_id = cursor.lastrowid
        
        # Insertar bonificaciones
        if nomina.bonificaciones:
            for bonif in nomina.bonificaciones:
                db.execute_query("""
                    INSERT INTO Nomina_Bonificaciones (id_nomina, concepto, tipo, monto, descripcion)
                    VALUES (?, ?, ?, ?, ?)
                """, (nomina_id, bonif.get('concepto', ''), bonif.get('tipo'), bonif.get('monto', 0), bonif.get('descripcion')))
        
        # Insertar deducciones
        if nomina.deducciones:
            for deduc in nomina.deducciones:
                db.execute_query("""
                    INSERT INTO Nomina_Deducciones (id_nomina, concepto, tipo, monto, descripcion)
                    VALUES (?, ?, ?, ?, ?)
                """, (nomina_id, deduc.get('concepto', ''), deduc.get('tipo'), deduc.get('monto', 0), deduc.get('descripcion')))
        
        # Obtener nómina creada con manejo robusto
        nueva_nomina = None
        try:
            nueva_nomina = db.fetch_one("""
                SELECT n.*, 
                       COALESCE(e.nombre || ' ' || e.apellido, 'Empleado no encontrado') as nombre_empleado
                FROM Nomina n
                LEFT JOIN Empleados e ON n.id_empleado = e.id_empleado
                WHERE n.id_nomina = ?
            """, (nomina_id,))
        except Exception:
            # Si falla el JOIN, obtener sin nombre de empleado
            try:
                nueva_nomina = db.fetch_one("""
                    SELECT n.*, 'Empleado ID: ' || n.id_empleado as nombre_empleado
                    FROM Nomina n
                    WHERE n.id_nomina = ?
                """, (nomina_id,))
            except Exception:
                # Si todo falla, obtener solo la nómina
                nueva_nomina = db.fetch_one("""
                    SELECT * FROM Nomina WHERE id_nomina = ?
                """, (nomina_id,))
                if nueva_nomina:
                    nueva_nomina['nombre_empleado'] = f"Empleado ID: {nomina.id_empleado}"
        
        return {"success": True, "message": "Nómina creada exitosamente", "data": nueva_nomina}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al crear nómina: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al crear nómina: {str(e)}")

@app.get("/api/nomina/empleado/{empleado_id}/historial", response_model=dict)
async def historial_empleado(empleado_id: int, db: Database = Depends(get_db)):
    """Obtener historial de nóminas de un empleado con manejo robusto"""
    try:
        nominas = []
        
        # Intentar con JOIN primero
        try:
            nominas = db.fetch_all("""
                SELECT n.*, 
                       COALESCE(e.nombre || ' ' || e.apellido, 'Empleado no encontrado') as nombre_empleado
                FROM Nomina n
                LEFT JOIN Empleados e ON n.id_empleado = e.id_empleado
                WHERE n.id_empleado = ?
                ORDER BY n.anio DESC, n.mes DESC
            """, (empleado_id,))
        except Exception:
            # Si falla, intentar sin JOIN
            try:
                nominas = db.fetch_all("""
                    SELECT n.*, 'Empleado ID: ' || n.id_empleado as nombre_empleado
                    FROM Nomina n
                    WHERE n.id_empleado = ?
                    ORDER BY n.anio DESC, n.mes DESC
                """, (empleado_id,))
            except Exception:
                nominas = []
        
        return {"success": True, "data": nominas, "count": len(nominas)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener historial: {str(e)}")

# ============================================================================
#                           ENDPOINTS DE VACACIONES
# ============================================================================

@app.get("/api/vacaciones", response_model=dict)
async def listar_vacaciones(
    id_empleado: Optional[int] = None,
    estado: Optional[str] = None,
    db: Database = Depends(get_db)
):
    """Listar vacaciones y permisos con manejo robusto"""
    try:
        # Verificar que la conexión a la base de datos esté activa
        if not db.connection:
            db.connect()
        
        vacaciones = []
        params = []
        
        # Intentar obtener de la tabla nueva (Vacaciones_Permisos con Empleados) primero
        try:
            query = """
                SELECT v.*, 
                       COALESCE(e.nombre || ' ' || e.apellido, 'Empleado no encontrado') as nombre_empleado
                FROM Vacaciones_Permisos v
                LEFT JOIN Empleados e ON v.id_empleado = e.id_empleado
                WHERE 1=1
            """
            
            if id_empleado:
                query += " AND v.id_empleado = ?"
                params.append(id_empleado)
            if estado:
                query += " AND v.estado = ?"
                params.append(estado)
            
            query += " ORDER BY v.fecha_solicitud DESC"
            
            vacaciones = db.fetch_all(query, tuple(params))
        except Exception as table_error:
            # Si falla el JOIN, intentar sin JOIN
            error_msg = str(table_error).lower()
            logger.warning(f"Error al consultar vacaciones: {str(table_error)}")
            
            try:
                query = """
                    SELECT v.*, 'Empleado ID: ' || v.id_empleado as nombre_empleado
                    FROM Vacaciones_Permisos v
                    WHERE 1=1
                """
                
                if id_empleado:
                    query += " AND v.id_empleado = ?"
                    params.append(id_empleado)
                if estado:
                    query += " AND v.estado = ?"
                    params.append(estado)
                
                query += " ORDER BY v.fecha_solicitud DESC"
                
                vacaciones = db.fetch_all(query, tuple(params))
            except Exception as fallback_error:
                logger.error(f"Error al consultar vacaciones sin JOIN: {str(fallback_error)}")
                # Si la tabla no existe, retornar lista vacía
                if 'no such table' in error_msg or 'does not exist' in error_msg:
                    logger.info("Tabla Vacaciones_Permisos no existe, retornando lista vacía")
                    vacaciones = []
                else:
                    vacaciones = []
        
        return {"success": True, "data": vacaciones, "count": len(vacaciones)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado al obtener vacaciones: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error al obtener vacaciones: {str(e)}"
        )

@app.post("/api/vacaciones", response_model=dict, status_code=201)
async def crear_vacacion(vacacion: VacacionPermisoCreate, db: Database = Depends(get_db)):
    """Crear una solicitud de vacaciones o permiso"""
    try:
        cursor = db.execute_query("""
            INSERT INTO Vacaciones_Permisos 
            (id_empleado, tipo, fecha_inicio, fecha_fin, dias_solicitados, motivo, estado)
            VALUES (?, ?, ?, ?, ?, ?, 'pendiente')
        """, (
            vacacion.id_empleado, vacacion.tipo, vacacion.fecha_inicio,
            vacacion.fecha_fin, vacacion.dias_solicitados, vacacion.motivo
        ))
        
        # Obtener vacación creada con manejo robusto
        nueva_vacacion = None
        try:
            nueva_vacacion = db.fetch_one("""
                SELECT v.*, 
                       COALESCE(e.nombre || ' ' || e.apellido, 'Empleado no encontrado') as nombre_empleado
                FROM Vacaciones_Permisos v
                LEFT JOIN Empleados e ON v.id_empleado = e.id_empleado
                WHERE v.id_permiso = ?
            """, (cursor.lastrowid,))
        except Exception:
            # Si falla el JOIN, obtener sin nombre de empleado
            try:
                nueva_vacacion = db.fetch_one("""
                    SELECT v.*, 'Empleado ID: ' || v.id_empleado as nombre_empleado
                    FROM Vacaciones_Permisos v
                    WHERE v.id_permiso = ?
                """, (cursor.lastrowid,))
            except Exception:
                # Si todo falla, obtener solo la vacación
                nueva_vacacion = db.fetch_one("""
                    SELECT * FROM Vacaciones_Permisos WHERE id_permiso = ?
                """, (cursor.lastrowid,))
                if nueva_vacacion:
                    nueva_vacacion['nombre_empleado'] = f"Empleado ID: {vacacion.id_empleado}"
        
        # Notificar a supervisores y RRHH
        try:
            empleado = db.fetch_one(
                "SELECT nombre, apellido FROM Empleados WHERE id_empleado = ?",
                (vacacion.id_empleado,)
            )
            if empleado:
                nombre_empleado = f"{empleado['nombre']} {empleado['apellido']}"
                # Notificar a administradores y supervisores
                supervisores = db.fetch_all(
                    "SELECT id FROM usuarios WHERE rol IN ('administrador', 'supervisor')"
                )
                for supervisor in supervisores:
                    NotificationHelper.notificar_vacaciones_solicitadas(
                        db, supervisor['id'], nombre_empleado, cursor.lastrowid
                    )
        except Exception as notif_error:
            logger.warning(f"No se pudo crear notificación de vacaciones: {str(notif_error)}")
        
        return {"success": True, "message": "Solicitud creada exitosamente", "data": nueva_vacacion}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear solicitud: {str(e)}")

# ============================================================================
#                           ENDPOINTS DE DOCUMENTOS
# ============================================================================

@app.get("/api/documentos", response_model=dict)
async def listar_documentos(
    id_empleado: Optional[int] = None,
    tipo_documento: Optional[str] = None,
    db: Database = Depends(get_db)
):
    """Listar documentos con manejo robusto de JOINs"""
    try:
        # Verificar que la conexión a la base de datos esté activa
        if not db.connection:
            db.connect()
        
        documentos = []
        params = []
        
        # Intentar obtener de la tabla nueva (Documentos con Empleados) primero
        try:
            query = """
                SELECT 
                    d.*,
                    COALESCE(e.nombre || ' ' || e.apellido, 'Empleado no encontrado') as nombre_empleado
                FROM Documentos d
                LEFT JOIN Empleados e ON d.id_empleado = e.id_empleado
                WHERE 1=1
            """
            
            if id_empleado:
                query += " AND d.id_empleado = ?"
                params.append(id_empleado)
            if tipo_documento:
                query += " AND d.tipo_documento = ?"
                params.append(tipo_documento)
            
            query += " ORDER BY d.fecha_subida DESC"
            
            documentos = db.fetch_all(query, tuple(params))
        except Exception as table_error:
            # Si falla el JOIN, intentar sin JOIN
            logger.warning(f"Error al consultar documentos con JOIN, intentando sin JOIN: {str(table_error)}")
            try:
                query = """
                    SELECT 
                        d.*,
                        'Empleado ID: ' || d.id_empleado as nombre_empleado
                    FROM Documentos d
                    WHERE 1=1
                """
                
                if id_empleado:
                    query += " AND d.id_empleado = ?"
                    params.append(id_empleado)
                if tipo_documento:
                    query += " AND d.tipo_documento = ?"
                    params.append(tipo_documento)
                
                query += " ORDER BY d.fecha_subida DESC"
                
                documentos = db.fetch_all(query, tuple(params))
            except Exception as fallback_error:
                logger.error(f"Error al consultar documentos sin JOIN: {str(fallback_error)}")
                # Si la tabla no existe, retornar lista vacía
                if 'no such table' in str(fallback_error).lower() or 'does not exist' in str(fallback_error).lower():
                    logger.info("Tabla Documentos no existe, retornando lista vacía")
                    documentos = []
                else:
                    raise
        
        return {"success": True, "data": documentos, "count": len(documentos)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado al obtener documentos: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error al obtener documentos: {str(e)}"
        )

# ============================================================================
#                           ENDPOINTS DE CAPACITACIONES
# ============================================================================

@app.get("/api/capacitaciones", response_model=dict)
async def listar_capacitaciones(
    id_empleado: Optional[int] = None, 
    db: Database = Depends(get_db)
):
    """Listar todas las capacitaciones, opcionalmente filtradas por empleado"""
    try:
        # Verificar que la conexión a la base de datos esté activa
        if not db.connection:
            db.connect()
        
        capacitaciones = []
        
        try:
            if id_empleado:
                # Filtrar por empleado específico
                capacitaciones = db.fetch_all("""
                    SELECT c.*, 
                           COALESCE(e.nombre || ' ' || e.apellido, 'Empleado no encontrado') as nombre_empleado
                    FROM Capacitaciones c
                    LEFT JOIN Empleados e ON c.id_empleado = e.id_empleado
                    WHERE c.id_empleado = ?
                    ORDER BY c.fecha_inicio DESC
                """, (id_empleado,))
            else:
                # Listar todas
                capacitaciones = db.fetch_all("""
                    SELECT c.*, 
                           COALESCE(e.nombre || ' ' || e.apellido, 'Empleado no encontrado') as nombre_empleado
                    FROM Capacitaciones c
                    LEFT JOIN Empleados e ON c.id_empleado = e.id_empleado
                    ORDER BY c.fecha_inicio DESC
                """)
        except Exception as e:
            error_msg = str(e).lower()
            logger.warning(f"Error al consultar capacitaciones: {str(e)}")
            
            # Si la tabla no existe, retornar lista vacía
            if 'no such table' in error_msg or 'does not exist' in error_msg:
                logger.info("Tabla Capacitaciones no existe, retornando lista vacía")
                capacitaciones = []
            else:
                # Intentar sin JOIN como fallback
                try:
                    if id_empleado:
                        capacitaciones = db.fetch_all(
                            "SELECT * FROM Capacitaciones WHERE id_empleado = ? ORDER BY fecha_inicio DESC",
                            (id_empleado,)
                        )
                    else:
                        capacitaciones = db.fetch_all(
                            "SELECT * FROM Capacitaciones ORDER BY fecha_inicio DESC"
                        )
                    # Agregar nombre de empleado como campo vacío
                    for cap in capacitaciones:
                        cap['nombre_empleado'] = f"Empleado ID: {cap['id_empleado']}"
                except Exception:
                    capacitaciones = []
        
        return {
            "success": True,
            "data": capacitaciones,
            "count": len(capacitaciones)
        }
    except Exception as e:
        logger.error(f"Error inesperado al obtener capacitaciones: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener capacitaciones: {str(e)}"
        )

@app.get("/api/capacitaciones/{capacitacion_id}", response_model=dict)
async def obtener_capacitacion(capacitacion_id: int, db: Database = Depends(get_db)):
    """Obtener una capacitación por ID"""
    try:
        # Verificar que la conexión a la base de datos esté activa
        if not db.connection:
            db.connect()
        
        capacitacion = None
        
        try:
            capacitacion = db.fetch_one("""
                SELECT c.*, 
                       COALESCE(e.nombre || ' ' || e.apellido, 'Empleado no encontrado') as nombre_empleado,
                       e.correo as email_empleado
                FROM Capacitaciones c
                LEFT JOIN Empleados e ON c.id_empleado = e.id_empleado
                WHERE c.id_capacitacion = ?
            """, (capacitacion_id,))
        except Exception as e:
            logger.warning(f"Error con JOIN en capacitación: {str(e)}")
            # Intentar sin JOIN
            try:
                capacitacion = db.fetch_one(
                    "SELECT * FROM Capacitaciones WHERE id_capacitacion = ?",
                    (capacitacion_id,)
                )
                if capacitacion:
                    capacitacion['nombre_empleado'] = f"Empleado ID: {capacitacion['id_empleado']}"
            except Exception:
                capacitacion = None
        
        if not capacitacion:
            raise HTTPException(
                status_code=404,
                detail=f"Capacitación con ID {capacitacion_id} no encontrada"
            )
        
        return {
            "success": True,
            "data": capacitacion
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener capacitación: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener capacitación: {str(e)}"
        )

@app.post("/api/capacitaciones", response_model=dict, status_code=201)
async def crear_capacitacion(capacitacion: CapacitacionCreate, db: Database = Depends(get_db)):
    """Crear una nueva capacitación"""
    try:
        # Verificar que la conexión a la base de datos esté activa
        if not db.connection:
            db.connect()
        
        # Verificar que el empleado existe
        empleado = db.fetch_one(
            "SELECT id_empleado, nombre, apellido FROM Empleados WHERE id_empleado = ?",
            (capacitacion.id_empleado,)
        )
        
        if not empleado:
            raise HTTPException(
                status_code=404,
                detail=f"Empleado con ID {capacitacion.id_empleado} no encontrado"
            )
        
        # Insertar la capacitación
        cursor = db.execute_query("""
            INSERT INTO Capacitaciones (id_empleado, nombre_curso, institucion, fecha_inicio, fecha_fin, certificado)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            capacitacion.id_empleado,
            capacitacion.nombre_curso,
            capacitacion.institucion,
            capacitacion.fecha_inicio,
            capacitacion.fecha_fin,
            capacitacion.certificado
        ))
        
        # Obtener la capacitación recién creada
        nueva_capacitacion = None
        try:
            nueva_capacitacion = db.fetch_one("""
                SELECT c.*, 
                       COALESCE(e.nombre || ' ' || e.apellido, 'Empleado no encontrado') as nombre_empleado
                FROM Capacitaciones c
                LEFT JOIN Empleados e ON c.id_empleado = e.id_empleado
                WHERE c.id_capacitacion = ?
            """, (cursor.lastrowid,))
        except Exception:
            # Fallback sin JOIN
            nueva_capacitacion = db.fetch_one(
                "SELECT * FROM Capacitaciones WHERE id_capacitacion = ?",
                (cursor.lastrowid,)
            )
            if nueva_capacitacion:
                nueva_capacitacion['nombre_empleado'] = f"{empleado['nombre']} {empleado['apellido']}"
        
        return {
            "success": True,
            "message": "Capacitación registrada exitosamente",
            "data": nueva_capacitacion
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al crear capacitación: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear capacitación: {str(e)}"
        )

@app.put("/api/capacitaciones/{capacitacion_id}", response_model=dict)
async def actualizar_capacitacion(
    capacitacion_id: int, 
    capacitacion: CapacitacionUpdate, 
    db: Database = Depends(get_db)
):
    """Actualizar una capacitación existente"""
    try:
        # Verificar que la conexión a la base de datos esté activa
        if not db.connection:
            db.connect()
        
        # Verificar que la capacitación existe
        capacitacion_existente = db.fetch_one(
            "SELECT id_capacitacion FROM Capacitaciones WHERE id_capacitacion = ?",
            (capacitacion_id,)
        )
        
        if not capacitacion_existente:
            raise HTTPException(
                status_code=404,
                detail=f"Capacitación con ID {capacitacion_id} no encontrada"
            )
        
        # Construir la consulta de actualización dinámicamente
        campos_actualizar = []
        valores = []
        
        if capacitacion.nombre_curso is not None:
            campos_actualizar.append("nombre_curso = ?")
            valores.append(capacitacion.nombre_curso)
        
        if capacitacion.institucion is not None:
            campos_actualizar.append("institucion = ?")
            valores.append(capacitacion.institucion)
        
        if capacitacion.fecha_inicio is not None:
            campos_actualizar.append("fecha_inicio = ?")
            valores.append(capacitacion.fecha_inicio)
        
        if capacitacion.fecha_fin is not None:
            campos_actualizar.append("fecha_fin = ?")
            valores.append(capacitacion.fecha_fin)
        
        if capacitacion.certificado is not None:
            campos_actualizar.append("certificado = ?")
            valores.append(capacitacion.certificado)
        
        # Si no hay campos para actualizar, retornar sin cambios
        if not campos_actualizar:
            capacitacion_actual = db.fetch_one(
                "SELECT * FROM Capacitaciones WHERE id_capacitacion = ?",
                (capacitacion_id,)
            )
            return {
                "success": True,
                "message": "No hay cambios para aplicar",
                "data": capacitacion_actual
            }
        
        # Agregar el ID al final de los valores
        valores.append(capacitacion_id)
        
        # Ejecutar la actualización
        query = f"UPDATE Capacitaciones SET {', '.join(campos_actualizar)} WHERE id_capacitacion = ?"
        db.execute_query(query, tuple(valores))
        
        # Obtener la capacitación actualizada
        capacitacion_actualizada = None
        try:
            capacitacion_actualizada = db.fetch_one("""
                SELECT c.*, 
                       COALESCE(e.nombre || ' ' || e.apellido, 'Empleado no encontrado') as nombre_empleado
                FROM Capacitaciones c
                LEFT JOIN Empleados e ON c.id_empleado = e.id_empleado
                WHERE c.id_capacitacion = ?
            """, (capacitacion_id,))
        except Exception:
            capacitacion_actualizada = db.fetch_one(
                "SELECT * FROM Capacitaciones WHERE id_capacitacion = ?",
                (capacitacion_id,)
            )
        
        return {
            "success": True,
            "message": "Capacitación actualizada exitosamente",
            "data": capacitacion_actualizada
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar capacitación: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar capacitación: {str(e)}"
        )

@app.delete("/api/capacitaciones/{capacitacion_id}", response_model=dict)
async def eliminar_capacitacion(capacitacion_id: int, db: Database = Depends(get_db)):
    """Eliminar una capacitación"""
    try:
        # Verificar que la conexión a la base de datos esté activa
        if not db.connection:
            db.connect()
        
        # Verificar que la capacitación existe
        capacitacion = db.fetch_one(
            "SELECT id_capacitacion, nombre_curso FROM Capacitaciones WHERE id_capacitacion = ?",
            (capacitacion_id,)
        )
        
        if not capacitacion:
            raise HTTPException(
                status_code=404,
                detail=f"Capacitación con ID {capacitacion_id} no encontrada"
            )
        
        # Eliminar la capacitación
        db.execute_query(
            "DELETE FROM Capacitaciones WHERE id_capacitacion = ?",
            (capacitacion_id,)
        )
        
        return {
            "success": True,
            "message": f"Capacitación '{capacitacion['nombre_curso']}' eliminada exitosamente"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar capacitación: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al eliminar capacitación: {str(e)}"
        )

# ============================================================================
#                           ENDPOINTS DE EVALUACIONES
# ============================================================================

@app.get("/api/evaluaciones", response_model=dict)
async def listar_evaluaciones(
    id_empleado: Optional[int] = None,
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None,
    db: Database = Depends(get_db)
):
    """Listar todas las evaluaciones, con filtros opcionales"""
    try:
        # Verificar que la conexión a la base de datos esté activa
        if not db.connection:
            db.connect()
        
        evaluaciones = []
        
        try:
            # Construir query dinámica con filtros
            query = """
                SELECT ev.*, 
                       COALESCE(e.nombre || ' ' || e.apellido, 'Empleado no encontrado') as nombre_empleado
                FROM Evaluaciones ev
                LEFT JOIN Empleados e ON ev.id_empleado = e.id_empleado
                WHERE 1=1
            """
            params = []
            
            if id_empleado:
                query += " AND ev.id_empleado = ?"
                params.append(id_empleado)
            
            if fecha_inicio:
                query += " AND ev.fecha >= ?"
                params.append(fecha_inicio)
            
            if fecha_fin:
                query += " AND ev.fecha <= ?"
                params.append(fecha_fin)
            
            query += " ORDER BY ev.fecha DESC"
            
            evaluaciones = db.fetch_all(query, tuple(params))
            
        except Exception as e:
            error_msg = str(e).lower()
            logger.warning(f"Error al consultar evaluaciones: {str(e)}")
            
            # Si la tabla no existe, retornar lista vacía
            if 'no such table' in error_msg or 'does not exist' in error_msg:
                logger.info("Tabla Evaluaciones no existe, retornando lista vacía")
                evaluaciones = []
            else:
                # Intentar sin JOIN como fallback
                try:
                    query_fallback = "SELECT * FROM Evaluaciones WHERE 1=1"
                    params_fallback = []
                    
                    if id_empleado:
                        query_fallback += " AND id_empleado = ?"
                        params_fallback.append(id_empleado)
                    
                    if fecha_inicio:
                        query_fallback += " AND fecha >= ?"
                        params_fallback.append(fecha_inicio)
                    
                    if fecha_fin:
                        query_fallback += " AND fecha <= ?"
                        params_fallback.append(fecha_fin)
                    
                    query_fallback += " ORDER BY fecha DESC"
                    
                    evaluaciones = db.fetch_all(query_fallback, tuple(params_fallback))
                    
                    # Agregar nombre de empleado como campo
                    for ev in evaluaciones:
                        ev['nombre_empleado'] = f"Empleado ID: {ev['id_empleado']}"
                except Exception:
                    evaluaciones = []
        
        return {
            "success": True,
            "data": evaluaciones,
            "count": len(evaluaciones)
        }
    except Exception as e:
        logger.error(f"Error inesperado al obtener evaluaciones: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener evaluaciones: {str(e)}"
        )

@app.get("/api/evaluaciones/{evaluacion_id}", response_model=dict)
async def obtener_evaluacion(evaluacion_id: int, db: Database = Depends(get_db)):
    """Obtener una evaluación por ID"""
    try:
        # Verificar que la conexión a la base de datos esté activa
        if not db.connection:
            db.connect()
        
        evaluacion = None
        
        try:
            evaluacion = db.fetch_one("""
                SELECT ev.*, 
                       COALESCE(e.nombre || ' ' || e.apellido, 'Empleado no encontrado') as nombre_empleado,
                       e.correo as email_empleado,
                       d.nombre_departamento as departamento
                FROM Evaluaciones ev
                LEFT JOIN Empleados e ON ev.id_empleado = e.id_empleado
                LEFT JOIN Departamentos d ON e.id_departamento = d.id_departamento
                WHERE ev.id_evaluacion = ?
            """, (evaluacion_id,))
        except Exception as e:
            logger.warning(f"Error con JOIN en evaluación: {str(e)}")
            # Intentar sin JOIN
            try:
                evaluacion = db.fetch_one(
                    "SELECT * FROM Evaluaciones WHERE id_evaluacion = ?",
                    (evaluacion_id,)
                )
                if evaluacion:
                    evaluacion['nombre_empleado'] = f"Empleado ID: {evaluacion['id_empleado']}"
            except Exception:
                evaluacion = None
        
        if not evaluacion:
            raise HTTPException(
                status_code=404,
                detail=f"Evaluación con ID {evaluacion_id} no encontrada"
            )
        
        return {
            "success": True,
            "data": evaluacion
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener evaluación: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener evaluación: {str(e)}"
        )

@app.post("/api/evaluaciones", response_model=dict, status_code=201)
async def crear_evaluacion(evaluacion: EvaluacionCreate, db: Database = Depends(get_db)):
    """Crear una nueva evaluación de desempeño"""
    try:
        # Verificar que la conexión a la base de datos esté activa
        if not db.connection:
            db.connect()
        
        # Verificar que el empleado existe
        empleado = db.fetch_one(
            "SELECT id_empleado, nombre, apellido FROM Empleados WHERE id_empleado = ?",
            (evaluacion.id_empleado,)
        )
        
        if not empleado:
            raise HTTPException(
                status_code=404,
                detail=f"Empleado con ID {evaluacion.id_empleado} no encontrado"
            )
        
        # Validar el puntaje
        if evaluacion.puntaje < 0 or evaluacion.puntaje > 100:
            raise HTTPException(
                status_code=400,
                detail="El puntaje debe estar entre 0 y 100"
            )
        
        # Insertar la evaluación
        cursor = db.execute_query("""
            INSERT INTO Evaluaciones (id_empleado, fecha, evaluador, puntaje, observaciones)
            VALUES (?, ?, ?, ?, ?)
        """, (
            evaluacion.id_empleado,
            evaluacion.fecha,
            evaluacion.evaluador,
            evaluacion.puntaje,
            evaluacion.observaciones
        ))
        
        # Obtener la evaluación recién creada
        nueva_evaluacion = None
        try:
            nueva_evaluacion = db.fetch_one("""
                SELECT ev.*, 
                       COALESCE(e.nombre || ' ' || e.apellido, 'Empleado no encontrado') as nombre_empleado
                FROM Evaluaciones ev
                LEFT JOIN Empleados e ON ev.id_empleado = e.id_empleado
                WHERE ev.id_evaluacion = ?
            """, (cursor.lastrowid,))
        except Exception:
            # Fallback sin JOIN
            nueva_evaluacion = db.fetch_one(
                "SELECT * FROM Evaluaciones WHERE id_evaluacion = ?",
                (cursor.lastrowid,)
            )
            if nueva_evaluacion:
                nueva_evaluacion['nombre_empleado'] = f"{empleado['nombre']} {empleado['apellido']}"
        
        return {
            "success": True,
            "message": "Evaluación registrada exitosamente",
            "data": nueva_evaluacion
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al crear evaluación: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear evaluación: {str(e)}"
        )

@app.put("/api/evaluaciones/{evaluacion_id}", response_model=dict)
async def actualizar_evaluacion(
    evaluacion_id: int, 
    evaluacion: EvaluacionUpdate, 
    db: Database = Depends(get_db)
):
    """Actualizar una evaluación existente"""
    try:
        # Verificar que la conexión a la base de datos esté activa
        if not db.connection:
            db.connect()
        
        # Verificar que la evaluación existe
        evaluacion_existente = db.fetch_one(
            "SELECT id_evaluacion FROM Evaluaciones WHERE id_evaluacion = ?",
            (evaluacion_id,)
        )
        
        if not evaluacion_existente:
            raise HTTPException(
                status_code=404,
                detail=f"Evaluación con ID {evaluacion_id} no encontrada"
            )
        
        # Validar el puntaje si se proporciona
        if evaluacion.puntaje is not None and (evaluacion.puntaje < 0 or evaluacion.puntaje > 100):
            raise HTTPException(
                status_code=400,
                detail="El puntaje debe estar entre 0 y 100"
            )
        
        # Construir la consulta de actualización dinámicamente
        campos_actualizar = []
        valores = []
        
        if evaluacion.fecha is not None:
            campos_actualizar.append("fecha = ?")
            valores.append(evaluacion.fecha)
        
        if evaluacion.evaluador is not None:
            campos_actualizar.append("evaluador = ?")
            valores.append(evaluacion.evaluador)
        
        if evaluacion.puntaje is not None:
            campos_actualizar.append("puntaje = ?")
            valores.append(evaluacion.puntaje)
        
        if evaluacion.observaciones is not None:
            campos_actualizar.append("observaciones = ?")
            valores.append(evaluacion.observaciones)
        
        # Si no hay campos para actualizar, retornar sin cambios
        if not campos_actualizar:
            evaluacion_actual = db.fetch_one(
                "SELECT * FROM Evaluaciones WHERE id_evaluacion = ?",
                (evaluacion_id,)
            )
            return {
                "success": True,
                "message": "No hay cambios para aplicar",
                "data": evaluacion_actual
            }
        
        # Agregar el ID al final de los valores
        valores.append(evaluacion_id)
        
        # Ejecutar la actualización
        query = f"UPDATE Evaluaciones SET {', '.join(campos_actualizar)} WHERE id_evaluacion = ?"
        db.execute_query(query, tuple(valores))
        
        # Obtener la evaluación actualizada
        evaluacion_actualizada = None
        try:
            evaluacion_actualizada = db.fetch_one("""
                SELECT ev.*, 
                       COALESCE(e.nombre || ' ' || e.apellido, 'Empleado no encontrado') as nombre_empleado
                FROM Evaluaciones ev
                LEFT JOIN Empleados e ON ev.id_empleado = e.id_empleado
                WHERE ev.id_evaluacion = ?
            """, (evaluacion_id,))
        except Exception:
            evaluacion_actualizada = db.fetch_one(
                "SELECT * FROM Evaluaciones WHERE id_evaluacion = ?",
                (evaluacion_id,)
            )
        
        return {
            "success": True,
            "message": "Evaluación actualizada exitosamente",
            "data": evaluacion_actualizada
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar evaluación: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar evaluación: {str(e)}"
        )

@app.delete("/api/evaluaciones/{evaluacion_id}", response_model=dict)
async def eliminar_evaluacion(evaluacion_id: int, db: Database = Depends(get_db)):
    """Eliminar una evaluación"""
    try:
        # Verificar que la conexión a la base de datos esté activa
        if not db.connection:
            db.connect()
        
        # Verificar que la evaluación existe
        evaluacion = db.fetch_one(
            "SELECT id_evaluacion, fecha, evaluador FROM Evaluaciones WHERE id_evaluacion = ?",
            (evaluacion_id,)
        )
        
        if not evaluacion:
            raise HTTPException(
                status_code=404,
                detail=f"Evaluación con ID {evaluacion_id} no encontrada"
            )
        
        # Eliminar la evaluación
        db.execute_query(
            "DELETE FROM Evaluaciones WHERE id_evaluacion = ?",
            (evaluacion_id,)
        )
        
        return {
            "success": True,
            "message": f"Evaluación del {evaluacion['fecha']} por {evaluacion['evaluador']} eliminada exitosamente"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar evaluación: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al eliminar evaluación: {str(e)}"
        )

# ============================================================================
#                        ENDPOINTS DE NOTIFICACIONES
# ============================================================================

@app.get("/api/notificaciones", response_model=dict)
async def obtener_notificaciones(
    usuario_id: Optional[int] = None,
    is_read: Optional[bool] = None,
    tipo: Optional[str] = None,
    limit: int = 50,
    db: Database = Depends(get_db)
):
    """
    Obtener notificaciones con filtros opcionales
    
    - **usuario_id**: ID del usuario (opcional)
    - **is_read**: Filtrar por leídas/no leídas (opcional)
    - **tipo**: Filtrar por tipo de notificación (opcional)
    - **limit**: Número máximo de notificaciones a retornar (default: 50)
    """
    try:
        if not db.connection:
            db.connect()
        
        # Construir query con filtros
        query = "SELECT * FROM Notificaciones WHERE 1=1"
        params = []
        
        if usuario_id is not None:
            query += " AND usuario_id = ?"
            params.append(usuario_id)
        
        if is_read is not None:
            query += " AND is_read = ?"
            params.append(1 if is_read else 0)
        
        if tipo:
            query += " AND tipo = ?"
            params.append(tipo)
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        notificaciones = db.fetch_all(query, tuple(params))
        
        return {
            "success": True,
            "count": len(notificaciones),
            "data": notificaciones
        }
    except Exception as e:
        logger.error(f"Error al obtener notificaciones: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener notificaciones: {str(e)}"
        )

@app.get("/api/notificaciones/{notificacion_id}", response_model=dict)
async def obtener_notificacion(notificacion_id: int, db: Database = Depends(get_db)):
    """Obtener una notificación específica"""
    try:
        if not db.connection:
            db.connect()
        
        notificacion = db.fetch_one(
            "SELECT * FROM Notificaciones WHERE id = ?",
            (notificacion_id,)
        )
        
        if not notificacion:
            raise HTTPException(
                status_code=404,
                detail=f"Notificación con ID {notificacion_id} no encontrada"
            )
        
        return {
            "success": True,
            "data": notificacion
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener notificación: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener notificación: {str(e)}"
        )

@app.get("/api/notificaciones/usuario/{usuario_id}/no-leidas", response_model=dict)
async def obtener_notificaciones_no_leidas(usuario_id: int, db: Database = Depends(get_db)):
    """Obtener notificaciones no leídas de un usuario"""
    try:
        if not db.connection:
            db.connect()
        
        notificaciones = db.fetch_all(
            """SELECT * FROM Notificaciones 
               WHERE usuario_id = ? AND is_read = 0 
               ORDER BY created_at DESC""",
            (usuario_id,)
        )
        
        return {
            "success": True,
            "count": len(notificaciones),
            "data": notificaciones
        }
    except Exception as e:
        logger.error(f"Error al obtener notificaciones no leídas: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener notificaciones no leídas: {str(e)}"
        )

@app.get("/api/notificaciones/usuario/{usuario_id}/count", response_model=dict)
async def contar_notificaciones_no_leidas(usuario_id: int, db: Database = Depends(get_db)):
    """Obtener el conteo de notificaciones no leídas de un usuario"""
    try:
        if not db.connection:
            db.connect()
        
        resultado = db.fetch_one(
            "SELECT COUNT(*) as count FROM Notificaciones WHERE usuario_id = ? AND is_read = 0",
            (usuario_id,)
        )
        
        return {
            "success": True,
            "usuario_id": usuario_id,
            "unread_count": resultado['count'] if resultado else 0
        }
    except Exception as e:
        logger.error(f"Error al contar notificaciones: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al contar notificaciones: {str(e)}"
        )

@app.post("/api/notificaciones", response_model=dict, status_code=201)
async def crear_notificacion(notificacion: NotificacionCreate, db: Database = Depends(get_db)):
    """Crear una nueva notificación"""
    try:
        if not db.connection:
            db.connect()
        
        # Verificar que el usuario existe
        usuario = db.fetch_one(
            "SELECT id FROM Usuarios WHERE id = ?",
            (notificacion.usuario_id,)
        )
        
        if not usuario:
            raise HTTPException(
                status_code=404,
                detail=f"Usuario con ID {notificacion.usuario_id} no encontrado"
            )
        
        # Insertar notificación
        db.execute_query(
            """INSERT INTO Notificaciones 
               (usuario_id, tipo, titulo, mensaje, modulo, modulo_id, redirect_url, metadata, is_read)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)""",
            (
                notificacion.usuario_id,
                notificacion.tipo,
                notificacion.titulo,
                notificacion.mensaje,
                notificacion.modulo,
                notificacion.modulo_id,
                notificacion.redirect_url,
                notificacion.metadata
            )
        )
        
        # Obtener la notificación creada
        nueva_notificacion = db.fetch_one(
            "SELECT * FROM Notificaciones WHERE id = last_insert_rowid()"
        )
        
        return {
            "success": True,
            "message": "Notificación creada exitosamente",
            "data": nueva_notificacion
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al crear notificación: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear notificación: {str(e)}"
        )

@app.patch("/api/notificaciones/{notificacion_id}", response_model=dict)
async def actualizar_notificacion(
    notificacion_id: int,
    notificacion: NotificacionUpdate,
    db: Database = Depends(get_db)
):
    """Actualizar una notificación (principalmente para marcar como leída)"""
    try:
        if not db.connection:
            db.connect()
        
        # Verificar que la notificación existe
        notif_existente = db.fetch_one(
            "SELECT * FROM Notificaciones WHERE id = ?",
            (notificacion_id,)
        )
        
        if not notif_existente:
            raise HTTPException(
                status_code=404,
                detail=f"Notificación con ID {notificacion_id} no encontrada"
            )
        
        # Actualizar campos
        campos = []
        params = []
        
        if notificacion.is_read is not None:
            campos.append("is_read = ?")
            params.append(1 if notificacion.is_read else 0)
            
            if notificacion.is_read:
                campos.append("read_at = ?")
                params.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        if notificacion.read_at:
            campos.append("read_at = ?")
            params.append(notificacion.read_at)
        
        if not campos:
            raise HTTPException(
                status_code=400,
                detail="No hay campos para actualizar"
            )
        
        params.append(notificacion_id)
        query = f"UPDATE Notificaciones SET {', '.join(campos)} WHERE id = ?"
        
        db.execute_query(query, tuple(params))
        
        # Obtener notificación actualizada
        notif_actualizada = db.fetch_one(
            "SELECT * FROM Notificaciones WHERE id = ?",
            (notificacion_id,)
        )
        
        return {
            "success": True,
            "message": "Notificación actualizada exitosamente",
            "data": notif_actualizada
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar notificación: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar notificación: {str(e)}"
        )

@app.post("/api/notificaciones/marcar-todas-leidas/{usuario_id}", response_model=dict)
async def marcar_todas_leidas(usuario_id: int, db: Database = Depends(get_db)):
    """Marcar todas las notificaciones de un usuario como leídas"""
    try:
        if not db.connection:
            db.connect()
        
        db.execute_query(
            """UPDATE Notificaciones 
               SET is_read = 1, read_at = ? 
               WHERE usuario_id = ? AND is_read = 0""",
            (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), usuario_id)
        )
        
        return {
            "success": True,
            "message": "Todas las notificaciones marcadas como leídas"
        }
    except Exception as e:
        logger.error(f"Error al marcar notificaciones como leídas: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al marcar notificaciones como leídas: {str(e)}"
        )

@app.delete("/api/notificaciones/{notificacion_id}", response_model=dict)
async def eliminar_notificacion(notificacion_id: int, db: Database = Depends(get_db)):
    """Eliminar una notificación"""
    try:
        if not db.connection:
            db.connect()
        
        # Verificar que la notificación existe
        notificacion = db.fetch_one(
            "SELECT * FROM Notificaciones WHERE id = ?",
            (notificacion_id,)
        )
        
        if not notificacion:
            raise HTTPException(
                status_code=404,
                detail=f"Notificación con ID {notificacion_id} no encontrada"
            )
        
        db.execute_query(
            "DELETE FROM Notificaciones WHERE id = ?",
            (notificacion_id,)
        )
        
        return {
            "success": True,
            "message": "Notificación eliminada exitosamente"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar notificación: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al eliminar notificación: {str(e)}"
        )

@app.delete("/api/notificaciones/usuario/{usuario_id}/leidas", response_model=dict)
async def eliminar_notificaciones_leidas(usuario_id: int, db: Database = Depends(get_db)):
    """Eliminar todas las notificaciones leídas de un usuario"""
    try:
        if not db.connection:
            db.connect()
        
        resultado = db.fetch_one(
            "SELECT COUNT(*) as count FROM Notificaciones WHERE usuario_id = ? AND is_read = 1",
            (usuario_id,)
        )
        
        count = resultado['count'] if resultado else 0
        
        db.execute_query(
            "DELETE FROM Notificaciones WHERE usuario_id = ? AND is_read = 1",
            (usuario_id,)
        )
        
        return {
            "success": True,
            "message": f"{count} notificaciones eliminadas",
            "count": count
        }
    except Exception as e:
        logger.error(f"Error al eliminar notificaciones leídas: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al eliminar notificaciones leídas: {str(e)}"
        )

# ============================================================================
#                      ENDPOINTS DE EXPORTACIÓN DE REPORTES
# ============================================================================

@app.get("/api/reportes/empleados/export/pdf")
async def export_employees_pdf(db: Database = Depends(get_db)):
    """Exportar reporte de empleados a PDF"""
    try:
        from fastapi.responses import StreamingResponse
        
        # Obtener datos de empleados con sus relaciones
        empleados = db.fetch_all("""
            SELECT 
                e.id as id_empleado,
                e.nombre,
                e.apellido,
                e.email,
                COALESCE(d.nombre, 'Sin departamento') as departamento,
                e.puesto,
                e.salario,
                e.fecha_ingreso,
                CASE WHEN e.activo = 1 THEN 'Activo' ELSE 'Inactivo' END as estado
            FROM empleados e
            LEFT JOIN departamentos d ON e.departamento_id = d.id
            ORDER BY e.nombre, e.apellido
        """)
        
        if not empleados:
            raise HTTPException(status_code=404, detail="No hay empleados para exportar")
        
        # Generar PDF
        pdf_buffer = ExportHelper.export_employee_report_pdf(empleados)
        
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=reporte_empleados_{datetime.now().strftime('%Y%m%d')}.pdf"
            }
        )
    except Exception as e:
        logger.error(f"Error al exportar empleados a PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al exportar: {str(e)}")

@app.get("/api/reportes/empleados/export/excel")
async def export_employees_excel(db: Database = Depends(get_db)):
    """Exportar reporte de empleados a Excel"""
    try:
        from fastapi.responses import StreamingResponse
        
        # Obtener datos de empleados
        empleados = db.fetch_all("""
            SELECT 
                e.id as id_empleado,
                e.nombre,
                e.apellido,
                e.email,
                COALESCE(d.nombre, 'Sin departamento') as departamento,
                e.puesto,
                e.salario,
                e.fecha_ingreso,
                CASE WHEN e.activo = 1 THEN 'Activo' ELSE 'Inactivo' END as estado
            FROM empleados e
            LEFT JOIN departamentos d ON e.departamento_id = d.id
            ORDER BY e.nombre, e.apellido
        """)
        
        if not empleados:
            raise HTTPException(status_code=404, detail="No hay empleados para exportar")
        
        # Generar Excel
        excel_buffer = ExportHelper.export_employee_report_excel(empleados)
        
        return StreamingResponse(
            excel_buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename=reporte_empleados_{datetime.now().strftime('%Y%m%d')}.xlsx"
            }
        )
    except Exception as e:
        logger.error(f"Error al exportar empleados a Excel: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al exportar: {str(e)}")

@app.post("/api/reportes/asistencias/export/pdf")
async def export_attendance_pdf(reporte: AsistenciaReporteRequest, db: Database = Depends(get_db)):
    """Exportar reporte de asistencias a PDF"""
    try:
        from fastapi.responses import StreamingResponse
        
        # Construir query base
        query = """
            SELECT 
                COALESCE(e.nombre || ' ' || e.apellido, 'Desconocido') as empleado,
                COALESCE(d.nombre, 'Sin departamento') as departamento,
                COUNT(CASE WHEN a.hora_entrada IS NOT NULL THEN 1 END) as presente,
                COUNT(CASE WHEN a.hora_entrada IS NULL THEN 1 END) as ausente,
                COUNT(CASE WHEN TIME(a.hora_entrada) > '08:30:00' THEN 1 END) as tardanzas,
                ROUND(
                    CAST(COUNT(CASE WHEN a.hora_entrada IS NOT NULL THEN 1 END) AS FLOAT) * 100.0 / 
                    NULLIF(COUNT(*), 0), 2
                ) as porcentaje_asistencia
            FROM asistencias a
            LEFT JOIN empleados e ON a.empleado_id = e.id
            LEFT JOIN departamentos d ON e.departamento_id = d.id
            WHERE a.fecha BETWEEN ? AND ?
        """
        
        params = [reporte.fecha_inicio, reporte.fecha_fin]
        
        if reporte.id_empleado:
            query += " AND a.empleado_id = ?"
            params.append(reporte.id_empleado)
        
        query += " GROUP BY e.id, e.nombre, e.apellido, d.nombre"
        
        asistencias = db.fetch_all(query, tuple(params))
        
        if not asistencias:
            raise HTTPException(status_code=404, detail="No hay datos de asistencia para el período seleccionado")
        
        # Generar PDF
        pdf_buffer = ExportHelper.export_attendance_report_pdf(
            asistencias,
            reporte.fecha_inicio,
            reporte.fecha_fin
        )
        
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=reporte_asistencias_{datetime.now().strftime('%Y%m%d')}.pdf"
            }
        )
    except Exception as e:
        logger.error(f"Error al exportar asistencias a PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al exportar: {str(e)}")

@app.post("/api/reportes/asistencias/export/excel")
async def export_attendance_excel(reporte: AsistenciaReporteRequest, db: Database = Depends(get_db)):
    """Exportar reporte de asistencias a Excel"""
    try:
        from fastapi.responses import StreamingResponse
        
        # Construir query
        query = """
            SELECT 
                COALESCE(e.nombre || ' ' || e.apellido, 'Desconocido') as empleado,
                COALESCE(d.nombre, 'Sin departamento') as departamento,
                COUNT(CASE WHEN a.hora_entrada IS NOT NULL THEN 1 END) as presente,
                COUNT(CASE WHEN a.hora_entrada IS NULL THEN 1 END) as ausente,
                COUNT(CASE WHEN TIME(a.hora_entrada) > '08:30:00' THEN 1 END) as tardanzas,
                ROUND(
                    CAST(COUNT(CASE WHEN a.hora_entrada IS NOT NULL THEN 1 END) AS FLOAT) * 100.0 / 
                    NULLIF(COUNT(*), 0), 2
                ) as porcentaje_asistencia
            FROM asistencias a
            LEFT JOIN empleados e ON a.empleado_id = e.id
            LEFT JOIN departamentos d ON e.departamento_id = d.id
            WHERE a.fecha BETWEEN ? AND ?
        """
        
        params = [reporte.fecha_inicio, reporte.fecha_fin]
        
        if reporte.id_empleado:
            query += " AND a.empleado_id = ?"
            params.append(reporte.id_empleado)
        
        query += " GROUP BY e.id, e.nombre, e.apellido, d.nombre"
        
        asistencias = db.fetch_all(query, tuple(params))
        
        if not asistencias:
            raise HTTPException(status_code=404, detail="No hay datos de asistencia para el período seleccionado")
        
        # Generar Excel
        excel_buffer = ExportHelper.export_attendance_report_excel(
            asistencias,
            reporte.fecha_inicio,
            reporte.fecha_fin
        )
        
        return StreamingResponse(
            excel_buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename=reporte_asistencias_{datetime.now().strftime('%Y%m%d')}.xlsx"
            }
        )
    except Exception as e:
        logger.error(f"Error al exportar asistencias a Excel: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al exportar: {str(e)}")

@app.get("/api/reportes/nomina/export/pdf")
async def export_payroll_pdf(mes: int, anio: int, db: Database = Depends(get_db)):
    """Exportar reporte de nómina a PDF"""
    try:
        from fastapi.responses import StreamingResponse
        
        nominas = db.fetch_all("""
            SELECT 
                COALESCE(e.nombre || ' ' || e.apellido, 'Desconocido') as empleado,
                COALESCE(d.nombre_departamento, 'Sin departamento') as departamento,
                n.salario_base,
                COALESCE(n.bonificaciones_total, 0) as bonificaciones,
                COALESCE(n.deducciones_total, 0) as deducciones,
                n.salario_neto as total
            FROM Nomina n
            LEFT JOIN Empleados e ON n.id_empleado = e.id_empleado
            LEFT JOIN Departamentos d ON e.id_departamento = d.id_departamento
            WHERE n.mes = ? AND n.anio = ?
            ORDER BY e.nombre, e.apellido
        """, (mes, anio))
        
        if not nominas:
            raise HTTPException(status_code=404, detail=f"No hay datos de nómina para {mes}/{anio}")
        
        # Generar PDF
        pdf_buffer = ExportHelper.export_payroll_report_pdf(nominas, mes, anio)
        
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=reporte_nomina_{mes}_{anio}.pdf"
            }
        )
    except Exception as e:
        logger.error(f"Error al exportar nómina a PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al exportar: {str(e)}")

@app.get("/api/reportes/nomina/export/excel")
async def export_payroll_excel(mes: int, anio: int, db: Database = Depends(get_db)):
    """Exportar reporte de nómina a Excel"""
    try:
        from fastapi.responses import StreamingResponse
        
        nominas = db.fetch_all("""
            SELECT 
                COALESCE(e.nombre || ' ' || e.apellido, 'Desconocido') as empleado,
                COALESCE(d.nombre_departamento, 'Sin departamento') as departamento,
                n.salario_base,
                COALESCE(n.bonificaciones_total, 0) as bonificaciones,
                COALESCE(n.deducciones_total, 0) as deducciones,
                n.salario_neto as total
            FROM Nomina n
            LEFT JOIN Empleados e ON n.id_empleado = e.id_empleado
            LEFT JOIN Departamentos d ON e.id_departamento = d.id_departamento
            WHERE n.mes = ? AND n.anio = ?
            ORDER BY e.nombre, e.apellido
        """, (mes, anio))
        
        if not nominas:
            raise HTTPException(status_code=404, detail=f"No hay datos de nómina para {mes}/{anio}")
        
        # Generar Excel
        excel_buffer = ExportHelper.export_payroll_report_excel(nominas, mes, anio)
        
        return StreamingResponse(
            excel_buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename=reporte_nomina_{mes}_{anio}.xlsx"
            }
        )
    except Exception as e:
        logger.error(f"Error al exportar nómina a Excel: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al exportar: {str(e)}")

@app.get("/api/reportes/vacaciones/export/pdf")
async def export_vacations_pdf(db: Database = Depends(get_db)):
    """Exportar reporte de vacaciones a PDF"""
    try:
        from fastapi.responses import StreamingResponse
        
        vacaciones = db.fetch_all("""
            SELECT 
                COALESCE(e.nombre || ' ' || e.apellido, 'Desconocido') as empleado,
                v.tipo,
                v.fecha_inicio,
                v.fecha_fin,
                CAST((julianday(v.fecha_fin) - julianday(v.fecha_inicio) + 1) AS INTEGER) as dias,
                v.estado,
                v.fecha_solicitud
            FROM Vacaciones_Permisos v
            LEFT JOIN Empleados e ON v.id_empleado = e.id_empleado
            ORDER BY v.fecha_solicitud DESC
        """)
        
        if not vacaciones:
            raise HTTPException(status_code=404, detail="No hay datos de vacaciones")
        
        # Generar PDF
        pdf_buffer = ExportHelper.export_vacation_report_pdf(vacaciones)
        
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=reporte_vacaciones_{datetime.now().strftime('%Y%m%d')}.pdf"
            }
        )
    except Exception as e:
        logger.error(f"Error al exportar vacaciones a PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al exportar: {str(e)}")

@app.get("/api/reportes/vacaciones/export/excel")
async def export_vacations_excel(db: Database = Depends(get_db)):
    """Exportar reporte de vacaciones a Excel"""
    try:
        from fastapi.responses import StreamingResponse
        
        vacaciones = db.fetch_all("""
            SELECT 
                COALESCE(e.nombre || ' ' || e.apellido, 'Desconocido') as empleado,
                v.tipo,
                v.fecha_inicio,
                v.fecha_fin,
                CAST((julianday(v.fecha_fin) - julianday(v.fecha_inicio) + 1) AS INTEGER) as dias,
                v.estado,
                v.fecha_solicitud
            FROM Vacaciones_Permisos v
            LEFT JOIN Empleados e ON v.id_empleado = e.id_empleado
            ORDER BY v.fecha_solicitud DESC
        """)
        
        if not vacaciones:
            raise HTTPException(status_code=404, detail="No hay datos de vacaciones")
        
        # Generar Excel
        excel_buffer = ExportHelper.export_vacation_report_excel(vacaciones)
        
        return StreamingResponse(
            excel_buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename=reporte_vacaciones_{datetime.now().strftime('%Y%m%d')}.xlsx"
            }
        )
    except Exception as e:
        logger.error(f"Error al exportar vacaciones a Excel: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al exportar: {str(e)}")

# ============================================================================
#                           PUNTO DE ENTRADA
# ============================================================================

if __name__ == "__main__":
    try:
        print("\nIniciando servidor FastAPI...")
        print("URL: http://localhost:8000")
        print("Docs: http://localhost:8000/docs\n")
        
        uvicorn.run(
            "main:app",
            host="0.0.0.0",  # Escuchar en todas las interfaces
            port=8000,
            reload=True,
            log_level="info",
            access_log=True
        )
    except OSError as e:
        if "Address already in use" in str(e) or "address is already in use" in str(e).lower():
            print("\n" + "="*60)
            print("ERROR: El puerto 8000 ya esta en uso")
            print("="*60)
            print("\nSOLUCIONES:")
            print("1. Cierra otros procesos que usen el puerto 8000")
            print("2. O cambia el puerto en main.py (linea 1368)")
            print("3. Para ver que proceso usa el puerto, ejecuta:")
            print("   netstat -ano | findstr :8000")
            print("="*60 + "\n")
        else:
            print(f"\nERROR al iniciar servidor: {e}\n")
        raise
    except Exception as e:
        print(f"\nERROR INESPERADO: {e}")
        import traceback
        print(f"\nTraceback completo:\n{traceback.format_exc()}\n")
        raise

