"""Vincular Empleados con Usuarios y Roles - Version Simple"""
import sqlite3
import bcrypt

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8')[:72], bcrypt.gensalt()).decode('utf-8')

conn = sqlite3.connect('rrhh.db')
cursor = conn.cursor()

print("\n" + "="*70)
print("VINCULANDO EMPLEADOS CON USUARIOS Y ROLES")
print("="*70)

# Obtener empleados sin usuario
cursor.execute("""
    SELECT id, nombre, apellido, email
    FROM empleados
    WHERE usuario_id IS NULL AND activo = 1
""")

empleados = cursor.fetchall()
print(f"\n{len(empleados)} empleados necesitan usuario")

creados = 0
for emp_id, nombre, apellido, email in empleados:
    try:
        # Verificar si ya existe usuario con ese email
        cursor.execute("SELECT id FROM usuarios WHERE email = ?", (email,))
        usuario_existente = cursor.fetchone()
        
        if usuario_existente:
            usuario_id = usuario_existente[0]
        else:
            # Crear usuario
            password_hash = hash_password("Empleado123")
            cursor.execute("""
                INSERT INTO usuarios (nombre, email, password, activo)
                VALUES (?, ?, ?, 1)
            """, (f"{nombre} {apellido}", email, password_hash))
            usuario_id = cursor.lastrowid
            creados += 1
        
        # Vincular empleado con usuario
        cursor.execute("UPDATE empleados SET usuario_id = ? WHERE id = ?", (usuario_id, emp_id))
        
    except Exception as e:
        print(f"ERROR con {nombre} {apellido}: {e}")

conn.commit()
print(f"{creados} usuarios creados")

# Asignar roles
print("\nAsignando roles segun puestos...")
cursor.execute("""
    SELECT e.id, e.nombre, e.apellido, e.usuario_id, p.nombre_puesto, p.id_rol
    FROM empleados e
    INNER JOIN Puestos p ON e.puesto = p.id_puesto
    WHERE e.usuario_id IS NOT NULL AND e.activo = 1
""")

empleados_con_puesto = cursor.fetchall()
asignados = 0

for emp_id, nombre, apellido, usuario_id, puesto, rol_id in empleados_con_puesto:
    if not rol_id:
        continue
    
    try:
        # Verificar si ya tiene rol
        cursor.execute("""
            SELECT COUNT(*) FROM Usuarios_Roles
            WHERE usuario_id = ? AND activo = 1
        """, (usuario_id,))
        
        if cursor.fetchone()[0] == 0:
            # Asignar rol
            cursor.execute("""
                INSERT INTO Usuarios_Roles (usuario_id, id_rol, es_principal, activo)
                VALUES (?, ?, 1, 1)
            """, (usuario_id, rol_id))
            
            # Historial
            cursor.execute("""
                INSERT INTO Historial_Roles (usuario_id, id_rol_nuevo, motivo)
                VALUES (?, ?, 'Asignacion automatica')
            """, (usuario_id, rol_id))
            
            asignados += 1
    except Exception as e:
        pass

conn.commit()
print(f"{asignados} roles asignados")

# Actualizar campo 'rol' en usuarios
print("\nActualizando campo 'rol' en usuarios...")
cursor.execute("""
    UPDATE usuarios
    SET rol = (
        SELECT r.nombre
        FROM Roles r
        INNER JOIN Usuarios_Roles ur ON r.id_rol = ur.id_rol
        WHERE ur.usuario_id = usuarios.id AND ur.activo = 1
        LIMIT 1
    )
    WHERE id IN (SELECT usuario_id FROM Usuarios_Roles WHERE activo = 1)
""")
actualizados = cursor.rowcount
conn.commit()

print(f"{actualizados} usuarios actualizados")
print("\n" + "="*70)
print("VINCULACION COMPLETADA")
print("="*70)

conn.close()

print("\nAhora ejecuta: python ver_estado_simple.py")

