"""
Script para ver las credenciales de usuarios disponibles
"""
from database import get_db

def ver_credenciales():
    """Muestra las credenciales de usuarios disponibles"""
    print("=" * 70)
    print("CREDENCIALES DE USUARIOS DISPONIBLES")
    print("=" * 70)
    print()
    
    try:
        db = get_db()
        
        # Buscar usuarios SUPER ADMIN
        print("USUARIOS SUPER ADMIN (con acceso total):")
        print("-" * 70)
        super_admins = db.fetch_all(
            """SELECT id, nombre, email, rol, activo 
               FROM usuarios 
               WHERE activo = 1 
               AND (UPPER(rol) LIKE '%SUPER ADMIN%' OR UPPER(rol) LIKE '%ADMIN%')
               ORDER BY id
               LIMIT 10"""
        )
        
        if super_admins:
            # Contraseñas comunes a probar
            passwords_comunes = ["admin123", "admin", "pass123", "password", "123456"]
            
            for u in super_admins:
                print(f"Email: {u['email']}")
                print(f"  Nombre: {u['nombre']}")
                print(f"  Rol: {u['rol']}")
                print(f"  Contraseñas a probar: {', '.join(passwords_comunes)}")
                print()
        else:
            print("No se encontraron usuarios SUPER ADMIN")
            print()
        
        # Verificar si hay algún usuario con contraseña conocida
        print("=" * 70)
        print("RECOMENDACION:")
        print("=" * 70)
        print()
        print("USUARIO RECOMENDADO (ya configurado):")
        print("  Email: admin@rrhh.com")
        print("  Password: admin123")
        print()
        print("Este usuario:")
        print("  ✓ Tiene rol SUPER ADMIN")
        print("  ✓ Está en la lista de acceso total")
        print("  ✓ Tiene acceso completo sin restricciones")
        print()
        
        # Verificar admin@rrhh.com específicamente
        admin = db.fetch_one(
            "SELECT id, nombre, email, rol, activo FROM usuarios WHERE email = ?",
            ("admin@rrhh.com",)
        )
        
        if admin:
            if admin['activo'] == 1:
                print("[OK] El usuario admin@rrhh.com existe y está ACTIVO")
            else:
                print("[ADVERTENCIA] El usuario admin@rrhh.com existe pero está INACTIVO")
        else:
            print("[ADVERTENCIA] El usuario admin@rrhh.com NO existe")
        
        print()
        
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            db.disconnect()
        except:
            pass

if __name__ == "__main__":
    ver_credenciales()

