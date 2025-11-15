"""
Script para crear las tablas Departamentos y Puestos en la base de datos existente
"""
import sqlite3
import os
from database import Database

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'rrhh.db')

def crear_tablas_nuevas():
    """Crear las tablas Departamentos y Puestos"""
    print("=" * 70)
    print("CREANDO TABLAS: Departamentos y Puestos")
    print("=" * 70)
    print()
    
    try:
        db = Database()
        db.connect()
        
        # Verificar si las tablas ya existen
        tablas_existentes = db.fetch_all(
            "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('Departamentos', 'Puestos')"
        )
        
        nombres_existentes = [t['name'] for t in tablas_existentes]
        
        # Crear tabla Departamentos si no existe
        print("[INFO] Creando tabla Departamentos...")
        try:
            db.execute_query('''
                CREATE TABLE IF NOT EXISTS Departamentos (
                    id_departamento INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre_departamento VARCHAR(100) NOT NULL,
                    descripcion TEXT
                )
            ''')
            print("[OK] Tabla Departamentos creada/verificada exitosamente")
        except Exception as e:
            print(f"[ADVERTENCIA] Error al crear Departamentos: {e}")
        
        print()
        
        # Crear tabla Puestos si no existe
        print("[INFO] Creando tabla Puestos...")
        try:
            db.execute_query('''
                CREATE TABLE IF NOT EXISTS Puestos (
                    id_puesto INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre_puesto VARCHAR(100) NOT NULL,
                    nivel VARCHAR(50),
                    salario_base DECIMAL(10,2)
                )
            ''')
            print("[OK] Tabla Puestos creada/verificada exitosamente")
        except Exception as e:
            print(f"[ADVERTENCIA] Error al crear Puestos: {e}")
        
        print()
        
        # Verificar que se crearon correctamente
        print("[INFO] Verificando tablas creadas...")
        tablas = db.fetch_all(
            "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('Departamentos', 'Puestos')"
        )
        
        for tabla in tablas:
            nombre = tabla['name']
            # Obtener estructura
            columnas = db.fetch_all(f"PRAGMA table_info({nombre})")
            print(f"\n[TABLA] {nombre}")
            print(f"   Columnas ({len(columnas)}):")
            for col in columnas:
                pk_str = " [PRIMARY KEY]" if col['pk'] else ""
                not_null_str = " NOT NULL" if col['notnull'] else ""
                print(f"      - {col['name']}: {col['type']}{not_null_str}{pk_str}")
        
        print()
        print("=" * 70)
        print("[OK] Proceso completado exitosamente")
        print("=" * 70)
        
        db.disconnect()
        return True
        
    except sqlite3.Error as e:
        print(f"[ERROR] Error de SQLite: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Error inesperado: {e}")
        return False

if __name__ == "__main__":
    crear_tablas_nuevas()

