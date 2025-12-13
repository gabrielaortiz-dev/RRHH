"""
Script para verificar la estructura actual de la tabla Nomina
"""
import sqlite3
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'rrhh.db')

print("=" * 70)
print("VERIFICANDO ESTRUCTURA DE TABLA NOMINA")
print("=" * 70)
print()

try:
    conn = sqlite3.connect(DATABASE_PATH, timeout=10.0)
    cursor = conn.cursor()
    
    # Verificar si la tabla existe
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Nomina'")
    if not cursor.fetchone():
        print("[ERROR] La tabla Nomina no existe!")
        conn.close()
        exit(1)
    
    print("[OK] La tabla Nomina existe")
    print()
    
    # Obtener estructura completa
    cursor.execute("PRAGMA table_info(Nomina)")
    columnas = cursor.fetchall()
    
    print("ESTRUCTURA DE LA TABLA:")
    print("-" * 70)
    print(f"{'Columna':<25} {'Tipo':<20} {'Not Null':<10} {'Default':<15}")
    print("-" * 70)
    
    for col in columnas:
        cid, name, type_, notnull, default_value, pk = col
        not_null = "YES" if notnull else "NO"
        default_val = str(default_value) if default_value else ""
        print(f"{name:<25} {type_:<20} {not_null:<10} {default_val:<15}")
    
    print()
    print("=" * 70)
    
    # Verificar columnas críticas
    nombres_columnas = [col[1] for col in columnas]
    columnas_criticas = ['id_empleado', 'mes', 'anio', 'salario_base', 'periodo', 
                        'total_bonificaciones', 'total_deducciones', 'salario_neto']
    
    print("VERIFICACION DE COLUMNAS CRITICAS:")
    print("-" * 70)
    for col in columnas_criticas:
        if col in nombres_columnas:
            print(f"[OK] {col}")
        else:
            print(f"[FALTA] {col}")
    
    print()
    print("=" * 70)
    print(f"Total de columnas: {len(columnas)}")
    print("=" * 70)
    
    conn.close()
    
except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    print(traceback.format_exc())

