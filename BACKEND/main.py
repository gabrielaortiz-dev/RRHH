from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from database import init_db, get_db
from models import (
    UsuarioCreate, UsuarioUpdate, UsuarioResponse, UsuarioLogin,
    DepartamentoCreate, DepartamentoUpdate,
    EmpleadoCreate, EmpleadoUpdate
)
import uvicorn
import sqlite3

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
    init_db()
    print("[OK] Base de datos inicializada")

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

