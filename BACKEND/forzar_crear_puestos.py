"""
Script para FORZAR la creacion de la tabla Puestos
Cierra DB Browser antes de ejecutar este script
"""
import sqlite3
import os
import sys

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'rrhh.db')

print("=" * 70)
print("FORZANDO CREACION DE TABLA PUESTOS")
print("=" * 70)
print()

# Verificar si DB Browser podría estar abierto
try:
    conn = sqlite3.connect(DATABASE_PATH, timeout=1.0)
    conn.close()
    print("[OK] Base de datos disponible")
except sqlite3.OperationalError as e:
    if "locked" in str(e).lower():
        print("[ERROR] La base de datos esta BLOQUEADA")
        print("\nPor favor CIERRA DB Browser for SQLite completamente")
        print("Luego ejecuta este script nuevamente")
        sys.exit(1)

try:
    conn = sqlite3.connect(DATABASE_PATH, timeout=5.0)
    cursor = conn.cursor()
    
    # Verificar si existe
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Puestos'")
    existe = cursor.fetchone()
    
    if existe:
        print("[INFO] La tabla Puestos ya existe")
    else:
        print("[INFO] Creando tabla Puestos...")
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
    
    # Verificar estructura
    cursor.execute("PRAGMA table_info(Puestos)")
    columnas = cursor.fetchall()
    print(f"\nEstructura de la tabla ({len(columnas)} columnas):")
    for col in columnas:
        pk_str = " [PRIMARY KEY]" if col[5] else ""
        not_null_str = " NOT NULL" if col[3] else ""
        print(f"  - {col[1]}: {col[2]}{not_null_str}{pk_str}")
    
    # Listar TODAS las tablas
    print("\n" + "=" * 70)
    print("TODAS LAS TABLAS EN LA BASE DE DATOS:")
    print("=" * 70)
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tablas = cursor.fetchall()
    for tabla in tablas:
        if tabla[0] != 'sqlite_sequence':
            marca = " <-- NUEVA!" if tabla[0] == 'Puestos' else ""
            print(f"  ✓ {tabla[0]}{marca}")
    
    conn.close()
    
    print("\n" + "=" * 70)
    print("[OK] Proceso completado!")
    print("=" * 70)
    print("\nAhora:")
    print("1. Abre DB Browser for SQLite")
    print("2. Abre la base de datos rrhh.db")
    print("3. Ve a la pestaña 'Database Structure'")
    print("4. Haz click en el boton 'Refresh' (o presiona F5)")
    print("5. Deberias ver la tabla 'Puestos' en la lista")
    
except sqlite3.Error as e:
    print(f"[ERROR] Error de SQLite: {e}")
except Exception as e:
    print(f"[ERROR] Error: {e}")

