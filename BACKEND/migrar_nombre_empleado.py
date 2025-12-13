"""
Script de migración para agregar y actualizar la columna nombre_empleado
en todas las tablas que tienen id_empleado o empleado_id
"""
import sqlite3
import os
from database import Database

def migrar_nombre_empleado():
    """Migrar y actualizar nombre_empleado en todas las tablas"""
    print("=" * 70)
    print("MIGRACIÓN: Agregar nombre_empleado a tablas con ID de empleado")
    print("=" * 70)
    print()
    
    db = Database()
    db.connect()
    
    try:
        # Lista de tablas con sus columnas de ID de empleado
        tablas_con_empleado = [
            ("Contratos", "id_empleado"),
            ("Asistencias", "id_empleado"),
            ("asistencias", "empleado_id"),
            ("Nomina", "id_empleado"),
            ("Vacaciones_Permisos", "id_empleado"),
            ("Capacitaciones", "id_empleado"),
            ("Evaluaciones", "id_empleado"),
            ("Documentos", "id_empleado")
        ]
        
        for tabla, columna_id in tablas_con_empleado:
            try:
                # Verificar si la tabla existe
                cursor = db.connection.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (tabla,))
                if not cursor.fetchone():
                    print(f"[INFO] Tabla {tabla} no existe, omitiendo...")
                    continue
                
                # Verificar si la columna nombre_empleado ya existe
                cursor.execute(f"PRAGMA table_info({tabla})")
                columnas_existentes = [col[1] for col in cursor.fetchall()]
                
                if "nombre_empleado" not in columnas_existentes:
                    # Agregar la columna
                    db.execute_query(f"ALTER TABLE {tabla} ADD COLUMN nombre_empleado VARCHAR(200)")
                    print(f"[OK] Columna nombre_empleado agregada a tabla {tabla}")
                else:
                    print(f"[INFO] Columna nombre_empleado ya existe en tabla {tabla}")
                
                # Actualizar registros existentes con el nombre del empleado
                registros_actualizados = 0
                cursor = db.connection.cursor()
                
                if tabla == "asistencias":
                    # Para la tabla asistencias (minúscula) usar empleado_id
                    # Intentar primero con tabla empleados (minúscula)
                    try:
                        cursor.execute(f"""
                            UPDATE {tabla} 
                            SET nombre_empleado = (
                                SELECT nombre || ' ' || apellido 
                                FROM empleados 
                                WHERE empleados.id = {tabla}.empleado_id
                            )
                            WHERE nombre_empleado IS NULL AND empleado_id IS NOT NULL
                        """)
                        registros_actualizados = cursor.rowcount
                    except Exception:
                        # Si falla, intentar con tabla Empleados (mayúscula)
                        try:
                            cursor.execute(f"""
                                UPDATE {tabla} 
                                SET nombre_empleado = (
                                    SELECT nombre || ' ' || apellido 
                                    FROM Empleados 
                                    WHERE Empleados.id_empleado = {tabla}.empleado_id
                                )
                                WHERE nombre_empleado IS NULL AND empleado_id IS NOT NULL
                            """)
                            registros_actualizados = cursor.rowcount
                        except Exception as e:
                            print(f"[ERROR] No se pudo actualizar {tabla}: {str(e)}")
                else:
                    # Para las demás tablas usar id_empleado
                    # Intentar primero con tabla Empleados (mayúscula)
                    try:
                        cursor.execute(f"""
                            UPDATE {tabla} 
                            SET nombre_empleado = (
                                SELECT nombre || ' ' || apellido 
                                FROM Empleados 
                                WHERE Empleados.id_empleado = {tabla}.{columna_id}
                            )
                            WHERE nombre_empleado IS NULL AND {columna_id} IS NOT NULL
                        """)
                        registros_actualizados = cursor.rowcount
                    except Exception:
                        # Si falla, intentar con tabla empleados (minúscula) usando id
                        try:
                            cursor.execute(f"""
                                UPDATE {tabla} 
                                SET nombre_empleado = (
                                    SELECT nombre || ' ' || apellido 
                                    FROM empleados 
                                    WHERE empleados.id = {tabla}.{columna_id}
                                )
                                WHERE nombre_empleado IS NULL AND {columna_id} IS NOT NULL
                            """)
                            registros_actualizados = cursor.rowcount
                        except Exception as e:
                            print(f"[ERROR] No se pudo actualizar {tabla}: {str(e)}")
                
                db.connection.commit()
                
                if registros_actualizados > 0:
                    print(f"[OK] {registros_actualizados} registros actualizados en tabla {tabla}")
                else:
                    print(f"[INFO] No hay registros para actualizar en tabla {tabla}")
                    
            except Exception as e:
                print(f"[ERROR] Error al procesar tabla {tabla}: {str(e)}")
                continue
        
        print()
        print("=" * 70)
        print("[OK] Migración completada exitosamente")
        print("=" * 70)
        
    except Exception as e:
        print(f"[ERROR] Error en la migración: {str(e)}")
        raise
    finally:
        db.disconnect()

if __name__ == "__main__":
    migrar_nombre_empleado()

