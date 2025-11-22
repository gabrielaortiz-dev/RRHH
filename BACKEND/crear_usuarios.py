"""
Script para crear usuarios de ejemplo en la base de datos
Ejecuta este script si no puedes iniciar sesión
"""
from database import get_db

def crear_usuarios():
    """Crear usuarios de ejemplo si no existen"""
    print("=" * 60)
    print("CREANDO USUARIOS DE EJEMPLO")
    print("=" * 60)
    
    try:
        db = get_db()
        
        # Verificar si ya existen usuarios
        usuarios_existentes = db.fetch_all("SELECT email FROM usuarios WHERE activo = 1")
        if usuarios_existentes:
            print(f"\n[INFO] Ya existen {len(usuarios_existentes)} usuarios activos en la base de datos:")
            for u in usuarios_existentes:
                print(f"       - {u['email']}")
            print("\n[INFO] Si no puedes iniciar sesión, verifica las credenciales.")
            return True
        
        # Crear usuarios de ejemplo
        print("\n[INFO] No hay usuarios activos. Creando usuarios de ejemplo...")
        usuarios_ejemplo = [
            ('Admin Sistema', 'admin@rrhh.com', 'admin123', 'administrador'),
            ('Juan Perez', 'juan.perez@rrhh.com', 'pass123', 'empleado'),
            ('Maria Garcia', 'maria.garcia@rrhh.com', 'pass123', 'supervisor'),
        ]
        
        usuarios_creados = 0
        for usuario in usuarios_ejemplo:
            nombre, email, password, rol = usuario
            # Verificar si el usuario ya existe (aunque esté desactivado)
            existente = db.fetch_one("SELECT id, activo FROM usuarios WHERE email = ?", (email,))
            
            if existente:
                # Si existe pero está desactivado, activarlo y actualizar datos
                if existente['activo'] == 0:
                    db.execute_query(
                        "UPDATE usuarios SET nombre = ?, password = ?, rol = ?, activo = 1 WHERE email = ?",
                        (nombre, password, rol, email)
                    )
                    print(f"[OK] Usuario {email} reactivado y actualizado")
                    usuarios_creados += 1
                else:
                    print(f"[INFO] Usuario {email} ya existe y está activo")
            else:
                # Crear nuevo usuario
                db.execute_query(
                    "INSERT INTO usuarios (nombre, email, password, rol) VALUES (?, ?, ?, ?)",
                    usuario
                )
                print(f"[OK] Usuario {email} creado")
                usuarios_creados += 1
        
        print(f"\n[OK] {usuarios_creados} usuarios procesados correctamente")
        print("\n" + "=" * 60)
        print("CREDENCIALES DISPONIBLES:")
        print("=" * 60)
        print("\nUSUARIO ADMINISTRADOR:")
        print("  Email:    admin@rrhh.com")
        print("  Password: admin123")
        print("\nUSUARIO EMPLEADO:")
        print("  Email:    juan.perez@rrhh.com")
        print("  Password: pass123")
        print("\nUSUARIO SUPERVISOR:")
        print("  Email:    maria.garcia@rrhh.com")
        print("  Password: pass123")
        print("\n" + "=" * 60)
        print("\n")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Error al crear usuarios: {e}\n")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    crear_usuarios()

