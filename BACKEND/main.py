from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from database import init_db, get_db
from models import (
    UsuarioCreate, UsuarioUpdate, UsuarioResponse, UsuarioLogin,
    DepartamentoCreate, DepartamentoUpdate,
    EmpleadoCreate, EmpleadoUpdate,
    ContratoCreate, ContratoUpdate,
    AsistenciaCreate, AsistenciaUpdate, AsistenciaReporteRequest,
    NominaCreate, NominaUpdate, BonificacionItem, DeduccionItem,
    ConfigImpuestoCreate, ConfigDeduccionCreate, ConfigBeneficioCreate,
    VacacionPermisoCreate, VacacionPermisoUpdate, VacacionPermisoAprobacion,
    DocumentoCreate, DocumentoUpdate, DocumentoPermisoCreate
)
from fastapi import UploadFile, File
import os
import shutil
from datetime import datetime
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
async def login_usuario(credentials: UsuarioLogin, request: Request):
    """Autenticar un usuario (login) con control de intentos fallidos"""
    try:
        db = get_db()
        
        # Verificar intentos fallidos recientes (últimos 15 minutos)
        intentos_recientes = db.fetch_all(
            """SELECT COUNT(*) as total FROM Login_Intentos 
               WHERE email = ? AND exitoso = 0 
               AND fecha_intento >= datetime('now', '-15 minutes')""",
            (credentials.email,)
        )
        
        if intentos_recientes and intentos_recientes[0]['total'] >= 5:
            raise HTTPException(
                status_code=429,
                detail="Demasiados intentos fallidos. Cuenta bloqueada temporalmente por 15 minutos."
            )
        
        # Buscar usuario
        usuario = db.fetch_one(
            "SELECT id, nombre, email, rol, fecha_creacion, activo, password FROM usuarios WHERE email = ? AND activo = 1",
            (credentials.email,)
        )
        
        if not usuario or usuario['password'] != credentials.password:
            # Registrar intento fallido
            client_host = request.client.host if request.client else None
            db.execute_query(
                """INSERT INTO Login_Intentos (email, exitoso, ip_address)
                   VALUES (?, 0, ?)""",
                (credentials.email, client_host)
            )
            raise HTTPException(status_code=401, detail="Credenciales inválidas")
        
        # Registrar intento exitoso
        client_host = request.client.host if request.client else None
        db.execute_query(
            """INSERT INTO Login_Intentos (email, exitoso, ip_address)
               VALUES (?, 1, ?)""",
            (credentials.email, client_host)
        )
        
        # Registrar en auditoría
        db.execute_query(
            """INSERT INTO Usuarios_Auditoria (usuario_id, accion, modulo, detalles, ip_address)
               VALUES (?, ?, ?, ?, ?)""",
            (usuario['id'], "LOGIN", "Sistema", "Inicio de sesión exitoso", client_host)
        )
        
        # Retornar sin password
        usuario_response = {k: v for k, v in usuario.items() if k != 'password'}
        
        return {
            "success": True,
            "message": "Login exitoso",
            "data": usuario_response
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

# ============================================================================
#                           ENDPOINTS DE NÓMINA
# ============================================================================

@app.get("/api/nomina", tags=["Nómina"])
async def get_nomina(id_empleado: Optional[int] = None, mes: Optional[int] = None, anio: Optional[int] = None):
    """Obtener registros de nómina con filtros opcionales"""
    try:
        db = get_db()
        query = """SELECT n.*, e.nombre || ' ' || e.apellido as nombre_empleado 
                   FROM Nomina n
                   LEFT JOIN Empleados e ON n.id_empleado = e.id_empleado
                   WHERE 1=1"""
        params = []
        
        if id_empleado:
            query += " AND n.id_empleado = ?"
            params.append(id_empleado)
        if mes:
            query += " AND n.mes = ?"
            params.append(mes)
        if anio:
            query += " AND n.anio = ?"
            params.append(anio)
        
        query += " ORDER BY n.anio DESC, n.mes DESC, e.nombre"
        
        nomina = db.fetch_all(query, tuple(params) if params else ())
        
        # Obtener detalles de bonificaciones y deducciones
        for registro in nomina:
            registro['bonificaciones_detalle'] = db.fetch_all(
                "SELECT * FROM Nomina_Bonificaciones WHERE id_nomina = ?",
                (registro['id_nomina'],)
            )
            registro['deducciones_detalle'] = db.fetch_all(
                "SELECT * FROM Nomina_Deducciones WHERE id_nomina = ?",
                (registro['id_nomina'],)
            )
        
        return {
            "success": True,
            "data": nomina,
            "count": len(nomina)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener nómina: {str(e)}")

@app.get("/api/nomina/{nomina_id}", tags=["Nómina"])
async def get_nomina_by_id(nomina_id: int):
    """Obtener un registro de nómina específico"""
    try:
        db = get_db()
        nomina = db.fetch_one(
            """SELECT n.*, e.nombre || ' ' || e.apellido as nombre_empleado 
               FROM Nomina n
               LEFT JOIN Empleados e ON n.id_empleado = e.id_empleado
               WHERE n.id_nomina = ?""",
            (nomina_id,)
        )
        if not nomina:
            raise HTTPException(status_code=404, detail=f"Nómina con ID {nomina_id} no encontrada")
        
        nomina['bonificaciones_detalle'] = db.fetch_all(
            "SELECT * FROM Nomina_Bonificaciones WHERE id_nomina = ?",
            (nomina_id,)
        )
        nomina['deducciones_detalle'] = db.fetch_all(
            "SELECT * FROM Nomina_Deducciones WHERE id_nomina = ?",
            (nomina_id,)
        )
        
        return {"success": True, "data": nomina}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener nómina: {str(e)}")

@app.post("/api/nomina", status_code=status.HTTP_201_CREATED, tags=["Nómina"])
async def create_nomina(nomina: NominaCreate, usuario_id: Optional[int] = None):
    """Crear un nuevo registro de nómina con cálculos automáticos"""
    try:
        db = get_db()
        
        # Verificar que el empleado existe
        empleado = db.fetch_one("SELECT id_empleado FROM Empleados WHERE id_empleado = ?", (nomina.id_empleado,))
        if not empleado:
            raise HTTPException(status_code=404, detail=f"Empleado con ID {nomina.id_empleado} no encontrado")
        
        # Verificar que no existe nómina para ese período
        existente = db.fetch_one(
            "SELECT id_nomina FROM Nomina WHERE id_empleado = ? AND mes = ? AND anio = ?",
            (nomina.id_empleado, nomina.mes, nomina.anio)
        )
        if existente:
            raise HTTPException(
                status_code=400,
                detail=f"Ya existe nómina para el empleado en {nomina.mes}/{nomina.anio}"
            )
        
        # Calcular totales
        total_bonificaciones = sum(b.monto for b in nomina.bonificaciones) if nomina.bonificaciones else 0
        total_deducciones = sum(d.monto for d in nomina.deducciones) if nomina.deducciones else 0
        salario_neto = nomina.salario_base + total_bonificaciones - total_deducciones
        
        # Validar que el salario neto no sea negativo
        if salario_neto < 0:
            raise HTTPException(
                status_code=400,
                detail="El salario neto no puede ser negativo. Verifique las deducciones."
            )
        
        periodo = f"{nomina.anio}-{nomina.mes:02d}"
        
        # Insertar nómina
        cursor = db.execute_query(
            """INSERT INTO Nomina (id_empleado, mes, anio, periodo, salario_base, 
                                   total_bonificaciones, total_deducciones, salario_neto, 
                                   fecha_pago, creado_por, observaciones)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (nomina.id_empleado, nomina.mes, nomina.anio, periodo, nomina.salario_base,
             total_bonificaciones, total_deducciones, salario_neto, nomina.fecha_pago,
             usuario_id, nomina.observaciones)
        )
        
        nomina_id = cursor.lastrowid
        
        # Insertar bonificaciones
        if nomina.bonificaciones:
            for bonif in nomina.bonificaciones:
                db.execute_query(
                    """INSERT INTO Nomina_Bonificaciones (id_nomina, concepto, tipo, monto, descripcion)
                       VALUES (?, ?, ?, ?, ?)""",
                    (nomina_id, bonif.concepto, bonif.tipo, bonif.monto, bonif.descripcion)
                )
        
        # Insertar deducciones
        if nomina.deducciones:
            for deduc in nomina.deducciones:
                db.execute_query(
                    """INSERT INTO Nomina_Deducciones (id_nomina, concepto, tipo, monto, descripcion)
                       VALUES (?, ?, ?, ?, ?)""",
                    (nomina_id, deduc.concepto, deduc.tipo, deduc.monto, deduc.descripcion)
                )
        
        # Registrar en auditoría
        db.execute_query(
            """INSERT INTO Nomina_Auditoria (id_nomina, accion, usuario_id, campo_modificado, valor_nuevo)
               VALUES (?, ?, ?, ?, ?)""",
            (nomina_id, "CREAR", usuario_id, "Registro completo", f"Nómina creada para período {periodo}")
        )
        
        # Obtener nómina creada
        nueva_nomina = db.fetch_one(
            """SELECT n.*, e.nombre || ' ' || e.apellido as nombre_empleado 
               FROM Nomina n
               LEFT JOIN Empleados e ON n.id_empleado = e.id_empleado
               WHERE n.id_nomina = ?""",
            (nomina_id,)
        )
        nueva_nomina['bonificaciones_detalle'] = db.fetch_all(
            "SELECT * FROM Nomina_Bonificaciones WHERE id_nomina = ?", (nomina_id,)
        )
        nueva_nomina['deducciones_detalle'] = db.fetch_all(
            "SELECT * FROM Nomina_Deducciones WHERE id_nomina = ?", (nomina_id,)
        )
        
        return {
            "success": True,
            "message": "Nómina creada exitosamente",
            "data": nueva_nomina
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear nómina: {str(e)}")

@app.put("/api/nomina/{nomina_id}", tags=["Nómina"])
async def update_nomina(nomina_id: int, nomina: NominaUpdate, usuario_id: Optional[int] = None):
    """Actualizar un registro de nómina existente con trazabilidad"""
    try:
        db = get_db()
        
        # Verificar que existe
        existente = db.fetch_one("SELECT * FROM Nomina WHERE id_nomina = ?", (nomina_id,))
        if not existente:
            raise HTTPException(status_code=404, detail=f"Nómina con ID {nomina_id} no encontrada")
        
        # Obtener valores anteriores para auditoría
        valores_anteriores = {
            'salario_base': existente.get('salario_base'),
            'total_bonificaciones': existente.get('total_bonificaciones'),
            'total_deducciones': existente.get('total_deducciones'),
            'salario_neto': existente.get('salario_neto'),
            'estado': existente.get('estado')
        }
        
        # Construir actualización
        updates = []
        params = []
        
        if nomina.salario_base is not None:
            updates.append("salario_base = ?")
            params.append(nomina.salario_base)
            # Registrar en auditoría
            db.execute_query(
                """INSERT INTO Nomina_Auditoria (id_nomina, accion, usuario_id, campo_modificado, valor_anterior, valor_nuevo)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (nomina_id, "MODIFICAR", usuario_id, "salario_base", 
                 str(valores_anteriores['salario_base']), str(nomina.salario_base))
            )
        
        # Recalcular si hay cambios en bonificaciones o deducciones
        if nomina.bonificaciones is not None or nomina.deducciones is not None:
            # Eliminar bonificaciones y deducciones existentes
            if nomina.bonificaciones is not None:
                db.execute_query("DELETE FROM Nomina_Bonificaciones WHERE id_nomina = ?", (nomina_id,))
                total_bonificaciones = sum(b.monto for b in nomina.bonificaciones)
                # Insertar nuevas
                for bonif in nomina.bonificaciones:
                    db.execute_query(
                        """INSERT INTO Nomina_Bonificaciones (id_nomina, concepto, tipo, monto, descripcion)
                           VALUES (?, ?, ?, ?, ?)""",
                        (nomina_id, bonif.concepto, bonif.tipo, bonif.monto, bonif.descripcion)
                    )
            else:
                total_bonificaciones = valores_anteriores['total_bonificaciones']
            
            if nomina.deducciones is not None:
                db.execute_query("DELETE FROM Nomina_Deducciones WHERE id_nomina = ?", (nomina_id,))
                total_deducciones = sum(d.monto for d in nomina.deducciones)
                # Insertar nuevas
                for deduc in nomina.deducciones:
                    db.execute_query(
                        """INSERT INTO Nomina_Deducciones (id_nomina, concepto, tipo, monto, descripcion)
                           VALUES (?, ?, ?, ?, ?)""",
                        (nomina_id, deduc.concepto, deduc.tipo, deduc.monto, deduc.descripcion)
                    )
            else:
                total_deducciones = valores_anteriores['total_deducciones']
            
            salario_base = nomina.salario_base if nomina.salario_base is not None else valores_anteriores['salario_base']
            salario_neto = salario_base + total_bonificaciones - total_deducciones
            
            if salario_neto < 0:
                raise HTTPException(status_code=400, detail="El salario neto no puede ser negativo")
            
            updates.append("total_bonificaciones = ?")
            params.append(total_bonificaciones)
            updates.append("total_deducciones = ?")
            params.append(total_deducciones)
            updates.append("salario_neto = ?")
            params.append(salario_neto)
            updates.append("fecha_modificacion = CURRENT_TIMESTAMP")
            updates.append("modificado_por = ?")
            params.append(usuario_id)
        
        if nomina.fecha_pago is not None:
            updates.append("fecha_pago = ?")
            params.append(nomina.fecha_pago)
        
        if nomina.estado is not None:
            updates.append("estado = ?")
            params.append(nomina.estado)
            db.execute_query(
                """INSERT INTO Nomina_Auditoria (id_nomina, accion, usuario_id, campo_modificado, valor_anterior, valor_nuevo)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (nomina_id, "MODIFICAR", usuario_id, "estado", 
                 valores_anteriores['estado'], nomina.estado)
            )
        
        if nomina.observaciones is not None:
            updates.append("observaciones = ?")
            params.append(nomina.observaciones)
        
        if updates:
            params.append(nomina_id)
            query = f"UPDATE Nomina SET {', '.join(updates)} WHERE id_nomina = ?"
            db.execute_query(query, tuple(params))
        
        # Obtener nómina actualizada
        nomina_actualizada = db.fetch_one(
            """SELECT n.*, e.nombre || ' ' || e.apellido as nombre_empleado 
               FROM Nomina n
               LEFT JOIN Empleados e ON n.id_empleado = e.id_empleado
               WHERE n.id_nomina = ?""",
            (nomina_id,)
        )
        nomina_actualizada['bonificaciones_detalle'] = db.fetch_all(
            "SELECT * FROM Nomina_Bonificaciones WHERE id_nomina = ?", (nomina_id,)
        )
        nomina_actualizada['deducciones_detalle'] = db.fetch_all(
            "SELECT * FROM Nomina_Deducciones WHERE id_nomina = ?", (nomina_id,)
        )
        
        return {
            "success": True,
            "message": "Nómina actualizada exitosamente",
            "data": nomina_actualizada
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar nómina: {str(e)}")

@app.get("/api/nomina/{nomina_id}/historial", tags=["Nómina"])
async def get_nomina_historial(nomina_id: int):
    """Obtener historial de modificaciones de una nómina"""
    try:
        db = get_db()
        historial = db.fetch_all(
            """SELECT * FROM Nomina_Auditoria 
               WHERE id_nomina = ? 
               ORDER BY fecha_modificacion DESC""",
            (nomina_id,)
        )
        return {"success": True, "data": historial, "count": len(historial)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener historial: {str(e)}")

@app.get("/api/nomina/empleado/{empleado_id}/historial", tags=["Nómina"])
async def get_empleado_nomina_historial(empleado_id: int):
    """Obtener historial completo de nómina de un empleado"""
    try:
        db = get_db()
        nomina = db.fetch_all(
            """SELECT n.*, e.nombre || ' ' || e.apellido as nombre_empleado 
               FROM Nomina n
               LEFT JOIN Empleados e ON n.id_empleado = e.id_empleado
               WHERE n.id_empleado = ?
               ORDER BY n.anio DESC, n.mes DESC""",
            (empleado_id,)
        )
        
        for registro in nomina:
            registro['bonificaciones_detalle'] = db.fetch_all(
                "SELECT * FROM Nomina_Bonificaciones WHERE id_nomina = ?", (registro['id_nomina'],)
            )
            registro['deducciones_detalle'] = db.fetch_all(
                "SELECT * FROM Nomina_Deducciones WHERE id_nomina = ?", (registro['id_nomina'],)
            )
        
        return {"success": True, "data": nomina, "count": len(nomina)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener historial: {str(e)}")

# ============================================================================
#                    ENDPOINTS DE CONFIGURACIÓN DE NÓMINA
# ============================================================================

@app.get("/api/nomina/config/impuestos", tags=["Nómina - Configuración"])
async def get_config_impuestos():
    """Obtener configuración de impuestos"""
    try:
        db = get_db()
        impuestos = db.fetch_all("SELECT * FROM Config_Impuestos WHERE activo = 1 ORDER BY nombre")
        return {"success": True, "data": impuestos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener impuestos: {str(e)}")

@app.post("/api/nomina/config/impuestos", tags=["Nómina - Configuración"])
async def create_config_impuesto(impuesto: ConfigImpuestoCreate):
    """Crear configuración de impuesto"""
    try:
        db = get_db()
        cursor = db.execute_query(
            """INSERT INTO Config_Impuestos (nombre, tipo, porcentaje, monto_fijo, rango_minimo, rango_maximo)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (impuesto.nombre, impuesto.tipo, impuesto.porcentaje, impuesto.monto_fijo,
             impuesto.rango_minimo, impuesto.rango_maximo)
        )
        nuevo = db.fetch_one("SELECT * FROM Config_Impuestos WHERE id_impuesto = ?", (cursor.lastrowid,))
        return {"success": True, "message": "Impuesto configurado exitosamente", "data": nuevo}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear impuesto: {str(e)}")

@app.get("/api/nomina/config/deducciones", tags=["Nómina - Configuración"])
async def get_config_deducciones():
    """Obtener configuración de deducciones"""
    try:
        db = get_db()
        deducciones = db.fetch_all("SELECT * FROM Config_Deducciones WHERE activo = 1 ORDER BY nombre")
        return {"success": True, "data": deducciones}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener deducciones: {str(e)}")

@app.post("/api/nomina/config/deducciones", tags=["Nómina - Configuración"])
async def create_config_deduccion(deduccion: ConfigDeduccionCreate):
    """Crear configuración de deducción"""
    try:
        db = get_db()
        cursor = db.execute_query(
            """INSERT INTO Config_Deducciones (nombre, tipo, porcentaje, monto_fijo, aplica_a_todos)
               VALUES (?, ?, ?, ?, ?)""",
            (deduccion.nombre, deduccion.tipo, deduccion.porcentaje, deduccion.monto_fijo, deduccion.aplica_a_todos)
        )
        nuevo = db.fetch_one("SELECT * FROM Config_Deducciones WHERE id_deduccion_config = ?", (cursor.lastrowid,))
        return {"success": True, "message": "Deducción configurada exitosamente", "data": nuevo}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear deducción: {str(e)}")

@app.get("/api/nomina/config/beneficios", tags=["Nómina - Configuración"])
async def get_config_beneficios():
    """Obtener configuración de beneficios"""
    try:
        db = get_db()
        beneficios = db.fetch_all("SELECT * FROM Config_Beneficios WHERE activo = 1 ORDER BY nombre")
        return {"success": True, "data": beneficios}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener beneficios: {str(e)}")

@app.post("/api/nomina/config/beneficios", tags=["Nómina - Configuración"])
async def create_config_beneficio(beneficio: ConfigBeneficioCreate):
    """Crear configuración de beneficio"""
    try:
        db = get_db()
        cursor = db.execute_query(
            """INSERT INTO Config_Beneficios (nombre, tipo, porcentaje, monto_fijo, aplica_a_todos)
               VALUES (?, ?, ?, ?, ?)""",
            (beneficio.nombre, beneficio.tipo, beneficio.porcentaje, beneficio.monto_fijo, beneficio.aplica_a_todos)
        )
        nuevo = db.fetch_one("SELECT * FROM Config_Beneficios WHERE id_beneficio = ?", (cursor.lastrowid,))
        return {"success": True, "message": "Beneficio configurado exitosamente", "data": nuevo}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear beneficio: {str(e)}")

# ============================================================================
#                    ENDPOINTS DE VACACIONES Y PERMISOS
# ============================================================================

@app.get("/api/vacaciones", tags=["Vacaciones y Permisos"])
async def get_vacaciones(id_empleado: Optional[int] = None, estado: Optional[str] = None):
    """Obtener solicitudes de vacaciones y permisos"""
    try:
        db = get_db()
        query = """SELECT v.*, e.nombre || ' ' || e.apellido as nombre_empleado,
                          u1.nombre as nombre_aprobador_jefe,
                          u2.nombre as nombre_aprobador_rrhh
                   FROM Vacaciones_Permisos v
                   LEFT JOIN Empleados e ON v.id_empleado = e.id_empleado
                   LEFT JOIN usuarios u1 ON v.aprobado_por_jefe = u1.id
                   LEFT JOIN usuarios u2 ON v.aprobado_por_rrhh = u2.id
                   WHERE 1=1"""
        params = []
        
        if id_empleado:
            query += " AND v.id_empleado = ?"
            params.append(id_empleado)
        if estado:
            query += " AND v.estado = ?"
            params.append(estado)
        
        query += " ORDER BY v.fecha_solicitud DESC"
        
        vacaciones = db.fetch_all(query, tuple(params) if params else ())
        return {"success": True, "data": vacaciones, "count": len(vacaciones)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener vacaciones: {str(e)}")

@app.post("/api/vacaciones", status_code=status.HTTP_201_CREATED, tags=["Vacaciones y Permisos"])
async def create_vacacion(vacacion: VacacionPermisoCreate):
    """Crear solicitud de vacaciones o permisos con cálculo automático de días"""
    try:
        db = get_db()
        from datetime import datetime, timedelta
        
        # Verificar empleado
        empleado = db.fetch_one("SELECT id_empleado FROM Empleados WHERE id_empleado = ?", (vacacion.id_empleado,))
        if not empleado:
            raise HTTPException(status_code=404, detail="Empleado no encontrado")
        
        # Calcular días solicitados
        fecha_inicio = datetime.strptime(vacacion.fecha_inicio, "%Y-%m-%d")
        fecha_fin = datetime.strptime(vacacion.fecha_fin, "%Y-%m-%d")
        dias_solicitados = (fecha_fin - fecha_inicio).days + 1
        
        if dias_solicitados <= 0:
            raise HTTPException(status_code=400, detail="La fecha fin debe ser posterior a la fecha inicio")
        
        # Obtener balance de vacaciones del año actual
        anio_actual = fecha_inicio.year
        balance = db.fetch_one(
            "SELECT * FROM Balance_Vacaciones WHERE id_empleado = ? AND anio = ?",
            (vacacion.id_empleado, anio_actual)
        )
        
        if not balance:
            # Crear balance inicial (asumiendo 15 días por año)
            dias_totales = 15
            db.execute_query(
                """INSERT INTO Balance_Vacaciones (id_empleado, anio, dias_totales, dias_disponibles)
                   VALUES (?, ?, ?, ?)""",
                (vacacion.id_empleado, anio_actual, dias_totales, dias_totales)
            )
            balance = db.fetch_one(
                "SELECT * FROM Balance_Vacaciones WHERE id_empleado = ? AND anio = ?",
                (vacacion.id_empleado, anio_actual)
            )
        
        dias_disponibles = balance.get('dias_disponibles', 0)
        
        # Validar días disponibles (solo para vacaciones)
        if vacacion.tipo.lower() == 'vacaciones' and dias_solicitados > dias_disponibles:
            raise HTTPException(
                status_code=400,
                detail=f"Días solicitados ({dias_solicitados}) exceden los disponibles ({dias_disponibles})"
            )
        
        # Crear solicitud
        cursor = db.execute_query(
            """INSERT INTO Vacaciones_Permisos (id_empleado, tipo, fecha_inicio, fecha_fin, 
                                               dias_solicitados, dias_disponibles, motivo, observaciones)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (vacacion.id_empleado, vacacion.tipo, vacacion.fecha_inicio, vacacion.fecha_fin,
             dias_solicitados, dias_disponibles, vacacion.motivo, vacacion.observaciones)
        )
        
        permiso_id = cursor.lastrowid
        
        # Crear notificaciones para jefe y RRHH
        # Obtener jefe del empleado (simplificado - en producción debería venir de la estructura organizacional)
        db.execute_query(
            """INSERT INTO Notificaciones_Vacaciones (id_permiso, usuario_id, tipo_notificacion, mensaje)
               SELECT ?, id, 'solicitud_pendiente', 
                      'Nueva solicitud de ' || ? || ' de ' || (SELECT nombre || ' ' || apellido FROM Empleados WHERE id_empleado = ?)
               FROM usuarios WHERE rol = 'supervisor' OR rol = 'administrador' LIMIT 1""",
            (permiso_id, vacacion.tipo, vacacion.id_empleado)
        )
        
        # Obtener solicitud creada
        nueva_solicitud = db.fetch_one(
            """SELECT v.*, e.nombre || ' ' || e.apellido as nombre_empleado
               FROM Vacaciones_Permisos v
               LEFT JOIN Empleados e ON v.id_empleado = e.id_empleado
               WHERE v.id_permiso = ?""",
            (permiso_id,)
        )
        
        return {
            "success": True,
            "message": "Solicitud creada exitosamente",
            "data": nueva_solicitud
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear solicitud: {str(e)}")

@app.put("/api/vacaciones/{permiso_id}/aprobar", tags=["Vacaciones y Permisos"])
async def aprobar_rechazar_vacacion(permiso_id: int, aprobacion: VacacionPermisoAprobacion, usuario_id: int):
    """Aprobar o rechazar solicitud de vacaciones (jefe o RRHH)"""
    try:
        db = get_db()
        from datetime import datetime
        
        # Verificar que existe
        solicitud = db.fetch_one("SELECT * FROM Vacaciones_Permisos WHERE id_permiso = ?", (permiso_id,))
        if not solicitud:
            raise HTTPException(status_code=404, detail="Solicitud no encontrada")
        
        if solicitud['estado'] != 'pendiente':
            raise HTTPException(status_code=400, detail="La solicitud ya fue procesada")
        
        # Obtener usuario
        usuario = db.fetch_one("SELECT rol FROM usuarios WHERE id = ?", (usuario_id,))
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        if aprobacion.aprobar:
            if aprobacion.nivel == 'jefe':
                db.execute_query(
                    """UPDATE Vacaciones_Permisos 
                       SET estado = 'aprobado_jefe', aprobado_por_jefe = ?, fecha_aprobacion_jefe = CURRENT_TIMESTAMP
                       WHERE id_permiso = ?""",
                    (usuario_id, permiso_id)
                )
                # Notificar a RRHH
                db.execute_query(
                    """INSERT INTO Notificaciones_Vacaciones (id_permiso, usuario_id, tipo_notificacion, mensaje)
                       SELECT ?, id, 'aprobado_jefe', 
                              'Solicitud aprobada por jefe, requiere aprobación RRHH'
                       FROM usuarios WHERE rol = 'administrador' OR rol LIKE '%rrhh%' LIMIT 1""",
                    (permiso_id,)
                )
            elif aprobacion.nivel == 'rrhh':
                # Aprobar final y actualizar balance
                db.execute_query(
                    """UPDATE Vacaciones_Permisos 
                       SET estado = 'aprobado', aprobado_por_rrhh = ?, fecha_aprobacion_rrhh = CURRENT_TIMESTAMP
                       WHERE id_permiso = ?""",
                    (usuario_id, permiso_id)
                )
                
                # Actualizar balance de vacaciones
                if solicitud['tipo'].lower() == 'vacaciones':
                    anio = datetime.strptime(solicitud['fecha_inicio'], "%Y-%m-%d").year
                    db.execute_query(
                        """UPDATE Balance_Vacaciones 
                           SET dias_usados = dias_usados + ?,
                               dias_disponibles = dias_disponibles - ?,
                               fecha_actualizacion = CURRENT_TIMESTAMP
                           WHERE id_empleado = ? AND anio = ?""",
                        (solicitud['dias_solicitados'], solicitud['dias_solicitados'], 
                         solicitud['id_empleado'], anio)
                    )
                
                # Notificar al empleado
                db.execute_query(
                    """INSERT INTO Notificaciones_Vacaciones (id_permiso, usuario_id, tipo_notificacion, mensaje)
                       VALUES (?, (SELECT id FROM usuarios WHERE email = 
                                   (SELECT correo FROM Empleados WHERE id_empleado = ?) LIMIT 1),
                               'aprobado', 'Su solicitud de vacaciones ha sido aprobada')""",
                    (permiso_id, solicitud['id_empleado'])
                )
        else:
            # Rechazar
            db.execute_query(
                """UPDATE Vacaciones_Permisos 
                   SET estado = 'rechazado', fecha_rechazo = CURRENT_TIMESTAMP, motivo_rechazo = ?
                   WHERE id_permiso = ?""",
                (aprobacion.motivo, permiso_id)
            )
            
            # Notificar al empleado
            db.execute_query(
                """INSERT INTO Notificaciones_Vacaciones (id_permiso, usuario_id, tipo_notificacion, mensaje)
                   VALUES (?, (SELECT id FROM usuarios WHERE email = 
                               (SELECT correo FROM Empleados WHERE id_empleado = ?) LIMIT 1),
                           'rechazado', ?)""",
                (permiso_id, solicitud['id_empleado'], f"Solicitud rechazada: {aprobacion.motivo}")
            )
        
        solicitud_actualizada = db.fetch_one(
            """SELECT v.*, e.nombre || ' ' || e.apellido as nombre_empleado
               FROM Vacaciones_Permisos v
               LEFT JOIN Empleados e ON v.id_empleado = e.id_empleado
               WHERE v.id_permiso = ?""",
            (permiso_id,)
        )
        
        return {
            "success": True,
            "message": "Solicitud procesada exitosamente",
            "data": solicitud_actualizada
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar solicitud: {str(e)}")

@app.get("/api/vacaciones/empleado/{empleado_id}/balance", tags=["Vacaciones y Permisos"])
async def get_balance_vacaciones(empleado_id: int, anio: Optional[int] = None):
    """Obtener balance de vacaciones de un empleado"""
    try:
        db = get_db()
        if not anio:
            from datetime import datetime
            anio = datetime.now().year
        
        balance = db.fetch_one(
            "SELECT * FROM Balance_Vacaciones WHERE id_empleado = ? AND anio = ?",
            (empleado_id, anio)
        )
        
        if not balance:
            # Crear balance inicial
            db.execute_query(
                """INSERT INTO Balance_Vacaciones (id_empleado, anio, dias_totales, dias_disponibles)
                   VALUES (?, ?, 15, 15)""",
                (empleado_id, anio)
            )
            balance = db.fetch_one(
                "SELECT * FROM Balance_Vacaciones WHERE id_empleado = ? AND anio = ?",
                (empleado_id, anio)
            )
        
        return {"success": True, "data": balance}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener balance: {str(e)}")

@app.get("/api/vacaciones/calendario", tags=["Vacaciones y Permisos"])
async def get_calendario_vacaciones(mes: int, anio: int):
    """Obtener calendario de ausencias para un mes específico"""
    try:
        db = get_db()
        vacaciones = db.fetch_all(
            """SELECT v.*, e.nombre || ' ' || e.apellido as nombre_empleado
               FROM Vacaciones_Permisos v
               LEFT JOIN Empleados e ON v.id_empleado = e.id_empleado
               WHERE v.estado = 'aprobado'
                 AND (strftime('%m', v.fecha_inicio) = ? OR strftime('%m', v.fecha_fin) = ?)
                 AND (strftime('%Y', v.fecha_inicio) = ? OR strftime('%Y', v.fecha_fin) = ?)""",
            (f"{mes:02d}", f"{mes:02d}", str(anio), str(anio))
        )
        return {"success": True, "data": vacaciones, "count": len(vacaciones)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener calendario: {str(e)}")

# ============================================================================
#                           ENDPOINTS DE DOCUMENTOS
# ============================================================================

# Directorio para almacenar documentos
DOCUMENTS_DIR = os.path.join(os.path.dirname(__file__), "uploads", "documents")
os.makedirs(DOCUMENTS_DIR, exist_ok=True)

@app.get("/api/documentos", tags=["Documentos"])
async def get_documentos(id_empleado: Optional[int] = None, tipo: Optional[str] = None, 
                         categoria: Optional[str] = None, buscar: Optional[str] = None):
    """Obtener documentos con filtros y búsqueda"""
    try:
        db = get_db()
        query = """SELECT d.*, e.nombre || ' ' || e.apellido as nombre_empleado,
                          u.nombre as nombre_subido_por
                   FROM Documentos d
                   LEFT JOIN Empleados e ON d.id_empleado = e.id_empleado
                   LEFT JOIN usuarios u ON d.subido_por = u.id
                   WHERE d.estado = 'activo'"""
        params = []
        
        if id_empleado:
            query += " AND d.id_empleado = ?"
            params.append(id_empleado)
        if tipo:
            query += " AND d.tipo_documento = ?"
            params.append(tipo)
        if categoria:
            query += " AND d.categoria = ?"
            params.append(categoria)
        if buscar:
            query += " AND (d.nombre_original LIKE ? OR d.descripcion LIKE ?)"
            params.extend([f"%{buscar}%", f"%{buscar}%"])
        
        query += " ORDER BY d.fecha_subida DESC"
        
        documentos = db.fetch_all(query, tuple(params) if params else ())
        
        # Verificar expiración
        hoy = datetime.now().date()
        for doc in documentos:
            if doc.get('fecha_expiracion'):
                fecha_exp = datetime.strptime(doc['fecha_expiracion'], "%Y-%m-%d").date()
                doc['expirado'] = fecha_exp < hoy
                doc['dias_para_expiracion'] = (fecha_exp - hoy).days if fecha_exp >= hoy else 0
            else:
                doc['expirado'] = False
        
        return {"success": True, "data": documentos, "count": len(documentos)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener documentos: {str(e)}")

@app.post("/api/documentos/upload", tags=["Documentos"])
async def upload_documento(
    file: UploadFile = File(...),
    id_empleado: int = None,
    tipo_documento: str = None,
    categoria: str = None,
    descripcion: str = None,
    fecha_expiracion: str = None,
    usuario_id: int = None
):
    """Subir un documento"""
    try:
        db = get_db()
        
        # Validar tipo de archivo
        allowed_types = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg',
                        'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Tipo de archivo no permitido")
        
        # Validar tamaño (máx 10MB)
        file_content = await file.read()
        if len(file_content) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="El archivo excede 10MB")
        
        # Guardar archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(DOCUMENTS_DIR, safe_filename)
        
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)
        
        # Guardar en BD
        cursor = db.execute_query(
            """INSERT INTO Documentos (id_empleado, nombre_archivo, nombre_original, tipo_documento,
                                     categoria, ruta_archivo, tamano_bytes, mime_type, descripcion,
                                     fecha_expiracion, subido_por)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (id_empleado, safe_filename, file.filename, tipo_documento, categoria, file_path,
             len(file_content), file.content_type, descripcion, fecha_expiracion, usuario_id)
        )
        
        documento = db.fetch_one(
            """SELECT d.*, e.nombre || ' ' || e.apellido as nombre_empleado
               FROM Documentos d
               LEFT JOIN Empleados e ON d.id_empleado = e.id_empleado
               WHERE d.id_documento = ?""",
            (cursor.lastrowid,)
        )
        
        return {"success": True, "message": "Documento subido exitosamente", "data": documento}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al subir documento: {str(e)}")

@app.get("/api/documentos/{documento_id}/download", tags=["Documentos"])
async def download_documento(documento_id: int):
    """Descargar un documento"""
    try:
        db = get_db()
        from fastapi.responses import FileResponse
        
        documento = db.fetch_one("SELECT * FROM Documentos WHERE id_documento = ?", (documento_id,))
        if not documento:
            raise HTTPException(status_code=404, detail="Documento no encontrado")
        
        if not os.path.exists(documento['ruta_archivo']):
            raise HTTPException(status_code=404, detail="Archivo físico no encontrado")
        
        return FileResponse(
            documento['ruta_archivo'],
            filename=documento['nombre_original'],
            media_type=documento.get('mime_type', 'application/octet-stream')
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al descargar documento: {str(e)}")

@app.delete("/api/documentos/{documento_id}", tags=["Documentos"])
async def delete_documento(documento_id: int):
    """Eliminar un documento"""
    try:
        db = get_db()
        
        documento = db.fetch_one("SELECT * FROM Documentos WHERE id_documento = ?", (documento_id,))
        if not documento:
            raise HTTPException(status_code=404, detail="Documento no encontrado")
        
        # Eliminar archivo físico
        if os.path.exists(documento['ruta_archivo']):
            os.remove(documento['ruta_archivo'])
        
        # Eliminar de BD
        db.execute_query("DELETE FROM Documentos WHERE id_documento = ?", (documento_id,))
        
        return {"success": True, "message": "Documento eliminado exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar documento: {str(e)}")

@app.get("/api/documentos/vencidos", tags=["Documentos"])
async def get_documentos_vencidos():
    """Obtener documentos próximos a vencer o vencidos"""
    try:
        db = get_db()
        hoy = datetime.now().date()
        
        documentos = db.fetch_all(
            """SELECT d.*, e.nombre || ' ' || e.apellido as nombre_empleado,
                      julianday(d.fecha_expiracion) - julianday('now') as dias_restantes
               FROM Documentos d
               LEFT JOIN Empleados e ON d.id_empleado = e.id_empleado
               WHERE d.fecha_expiracion IS NOT NULL
                 AND d.estado = 'activo'
                 AND d.fecha_expiracion <= date('now', '+30 days')
               ORDER BY d.fecha_expiracion ASC"""
        )
        
        return {"success": True, "data": documentos, "count": len(documentos)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener documentos vencidos: {str(e)}")

# ============================================================================
#                    ENDPOINTS DE REPORTES Y DASHBOARDS
# ============================================================================

@app.get("/api/reportes/indicadores", tags=["Reportes"])
async def get_indicadores(fecha_inicio: Optional[str] = None, fecha_fin: Optional[str] = None):
    """Obtener indicadores clave del sistema"""
    try:
        db = get_db()
        from datetime import datetime
        
        # Total empleados
        total_empleados = db.fetch_one("SELECT COUNT(*) as total FROM Empleados WHERE estado = 'activo'")
        
        # Tasa de rotación (empleados inactivos en el período)
        if fecha_inicio and fecha_fin:
            rotacion = db.fetch_one(
                """SELECT COUNT(*) as total FROM Empleados 
                   WHERE estado = 'inactivo' AND fecha_ingreso BETWEEN ? AND ?""",
                (fecha_inicio, fecha_fin)
            )
        else:
            rotacion = db.fetch_one("SELECT COUNT(*) as total FROM Empleados WHERE estado = 'inactivo'")
        
        # Tasa de asistencia (promedio)
        asistencias = db.fetch_all(
            """SELECT COUNT(*) as total, 
                      SUM(CASE WHEN hora_entrada IS NOT NULL THEN 1 ELSE 0 END) as presentes
               FROM Asistencias
               WHERE fecha >= date('now', '-30 days')"""
        )
        
        # Antigüedad promedio
        antiguedad = db.fetch_one(
            """SELECT AVG(julianday('now') - julianday(fecha_ingreso)) / 365.25 as promedio_anios
               FROM Empleados WHERE estado = 'activo'"""
        )
        
        return {
            "success": True,
            "data": {
                "total_empleados": total_empleados['total'] if total_empleados else 0,
                "tasa_rotacion": (rotacion['total'] / total_empleados['total'] * 100) if total_empleados and total_empleados['total'] > 0 else 0,
                "tasa_asistencia": (asistencias[0]['presentes'] / asistencias[0]['total'] * 100) if asistencias and asistencias[0]['total'] > 0 else 0,
                "antiguedad_promedio": round(antiguedad['promedio_anios'], 2) if antiguedad and antiguedad['promedio_anios'] else 0
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener indicadores: {str(e)}")

@app.get("/api/reportes/comparativa", tags=["Reportes"])
async def get_comparativa_periodos(periodo1_inicio: str, periodo1_fin: str, 
                                    periodo2_inicio: str, periodo2_fin: str):
    """Comparar indicadores entre dos períodos"""
    try:
        db = get_db()
        
        # Obtener indicadores para período 1
        indicadores1 = await get_indicadores(periodo1_inicio, periodo1_fin)
        # Obtener indicadores para período 2
        indicadores2 = await get_indicadores(periodo2_inicio, periodo2_fin)
        
        # Calcular diferencias
        data1 = indicadores1['data']
        data2 = indicadores2['data']
        
        comparativa = {
            "periodo1": {
                "fecha_inicio": periodo1_inicio,
                "fecha_fin": periodo1_fin,
                "indicadores": data1
            },
            "periodo2": {
                "fecha_inicio": periodo2_inicio,
                "fecha_fin": periodo2_fin,
                "indicadores": data2
            },
            "diferencias": {
                "total_empleados": data2['total_empleados'] - data1['total_empleados'],
                "tasa_rotacion": data2['tasa_rotacion'] - data1['tasa_rotacion'],
                "tasa_asistencia": data2['tasa_asistencia'] - data1['tasa_asistencia'],
                "antiguedad_promedio": data2['antiguedad_promedio'] - data1['antiguedad_promedio']
            }
        }
        
        return {"success": True, "data": comparativa}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar comparativa: {str(e)}")

@app.get("/api/reportes/graficas/empleados-departamento", tags=["Reportes"])
async def get_grafica_empleados_departamento():
    """Datos para gráfica de empleados por departamento"""
    try:
        db = get_db()
        datos = db.fetch_all(
            """SELECT d.nombre_departamento as departamento, COUNT(e.id_empleado) as cantidad
               FROM Departamentos d
               LEFT JOIN Empleados e ON d.id_departamento = e.id_departamento AND e.estado = 'activo'
               GROUP BY d.id_departamento, d.nombre_departamento
               ORDER BY cantidad DESC"""
        )
        return {"success": True, "data": datos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener datos: {str(e)}")

@app.get("/api/reportes/graficas/asistencia-tiempo", tags=["Reportes"])
async def get_grafica_asistencia_tiempo(dias: int = 30):
    """Datos para gráfica de asistencia en el tiempo"""
    try:
        db = get_db()
        datos = db.fetch_all(
            """SELECT fecha, 
                      COUNT(*) as total,
                      SUM(CASE WHEN hora_entrada IS NOT NULL THEN 1 ELSE 0 END) as presentes
               FROM Asistencias
               WHERE fecha >= date('now', '-' || ? || ' days')
               GROUP BY fecha
               ORDER BY fecha ASC""",
            (dias,)
        )
        return {"success": True, "data": datos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener datos: {str(e)}")

# ============================================================================
#                    ENDPOINTS DE NÓMINA - PDF
# ============================================================================

@app.get("/api/nomina/{nomina_id}/recibo-pdf", tags=["Nómina"])
async def generar_recibo_pdf(nomina_id: int):
    """Generar recibo de nómina en formato PDF/HTML"""
    try:
        db = get_db()
        from fastapi.responses import HTMLResponse
        
        nomina = db.fetch_one(
            """SELECT n.*, e.nombre || ' ' || e.apellido as nombre_empleado,
                      e.correo as email_empleado
               FROM Nomina n
               LEFT JOIN Empleados e ON n.id_empleado = e.id_empleado
               WHERE n.id_nomina = ?""",
            (nomina_id,)
        )
        if not nomina:
            raise HTTPException(status_code=404, detail="Nómina no encontrada")
        
        bonificaciones = db.fetch_all(
            "SELECT * FROM Nomina_Bonificaciones WHERE id_nomina = ?", (nomina_id,)
        )
        deducciones = db.fetch_all(
            "SELECT * FROM Nomina_Deducciones WHERE id_nomina = ?", (nomina_id,)
        )
        
        # Generar HTML del recibo
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Recibo de Nómina - {nomina['nombre_empleado']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; max-width: 800px; margin: 0 auto; }}
        .header {{ text-align: center; border-bottom: 3px solid #333; padding-bottom: 20px; margin-bottom: 30px; }}
        .info-section {{ margin-bottom: 20px; }}
        .receipt-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        .receipt-table th, .receipt-table td {{ padding: 12px; border: 1px solid #ddd; text-align: left; }}
        .receipt-table th {{ background-color: #f2f2f2; font-weight: bold; }}
        .total-row {{ font-weight: bold; background-color: #e8f5e9; font-size: 1.1em; }}
        .signature-section {{ margin-top: 50px; display: flex; justify-content: space-between; }}
        .signature-box {{ width: 250px; border-top: 2px solid #000; padding-top: 10px; text-align: center; }}
        .footer {{ margin-top: 30px; font-size: 12px; color: #666; text-align: center; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>RECIBO DE NÓMINA</h1>
        <p><strong>Período:</strong> {nomina['periodo']}</p>
    </div>
    
    <div class="info-section">
        <p><strong>Empleado:</strong> {nomina['nombre_empleado']}</p>
        <p><strong>Email:</strong> {nomina.get('email_empleado', 'N/A')}</p>
        <p><strong>Fecha de Pago:</strong> {nomina.get('fecha_pago', 'Pendiente')}</p>
        <p><strong>Estado:</strong> {nomina['estado']}</p>
    </div>
    
    <table class="receipt-table">
        <thead>
            <tr>
                <th>Concepto</th>
                <th>Descripción</th>
                <th style="text-align: right;">Monto</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>Salario Base</strong></td>
                <td>-</td>
                <td style="text-align: right;">${nomina['salario_base']:,.2f}</td>
            </tr>
            {''.join([f'''
            <tr>
                <td>Bonificación</td>
                <td>{b['concepto']}</td>
                <td style="text-align: right;">${b['monto']:,.2f}</td>
            </tr>''' for b in bonificaciones])}
            {''.join([f'''
            <tr>
                <td>Deducción</td>
                <td>{d['concepto']}</td>
                <td style="text-align: right;">-${d['monto']:,.2f}</td>
            </tr>''' for d in deducciones])}
            <tr class="total-row">
                <td colspan="2"><strong>SALARIO NETO</strong></td>
                <td style="text-align: right;"><strong>${nomina['salario_neto']:,.2f}</strong></td>
            </tr>
        </tbody>
    </table>
    
    <div class="signature-section">
        <div class="signature-box">
            <p><strong>Firma del Empleado</strong></p>
            <p style="margin-top: 40px;">_________________________</p>
        </div>
        <div class="signature-box">
            <p><strong>Firma de RRHH</strong></p>
            <p style="margin-top: 40px;">_________________________</p>
        </div>
    </div>
    
    <div class="footer">
        <p>Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
        <p>Este documento es generado automáticamente por el Sistema de RRHH</p>
    </div>
</body>
</html>
        """
        
        return HTMLResponse(content=html_content)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar recibo: {str(e)}")

# ============================================================================
#                    ENDPOINTS DE DOCUMENTOS - VISTA PREVIA
# ============================================================================

@app.get("/api/documentos/{documento_id}/preview", tags=["Documentos"])
async def preview_documento(documento_id: int):
    """Vista previa de documento en el navegador"""
    try:
        db = get_db()
        from fastapi.responses import FileResponse, StreamingResponse
        
        documento = db.fetch_one("SELECT * FROM Documentos WHERE id_documento = ?", (documento_id,))
        if not documento:
            raise HTTPException(status_code=404, detail="Documento no encontrado")
        
        if not os.path.exists(documento['ruta_archivo']):
            raise HTTPException(status_code=404, detail="Archivo físico no encontrado")
        
        mime_type = documento.get('mime_type', 'application/octet-stream')
        
        # Si es PDF o imagen, mostrar directamente
        if mime_type in ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg']:
            return FileResponse(
                documento['ruta_archivo'],
                media_type=mime_type,
                headers={"Content-Disposition": f"inline; filename={documento['nombre_original']}"}
            )
        else:
            # Para otros tipos, ofrecer descarga
            return FileResponse(
                documento['ruta_archivo'],
                filename=documento['nombre_original'],
                media_type=mime_type
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener vista previa: {str(e)}")

# ============================================================================
#                    ENDPOINTS DE USUARIOS - SEGURIDAD MEJORADA
# ============================================================================
async def cambiar_password(usuario_id: int, password_actual: str, password_nueva: str):
    """Cambiar contraseña de usuario"""
    try:
        db = get_db()
        
        # Verificar contraseña actual
        usuario = db.fetch_one(
            "SELECT id, password FROM usuarios WHERE id = ? AND activo = 1",
            (usuario_id,)
        )
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        if usuario['password'] != password_actual:
            raise HTTPException(status_code=401, detail="Contraseña actual incorrecta")
        
        # Validar nueva contraseña
        if len(password_nueva) < 6:
            raise HTTPException(status_code=400, detail="La nueva contraseña debe tener al menos 6 caracteres")
        
        # Actualizar contraseña
        db.execute_query("UPDATE usuarios SET password = ? WHERE id = ?", (password_nueva, usuario_id))
        
        # Registrar en auditoría
        db.execute_query(
            """INSERT INTO Usuarios_Auditoria (usuario_id, accion, modulo, detalles)
               VALUES (?, ?, ?, ?)""",
            (usuario_id, "CAMBIAR_PASSWORD", "Usuarios", "Contraseña actualizada")
        )
        
        return {"success": True, "message": "Contraseña actualizada exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al cambiar contraseña: {str(e)}")

@app.get("/api/usuarios/{usuario_id}/auditoria", tags=["Usuarios"])
async def get_auditoria_usuario(usuario_id: int, limite: int = 100):
    """Obtener historial de auditoría de un usuario"""
    try:
        db = get_db()
        auditoria = db.fetch_all(
            """SELECT * FROM Usuarios_Auditoria 
               WHERE usuario_id = ?
               ORDER BY fecha_accion DESC
               LIMIT ?""",
            (usuario_id, limite)
        )
        return {"success": True, "data": auditoria, "count": len(auditoria)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener auditoría: {str(e)}")

# ============================================================================
#                    ENDPOINTS DE CONFIGURACIÓN DEL SISTEMA
# ============================================================================

@app.get("/api/config", tags=["Configuración"])
async def get_config(clave: Optional[str] = None, categoria: Optional[str] = None):
    """Obtener configuración del sistema"""
    try:
        db = get_db()
        if clave:
            config = db.fetch_one("SELECT * FROM Config_Sistema WHERE clave = ?", (clave,))
            return {"success": True, "data": config} if config else {"success": False, "data": None}
        elif categoria:
            configs = db.fetch_all("SELECT * FROM Config_Sistema WHERE categoria = ?", (categoria,))
            return {"success": True, "data": configs}
        else:
            configs = db.fetch_all("SELECT * FROM Config_Sistema ORDER BY categoria, clave")
            return {"success": True, "data": configs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener configuración: {str(e)}")

@app.post("/api/config", tags=["Configuración"])
async def create_config(clave: str, valor: str, tipo: str = "texto", 
                       descripcion: Optional[str] = None, categoria: Optional[str] = None):
    """Crear o actualizar configuración"""
    try:
        db = get_db()
        
        # Verificar si existe
        existente = db.fetch_one("SELECT id_config FROM Config_Sistema WHERE clave = ?", (clave,))
        
        if existente:
            db.execute_query(
                """UPDATE Config_Sistema 
                   SET valor = ?, tipo = ?, descripcion = ?, categoria = ?, fecha_modificacion = CURRENT_TIMESTAMP
                   WHERE clave = ?""",
                (valor, tipo, descripcion, categoria, clave)
            )
            mensaje = "Configuración actualizada"
        else:
            db.execute_query(
                """INSERT INTO Config_Sistema (clave, valor, tipo, descripcion, categoria)
                   VALUES (?, ?, ?, ?, ?)""",
                (clave, valor, tipo, descripcion, categoria)
            )
            mensaje = "Configuración creada"
        
        config = db.fetch_one("SELECT * FROM Config_Sistema WHERE clave = ?", (clave,))
        return {"success": True, "message": mensaje, "data": config}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar configuración: {str(e)}")

@app.get("/api/config/catalogos", tags=["Configuración"])
async def get_catalogos(tipo: Optional[str] = None):
    """Obtener catálogos del sistema"""
    try:
        db = get_db()
        if tipo:
            catalogos = db.fetch_all(
                "SELECT * FROM Catalogos WHERE tipo = ? AND activo = 1 ORDER BY orden, nombre",
                (tipo,)
            )
        else:
            catalogos = db.fetch_all(
                "SELECT * FROM Catalogos WHERE activo = 1 ORDER BY tipo, orden, nombre"
            )
        return {"success": True, "data": catalogos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener catálogos: {str(e)}")

@app.post("/api/config/catalogos", tags=["Configuración"])
async def create_catalogo(tipo: str, nombre: str, codigo: Optional[str] = None,
                         descripcion: Optional[str] = None, orden: int = 0):
    """Crear nuevo catálogo"""
    try:
        db = get_db()
        cursor = db.execute_query(
            """INSERT INTO Catalogos (tipo, codigo, nombre, descripcion, orden)
               VALUES (?, ?, ?, ?, ?)""",
            (tipo, codigo, nombre, descripcion, orden)
        )
        catalogo = db.fetch_one("SELECT * FROM Catalogos WHERE id_catalogo = ?", (cursor.lastrowid,))
        return {"success": True, "message": "Catálogo creado exitosamente", "data": catalogo}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear catálogo: {str(e)}")

@app.post("/api/config/respaldo", tags=["Configuración"])
async def crear_respaldo():
    """Crear respaldo de la base de datos"""
    try:
        import shutil
        from datetime import datetime
        
        db = get_db()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(os.path.dirname(__file__), f"backups", f"rrhh_backup_{timestamp}.db")
        
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
        shutil.copy2(db.db_path, backup_path)
        
        return {
            "success": True,
            "message": "Respaldo creado exitosamente",
            "data": {"archivo": backup_path, "fecha": timestamp}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear respaldo: {str(e)}")

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

