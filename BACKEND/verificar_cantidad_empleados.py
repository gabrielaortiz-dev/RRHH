"""
Script simple para verificar cuantos empleados hay en la base de datos
"""
import sqlite3
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'rrhh.db')

try:
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Detectar que tabla de empleados existe
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND (name='Empleados' OR name='empleados')")
    tabla = cursor.fetchone()
    
    if not tabla:
        print("[ERROR] No se encontro tabla de empleados")
    else:
        table_name = tabla[0]
        print(f"[OK] Tabla encontrada: {table_name}")
        
        # Contar empleados
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        total = cursor.fetchone()[0]
        print(f"\nTotal de empleados en la base de datos: {total}")
        
        # Contar activos
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE activo = 1 OR activo IS NULL")
            activos = cursor.fetchone()[0]
            print(f"Empleados activos: {activos}")
        except:
            print("No se pudo contar activos (campo activo puede no existir)")
        
        # Mostrar algunos IDs
        try:
            cursor.execute(f"SELECT id_empleado, nombre, apellido FROM {table_name} LIMIT 5")
            empleados = cursor.fetchall()
            print(f"\nPrimeros 5 empleados:")
            for emp in empleados:
                print(f"   - ID {emp[0]}: {emp[1]} {emp[2]}")
        except:
            try:
                cursor.execute(f"SELECT id, nombre, apellido FROM {table_name} LIMIT 5")
                empleados = cursor.fetchall()
                print(f"\nPrimeros 5 empleados:")
                for emp in empleados:
                    print(f"   - ID {emp[0]}: {emp[1]} {emp[2]}")
            except:
                print("No se pudieron listar empleados")
    
    conn.close()
    
except Exception as e:
    print(f"[ERROR] Error: {str(e)}")
    import traceback
    traceback.print_exc()

