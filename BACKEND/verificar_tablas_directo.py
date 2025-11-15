"""
Verificacion directa de todas las tablas en la base de datos
"""
import sqlite3
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'rrhh.db')

try:
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Obtener TODAS las tablas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    todas = cursor.fetchall()
    
    print("=" * 70)
    print("TODAS LAS TABLAS EN LA BASE DE DATOS:")
    print("=" * 70)
    print()
    
    tablas_requeridas = ['Departamentos', 'Puestos', 'Empleados', 'Contratos', 
                        'Asistencias', 'Capacitaciones', 'Evaluaciones', 
                        'Nomina', 'Vacaciones_Permisos']
    
    for tabla in todas:
        nombre = tabla[0]
        if nombre == 'sqlite_sequence':
            continue
        if nombre in tablas_requeridas:
            print(f"[OK] {nombre} <-- REQUERIDA")
        else:
            print(f"[INFO] {nombre}")
    
    print()
    print("=" * 70)
    print("VERIFICANDO TABLAS REQUERIDAS:")
    print("=" * 70)
    
    nombres_tablas = [t[0] for t in todas if t[0] != 'sqlite_sequence']
    
    for req in tablas_requeridas:
        if req in nombres_tablas:
            # Verificar estructura
            cursor.execute(f"PRAGMA table_info({req})")
            cols = cursor.fetchall()
            print(f"[OK] {req} - EXISTE ({len(cols)} columnas)")
        else:
            print(f"[ERROR] {req} - NO EXISTE")
    
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")

