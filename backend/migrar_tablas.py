"""
Script para migrar y crear las nuevas tablas Departamentos y Puestos.
Este script maneja la migración de datos de la tabla antigua 'departments' si existe.
"""
from database import get_db, DB_PATH
import os

def migrar_tablas():
    """Migra las tablas existentes y crea las nuevas."""
    
    print("=" * 60)
    print("MIGRACION DE TABLAS")
    print("=" * 60)
    print()
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Verificar si existe la tabla antigua 'departments'
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='departments'
            """)
            existe_departments = cursor.fetchone() is not None
            
            # Verificar si existe la tabla nueva 'Departamentos'
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='Departamentos'
            """)
            existe_departamentos = cursor.fetchone() is not None
            
            # Si existe la tabla antigua y no la nueva, migrar datos
            if existe_departments and not existe_departamentos:
                print("[INFO] Tabla antigua 'departments' encontrada.")
                print("[INFO] Migrando datos a nueva tabla 'Departamentos'...")
                
                # Obtener datos de la tabla antigua
                cursor.execute("SELECT id, name, description FROM departments")
                datos_antiguos = cursor.fetchall()
                
                # Crear nueva tabla Departamentos
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS Departamentos (
                        id_departamento INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre_departamento TEXT NOT NULL,
                        descripcion TEXT
                    )
                """)
                
                # Migrar datos
                for row in datos_antiguos:
                    cursor.execute("""
                        INSERT INTO Departamentos (id_departamento, nombre_departamento, descripcion)
                        VALUES (?, ?, ?)
                    """, (row[0], row[1], row[2]))
                
                print(f"[OK] {len(datos_antiguos)} registros migrados.")
                
            else:
                # Solo crear la tabla si no existe
                if not existe_departamentos:
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS Departamentos (
                            id_departamento INTEGER PRIMARY KEY AUTOINCREMENT,
                            nombre_departamento TEXT NOT NULL,
                            descripcion TEXT
                        )
                    """)
                    print("[OK] Tabla 'Departamentos' creada.")
                else:
                    print("[INFO] Tabla 'Departamentos' ya existe.")
            
            # Crear tabla Puestos
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='Puestos'
            """)
            existe_puestos = cursor.fetchone() is not None
            
            if not existe_puestos:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS Puestos (
                        id_puesto INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre_puesto TEXT NOT NULL,
                        nivel TEXT,
                        salario_base REAL
                    )
                """)
                print("[OK] Tabla 'Puestos' creada.")
            else:
                print("[INFO] Tabla 'Puestos' ya existe.")
            
            # Verificar las tablas creadas
            print()
            print("=" * 60)
            print("TABLAS VERIFICADAS:")
            print("=" * 60)
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            tablas = cursor.fetchall()
            
            for tabla in tablas:
                nombre = tabla[0]
                cursor.execute(f"SELECT COUNT(*) FROM {nombre}")
                count = cursor.fetchone()[0]
                print(f"  - {nombre}: {count} registros")
            
            print()
            print("=" * 60)
            print("[OK] Migracion completada exitosamente")
            print("=" * 60)
            
    except Exception as e:
        print(f"[ERROR] Error durante la migracion: {str(e)}")
        return False
    
    return True


if __name__ == "__main__":
    migrar_tablas()

