"""
Helper para Crear Empleados con Usuario y Rol Automático
=========================================================

Este módulo proporciona funciones para crear empleados y automáticamente:
- Crear su usuario asociado
- Asignar el rol según su puesto

Uso en FastAPI:
--------------
```python
from helpers.empleado_usuario_helper import crear_empleado_completo

@app.post("/empleados")
async def crear_empleado(data: dict):
    empleado_id, usuario_id, rol_id = crear_empleado_completo(
        nombre=data['nombre'],
        apellido=data['apellido'],
        email=data['email'],
        puesto_id=data['puesto_id'],
        departamento_id=data['departamento_id'],
        salario=data['salario'],
        fecha_ingreso=data['fecha_ingreso']
    )
    return {"empleado_id": empleado_id, "usuario_id": usuario_id}
```

Autor: Sistema RRHH
Fecha: 2025
"""

import sqlite3
import bcrypt
from typing import Tuple, Optional
from datetime import datetime


def hash_password(password: str) -> str:
    """
    Hashea una contraseña usando bcrypt
    
    Args:
        password: Contraseña en texto plano
    
    Returns:
        str: Contraseña hasheada
    """
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode('utf-8')


def crear_usuario_para_empleado(
    nombre: str,
    apellido: str,
    email: str,
    password: Optional[str] = None
) -> int:
    """
    Crea un usuario para un empleado
    
    Args:
        nombre: Nombre del empleado
        apellido: Apellido del empleado
        email: Email del empleado
        password: Contraseña (opcional, por defecto 'Empleado123')
    
    Returns:
        int: ID del usuario creado
    
    Raises:
        Exception: Si el usuario ya existe o hay error en BD
    """
    conn = sqlite3.connect('rrhh.db')
    cursor = conn.cursor()
    
    try:
        # Verificar si ya existe un usuario con ese email
        cursor.execute("SELECT id FROM usuarios WHERE email = ?", (email,))
        usuario_existente = cursor.fetchone()
        
        if usuario_existente:
            # Ya existe, retornar el ID
            conn.close()
            return usuario_existente[0]
        
        # Crear nuevo usuario
        nombre_completo = f"{nombre} {apellido}"
        password_default = password or "Empleado123"
        password_hash = hash_password(password_default)
        
        cursor.execute("""
            INSERT INTO usuarios (nombre, email, password, activo)
            VALUES (?, ?, ?, 1)
        """, (nombre_completo, email, password_hash))
        
        usuario_id = cursor.lastrowid
        conn.commit()
        
        return usuario_id
        
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error al crear usuario: {e}")
    finally:
        conn.close()


def asignar_rol_segun_puesto(usuario_id: int, puesto_id: int) -> Optional[int]:
    """
    Asigna rol al usuario según su puesto
    
    Args:
        usuario_id: ID del usuario
        puesto_id: ID del puesto
    
    Returns:
        int: ID del rol asignado, o None si el puesto no tiene rol
    
    Raises:
        Exception: Si hay error en BD
    """
    conn = sqlite3.connect('rrhh.db')
    cursor = conn.cursor()
    
    try:
        # Obtener rol del puesto
        cursor.execute("""
            SELECT id_rol FROM Puestos WHERE id_puesto = ?
        """, (puesto_id,))
        
        resultado = cursor.fetchone()
        
        if not resultado or not resultado[0]:
            # El puesto no tiene rol asignado
            conn.close()
            return None
        
        rol_id = resultado[0]
        
        # Verificar si ya tiene este rol
        cursor.execute("""
            SELECT id_usuario_rol FROM Usuarios_Roles
            WHERE usuario_id = ? AND id_rol = ? AND activo = 1
        """, (usuario_id, rol_id))
        
        if cursor.fetchone():
            # Ya tiene el rol asignado
            conn.close()
            return rol_id
        
        # Desactivar roles principales anteriores
        cursor.execute("""
            UPDATE Usuarios_Roles
            SET activo = 0
            WHERE usuario_id = ? AND es_principal = 1
        """, (usuario_id,))
        
        # Asignar nuevo rol
        cursor.execute("""
            INSERT INTO Usuarios_Roles (usuario_id, id_rol, es_principal, activo)
            VALUES (?, ?, 1, 1)
        """, (usuario_id, rol_id))
        
        # Registrar en historial
        cursor.execute("""
            INSERT INTO Historial_Roles (usuario_id, id_rol_nuevo, motivo)
            VALUES (?, ?, 'Asignación automática al crear empleado')
        """, (usuario_id, rol_id))
        
        conn.commit()
        
        return rol_id
        
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error al asignar rol: {e}")
    finally:
        conn.close()


