"""
Script para limpiar contratos y asegurar que solo existan contratos
de los 40 empleados que deben estar en el sistema.
"""
import sqlite3
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'rrhh.db')

def limpiar_contratos_40_empleados():
    """Elimina todos los contratos que no pertenezcan a los 40 empleados"""
    print("=" * 70)
    print("LIMPIANDO CONTRATOS - SOLO 40 EMPLEADOS")
    print("=" * 70)
    
    conn = sqlite3.connect(DATABASE_PATH, timeout=10.0)
    conn.execute("PRAGMA foreign_keys = OFF")
    cursor = conn.cursor()
    
    try:
        # Detectar tabla de empleados
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND (name='Empleados' OR name='empleados')")
        tabla_empleados = cursor.fetchone()
        
        if not tabla_empleados:
            print("[ERROR] No se encontró tabla de empleados")
            return
        
        nombre_tabla = tabla_empleados[0]
        print(f"[INFO] Usando tabla de empleados: {nombre_tabla}")
        
        # Detectar columna ID de empleados
        cursor.execute(f"PRAGMA table_info({nombre_tabla})")
        columnas = cursor.fetchall()
        id_column = None
        for col in columnas:
            if col[1] in ['id_empleado', 'id']:
                id_column = col[1]
                break
        
        if not id_column:
            print("[ERROR] No se encontró columna ID en la tabla de empleados")
            return
        
        print(f"[INFO] Usando columna ID: {id_column}")
        
        # Obtener los IDs de los 40 empleados actuales
        cursor.execute(f"SELECT {id_column} FROM {nombre_tabla} ORDER BY {id_column} LIMIT 40")
        empleados_actuales = [row[0] for row in cursor.fetchall()]
        
        print(f"[INFO] Empleados actuales: {len(empleados_actuales)}")
        print(f"[INFO] IDs de empleados: {empleados_actuales}")
        
        if len(empleados_actuales) == 0:
            print("[ERROR] No se encontraron empleados en la base de datos")
            return
        
        # Verificar si existe la tabla Contratos
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND (name='Contratos' OR name='contratos')")
        tabla_contratos = cursor.fetchone()
        
        if not tabla_contratos:
            print("[INFO] No existe tabla de Contratos")
            return
        
        nombre_tabla_contratos = tabla_contratos[0]
        print(f"[INFO] Usando tabla de contratos: {nombre_tabla_contratos}")
        
        # Detectar columna de empleado en Contratos
        cursor.execute(f"PRAGMA table_info({nombre_tabla_contratos})")
        columnas_contratos = cursor.fetchall()
        empleado_col_contratos = None
        for col in columnas_contratos:
            if col[1] in ['id_empleado', 'empleado_id', 'id_empleado_id']:
                empleado_col_contratos = col[1]
                break
        
        if not empleado_col_contratos:
            print("[ERROR] No se encontró columna de empleado en Contratos")
            return
        
        print(f"[INFO] Usando columna de empleado en Contratos: {empleado_col_contratos}")
        
        # Contar contratos antes de eliminar
        cursor.execute(f"SELECT COUNT(*) FROM {nombre_tabla_contratos}")
        total_contratos_antes = cursor.fetchone()[0]
        print(f"\n[INFO] Total de contratos antes de limpiar: {total_contratos_antes}")
        
        # Contar contratos válidos (de los 40 empleados)
        placeholders = ','.join(['?'] * len(empleados_actuales))
        cursor.execute(
            f"SELECT COUNT(*) FROM {nombre_tabla_contratos} WHERE {empleado_col_contratos} IN ({placeholders})",
            empleados_actuales
        )
        contratos_validos = cursor.fetchone()[0]
        print(f"[INFO] Contratos válidos (de los 40 empleados): {contratos_validos}")
        
        # Contar contratos a eliminar
        contratos_a_eliminar = total_contratos_antes - contratos_validos
        print(f"[INFO] Contratos a eliminar: {contratos_a_eliminar}")
        
        if contratos_a_eliminar > 0:
            # Eliminar contratos que no pertenecen a los 40 empleados
            cursor.execute(
                f"DELETE FROM {nombre_tabla_contratos} WHERE {empleado_col_contratos} NOT IN ({placeholders})",
                empleados_actuales
            )
            contratos_eliminados = cursor.rowcount
            
            print(f"\n[OK] {contratos_eliminados} contratos eliminados")
        else:
            print("\n[INFO] No hay contratos que eliminar. Todos los contratos pertenecen a los 40 empleados.")
        
        # Contar contratos después de eliminar
        cursor.execute(f"SELECT COUNT(*) FROM {nombre_tabla_contratos}")
        total_contratos_despues = cursor.fetchone()[0]
        print(f"[INFO] Total de contratos después de limpiar: {total_contratos_despues}")
        
        # Mostrar resumen por empleado
        print("\n" + "=" * 70)
        print("RESUMEN DE CONTRATOS POR EMPLEADO")
        print("=" * 70)
        
        for empleado_id in empleados_actuales:
            cursor.execute(
                f"SELECT COUNT(*) FROM {nombre_tabla_contratos} WHERE {empleado_col_contratos} = ?",
                (empleado_id,)
            )
            count = cursor.fetchone()[0]
            if count > 0:
                # Obtener nombre del empleado
                cursor.execute(
                    f"SELECT nombre, apellido FROM {nombre_tabla} WHERE {id_column} = ?",
                    (empleado_id,)
                )
                empleado = cursor.fetchone()
                nombre_completo = f"{empleado[0]} {empleado[1]}" if empleado else f"ID {empleado_id}"
                print(f"  - {nombre_completo}: {count} contrato(s)")
        
        conn.commit()
        print("\n" + "=" * 70)
        print("[OK] PROCESO COMPLETADO EXITOSAMENTE")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n[ERROR] Ocurrió un error: {str(e)}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.close()

if __name__ == "__main__":
    limpiar_contratos_40_empleados()

