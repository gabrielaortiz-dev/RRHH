"""Script para activar y asignar rol de Super Admin a usuarios admin"""
import sqlite3
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'rrhh.db')

def activar_y_asignar_super_admin():
    """Activa y asigna rol de Super Admin a todos los usuarios admin"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Buscar todos los usuarios admin
        usuarios_admin = cursor.execute(
            """SELECT id, nombre, email, rol, activo 
               FROM usuarios 
               WHERE email LIKE '%admin%' 
               OR nombre LIKE '%Admin%' 
               OR rol LIKE '%admin%' 
               ORDER BY id"""
        ).fetchall()
        
        if not usuarios_admin:
            print("\n[ERROR] No se encontraron usuarios admin\n")
            return
        
        print("\n=== ASIGNANDO SUPER ADMIN A USUARIOS ADMIN ===\n")
        
        for usuario in usuarios_admin:
            # Actualizar rol a SUPER ADMIN y activar
            cursor.execute(
                "UPDATE usuarios SET rol = 'SUPER ADMIN', activo = 1 WHERE id = ?",
                (usuario['id'],)
            )
            
            print(f"[OK] Usuario actualizado:")
            print(f"   ID: {usuario['id']}")
            print(f"   Nombre: {usuario['nombre']}")
            print(f"   Email: {usuario['email']}")
            print(f"   Rol anterior: {usuario['rol']}")
            print(f"   Rol nuevo: SUPER ADMIN")
            print(f"   Estado: Activo\n")
        
        conn.commit()
        
        # También asignar en la tabla Usuarios_Roles si existe
        try:
            rol_super_admin = cursor.execute(
                "SELECT id_rol FROM Roles WHERE nombre LIKE '%super admin%' OR nombre LIKE '%SUPER ADMIN%' LIMIT 1"
            ).fetchone()
            
            if rol_super_admin:
                for usuario in usuarios_admin:
                    # Verificar si ya tiene el rol asignado
                    rol_asignado = cursor.execute(
                        "SELECT id_usuario_rol FROM Usuarios_Roles WHERE usuario_id = ? AND id_rol = ?",
                        (usuario['id'], rol_super_admin['id_rol'])
                    ).fetchone()
                    
                    if not rol_asignado:
                        cursor.execute(
                            "INSERT OR REPLACE INTO Usuarios_Roles (usuario_id, id_rol, activo) VALUES (?, ?, 1)",
                            (usuario['id'], rol_super_admin['id_rol'])
                        )
                        print(f"[OK] Rol tambien asignado en Usuarios_Roles para {usuario['email']}\n")
                conn.commit()
        except Exception as e:
            print(f"[ADVERTENCIA] No se pudo asignar en Usuarios_Roles: {e}\n")
        
        print("[OK] Proceso completado exitosamente\n")
        conn.close()
    except Exception as e:
        print(f"\n[ERROR] Error: {e}\n")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    activar_y_asignar_super_admin()

