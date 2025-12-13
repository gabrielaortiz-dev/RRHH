"""Script para asignar rol de Super Admin a un usuario"""
import sqlite3
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'rrhh.db')

def asignar_super_admin(email_usuario: str = None):
    """Asigna el rol de Super Admin a un usuario"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Si no se proporciona email, listar usuarios para seleccionar
        if not email_usuario:
            print("\n=== USUARIOS DISPONIBLES ===\n")
            usuarios = cursor.execute("SELECT id, nombre, email, rol, activo FROM usuarios ORDER BY id").fetchall()
            
            if not usuarios:
                print("No se encontraron usuarios en la base de datos\n")
                return
            
            for usuario in usuarios:
                estado = 'Activo' if usuario['activo'] else 'Inactivo'
                print(f"ID: {usuario['id']} - {usuario['nombre']} ({usuario['email']}) - Rol: {usuario['rol']} - {estado}")
            
            print("\nPor favor, proporciona el email del usuario al que quieres asignar Super Admin")
            print("Ejemplo: admin@rrhh.com\n")
            return
        
        # Buscar usuario por email
        usuario = cursor.execute(
            "SELECT id, nombre, email, rol FROM usuarios WHERE email = ?",
            (email_usuario,)
        ).fetchone()
        
        if not usuario:
            print(f"\n❌ No se encontró usuario con email: {email_usuario}\n")
            return
        
        # Verificar si ya es Super Admin
        rol_actual = usuario['rol'] or ''
        if 'super admin' in rol_actual.lower() or rol_actual.lower() == 'super admin':
            print(f"\n✅ El usuario {usuario['nombre']} ({usuario['email']}) ya tiene rol de Super Admin\n")
            return
        
        # Actualizar rol a Super Admin
        # Buscar el ID del rol Super Admin en la tabla Roles
        rol_super_admin = cursor.execute(
            "SELECT id_rol FROM Roles WHERE nombre LIKE '%super admin%' OR nombre LIKE '%SUPER ADMIN%' LIMIT 1"
        ).fetchone()
        
        # Actualizar el rol en la tabla usuarios
        cursor.execute(
            "UPDATE usuarios SET rol = ? WHERE email = ?",
            ('SUPER ADMIN', email_usuario)
        )
        conn.commit()
        
        print(f"\n✅ Rol actualizado exitosamente")
        print(f"   Usuario: {usuario['nombre']} ({usuario['email']})")
        print(f"   Rol anterior: {rol_actual}")
        print(f"   Rol nuevo: SUPER ADMIN\n")
        
        # Si existe la tabla Roles y hay un rol Super Admin, también asignarlo en Usuarios_Roles
        if rol_super_admin:
            try:
                # Verificar si ya tiene el rol asignado
                rol_asignado = cursor.execute(
                    "SELECT id_usuario_rol FROM Usuarios_Roles WHERE usuario_id = ? AND id_rol = ?",
                    (usuario['id'], rol_super_admin['id_rol'])
                ).fetchone()
                
                if not rol_asignado:
                    cursor.execute(
                        "INSERT INTO Usuarios_Roles (usuario_id, id_rol, activo) VALUES (?, ?, 1)",
                        (usuario['id'], rol_super_admin['id_rol'])
                    )
                    conn.commit()
                    print(f"✅ Rol también asignado en la tabla Usuarios_Roles\n")
            except Exception as e:
                print(f"⚠️  No se pudo asignar en Usuarios_Roles: {e}\n")
        
        conn.close()
    except Exception as e:
        print(f"\n❌ Error: {e}\n")

if __name__ == "__main__":
    import sys
    email = sys.argv[1] if len(sys.argv) > 1 else None
    asignar_super_admin(email)

