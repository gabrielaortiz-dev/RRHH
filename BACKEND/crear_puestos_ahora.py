"""
Script simple para crear la tabla Puestos
Ejecuta este script DESPUES de cerrar DB Browser
"""
import sqlite3
import os
import time

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'rrhh.db')

print("=" * 70)
print("CREANDO TABLA PUESTOS")
print("=" * 70)
print()
print("Esperando a que la base de datos este disponible...")
print()

intentos = 0
max_intentos = 10

while intentos < max_intentos:
    try:
        conn = sqlite3.connect(DATABASE_PATH, timeout=2.0)
        cursor = conn.cursor()
        
        # Verificar si ya existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Puestos'")
        if cursor.fetchone():
            print("[OK] La tabla Puestos ya existe!")
        else:
            # Crear la tabla
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
            print("[OK] Tabla Puestos creada exitosamente!")
        
        # Verificar estructura
        cursor.execute("PRAGMA table_info(Puestos)")
        columnas = cursor.fetchall()
        print(f"\nEstructura de la tabla ({len(columnas)} columnas):")
        for col in columnas:
            pk_str = " [PRIMARY KEY]" if col[5] else ""
            not_null_str = " NOT NULL" if col[3] else ""
            print(f"  - {col[1]}: {col[2]}{not_null_str}{pk_str}")
        
        # Listar todas las tablas
        print("\n" + "=" * 70)
        print("TODAS LAS TABLAS EN LA BASE DE DATOS:")
        print("=" * 70)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tablas = cursor.fetchall()
        for tabla in tablas:
            if tabla[0] != 'sqlite_sequence':
                print(f"  ✓ {tabla[0]}")
        
        conn.close()
        print("\n[OK] Proceso completado!")
        print("\nAhora puedes:")
        print("1. Abrir DB Browser for SQLite")
        print("2. Abrir la base de datos rrhh.db")
        print("3. Refrescar la vista (F5 o click derecho > Refresh)")
        print("4. Deberias ver la tabla 'Puestos' en la lista")
        break
        
    except sqlite3.OperationalError as e:
        if "locked" in str(e).lower():
            intentos += 1
            if intentos < max_intentos:
                print(f"[INFO] Base de datos bloqueada. Intento {intentos}/{max_intentos}... Esperando 2 segundos...")
                time.sleep(2)
            else:
                print("\n[ERROR] La base de datos sigue bloqueada despues de", max_intentos, "intentos")
                print("\nPor favor:")
                print("1. Cierra DB Browser for SQLite completamente")
                print("2. Deten el servidor FastAPI si esta corriendo")
                print("3. Ejecuta este script nuevamente")
                break
        else:
            print(f"[ERROR] Error: {e}")
            break
    except Exception as e:
        print(f"[ERROR] Error inesperado: {e}")
        break

