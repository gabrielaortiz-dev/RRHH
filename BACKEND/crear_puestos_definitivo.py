"""
Script DEFINITIVO para crear la tabla Puestos
CIERRA DB Browser antes de ejecutar este script
"""
import sqlite3
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'rrhh.db')

print("=" * 70)
print("CREANDO TABLA PUESTOS - SCRIPT DEFINITIVO")
print("=" * 70)
print()

try:
    print("[INFO] Conectando a la base de datos...")
    conn = sqlite3.connect(DATABASE_PATH, timeout=10.0)
    cursor = conn.cursor()
    print("[OK] Conexion establecida")
    
    # Verificar si existe
    print("\n[INFO] Verificando si la tabla existe...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Puestos'")
    existe = cursor.fetchone()
    
    if existe:
        print("[INFO] La tabla Puestos ya existe")
    else:
        print("[INFO] La tabla NO existe. Creandola...")
        cursor.execute('''
            CREATE TABLE Puestos (
                id_puesto INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_puesto VARCHAR(100) NOT NULL,
                nivel VARCHAR(50),
                salario_base DECIMAL(10,2)
            )
        ''')
        conn.commit()
        print("[OK] Tabla Puestos CREADA exitosamente!")
    
    # Verificar que se creo
    print("\n[INFO] Verificando creacion...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Puestos'")
    verificacion = cursor.fetchone()
    
    if verificacion:
        print(f"[OK] CONFIRMADO: La tabla '{verificacion[0]}' existe en la base de datos")
        
        # Mostrar estructura
        cursor.execute("PRAGMA table_info(Puestos)")
        columnas = cursor.fetchall()
        print(f"\nEstructura de la tabla ({len(columnas)} columnas):")
        for col in columnas:
            pk_str = " [PRIMARY KEY]" if col[5] else ""
            not_null_str = " NOT NULL" if col[3] else ""
            print(f"  - {col[1]}: {col[2]}{not_null_str}{pk_str}")
    else:
        print("[ERROR] La tabla no se pudo crear")
    
    # Listar TODAS las tablas
    print("\n" + "=" * 70)
    print("TODAS LAS TABLAS EN LA BASE DE DATOS:")
    print("=" * 70)
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tablas = cursor.fetchall()
    for tabla in tablas:
        if tabla[0] != 'sqlite_sequence':
            if tabla[0] == 'Puestos':
                print(f"  [OK] {tabla[0]} <-- NUEVA TABLA CREADA!")
            else:
                print(f"  - {tabla[0]}")
    
    conn.close()
    
    print("\n" + "=" * 70)
    print("[OK] PROCESO COMPLETADO")
    print("=" * 70)
    print("\nAHORA:")
    print("1. Abre DB Browser for SQLite")
    print("2. Abre la base de datos: rrhh.db")
    print("3. Ve a la pestaña 'Database Structure'")
    print("4. Haz click en el boton 'Refresh' (o presiona F5)")
    print("5. Deberias ver la tabla 'Puestos' en la lista de tablas")
    
except sqlite3.OperationalError as e:
    if "locked" in str(e).lower():
        print("\n[ERROR] La base de datos esta BLOQUEADA")
        print("\nINSTRUCCIONES:")
        print("1. CIERRA DB Browser for SQLite COMPLETAMENTE")
        print("2. Deten el servidor FastAPI si esta corriendo")
        print("3. Ejecuta este script nuevamente: python crear_puestos_definitivo.py")
    else:
        print(f"\n[ERROR] Error de SQLite: {e}")
except Exception as e:
    print(f"\n[ERROR] Error: {e}")

