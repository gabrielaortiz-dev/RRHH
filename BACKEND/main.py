from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from database import init_db, get_db
from models import (
    UsuarioCreate, UsuarioUpdate, UsuarioResponse, UsuarioLogin,
    DepartamentoCreate, DepartamentoUpdate,
    EmpleadoCreate, EmpleadoUpdate,
    ContratoCreate, ContratoUpdate,
    AsistenciaCreate, AsistenciaUpdate, AsistenciaReporteRequest
)
import uvicorn
import sqlite3
from typing import Optional

# Crear la aplicación FastAPI
app = FastAPI(
    title="Sistema de RRHH - API",
    description="API REST para el sistema de Recursos Humanos",
    version="1.0.0"
)

# Configurar CORS para permitir peticiones desde Angular
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://localhost:4201"],  # URLs de Angular
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Evento de inicio: Inicializar la base de datos
@app.on_event("startup")
async def startup_event():
    """Inicializar la base de datos al iniciar la aplicación"""
    print("[INFO] Iniciando servidor...")
    db = init_db()
    print("[OK] Base de datos inicializada")
    
    # Verificar si hay usuarios activos, si no, crear usuarios de ejemplo
    usuarios_activos = db.fetch_all("SELECT id FROM usuarios WHERE activo = 1")
    if not usuarios_activos or len(usuarios_activos) == 0:
        print("[INFO] No hay usuarios activos en la base de datos. Creando usuarios de ejemplo...")
        try:
            usuarios_ejemplo = [
                ('Admin Sistema', 'admin@rrhh.com', 'admin123', 'administrador'),
                ('Juan Perez', 'juan.perez@rrhh.com', 'pass123', 'empleado'),
                ('Maria Garcia', 'maria.garcia@rrhh.com', 'pass123', 'supervisor'),
            ]
            
            for usuario in usuarios_ejemplo:
                nombre, email, password, rol = usuario
                # Verificar si el usuario ya existe
                existente = db.fetch_one("SELECT id FROM usuarios WHERE email = ?", (email,))
                if existente:
                    # Si existe pero está desactivado, reactivarlo
                    db.execute_query(
                        "UPDATE usuarios SET nombre = ?, password = ?, rol = ?, activo = 1 WHERE email = ?",
                        (nombre, password, rol, email)
                    )
                else:
                    # Crear nuevo usuario
                    db.execute_query(
                        "INSERT INTO usuarios (nombre, email, password, rol) VALUES (?, ?, ?, ?)",
                        usuario
                    )
            print("[OK] Usuarios de ejemplo creados/actualizados")
            print("[INFO] Credenciales de prueba:")
            print("       Email: admin@rrhh.com / Password: admin123")
        except Exception as e:
            print(f"[ADVERTENCIA] No se pudieron crear usuarios de ejemplo: {e}")
            import traceback
            traceback.print_exc()

# Evento de cierre: Cerrar conexión a la base de datos
@app.on_event("shutdown")
async def shutdown_event():
    """Cerrar la conexión a la base de datos al cerrar la aplicación"""
    db = get_db()
    db.disconnect()
    print("[INFO] Servidor detenido")

# Ruta principal
@app.get("/")
async def root():
    """Endpoint principal"""
    return {
        "mensaje": "Bienvenido a la API del Sistema de RRHH",
        "version": "1.0.0",
        "status": "activo"
    }

