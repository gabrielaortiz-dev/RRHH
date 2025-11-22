"""Script para verificar y corregir la base de datos"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'rrhh.db')

def verificar_db():
    """Verificar y corregir la base de datos"""
    print("=" * 60)
    print("VERIFICANDO BASE DE DATOS")
    print("=" * 60)
    
    if not os.path.exists(DB_PATH):
        print(f"[ERROR] La base de datos no existe en: {DB_PATH}")
        print("[INFO] Ejecutando init_db() para crearla...")
        from database import init_db
        init_db()
        print("[OK] Base de datos creada")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Verificar tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tablas = [row[0] for row in cursor.fetchall()]
        print(f"\n[INFO] Tablas encontradas: {len(tablas)}")
        for tabla in tablas:
            print(f"  - {tabla}")
        
        # Verificar si existe la tabla usuarios
        if 'usuarios' not in tablas:
            print("\n[ERROR] La tabla 'usuarios' no existe!")
            print("[INFO] Creando tablas...")
            from database import init_db
            init_db()
            print("[OK] Tablas creadas")
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tablas = [row[0] for row in cursor.fetchall()]
        
        # Verificar usuarios
        cursor.execute("SELECT email, password, rol, activo FROM usuarios")
        usuarios = cursor.fetchall()
        
        print(f"\n[INFO] Usuarios encontrados: {len(usuarios)}")
        if usuarios:
            for usuario in usuarios:
                print(f"  - Email: {usuario['email']}, Rol: {usuario['rol']}, Activo: {usuario['activo']}")
        
        # Si no hay usuarios, crear el usuario admin
        if not usuarios or not any(u['email'] == 'admin@rrhh.com' for u in usuarios):
            print("\n[INFO] No se encontró el usuario admin, creándolo...")
            cursor.execute(
                "INSERT OR REPLACE INTO usuarios (nombre, email, password, rol, activo) VALUES (?, ?, ?, ?, ?)",
                ('Admin Sistema', 'admin@rrhh.com', 'admin123', 'administrador', 1)
            )
            conn.commit()
            print("[OK] Usuario admin creado")
            print("  - Email: admin@rrhh.com")
            print("  - Password: admin123")
            print("  - Rol: administrador")
        
        # Verificar usuario admin específicamente
        cursor.execute(
            "SELECT email, password, rol, activo FROM usuarios WHERE email = ?",
            ('admin@rrhh.com',)
        )
        admin = cursor.fetchone()
        
        if admin:
            print("\n" + "=" * 60)
            print("[OK] USUARIO ADMIN VERIFICADO")
            print("=" * 60)
            print(f"Email: {admin['email']}")
            print(f"Password: {admin['password']}")
            print(f"Rol: {admin['rol']}")
            print(f"Activo: {admin['activo']}")
        else:
            print("\n[ERROR] No se pudo verificar el usuario admin")
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("[OK] VERIFICACIÓN COMPLETADA")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n[ERROR] Error al verificar base de datos: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verificar_db()

