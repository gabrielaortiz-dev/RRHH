"""Script simple para crear la tabla Puestos"""
import sqlite3
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'rrhh.db')

try:
    print("Conectando a la base de datos...")
    conn = sqlite3.connect(DATABASE_PATH, timeout=10.0)
    cursor = conn.cursor()
    
    print("Creando tabla Puestos...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Puestos (
            id_puesto INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_puesto VARCHAR(100) NOT NULL,
            nivel VARCHAR(50),
            salario_base DECIMAL(10,2)
        )
    ''')
    conn.commit()
    
    # Verificar que se creó
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Puestos'")
    result = cursor.fetchone()
    
    if result:
        print("[OK] Tabla Puestos creada exitosamente")
        
        # Mostrar estructura
        cursor.execute("PRAGMA table_info(Puestos)")
        columnas = cursor.fetchall()
        print(f"\nEstructura de la tabla ({len(columnas)} columnas):")
        for col in columnas:
            pk_str = " [PRIMARY KEY]" if col[5] else ""
            not_null_str = " NOT NULL" if col[3] else ""
            print(f"  - {col[1]}: {col[2]}{not_null_str}{pk_str}")
    else:
        print("[ERROR] No se pudo crear la tabla")
    
    conn.close()
    print("\n[OK] Proceso completado")
    
except sqlite3.OperationalError as e:
    if "locked" in str(e).lower():
        print("[ERROR] La base de datos esta bloqueada")
        print("\nPor favor cierra:")
        print("  - DB Browser for SQLite")
        print("  - El servidor FastAPI (si esta corriendo)")
        print("  - Cualquier otra aplicacion usando la base de datos")
        print("\nLuego ejecuta este script nuevamente o usa el archivo crear_tablas.sql en DB Browser")
    else:
        print(f"[ERROR] Error de SQLite: {e}")
except Exception as e:
    print(f"[ERROR] Error: {e}")