# Ruta de prueba de conexión a la base de datos
@app.get("/api/health")
async def health_check():
    """Verificar el estado de la API y la base de datos"""
    try:
        db = get_db()
        # Intentar hacer una consulta simple
        result = db.fetch_one("SELECT 1 as test")
        return {
            "status": "ok",
            "database": "conectada",
            "mensaje": "Sistema funcionando correctamente"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en la base de datos: {str(e)}")

# ============================================================================
#                           ENDPOINTS DE USUARIOS
# ============================================================================

@app.get("/api/usuarios", response_model=None, tags=["Usuarios"])
async def get_usuarios():
    """Obtener todos los usuarios activos (sin passwords)"""
    try:
        db = get_db()
        usuarios = db.fetch_all("""
            SELECT id, nombre, email, rol, fecha_creacion, activo 
            FROM usuarios 
            WHERE activo = 1
        """)
        return {
            "success": True,
            "data": usuarios,
            "count": len(usuarios)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener usuarios: {str(e)}")

@app.get("/api/usuarios/{usuario_id}", response_model=None, tags=["Usuarios"])
async def get_usuario(usuario_id: int):
    """Obtener un usuario específico por ID (sin password)"""
    try:
        db = get_db()
        usuario = db.fetch_one(
            "SELECT id, nombre, email, rol, fecha_creacion, activo FROM usuarios WHERE id = ? AND activo = 1",
            (usuario_id,)
        )
        if not usuario:
            raise HTTPException(
                status_code=404, 
                detail=f"Usuario con ID {usuario_id} no encontrado"
            )
        return {
            "success": True,
            "data": usuario
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener usuario: {str(e)}")

@app.post("/api/usuarios", status_code=status.HTTP_201_CREATED, tags=["Usuarios"])
async def create_usuario(usuario: UsuarioCreate):
    """Crear un nuevo usuario"""
    try:
        db = get_db()
        
        # Verificar si el email ya existe
        existing = db.fetch_one("SELECT id FROM usuarios WHERE email = ?", (usuario.email,))
        if existing:
            raise HTTPException(
                status_code=400, 
                detail=f"El email {usuario.email} ya está registrado"
            )
        
        # Insertar el nuevo usuario
        cursor = db.execute_query(
            """INSERT INTO usuarios (nombre, email, password, rol) 
               VALUES (?, ?, ?, ?)""",
            (usuario.nombre, usuario.email, usuario.password, usuario.rol)
        )
        
        # Obtener el usuario creado (sin password)
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
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"Error de integridad: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear usuario: {str(e)}")

@app.put("/api/usuarios/{usuario_id}", tags=["Usuarios"])
async def update_usuario(usuario_id: int, usuario: UsuarioUpdate):
    """Actualizar un usuario existente"""
    try:
        db = get_db()
        
        # Verificar si el usuario existe
        existing = db.fetch_one("SELECT id FROM usuarios WHERE id = ?", (usuario_id,))
        if not existing:
            raise HTTPException(
                status_code=404, 
                detail=f"Usuario con ID {usuario_id} no encontrado"
            )
        
        # Construir la consulta de actualización dinámica
        updates = []
        params = []
        
        if usuario.nombre is not None:
            updates.append("nombre = ?")
            params.append(usuario.nombre)
        if usuario.email is not None:
            # Verificar que el email no esté en uso por otro usuario
            email_check = db.fetch_one(
                "SELECT id FROM usuarios WHERE email = ? AND id != ?", 
                (usuario.email, usuario_id)
            )
            if email_check:
                raise HTTPException(
                    status_code=400, 
                    detail=f"El email {usuario.email} ya está en uso"
                )
            updates.append("email = ?")
            params.append(usuario.email)
        if usuario.password is not None:
            updates.append("password = ?")
            params.append(usuario.password)
        if usuario.rol is not None:
            updates.append("rol = ?")
            params.append(usuario.rol)
        if usuario.activo is not None:
            updates.append("activo = ?")
            params.append(1 if usuario.activo else 0)
        
        if not updates:
            raise HTTPException(
                status_code=400, 
                detail="No se proporcionaron datos para actualizar"
            )
        
        # Ejecutar la actualización
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

@app.delete("/api/usuarios/{usuario_id}", tags=["Usuarios"])
async def delete_usuario(usuario_id: int):
    """Eliminar (desactivar) un usuario"""
    try:
        db = get_db()
        
        # Verificar si el usuario existe
        usuario = db.fetch_one("SELECT id, nombre FROM usuarios WHERE id = ?", (usuario_id,))
        if not usuario:
            raise HTTPException(
                status_code=404, 
                detail=f"Usuario con ID {usuario_id} no encontrado"
            )
        
        # Desactivar el usuario en lugar de eliminarlo
        db.execute_query("UPDATE usuarios SET activo = 0 WHERE id = ?", (usuario_id,))
        
        return {
            "success": True,
            "message": f"Usuario '{usuario['nombre']}' desactivado exitosamente"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar usuario: {str(e)}")

@app.post("/api/usuarios/login", tags=["Usuarios"])
async def login_usuario(credentials: UsuarioLogin):
    """Autenticar un usuario (login)"""
    try:
        db = get_db()
        
        # Buscar usuario por email y password
        usuario = db.fetch_one(
            "SELECT id, nombre, email, rol, fecha_creacion, activo FROM usuarios WHERE email = ? AND password = ? AND activo = 1",
            (credentials.email, credentials.password)
        )
        
        if not usuario:
            raise HTTPException(
                status_code=401, 
                detail="Credenciales inválidas"
            )
        
        return {
            "success": True,
            "message": "Login exitoso",
            "data": usuario
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en login: {str(e)}")

# ============================================================================
#                           ENDPOINTS DE DEPARTAMENTOS
# ============================================================================

# Departamentos
@app.get("/api/departamentos", tags=["Departamentos"])
async def get_departamentos():
    """Obtener todos los departamentos activos"""
    try:
        db = get_db()
        departamentos = db.fetch_all("SELECT * FROM departamentos WHERE activo = 1")
        return {
            "success": True,
            "data": departamentos,
            "count": len(departamentos)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener departamentos: {str(e)}")

@app.post("/api/departamentos", status_code=status.HTTP_201_CREATED, tags=["Departamentos"])
async def create_departamento(departamento: DepartamentoCreate):
    """Crear un nuevo departamento"""
    try:
        db = get_db()
        
        # Verificar si el nombre ya existe
        existing = db.fetch_one("SELECT id FROM departamentos WHERE nombre = ?", (departamento.nombre,))
        if existing:
            raise HTTPException(
                status_code=400, 
                detail=f"El departamento '{departamento.nombre}' ya existe"
            )
        
        # Insertar el nuevo departamento
        cursor = db.execute_query(
            """INSERT INTO departamentos (nombre, descripcion) 
               VALUES (?, ?)""",
            (departamento.nombre, departamento.descripcion)
        )
        
        # Obtener el departamento creado
        nuevo_departamento = db.fetch_one(
            "SELECT * FROM departamentos WHERE id = ?",
            (cursor.lastrowid,)
        )
        
        return {
            "success": True,
            "message": "Departamento creado exitosamente",
            "data": nuevo_departamento
        }
    except HTTPException:
        raise
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"Error de integridad: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear departamento: {str(e)}")

@app.put("/api/departamentos/{departamento_id}", tags=["Departamentos"])
async def update_departamento(departamento_id: int, departamento: DepartamentoUpdate):
    """Actualizar un departamento existente"""
    try:
        db = get_db()
        
        # Verificar si el departamento existe
        existing = db.fetch_one("SELECT id FROM departamentos WHERE id = ?", (departamento_id,))
        if not existing:
            raise HTTPException(
                status_code=404, 
                detail=f"Departamento con ID {departamento_id} no encontrado"
            )
        
        # Construir la consulta de actualización dinámica
        updates = []
        params = []
        
        if departamento.nombre is not None:
            # Verificar que el nombre no esté en uso por otro departamento
            nombre_check = db.fetch_one(
                "SELECT id FROM departamentos WHERE nombre = ? AND id != ?", 
                (departamento.nombre, departamento_id)
            )
            if nombre_check:
                raise HTTPException(
                    status_code=400, 
                    detail=f"El nombre '{departamento.nombre}' ya está en uso"
                )
            updates.append("nombre = ?")
            params.append(departamento.nombre)
        if departamento.descripcion is not None:
            updates.append("descripcion = ?")
            params.append(departamento.descripcion)
        if departamento.activo is not None:
            updates.append("activo = ?")
            params.append(1 if departamento.activo else 0)
        
        if not updates:
            raise HTTPException(
                status_code=400, 
                detail="No se proporcionaron datos para actualizar"
            )
        
        # Ejecutar la actualización
        params.append(departamento_id)
        query = f"UPDATE departamentos SET {', '.join(updates)} WHERE id = ?"
        db.execute_query(query, tuple(params))
        
        # Obtener el departamento actualizado
        departamento_actualizado = db.fetch_one(
            "SELECT * FROM departamentos WHERE id = ?",
            (departamento_id,)
        )
        
        return {
            "success": True,
            "message": "Departamento actualizado exitosamente",
            "data": departamento_actualizado
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar departamento: {str(e)}")

@app.delete("/api/departamentos/{departamento_id}", tags=["Departamentos"])
async def delete_departamento(departamento_id: int):
    """Eliminar (desactivar) un departamento"""
    try:
        db = get_db()
        
        # Verificar si el departamento existe
        departamento = db.fetch_one("SELECT id, nombre FROM departamentos WHERE id = ?", (departamento_id,))
        if not departamento:
            raise HTTPException(
                status_code=404, 
                detail=f"Departamento con ID {departamento_id} no encontrado"
            )
        
        # Desactivar el departamento en lugar de eliminarlo
        db.execute_query("UPDATE departamentos SET activo = 0 WHERE id = ?", (departamento_id,))
        
        return {
            "success": True,
            "message": f"Departamento '{departamento['nombre']}' desactivado exitosamente"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar departamento: {str(e)}")

# ============================================================================
#                           ENDPOINTS DE EMPLEADOS
# ============================================================================

@app.get("/api/empleados", tags=["Empleados"])
async def get_empleados():
    """Obtener todos los empleados activos"""
    try:
        db = get_db()
        empleados = db.fetch_all("""
            SELECT e.*, d.nombre as departamento_nombre 
            FROM empleados e 
            LEFT JOIN departamentos d ON e.departamento_id = d.id 
            WHERE e.activo = 1
        """)
        return {
            "success": True,
            "data": empleados,
            "count": len(empleados)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener empleados: {str(e)}")

@app.get("/api/empleados/{empleado_id}", tags=["Empleados"])
async def get_empleado(empleado_id: int):
    """Obtener un empleado específico por ID"""
    try:
        db = get_db()
        empleado = db.fetch_one("""
            SELECT e.*, d.nombre as departamento_nombre 
            FROM empleados e 
            LEFT JOIN departamentos d ON e.departamento_id = d.id 
            WHERE e.id = ? AND e.activo = 1
        """, (empleado_id,))
        if not empleado:
            raise HTTPException(
                status_code=404, 
                detail=f"Empleado con ID {empleado_id} no encontrado"
            )
        return {
            "success": True,
            "data": empleado
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener empleado: {str(e)}")

@app.post("/api/empleados", status_code=status.HTTP_201_CREATED, tags=["Empleados"])
async def create_empleado(empleado: EmpleadoCreate):
    """Crear un nuevo empleado"""
    try:
        db = get_db()
        
        # Verificar si el email ya existe
        existing = db.fetch_one("SELECT id FROM empleados WHERE email = ?", (empleado.email,))
        if existing:
            raise HTTPException(
                status_code=400, 
                detail=f"El email {empleado.email} ya está registrado"
            )
        
        # Verificar que el departamento existe
        departamento = db.fetch_one("SELECT id FROM departamentos WHERE id = ? AND activo = 1", (empleado.departamento_id,))
        if not departamento:
            raise HTTPException(
                status_code=400, 
                detail=f"El departamento con ID {empleado.departamento_id} no existe o está inactivo"
            )
        
        # Insertar el nuevo empleado
        cursor = db.execute_query(
            """INSERT INTO empleados (nombre, apellido, email, telefono, departamento_id, puesto, fecha_ingreso, salario) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (empleado.nombre, empleado.apellido, empleado.email, empleado.telefono, 
             empleado.departamento_id, empleado.puesto, empleado.fecha_ingreso, empleado.salario)
        )
        
        # Obtener el empleado creado
        nuevo_empleado = db.fetch_one("""
            SELECT e.*, d.nombre as departamento_nombre 
            FROM empleados e 
            LEFT JOIN departamentos d ON e.departamento_id = d.id 
            WHERE e.id = ?
        """, (cursor.lastrowid,))
        
        return {
            "success": True,
            "message": "Empleado creado exitosamente",
            "data": nuevo_empleado
        }
    except HTTPException:
        raise
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"Error de integridad: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear empleado: {str(e)}")

@app.put("/api/empleados/{empleado_id}", tags=["Empleados"])
async def update_empleado(empleado_id: int, empleado: EmpleadoUpdate):
    """Actualizar un empleado existente"""
    try:
        db = get_db()
        
        # Verificar si el empleado existe
        existing = db.fetch_one("SELECT id FROM empleados WHERE id = ?", (empleado_id,))
        if not existing:
            raise HTTPException(
                status_code=404, 
                detail=f"Empleado con ID {empleado_id} no encontrado"
            )
        
        # Construir la consulta de actualización dinámica
        updates = []
        params = []
        
        if empleado.nombre is not None:
            updates.append("nombre = ?")
            params.append(empleado.nombre)
        if empleado.apellido is not None:
            updates.append("apellido = ?")
            params.append(empleado.apellido)
        if empleado.email is not None:
            # Verificar que el email no esté en uso por otro empleado
            email_check = db.fetch_one(
                "SELECT id FROM empleados WHERE email = ? AND id != ?", 
                (empleado.email, empleado_id)
            )
            if email_check:
                raise HTTPException(
                    status_code=400, 
                    detail=f"El email {empleado.email} ya está en uso"
                )
            updates.append("email = ?")
            params.append(empleado.email)
        if empleado.telefono is not None:
            updates.append("telefono = ?")
            params.append(empleado.telefono)
        if empleado.departamento_id is not None:
            # Verificar que el departamento existe
            departamento = db.fetch_one("SELECT id FROM departamentos WHERE id = ? AND activo = 1", (empleado.departamento_id,))
            if not departamento:
                raise HTTPException(
                    status_code=400, 
                    detail=f"El departamento con ID {empleado.departamento_id} no existe o está inactivo"
                )
            updates.append("departamento_id = ?")
            params.append(empleado.departamento_id)
        if empleado.puesto is not None:
            updates.append("puesto = ?")
            params.append(empleado.puesto)
        if empleado.fecha_ingreso is not None:
            updates.append("fecha_ingreso = ?")
            params.append(empleado.fecha_ingreso)
        if empleado.salario is not None:
            updates.append("salario = ?")
            params.append(empleado.salario)
        if empleado.activo is not None:
            updates.append("activo = ?")
            params.append(1 if empleado.activo else 0)
        
        if not updates:
            raise HTTPException(
                status_code=400, 
                detail="No se proporcionaron datos para actualizar"
            )
        
        # Ejecutar la actualización
        params.append(empleado_id)
        query = f"UPDATE empleados SET {', '.join(updates)} WHERE id = ?"
        db.execute_query(query, tuple(params))
        
        # Obtener el empleado actualizado
        empleado_actualizado = db.fetch_one("""
            SELECT e.*, d.nombre as departamento_nombre 
            FROM empleados e 
            LEFT JOIN departamentos d ON e.departamento_id = d.id 
            WHERE e.id = ?
        """, (empleado_id,))
        
        return {
            "success": True,
            "message": "Empleado actualizado exitosamente",
            "data": empleado_actualizado
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar empleado: {str(e)}")

@app.delete("/api/empleados/{empleado_id}", tags=["Empleados"])
async def delete_empleado(empleado_id: int):
    """Eliminar (desactivar) un empleado"""
    try:
        db = get_db()
        
        # Verificar si el empleado existe
        empleado = db.fetch_one("SELECT id, nombre, apellido FROM empleados WHERE id = ?", (empleado_id,))
        if not empleado:
            raise HTTPException(
                status_code=404, 
                detail=f"Empleado con ID {empleado_id} no encontrado"
            )
        
        # Desactivar el empleado en lugar de eliminarlo
        db.execute_query("UPDATE empleados SET activo = 0 WHERE id = ?", (empleado_id,))
        
        return {
            "success": True,
            "message": f"Empleado '{empleado['nombre']} {empleado['apellido']}' desactivado exitosamente"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar empleado: {str(e)}")

# ============================================================================
#                           ENDPOINTS DE NOTIFICACIONES
# ============================================================================

@app.get("/api/notificaciones/{usuario_id}", tags=["Notificaciones"])
async def get_notificaciones(usuario_id: int):
    """Obtener notificaciones de un usuario"""
    try:
        db = get_db()
        notificaciones = db.fetch_all(
            "SELECT * FROM notificaciones WHERE usuario_id = ? ORDER BY fecha_creacion DESC",
            (usuario_id,)
        )
        return {
            "success": True,
            "data": notificaciones,
            "count": len(notificaciones)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener notificaciones: {str(e)}")

# ============================================================================
#                           ENDPOINTS DE CONTRATOS
# ============================================================================

@app.get("/api/contratos", tags=["Contratos"])
async def get_contratos(id_empleado: Optional[int] = None):
    """Obtener todos los contratos o los contratos de un empleado específico"""
    try:
        db = get_db()
        if id_empleado:
            # Obtener contratos de un empleado específico con información del empleado
            contratos = db.fetch_all(
                """SELECT c.*, e.nombre || ' ' || e.apellido as nombre_empleado 
                   FROM Contratos c
                   LEFT JOIN Empleados e ON c.id_empleado = e.id_empleado
                   WHERE c.id_empleado = ?
                   ORDER BY c.fecha_inicio DESC""",
                (id_empleado,)
            )
        else:
            # Obtener todos los contratos con información del empleado
            contratos = db.fetch_all(
                """SELECT c.*, e.nombre || ' ' || e.apellido as nombre_empleado 
                   FROM Contratos c
                   LEFT JOIN Empleados e ON c.id_empleado = e.id_empleado
                   ORDER BY c.fecha_inicio DESC"""
            )
        
        return {
            "success": True,
            "data": contratos,
            "count": len(contratos)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener contratos: {str(e)}")

@app.get("/api/contratos/{contrato_id}", tags=["Contratos"])
async def get_contrato(contrato_id: int):
    """Obtener un contrato específico por ID"""
    try:
        db = get_db()
        contrato = db.fetch_one(
            """SELECT c.*, e.nombre || ' ' || e.apellido as nombre_empleado 
               FROM Contratos c
               LEFT JOIN Empleados e ON c.id_empleado = e.id_empleado
               WHERE c.id_contrato = ?""",
            (contrato_id,)
        )
        if not contrato:
            raise HTTPException(
                status_code=404,
                detail=f"Contrato con ID {contrato_id} no encontrado"
            )
        return {
            "success": True,
            "data": contrato
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener contrato: {str(e)}")

@app.post("/api/contratos", status_code=status.HTTP_201_CREATED, tags=["Contratos"])
async def create_contrato(contrato: ContratoCreate):
    """Crear un nuevo contrato"""
    try:
        db = get_db()
        
        # Verificar que el empleado existe
        empleado = db.fetch_one(
            "SELECT id_empleado FROM Empleados WHERE id_empleado = ?",
            (contrato.id_empleado,)
        )
        if not empleado:
            raise HTTPException(
                status_code=404,
                detail=f"Empleado con ID {contrato.id_empleado} no encontrado"
            )
        
        # Insertar el nuevo contrato
        cursor = db.execute_query(
            """INSERT INTO Contratos (id_empleado, tipo_contrato, fecha_inicio, fecha_fin, salario, condiciones)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (contrato.id_empleado, contrato.tipo_contrato, contrato.fecha_inicio, 
             contrato.fecha_fin, contrato.salario, contrato.condiciones)
        )
        
        # Obtener el contrato creado
        nuevo_contrato = db.fetch_one(
            """SELECT c.*, e.nombre || ' ' || e.apellido as nombre_empleado 
               FROM Contratos c
               LEFT JOIN Empleados e ON c.id_empleado = e.id_empleado
               WHERE c.id_contrato = ?""",
            (cursor.lastrowid,)
        )
        
        return {
            "success": True,
            "message": "Contrato creado exitosamente",
            "data": nuevo_contrato
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear contrato: {str(e)}")

@app.put("/api/contratos/{contrato_id}", tags=["Contratos"])
async def update_contrato(contrato_id: int, contrato: ContratoUpdate):
    """Actualizar un contrato existente"""
    try:
        db = get_db()
        
        # Verificar si el contrato existe
        existing = db.fetch_one("SELECT id_contrato FROM Contratos WHERE id_contrato = ?", (contrato_id,))
        if not existing:
            raise HTTPException(
                status_code=404,
                detail=f"Contrato con ID {contrato_id} no encontrado"
            )
        
        # Construir la consulta de actualización dinámica
        updates = []
        params = []
        
        if contrato.tipo_contrato is not None:
            updates.append("tipo_contrato = ?")
            params.append(contrato.tipo_contrato)
        if contrato.fecha_inicio is not None:
            updates.append("fecha_inicio = ?")
            params.append(contrato.fecha_inicio)
        if contrato.fecha_fin is not None:
            updates.append("fecha_fin = ?")
            params.append(contrato.fecha_fin)
        if contrato.salario is not None:
            updates.append("salario = ?")
            params.append(contrato.salario)
        if contrato.condiciones is not None:
            updates.append("condiciones = ?")
            params.append(contrato.condiciones)
        
        if not updates:
            raise HTTPException(status_code=400, detail="No se proporcionaron campos para actualizar")
        
        params.append(contrato_id)
        query = f"UPDATE Contratos SET {', '.join(updates)} WHERE id_contrato = ?"
        db.execute_query(query, tuple(params))
        
        # Obtener el contrato actualizado
        contrato_actualizado = db.fetch_one(
            """SELECT c.*, e.nombre || ' ' || e.apellido as nombre_empleado 
               FROM Contratos c
               LEFT JOIN Empleados e ON c.id_empleado = e.id_empleado
               WHERE c.id_contrato = ?""",
            (contrato_id,)
        )
        
        return {
            "success": True,
            "message": "Contrato actualizado exitosamente",
            "data": contrato_actualizado
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar contrato: {str(e)}")

@app.delete("/api/contratos/{contrato_id}", tags=["Contratos"])
async def delete_contrato(contrato_id: int):
    """Eliminar un contrato"""
    try:
        db = get_db()
        
        # Verificar si el contrato existe
        contrato = db.fetch_one("SELECT id_contrato FROM Contratos WHERE id_contrato = ?", (contrato_id,))
        if not contrato:
            raise HTTPException(
                status_code=404,
                detail=f"Contrato con ID {contrato_id} no encontrado"
            )
        
        # Eliminar el contrato
        db.execute_query("DELETE FROM Contratos WHERE id_contrato = ?", (contrato_id,))
        
        return {
            "success": True,
            "message": f"Contrato con ID {contrato_id} eliminado exitosamente"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar contrato: {str(e)}")

@app.get("/api/contratos/alertas/vencimiento", tags=["Contratos"])
async def get_alertas_vencimiento(dias: int = 30):
    """Obtener contratos que están próximos a vencer en los próximos N días"""
    try:
        db = get_db()
        from datetime import datetime, timedelta
        
        fecha_limite = (datetime.now() + timedelta(days=dias)).strftime("%Y-%m-%d")
        fecha_hoy = datetime.now().strftime("%Y-%m-%d")
        
        contratos = db.fetch_all(
            """SELECT c.*, e.nombre || ' ' || e.apellido as nombre_empleado,
                      CASE 
                          WHEN c.fecha_fin < ? THEN 'vencido'
                          WHEN c.fecha_fin <= ? THEN 'por_vencer'
                          ELSE 'vigente'
                      END as estado_vencimiento,
                      julianday(c.fecha_fin) - julianday('now') as dias_restantes
               FROM Contratos c
               LEFT JOIN Empleados e ON c.id_empleado = e.id_empleado
               WHERE c.fecha_fin IS NOT NULL
                 AND c.fecha_fin <= ?
               ORDER BY c.fecha_fin ASC""",
            (fecha_hoy, fecha_limite, fecha_limite)
        )
        
        return {
            "success": True,
            "data": contratos,
            "count": len(contratos),
            "dias_consulta": dias
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener alertas de vencimiento: {str(e)}")

# ============================================================================
#                           ENDPOINTS DE ASISTENCIAS
# ============================================================================

@app.get("/api/asistencias", tags=["Asistencias"])
async def get_asistencias(id_empleado: Optional[int] = None, fecha_inicio: Optional[str] = None, fecha_fin: Optional[str] = None):
    """Obtener asistencias. Puede filtrar por empleado y rango de fechas"""
    try:
        db = get_db()
        
        query = """SELECT a.*, e.nombre || ' ' || e.apellido as nombre_empleado 
                   FROM Asistencias a
                   LEFT JOIN Empleados e ON a.id_empleado = e.id_empleado
                   WHERE 1=1"""
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
        
        asistencias = db.fetch_all(query, tuple(params) if params else ())
        
        return {
            "success": True,
            "data": asistencias,
            "count": len(asistencias)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener asistencias: {str(e)}")

@app.get("/api/asistencias/{asistencia_id}", tags=["Asistencias"])
async def get_asistencia(asistencia_id: int):
    """Obtener una asistencia específica por ID"""
    try:
        db = get_db()
        asistencia = db.fetch_one(
            """SELECT a.*, e.nombre || ' ' || e.apellido as nombre_empleado 
               FROM Asistencias a
               LEFT JOIN Empleados e ON a.id_empleado = e.id_empleado
               WHERE a.id_asistencia = ?""",
            (asistencia_id,)
        )
        if not asistencia:
            raise HTTPException(
                status_code=404,
                detail=f"Asistencia con ID {asistencia_id} no encontrada"
            )
        return {
            "success": True,
            "data": asistencia
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener asistencia: {str(e)}")

@app.post("/api/asistencias", status_code=status.HTTP_201_CREATED, tags=["Asistencias"])
async def create_asistencia(asistencia: AsistenciaCreate):
    """Registrar una nueva asistencia (manual o por reloj biométrico)"""
    try:
        db = get_db()
        
        # Verificar que el empleado existe
        empleado = db.fetch_one(
            "SELECT id_empleado FROM Empleados WHERE id_empleado = ?",
            (asistencia.id_empleado,)
        )
        if not empleado:
            raise HTTPException(
                status_code=404,
                detail=f"Empleado con ID {asistencia.id_empleado} no encontrado"
            )
        
        # Insertar la nueva asistencia
        cursor = db.execute_query(
            """INSERT INTO Asistencias (id_empleado, fecha, hora_entrada, hora_salida, observaciones)
               VALUES (?, ?, ?, ?, ?)""",
            (asistencia.id_empleado, asistencia.fecha, asistencia.hora_entrada, 
             asistencia.hora_salida, asistencia.observaciones)
        )
        
        # Obtener la asistencia creada
        nueva_asistencia = db.fetch_one(
            """SELECT a.*, e.nombre || ' ' || e.apellido as nombre_empleado 
               FROM Asistencias a
               LEFT JOIN Empleados e ON a.id_empleado = e.id_empleado
               WHERE a.id_asistencia = ?""",
            (cursor.lastrowid,)
        )
        
        return {
            "success": True,
            "message": f"Asistencia registrada exitosamente ({asistencia.metodo_registro})",
            "data": nueva_asistencia
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al registrar asistencia: {str(e)}")

@app.put("/api/asistencias/{asistencia_id}", tags=["Asistencias"])
async def update_asistencia(asistencia_id: int, asistencia: AsistenciaUpdate):
    """Actualizar una asistencia existente (para justificaciones y observaciones)"""
    try:
        db = get_db()
        
        # Verificar si la asistencia existe
        existing = db.fetch_one("SELECT id_asistencia FROM Asistencias WHERE id_asistencia = ?", (asistencia_id,))
        if not existing:
            raise HTTPException(
                status_code=404,
                detail=f"Asistencia con ID {asistencia_id} no encontrada"
            )
        
        # Construir la consulta de actualización dinámica
        updates = []
        params = []
        
        if asistencia.hora_entrada is not None:
            updates.append("hora_entrada = ?")
            params.append(asistencia.hora_entrada)
        if asistencia.hora_salida is not None:
            updates.append("hora_salida = ?")
            params.append(asistencia.hora_salida)
        if asistencia.observaciones is not None:
            updates.append("observaciones = ?")
            params.append(asistencia.observaciones)
        
        if not updates:
            raise HTTPException(status_code=400, detail="No se proporcionaron campos para actualizar")
        
        params.append(asistencia_id)
        query = f"UPDATE Asistencias SET {', '.join(updates)} WHERE id_asistencia = ?"
        db.execute_query(query, tuple(params))
        
        # Obtener la asistencia actualizada
        asistencia_actualizada = db.fetch_one(
            """SELECT a.*, e.nombre || ' ' || e.apellido as nombre_empleado 
               FROM Asistencias a
               LEFT JOIN Empleados e ON a.id_empleado = e.id_empleado
               WHERE a.id_asistencia = ?""",
            (asistencia_id,)
        )
        
        return {
            "success": True,
            "message": "Asistencia actualizada exitosamente",
            "data": asistencia_actualizada
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar asistencia: {str(e)}")

@app.delete("/api/asistencias/{asistencia_id}", tags=["Asistencias"])
async def delete_asistencia(asistencia_id: int):
    """Eliminar una asistencia"""
    try:
        db = get_db()
        
        # Verificar si la asistencia existe
        asistencia = db.fetch_one("SELECT id_asistencia FROM Asistencias WHERE id_asistencia = ?", (asistencia_id,))
        if not asistencia:
            raise HTTPException(
                status_code=404,
                detail=f"Asistencia con ID {asistencia_id} no encontrada"
            )
        
        # Eliminar la asistencia
        db.execute_query("DELETE FROM Asistencias WHERE id_asistencia = ?", (asistencia_id,))
        
        return {
            "success": True,
            "message": f"Asistencia con ID {asistencia_id} eliminada exitosamente"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar asistencia: {str(e)}")

@app.post("/api/asistencias/reporte", tags=["Asistencias"])
async def generar_reporte_asistencias(reporte: AsistenciaReporteRequest):
    """Generar reporte de asistencias por rango de fechas"""
    try:
        db = get_db()
        
        query = """SELECT a.*, e.nombre || ' ' || e.apellido as nombre_empleado,
                          e.correo as email_empleado,
                          CASE 
                              WHEN a.hora_entrada IS NULL THEN 'Falta'
                              WHEN a.hora_salida IS NULL THEN 'Incompleta'
                              ELSE 'Completa'
                          END as estado_asistencia
                   FROM Asistencias a
                   LEFT JOIN Empleados e ON a.id_empleado = e.id_empleado
                   WHERE a.fecha >= ? AND a.fecha <= ?"""
        params = [reporte.fecha_inicio, reporte.fecha_fin]
        
        if reporte.id_empleado:
            query += " AND a.id_empleado = ?"
            params.append(reporte.id_empleado)
        
        query += " ORDER BY a.fecha DESC, e.nombre, e.apellido"
        
        asistencias = db.fetch_all(query, tuple(params))
        
        # Calcular estadísticas
        total_registros = len(asistencias)
        completas = len([a for a in asistencias if a.get('hora_entrada') and a.get('hora_salida')])
        incompletas = len([a for a in asistencias if a.get('hora_entrada') and not a.get('hora_salida')])
        faltas = len([a for a in asistencias if not a.get('hora_entrada')])
        
        return {
            "success": True,
            "data": asistencias,
            "estadisticas": {
                "total_registros": total_registros,
                "completas": completas,
                "incompletas": incompletas,
                "faltas": faltas,
                "fecha_inicio": reporte.fecha_inicio,
                "fecha_fin": reporte.fecha_fin
            },
            "count": total_registros
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar reporte: {str(e)}")

if __name__ == "__main__":
    # Ejecutar el servidor
    print("=" * 50)
    print("Iniciando servidor FastAPI con SQLite")
    print("=" * 50)
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload en desarrollo
        log_level="info"
    )