def crear_empleado_completo(
    nombre: str,
    apellido: str,
    email: str,
    puesto_id: int,
    departamento_id: int,
    salario: float,
    fecha_ingreso: str,
    telefono: Optional[str] = None,
    password: Optional[str] = None
) -> Tuple[int, int, Optional[int]]:
    """
    Crea un empleado completo con usuario y rol automático
    
    Args:
        nombre: Nombre del empleado
        apellido: Apellido del empleado
        email: Email del empleado (será su username)
        puesto_id: ID del puesto
        departamento_id: ID del departamento
        salario: Salario del empleado
        fecha_ingreso: Fecha de ingreso (YYYY-MM-DD)
        telefono: Teléfono (opcional)
        password: Contraseña (opcional, default 'Empleado123')
    
    Returns:
        Tuple[int, int, Optional[int]]: (empleado_id, usuario_id, rol_id)
    
    Raises:
        Exception: Si hay algún error en el proceso
    """
    conn = sqlite3.connect('rrhh.db')
    cursor = conn.cursor()
    
    try:
        # 1. Crear usuario
        usuario_id = crear_usuario_para_empleado(nombre, apellido, email, password)
        
        # 2. Crear empleado
        cursor.execute("""
            INSERT INTO empleados 
            (nombre, apellido, email, telefono, departamento_id, puesto, 
             fecha_ingreso, salario, usuario_id, activo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """, (
            nombre,
            apellido,
            email,
            telefono,
            departamento_id,
            puesto_id,
            fecha_ingreso,
            salario,
            usuario_id
        ))
        
        empleado_id = cursor.lastrowid
        conn.commit()
        
        # 3. Asignar rol según puesto
        rol_id = asignar_rol_segun_puesto(usuario_id, puesto_id)
        
        return empleado_id, usuario_id, rol_id
        
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error al crear empleado completo: {e}")
    finally:
        conn.close()


def actualizar_rol_al_cambiar_puesto(empleado_id: int, nuevo_puesto_id: int) -> Optional[int]:
    """
    Actualiza el rol cuando un empleado cambia de puesto
    
    Args:
        empleado_id: ID del empleado
        nuevo_puesto_id: ID del nuevo puesto
    
    Returns:
        int: ID del nuevo rol asignado, o None si el puesto no tiene rol
    
    Raises:
        Exception: Si hay error en BD
    """
    conn = sqlite3.connect('rrhh.db')
    cursor = conn.cursor()
    
    try:
        # Obtener usuario_id del empleado
        cursor.execute("SELECT usuario_id FROM empleados WHERE id = ?", (empleado_id,))
        resultado = cursor.fetchone()
        
        if not resultado or not resultado[0]:
            raise Exception("Empleado no tiene usuario asociado")
        
        usuario_id = resultado[0]
        
        # Actualizar puesto
        cursor.execute("""
            UPDATE empleados SET puesto = ? WHERE id = ?
        """, (nuevo_puesto_id, empleado_id))
        
        conn.commit()
        
        # Asignar nuevo rol
        return asignar_rol_segun_puesto(usuario_id, nuevo_puesto_id)
        
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error al actualizar rol: {e}")
    finally:
        conn.close()


def obtener_info_empleado_completa(empleado_id: int) -> Optional[dict]:
    """
    Obtiene información completa de un empleado incluyendo usuario y rol
    
    Args:
        empleado_id: ID del empleado
    
    Returns:
        dict: Información completa del empleado o None si no existe
    """
    conn = sqlite3.connect('rrhh.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT 
                e.id as empleado_id,
                e.nombre,
                e.apellido,
                e.email,
                e.telefono,
                e.salario,
                e.fecha_ingreso,
                e.activo,
                d.nombre as departamento,
                p.nombre_puesto as puesto,
                p.id_puesto,
                u.id as usuario_id,
                u.activo as usuario_activo,
                r.id_rol,
                r.nombre as rol,
                r.nivel_acceso
            FROM empleados e
            LEFT JOIN departamentos d ON e.departamento_id = d.id
            LEFT JOIN Puestos p ON e.puesto = p.id_puesto
            LEFT JOIN usuarios u ON e.usuario_id = u.id
            LEFT JOIN Usuarios_Roles ur ON u.id = ur.usuario_id AND ur.activo = 1
            LEFT JOIN Roles r ON ur.id_rol = r.id_rol
            WHERE e.id = ?
        """, (empleado_id,))
        
        resultado = cursor.fetchone()
        
        if not resultado:
            return None
        
        return dict(resultado)
        
    finally:
        conn.close()


# Ejemplo de uso
if __name__ == "__main__":
    print("=" * 70)
    print("EJEMPLO DE USO - Helper Empleado-Usuario")
    print("=" * 70)
    
    # Ejemplo: Crear un empleado completo
    try:
        empleado_id, usuario_id, rol_id = crear_empleado_completo(
            nombre="Juan",
            apellido="Pérez",
            email="juan.perez@empresa.com",
            puesto_id=16,  # Ejecutivo de Ventas (Operativo)
            departamento_id=5,  # Ventas
            salario=38000,
            fecha_ingreso="2025-01-15",
            telefono="+504 9999-8888"
        )
        
        print(f"\n✅ Empleado creado exitosamente:")
        print(f"   Empleado ID: {empleado_id}")
        print(f"   Usuario ID: {usuario_id}")
        print(f"   Rol ID: {rol_id}")
        
        # Obtener información completa
        info = obtener_info_empleado_completa(empleado_id)
        if info:
            print(f"\n📋 Información completa:")
            print(f"   Nombre: {info['nombre']} {info['apellido']}")
            print(f"   Email: {info['email']}")
            print(f"   Puesto: {info['puesto']}")
            print(f"   Departamento: {info['departamento']}")
            print(f"   Rol: {info['rol']} (Nivel {info['nivel_acceso']})")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    print("\n" + "=" * 70)

