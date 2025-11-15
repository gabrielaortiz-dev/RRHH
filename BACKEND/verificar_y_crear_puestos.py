"""
Script para verificar y crear la tabla Puestos si no existe
"""
import sqlite3
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'rrhh.db')

def verificar_y_crear():
    """Verificar si existe la tabla Puestos y crearla si no existe"""
    print("=" * 70)
    print("VERIFICANDO Y CREANDO TABLA PUESTOS")
    print("=" * 70)
    print()
    
    try:
        conn = sqlite3.connect(DATABASE_PATH, timeout=10.0)
        cursor = conn.cursor()
        
        # Verificar todas las tablas que existen
        print("[INFO] Buscando todas las tablas en la base de datos...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        todas_las_tablas = cursor.fetchall()
        
        print(f"\nTablas encontradas ({len(todas_las_tablas)}):")
        for tabla in todas_las_tablas:
            nombre = tabla[0]
            if nombre != 'sqlite_sequence':  # Omitir tabla del sistema
                print(f"  - {nombre}")
        
        # Buscar específicamente la tabla Puestos (case insensitive)
        print("\n[INFO] Buscando tabla 'Puestos'...")
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND LOWER(name) = 'puestos'
        """)
        resultado = cursor.fetchone()
        
        if resultado:
            print(f"[OK] La tabla '{resultado[0]}' existe")
            
            # Mostrar estructura
            cursor.execute(f"PRAGMA table_info({resultado[0]})")
            columnas = cursor.fetchall()
            print(f"\nEstructura de la tabla '{resultado[0]}' ({len(columnas)} columnas):")
            for col in columnas:
                pk_str = " [PRIMARY KEY]" if col[5] else ""
                not_null_str = " NOT NULL" if col[3] else ""
                default_str = f" DEFAULT {col[4]}" if col[4] else ""
                print(f"  - {col[1]}: {col[2]}{not_null_str}{default_str}{pk_str}")
            
            # Contar registros
            cursor.execute(f"SELECT COUNT(*) FROM {resultado[0]}")
            count = cursor.fetchone()[0]
            print(f"\nRegistros en la tabla: {count}")
            
        else:
            print("[INFO] La tabla 'Puestos' NO existe. Creandola...")
            
            try:
                cursor.execute('''
                    CREATE TABLE Puestos (
                        id_puesto INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre_puesto VARCHAR(100) NOT NULL,
                        nivel VARCHAR(50),
                        salario_base DECIMAL(10,2)
                    )
                ''')
                conn.commit()
                print("[OK] Tabla 'Puestos' creada exitosamente")
                
                # Verificar estructura creada
                cursor.execute("PRAGMA table_info(Puestos)")
                columnas = cursor.fetchall()
                print(f"\nEstructura creada ({len(columnas)} columnas):")
                for col in columnas:
                    pk_str = " [PRIMARY KEY]" if col[5] else ""
                    not_null_str = " NOT NULL" if col[3] else ""
                    print(f"  - {col[1]}: {col[2]}{not_null_str}{pk_str}")
                
            except sqlite3.OperationalError as e:
                if "locked" in str(e).lower():
                    print("\n[ERROR] La base de datos esta bloqueada")
                    print("\nINSTRUCCIONES:")
                    print("1. Cierra DB Browser for SQLite completamente")
                    print("2. Deten el servidor FastAPI si esta corriendo")
                    print("3. Ejecuta este script nuevamente")
                    print("\nO ejecuta este SQL directamente en DB Browser:")
                    print("-" * 70)
                    print("CREATE TABLE Puestos (")
                    print("    id_puesto INTEGER PRIMARY KEY AUTOINCREMENT,")
                    print("    nombre_puesto VARCHAR(100) NOT NULL,")
                    print("    nivel VARCHAR(50),")
                    print("    salario_base DECIMAL(10,2)")
                    print(");")
                    print("-" * 70)
                else:
                    print(f"[ERROR] Error al crear la tabla: {e}")
        
        # Verificar también Departamentos
        print("\n" + "=" * 70)
        print("[INFO] Verificando tabla 'Departamentos'...")
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND LOWER(name) = 'departamentos'
        """)
        dept_result = cursor.fetchone()
        
        if dept_result:
            print(f"[OK] La tabla '{dept_result[0]}' existe")
        else:
            print("[INFO] La tabla 'Departamentos' NO existe")
        
        conn.close()
        print("\n" + "=" * 70)
        print("[OK] Verificacion completada")
        print("=" * 70)
        print("\nNOTA: Si la tabla existe pero no la ves en DB Browser:")
        print("1. Cierra y vuelve a abrir DB Browser")
        print("2. O haz click derecho en 'Database Structure' y selecciona 'Refresh'")
        print("3. O presiona F5 para refrescar")
        
        return True
        
    except sqlite3.OperationalError as e:
        if "locked" in str(e).lower():
            print("\n[ERROR] La base de datos esta bloqueada")
            print("Cierra DB Browser y cualquier otra aplicacion usando la base de datos")
        else:
            print(f"[ERROR] Error de SQLite: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Error inesperado: {e}")
        return False

if __name__ == "__main__":
    verificar_y_crear()

