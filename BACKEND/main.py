"""
Servidor FastAPI principal para el Sistema de RRHH
"""
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
from contextlib import asynccontextmanager
import uvicorn
from datetime import datetime, date, timedelta
import bcrypt

from database import get_db, Database
from models import (
    UsuarioCreate, UsuarioUpdate, UsuarioResponse, UsuarioLogin,
    DepartamentoCreate, DepartamentoUpdate,
    EmpleadoCreate, EmpleadoUpdate,
    ContratoCreate, ContratoUpdate,
    AsistenciaCreate, AsistenciaUpdate, AsistenciaReporteRequest,
    NominaCreate, NominaUpdate,
    VacacionPermisoCreate, VacacionPermisoUpdate,
    DocumentoCreate, DocumentoUpdate
)

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

# ============================================================================
#                           LIFESPAN EVENT HANDLER
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Maneja eventos de inicio y cierre de la aplicación"""
    # Startup
    try:
        db = get_db()
        db.create_tables()
        print("[OK] Base de datos inicializada")
    except Exception as e:
        print(f"[ERROR] Error al inicializar base de datos: {e}")
    
    yield
    
    # Shutdown (si necesitas limpiar recursos al cerrar)
    # Aquí puedes agregar código de limpieza si es necesario
    pass

# Crear instancia de FastAPI con lifespan
app = FastAPI(
    title="Sistema de RRHH API",
    description="API para gestión de Recursos Humanos",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS
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
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    """Listar todos los usuarios activos"""
    try:
        usuarios = db.fetch_all(
            "SELECT id, nombre, email, rol, fecha_creacion, activo FROM usuarios WHERE activo = 1"
        )
        return {
            "success": True,
            "data": usuarios,
            "count": len(usuarios)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener usuarios: {str(e)}")

@app.get("/api/usuarios/{usuario_id}", response_model=dict)
async def obtener_usuario(usuario_id: int, db: Database = Depends(get_db)):
    """Obtener un usuario por ID"""
    try:
        usuario = db.fetch_one(
            "SELECT id, nombre, email, rol, fecha_creacion, activo FROM usuarios WHERE id = ? AND activo = 1",
            (usuario_id,)
        )
        if not usuario:
            raise HTTPException(status_code=404, detail=f"Usuario con ID {usuario_id} no encontrado")
        return {"success": True, "data": usuario}
    except HTTPException:
        raise
    except Exception as e:
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
    """Autenticar un usuario"""
    try:
        # Buscar usuario por email
        usuario = db.fetch_one(
            "SELECT id, nombre, email, password, rol, activo FROM usuarios WHERE email = ?",
            (credenciales.email,)
        )
        
        if not usuario:
            raise HTTPException(status_code=401, detail="Credenciales inválidas")
        
        # Verificar si el usuario está activo
        if usuario['activo'] != 1:
            raise HTTPException(status_code=403, detail="Usuario inactivo")
        
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
        
        if not password_valid:
            raise HTTPException(status_code=401, detail="Credenciales inválidas")
        
        # Retornar datos del usuario (sin password)
        usuario_response = {
            "id": usuario['id'],
            "nombre": usuario['nombre'],
            "email": usuario['email'],
            "rol": usuario['rol'],
            "fecha_creacion": usuario.get('fecha_creacion', ''),
            "activo": usuario['activo']
        }
        
        return {
            "success": True,
            "message": "Login exitoso",
            "data": usuario_response
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en el login: {str(e)}")

# ============================================================================
#                           ENDPOINTS DE DEPARTAMENTOS
# ============================================================================

@app.get("/api/departamentos", response_model=dict)
async def listar_departamentos(db: Database = Depends(get_db)):
    """Listar todos los departamentos"""
    try:
        # Intentar obtener de la tabla nueva primero
        departamentos = db.fetch_all(
            "SELECT id_departamento as id, nombre_departamento as nombre, descripcion FROM Departamentos"
        )
        
        # Si no hay datos en la tabla nueva, usar la tabla antigua
        if not departamentos:
            departamentos = db.fetch_all(
                "SELECT id, nombre, descripcion, fecha_creacion, activo FROM departamentos WHERE activo = 1"
            )
        
        return {
            "status": "success",
            "data": departamentos,
            "count": len(departamentos)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener departamentos: {str(e)}")

@app.get("/api/departamentos/{departamento_id}", response_model=dict)
async def obtener_departamento(departamento_id: int, db: Database = Depends(get_db)):
    """Obtener un departamento por ID"""
    try:
        # Intentar tabla nueva
        departamento = db.fetch_one(
            "SELECT id_departamento as id, nombre_departamento as nombre, descripcion FROM Departamentos WHERE id_departamento = ?",
            (departamento_id,)
        )
        
        # Si no existe, buscar en tabla antigua
        if not departamento:
            departamento = db.fetch_one(
                "SELECT id, nombre, descripcion, fecha_creacion, activo FROM departamentos WHERE id = ? AND activo = 1",
                (departamento_id,)
            )
        
        if not departamento:
            raise HTTPException(status_code=404, detail=f"Departamento con ID {departamento_id} no encontrado")
        
        return {"status": "success", "data": departamento}
    except HTTPException:
        raise
    except Exception as e:
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
        # Intentar obtener de la tabla nueva (Empleados)
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
                COALESCE(e.salario, 0) as salario,
                d.nombre_departamento as departamento_nombre,
                p.nombre_puesto as puesto_nombre
            FROM Empleados e
            LEFT JOIN Departamentos d ON e.id_departamento = d.id_departamento
            LEFT JOIN Puestos p ON e.id_puesto = p.id_puesto
        """)
        
        # Si no hay datos, usar tabla antigua
        if not empleados:
            empleados = db.fetch_all("""
                SELECT 
                    e.id,
                    e.nombre,
                    e.apellido,
                    e.email,
                    e.telefono,
                    e.departamento_id,
                    e.puesto,
                    e.fecha_ingreso,
                    e.salario,
                    e.activo,
                    d.nombre as departamento_nombre
                FROM empleados e
                LEFT JOIN departamentos d ON e.departamento_id = d.id
                WHERE e.activo = 1
            """)
        
        return {
            "status": "success",
            "data": empleados,
            "count": len(empleados)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener empleados: {str(e)}")

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
                    e.nombre,
                    e.apellido,
                    e.email,
                    e.telefono,
                    e.departamento_id,
                    e.puesto,
                    e.fecha_ingreso,
                    e.salario,
                    e.activo,
                    d.nombre as departamento_nombre
                FROM empleados e
                LEFT JOIN departamentos d ON e.departamento_id = d.id
                WHERE e.id = ? AND e.activo = 1
            """, (empleado_id,))
        
        if not empleado:
            raise HTTPException(status_code=404, detail=f"Empleado con ID {empleado_id} no encontrado")
        
        return {"status": "success", "data": empleado}
    except HTTPException:
        raise
    except Exception as e:
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
                e.telefono,
                e.fecha_ingreso,
                e.estado,
                e.id_departamento,
                d.nombre_departamento as departamento_nombre
            FROM Empleados e
            LEFT JOIN Departamentos d ON e.id_departamento = d.id_departamento
            WHERE e.id_empleado = ?
        """, (cursor.lastrowid,))
        
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
                e.telefono,
                e.fecha_ingreso,
                e.estado,
                e.id_departamento,
                d.nombre_departamento as departamento_nombre
            FROM Empleados e
            LEFT JOIN Departamentos d ON e.id_departamento = d.id_departamento
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
            """SELECT id, usuario_id, titulo, mensaje, tipo, leido, fecha_creacion 
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
        if id_empleado:
            contratos = db.fetch_all("""
                SELECT c.*, e.nombre || ' ' || e.apellido as empleado_nombre
                FROM Contratos c
                JOIN Empleados e ON c.id_empleado = e.id_empleado
                WHERE c.id_empleado = ?
            """, (id_empleado,))
        else:
            contratos = db.fetch_all("""
                SELECT c.*, e.nombre || ' ' || e.apellido as empleado_nombre
                FROM Contratos c
                JOIN Empleados e ON c.id_empleado = e.id_empleado
            """)
        
        return {"status": "success", "data": contratos, "count": len(contratos)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener contratos: {str(e)}")

@app.get("/api/contratos/{contrato_id}", response_model=dict)
async def obtener_contrato(contrato_id: int, db: Database = Depends(get_db)):
    """Obtener un contrato por ID"""
    try:
        contrato = db.fetch_one("""
            SELECT c.*, e.nombre || ' ' || e.apellido as empleado_nombre
            FROM Contratos c
            JOIN Empleados e ON c.id_empleado = e.id_empleado
            WHERE c.id_contrato = ?
        """, (contrato_id,))
        
        if not contrato:
            raise HTTPException(status_code=404, detail=f"Contrato con ID {contrato_id} no encontrado")
        
        return {"status": "success", "data": contrato}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener contrato: {str(e)}")

@app.post("/api/contratos", response_model=dict, status_code=201)
async def crear_contrato(contrato: ContratoCreate, db: Database = Depends(get_db)):
    """Crear un nuevo contrato"""
    try:
        cursor = db.execute_query("""
            INSERT INTO Contratos (id_empleado, tipo_contrato, fecha_inicio, fecha_fin, salario, condiciones)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            contrato.id_empleado,
            contrato.tipo_contrato,
            contrato.fecha_inicio,
            contrato.fecha_fin,
            contrato.salario,
            contrato.condiciones
        ))
        
        nuevo_contrato = db.fetch_one("""
            SELECT c.*, e.nombre || ' ' || e.apellido as empleado_nombre
            FROM Contratos c
            JOIN Empleados e ON c.id_empleado = e.id_empleado
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
        
        if contrato.tipo_contrato:
            updates.append("tipo_contrato = ?")
            params.append(contrato.tipo_contrato)
        if contrato.fecha_inicio:
            updates.append("fecha_inicio = ?")
            params.append(contrato.fecha_inicio)
        if contrato.fecha_fin is not None:
            updates.append("fecha_fin = ?")
            params.append(contrato.fecha_fin)
        if contrato.salario:
            updates.append("salario = ?")
            params.append(contrato.salario)
        if contrato.condiciones:
            updates.append("condiciones = ?")
            params.append(contrato.condiciones)
        
        if not updates:
            raise HTTPException(status_code=400, detail="No se proporcionaron campos para actualizar")
        
        params.append(contrato_id)
        query = f"UPDATE Contratos SET {', '.join(updates)} WHERE id_contrato = ?"
        db.execute_query(query, tuple(params))
        
        contrato_actualizado = db.fetch_one("""
            SELECT c.*, e.nombre || ' ' || e.apellido as empleado_nombre
            FROM Contratos c
            JOIN Empleados e ON c.id_empleado = e.id_empleado
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
        fecha_limite = (datetime.now() + timedelta(days=dias)).date()
        
        contratos = db.fetch_all("""
            SELECT c.*, e.nombre || ' ' || e.apellido as empleado_nombre,
                   julianday(c.fecha_fin) - julianday('now') as dias_restantes
            FROM Contratos c
            JOIN Empleados e ON c.id_empleado = e.id_empleado
            WHERE c.fecha_fin IS NOT NULL 
            AND c.fecha_fin <= ? 
            AND c.fecha_fin >= date('now')
            ORDER BY c.fecha_fin ASC
        """, (fecha_limite,))
        
        return {"status": "success", "data": contratos, "count": len(contratos), "dias_consulta": dias}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener alertas: {str(e)}")

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
        query = """
            SELECT a.*, e.nombre || ' ' || e.apellido as empleado_nombre
            FROM Asistencias a
            JOIN Empleados e ON a.id_empleado = e.id_empleado
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
        return {"status": "success", "data": asistencias, "count": len(asistencias)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener asistencias: {str(e)}")

@app.get("/api/asistencias/{asistencia_id}", response_model=dict)
async def obtener_asistencia(asistencia_id: int, db: Database = Depends(get_db)):
    """Obtener una asistencia por ID"""
    try:
        asistencia = db.fetch_one("""
            SELECT a.*, e.nombre || ' ' || e.apellido as empleado_nombre
            FROM Asistencias a
            JOIN Empleados e ON a.id_empleado = e.id_empleado
            WHERE a.id_asistencia = ?
        """, (asistencia_id,))
        
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
    """Generar reporte de asistencias por rango de fechas"""
    try:
        query = """
            SELECT a.*, e.nombre || ' ' || e.apellido as empleado_nombre
            FROM Asistencias a
            JOIN Empleados e ON a.id_empleado = e.id_empleado
            WHERE a.fecha >= ? AND a.fecha <= ?
        """
        params = [reporte.fecha_inicio, reporte.fecha_fin]
        
        if reporte.id_empleado:
            query += " AND a.id_empleado = ?"
            params.append(reporte.id_empleado)
        
        query += " ORDER BY a.fecha DESC"
        
        asistencias = db.fetch_all(query, tuple(params))
        
        # Calcular estadísticas
        completas = sum(1 for a in asistencias if a.get('hora_entrada') and a.get('hora_salida'))
        incompletas = sum(1 for a in asistencias if a.get('hora_entrada') and not a.get('hora_salida'))
        faltas = len(asistencias) - completas - incompletas
        
        return {
            "success": True,
            "data": asistencias,
            "count": len(asistencias),
            "estadisticas": {
                "total_registros": len(asistencias),
                "completas": completas,
                "incompletas": incompletas,
                "faltas": faltas,
                "fecha_inicio": reporte.fecha_inicio,
                "fecha_fin": reporte.fecha_fin
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar reporte: {str(e)}")

# ============================================================================
#                           PUNTO DE ENTRADA
# ============================================================================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

