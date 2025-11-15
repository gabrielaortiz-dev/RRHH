"""
Script directo para crear la tabla Puestos
"""
import sqlite3
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'rrhh.db')

def crear_tabla_puestos():
    """Crear la tabla Puestos directamente"""
    print("=" * 70)
    print("CREANDO TABLA: Puestos")
    print("=" * 70)
    print()
    
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Verificar si la tabla ya existe
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='Puestos'
        """)
        existe = cursor.fetchone()
        
        if existe:
            print("[INFO] La tabla Puestos ya existe")
            # Mostrar estructura actual
            cursor.execute("PRAGMA table_info(Puestos)")
            columnas = cursor.fetchall()
            print(f"\nEstructura actual ({len(columnas)} columnas):")
            for col in columnas:
                print(f"  - {col[1]}: {col[2]}")
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
        
        # Listar todas las tablas para verificar
        print("\n" + "=" * 70)
        print("TODAS LAS TABLAS EN LA BASE DE DATOS:")
        print("=" * 70)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tablas = cursor.fetchall()
        for tabla in tablas:
            print(f"  - {tabla[0]}")
        
        conn.close()
        print("\n[OK] Proceso completado")
        return True
        
    except sqlite3.Error as e:
        print(f"[ERROR] Error de SQLite: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Error inesperado: {e}")
        return False

if __name__ == "__main__":
    crear_tabla_puestos()

