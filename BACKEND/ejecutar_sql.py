"""
Script para ejecutar el archivo crear_tablas.sql
"""
import sqlite3
import os
import time

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'rrhh.db')
SQL_FILE = os.path.join(os.path.dirname(__file__), 'crear_tablas.sql')

def ejecutar_sql():
    """Ejecutar el script SQL para crear las tablas"""
    print("=" * 70)
    print("EJECUTANDO SCRIPT SQL PARA CREAR TABLAS")
    print("=" * 70)
    print()
    
    # Leer el archivo SQL
    try:
        with open(SQL_FILE, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        print(f"[OK] Archivo SQL leido: {SQL_FILE}")
    except Exception as e:
        print(f"[ERROR] No se pudo leer el archivo SQL: {e}")
        return False
    
    # Intentar ejecutar el SQL
    max_intentos = 5
    for intento in range(1, max_intentos + 1):
        try:
            print(f"\n[INFO] Intento {intento} de {max_intentos}...")
            conn = sqlite3.connect(DATABASE_PATH, timeout=5.0)
            cursor = conn.cursor()
            
            # Ejecutar comandos SQL directamente
            print("[INFO] Creando tabla Departamentos...")
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Departamentos (
                    id_departamento INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre_departamento VARCHAR(100) NOT NULL,
                    descripcion TEXT
                )
            ''')
            print("[OK] Tabla Departamentos creada/verificada")
            
            print("[INFO] Creando tabla Puestos...")
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Puestos (
                    id_puesto INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre_puesto VARCHAR(100) NOT NULL,
                    nivel VARCHAR(50),
                    salario_base DECIMAL(10,2)
                )
            ''')
            print("[OK] Tabla Puestos creada/verificada")
            
            conn.commit()
            
            # Verificar que las tablas existen
            print("\n[INFO] Verificando tablas creadas...")
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('Departamentos', 'Puestos')")
            tablas = cursor.fetchall()
            
            print(f"\n[OK] Tablas encontradas: {len(tablas)}")
            for tabla in tablas:
                print(f"  - {tabla[0]}")
                
                # Mostrar estructura
                cursor.execute(f"PRAGMA table_info({tabla[0]})")
                columnas = cursor.fetchall()
                print(f"    Columnas ({len(columnas)}):")
                for col in columnas:
                    pk_str = " [PK]" if col[5] else ""
                    not_null_str = " NOT NULL" if col[3] else ""
                    print(f"      * {col[1]}: {col[2]}{not_null_str}{pk_str}")
            
            conn.close()
            print("\n" + "=" * 70)
            print("[OK] Proceso completado exitosamente")
            print("=" * 70)
            return True
            
        except sqlite3.OperationalError as e:
            if "locked" in str(e).lower():
                if intento < max_intentos:
                    wait_time = 2 * intento
                    print(f"[ADVERTENCIA] Base de datos bloqueada. Esperando {wait_time} segundos...")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"\n[ERROR] La base de datos esta bloqueada despues de {max_intentos} intentos.")
                    print("\nINSTRUCCIONES:")
                    print("1. Cierra DB Browser for SQLite completamente")
                    print("2. Deten el servidor FastAPI si esta corriendo")
                    print("3. Cierra cualquier otra aplicacion usando la base de datos")
                    print("4. Ejecuta este script nuevamente")
                    print("\nO ejecuta manualmente el archivo crear_tablas.sql en DB Browser")
                    return False
            else:
                print(f"[ERROR] Error de SQLite: {e}")
                return False
        except Exception as e:
            print(f"[ERROR] Error inesperado: {e}")
            return False
    
    return False

if __name__ == "__main__":
    ejecutar_sql()

