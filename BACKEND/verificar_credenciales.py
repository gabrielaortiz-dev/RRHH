"""Script para verificar las credenciales del usuario admin"""
import sqlite3
import os
import sys

# Configurar encoding UTF-8 para Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'rrhh.db')

def verificar_credenciales():
    """Verifica las credenciales del usuario admin"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Buscar usuario admin
        usuario = cursor.execute(
            "SELECT id, nombre, email, rol, activo FROM usuarios WHERE email = ?",
            ('admin@rrhh.com',)
        ).fetchone()
        
        if usuario:
            print("\n" + "="*60)
            print("CREDENCIALES DEL USUARIO ADMIN")
            print("="*60)
            print(f"Email: {usuario['email']}")
            print(f"Contraseña: admin123")
            print(f"Rol: {usuario['rol']}")
            print(f"Estado: {'Activo' if usuario['activo'] == 1 else 'Inactivo'}")
            print("="*60 + "\n")
        else:
            print("\n[ERROR] Usuario admin@rrhh.com no encontrado\n")
        
        conn.close()
    except Exception as e:
        print(f"\n[ERROR] Error: {e}\n")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verificar_credenciales()

