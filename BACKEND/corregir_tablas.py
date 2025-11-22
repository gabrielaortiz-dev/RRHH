"""Script para asegurar que todas las tablas necesarias estén creadas"""
from database import init_db, get_db

def corregir_tablas():
    """Crear todas las tablas necesarias"""
    print("=" * 60)
    print("CORRIGIENDO TABLAS DE BASE DE DATOS")
    print("=" * 60)
    
    try:
        # Inicializar base de datos (crea todas las tablas)
        db = init_db()
        print("[OK] Todas las tablas creadas/verificadas")
        
        # Verificar que las tablas críticas existan
        import sqlite3
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tablas = [row[0] for row in cursor.fetchall()]
        
        tablas_necesarias = [
            'usuarios',
            'Login_Intentos',
            'Usuarios_Auditoria',
            'departamentos',
            'empleados'
        ]
        
        print("\n[INFO] Verificando tablas necesarias:")
        for tabla in tablas_necesarias:
            if tabla in tablas:
                print(f"  ✓ {tabla} - OK")
            else:
                print(f"  ✗ {tabla} - FALTANTE")
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("[OK] CORRECCIÓN COMPLETADA")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n[ERROR] Error al corregir tablas: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    corregir_tablas()

