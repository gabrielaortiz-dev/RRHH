"""
Verificacion exacta de tablas con nombres case-sensitive
"""
import sqlite3
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'rrhh.db')

try:
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Obtener todas las tablas exactamente como están almacenadas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    todas = cursor.fetchall()
    
    print("TABLAS EXACTAS EN LA BASE DE DATOS:")
    print("=" * 70)
    for tabla in todas:
        nombre = tabla[0]
        if nombre != 'sqlite_sequence':
            # Intentar obtener info de la tabla
            try:
                cursor.execute(f'PRAGMA table_info("{nombre}")')
                cols = cursor.fetchall()
                print(f"  {nombre} ({len(cols)} columnas)")
            except:
                print(f"  {nombre} (error al leer)")
    
    # Verificar específicamente con comillas
    print("\n" + "=" * 70)
    print("VERIFICANDO TABLAS CON NOMBRES EXACTOS:")
    print("=" * 70)
    
    tablas_a_verificar = ['Departamentos', 'Empleados', 'Asistencias', 
                          'departamentos', 'empleados', 'asistencias']
    
    for nombre in tablas_a_verificar:
        try:
            cursor.execute(f'SELECT name FROM sqlite_master WHERE type="table" AND name="{nombre}"')
            resultado = cursor.fetchone()
            if resultado:
                cursor.execute(f'PRAGMA table_info("{nombre}")')
                cols = cursor.fetchall()
                print(f"[OK] '{nombre}' EXISTE ({len(cols)} columnas)")
            else:
                print(f"[NO] '{nombre}' NO EXISTE")
        except Exception as e:
            print(f"[ERROR] '{nombre}': {e}")
    
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")

