"""
Script para verificar si la tabla Puestos existe en la base de datos
"""
import sqlite3
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'rrhh.db')

print("=" * 70)
print("VERIFICANDO TABLA PUESTOS EN LA BASE DE DATOS")
print("=" * 70)
print()

try:
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Obtener TODAS las tablas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    todas_las_tablas = cursor.fetchall()
    
    print(f"TOTAL DE TABLAS EN LA BASE DE DATOS: {len(todas_las_tablas)}")
    print("\nLISTA COMPLETA DE TABLAS:")
    print("-" * 70)
    for tabla in todas_las_tablas:
        nombre = tabla[0]
        print(f"  - {nombre}")
    
    # Buscar específicamente Puestos (case insensitive)
    print("\n" + "=" * 70)
    print("BUSCANDO TABLA 'PUESTOS' (case insensitive):")
    print("=" * 70)
    
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' 
        AND (LOWER(name) = 'puestos' OR name LIKE '%puesto%')
    """)
    resultados = cursor.fetchall()
    
    if resultados:
        print(f"\n[OK] Se encontraron {len(resultados)} tabla(s) relacionada(s) con 'puestos':")
        for resultado in resultados:
            nombre = resultado[0]
            print(f"\n  [OK] Tabla encontrada: '{nombre}'")
            
            # Mostrar estructura
            cursor.execute(f"PRAGMA table_info({nombre})")
            columnas = cursor.fetchall()
            print(f"    Columnas ({len(columnas)}):")
            for col in columnas:
                pk_str = " [PRIMARY KEY]" if col[5] else ""
                not_null_str = " NOT NULL" if col[3] else ""
                print(f"      - {col[1]}: {col[2]}{not_null_str}{pk_str}")
            
            # Contar registros
            cursor.execute(f"SELECT COUNT(*) FROM {nombre}")
            count = cursor.fetchone()[0]
            print(f"    Registros: {count}")
    else:
        print("\n[ERROR] NO se encontró ninguna tabla con el nombre 'Puestos'")
        print("\nLa tabla NO existe en la base de datos.")
        print("\nPara crearla, ejecuta este SQL en DB Browser:")
        print("-" * 70)
        print("CREATE TABLE Puestos (")
        print("    id_puesto INTEGER PRIMARY KEY AUTOINCREMENT,")
        print("    nombre_puesto VARCHAR(100) NOT NULL,")
        print("    nivel VARCHAR(50),")
        print("    salario_base DECIMAL(10,2)")
        print(");")
        print("-" * 70)
    
    # Verificar también Departamentos
    print("\n" + "=" * 70)
    print("VERIFICANDO TABLA 'DEPARTAMENTOS':")
    print("=" * 70)
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' 
        AND (LOWER(name) = 'departamentos' OR LOWER(name) = 'departamento')
    """)
    dept = cursor.fetchall()
    if dept:
        print(f"[OK] Tabla encontrada: '{dept[0][0]}'")
    else:
        print("[INFO] No se encontró tabla Departamentos")
    
    conn.close()
    
    print("\n" + "=" * 70)
    print("INSTRUCCIONES PARA DB BROWSER:")
    print("=" * 70)
    print("Si la tabla existe pero no la ves en DB Browser:")
    print("1. Cierra DB Browser COMPLETAMENTE")
    print("2. Vuelve a abrir DB Browser")
    print("3. Abre la base de datos rrhh.db")
    print("4. Ve a la pestaña 'Database Structure'")
    print("5. Haz click en 'Refresh' o presiona F5")
    print("6. La tabla debería aparecer")
    
except sqlite3.OperationalError as e:
    if "locked" in str(e).lower():
        print("[ERROR] La base de datos está bloqueada")
        print("Cierra DB Browser y ejecuta este script nuevamente")
    else:
        print(f"[ERROR] Error de SQLite: {e}")
except Exception as e:
    print(f"[ERROR] Error: {e}")

