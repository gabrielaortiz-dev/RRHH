"""
Script para crear la tabla Puestos con reintentos
"""
import sqlite3
import os
import time

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'rrhh.db')

def crear_tabla_puestos():
    """Crear la tabla Puestos con reintentos"""
    print("=" * 70)
    print("CREANDO TABLA: Puestos")
    print("=" * 70)
    print()
    print("[INFO] IMPORTANTE: Cierra DB Browser for SQLite y cualquier")
    print("       servidor FastAPI que esté corriendo antes de continuar.")
    print()
    
    max_intentos = 3
    for intento in range(1, max_intentos + 1):
        try:
            print(f"[INFO] Intento {intento} de {max_intentos}...")
            conn = sqlite3.connect(DATABASE_PATH, timeout=5.0)
            cursor = conn.cursor()
            
            # Verificar si la tabla ya existe
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='Puestos'
            """)
            existe = cursor.fetchone()
            
            if existe:
                print("[OK] La tabla Puestos ya existe")
                # Mostrar estructura
                cursor.execute("PRAGMA table_info(Puestos)")
                columnas = cursor.fetchall()
                print(f"\nEstructura ({len(columnas)} columnas):")
                for col in columnas:
                    pk_str = " [PRIMARY KEY]" if col[5] else ""
                    not_null_str = " NOT NULL" if col[3] else ""
                    print(f"  - {col[1]}: {col[2]}{not_null_str}{pk_str}")
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
                print("[OK] Tabla Puestos creada exitosamente")
                
                # Verificar estructura
                cursor.execute("PRAGMA table_info(Puestos)")
                columnas = cursor.fetchall()
                print(f"\nEstructura creada ({len(columnas)} columnas):")
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
                if tabla[0] != 'sqlite_sequence':  # Omitir tabla del sistema
                    print(f"  ✓ {tabla[0]}")
            
            conn.close()
            print("\n[OK] Proceso completado exitosamente")
            return True
            
        except sqlite3.OperationalError as e:
            if "locked" in str(e).lower():
                if intento < max_intentos:
                    print(f"[ADVERTENCIA] Base de datos bloqueada. Esperando 2 segundos...")
                    time.sleep(2)
                    continue
                else:
                    print(f"\n[ERROR] La base de datos está bloqueada después de {max_intentos} intentos.")
                    print("\nPor favor:")
                    print("1. Cierra DB Browser for SQLite si lo tienes abierto")
                    print("2. Detén el servidor FastAPI si está corriendo")
                    print("3. Cierra cualquier otra aplicación que use la base de datos")
                    print("4. Ejecuta este script nuevamente")
                    return False
            else:
                print(f"[ERROR] Error de SQLite: {e}")
                return False
        except Exception as e:
            print(f"[ERROR] Error inesperado: {e}")
            return False
    
    return False

if __name__ == "__main__":
    crear_tabla_puestos()

