"""
Script para verificar y crear el usuario administrador si no existe
"""
from database import get_db
import bcrypt
import hashlib

def hash_password(password: str) -> str:
    """Hashea una contraseña usando bcrypt"""
    # Asegurar que la contraseña no exceda 72 bytes
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña contra su hash"""
    try:
        # Intentar verificar con bcrypt
        password_bytes = plain_password.encode('utf-8')[:72]
        hash_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)
    except Exception:
        # Fallback para contraseñas antiguas en SHA-256 o texto plano
        if hashed_password == plain_password:
            return True  # Contraseña en texto plano
        sha256_hash = hashlib.sha256(plain_password.encode()).hexdigest()
        return sha256_hash == hashed_password

def verificar_y_crear_admin():
    """Verifica si existe el admin y lo crea si no existe"""
    try:
        db = get_db()
        
        # Verificar si existe el admin
        admin = db.fetch_one(
            "SELECT id, nombre, email, password, rol, activo FROM usuarios WHERE email = ?",
            ('admin@rrhh.com',)
        )
        
        if admin:
            print(f"[INFO] Usuario admin encontrado:")
            print(f"  ID: {admin['id']}")
            print(f"  Nombre: {admin['nombre']}")
            print(f"  Email: {admin['email']}")
            print(f"  Rol: {admin['rol']}")
            print(f"  Activo: {admin['activo']}")
            print(f"  Password hash: {admin['password'][:50]}...")
            
            # Verificar si la contraseña funciona
            test_password = 'admin123'
            current_hash = admin['password']
            
            # Si la contraseña está en texto plano, actualizarla a bcrypt
            if current_hash == test_password or len(current_hash) < 50:
                print(f"\n[ADVERTENCIA] La contraseña está en texto plano o formato antiguo")
                print(f"[INFO] Actualizando contraseña a bcrypt...")
                new_hash = hash_password(test_password)
                db.execute_query(
                    "UPDATE usuarios SET password = ? WHERE email = ?",
                    (new_hash, 'admin@rrhh.com')
                )
                print(f"[OK] Contraseña actualizada correctamente a bcrypt")
            elif verify_password(test_password, current_hash):
                print(f"\n[OK] La contraseña 'admin123' es válida para este usuario")
            else:
                print(f"\n[ADVERTENCIA] La contraseña 'admin123' NO es válida")
                print(f"[INFO] Actualizando contraseña a bcrypt...")
                new_hash = hash_password(test_password)
                db.execute_query(
                    "UPDATE usuarios SET password = ? WHERE email = ?",
                    (new_hash, 'admin@rrhh.com')
                )
                print(f"[OK] Contraseña actualizada correctamente")
        else:
            print("[INFO] Usuario admin NO encontrado. Creándolo...")
            password_hash = hash_password('admin123')
            cursor = db.execute_query(
                "INSERT INTO usuarios (nombre, email, password, rol, activo) VALUES (?, ?, ?, ?, ?)",
                ('Admin Sistema', 'admin@rrhh.com', password_hash, 'administrador', 1)
            )
            print(f"[OK] Usuario admin creado exitosamente con ID: {cursor.lastrowid}")
        
        print("\n" + "=" * 60)
        print("CREDENCIALES DE ACCESO:")
        print("=" * 60)
        print("  Email:    admin@rrhh.com")
        print("  Password: admin123")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Error al verificar/crear admin: {e}\n")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    verificar_y_crear_admin()

