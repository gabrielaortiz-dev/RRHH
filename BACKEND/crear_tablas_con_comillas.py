"""
Crear tablas con nombres exactos usando comillas dobles
"""
import sqlite3
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'rrhh.db')

print("=" * 70)
print("CREANDO TABLAS CON NOMBRES EXACTOS")
print("=" * 70)
print()

try:
    conn = sqlite3.connect(DATABASE_PATH, timeout=10.0)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    
    # Crear Departamentos con comillas dobles
    print("[INFO] Creando tabla 'Departamentos'...")
    try:
        cursor.execute('''
            CREATE TABLE "Departamentos" (
                id_departamento INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_departamento VARCHAR(100) NOT NULL,
                descripcion TEXT
            )
        ''')
        conn.commit()
        print("[OK] Tabla 'Departamentos' creada")
    except sqlite3.OperationalError as e:
        if "already exists" in str(e).lower():
            print("[INFO] Tabla 'Departamentos' ya existe")
        else:
            print(f"[ERROR] {e}")
    
    # Crear Empleados con comillas dobles
    print("[INFO] Creando tabla 'Empleados'...")
    try:
        cursor.execute('''
            CREATE TABLE "Empleados" (
                id_empleado INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre VARCHAR(100) NOT NULL,
                apellido VARCHAR(100) NOT NULL,
                fecha_nacimiento DATE,
                genero VARCHAR(10),
                estado_civil VARCHAR(20),
                direccion TEXT,
                telefono VARCHAR(20),
                correo VARCHAR(100),
                fecha_ingreso DATE,
                estado VARCHAR(20),
                id_departamento INTEGER,
                id_puesto INTEGER,
                FOREIGN KEY (id_departamento) REFERENCES "Departamentos"(id_departamento),
                FOREIGN KEY (id_puesto) REFERENCES "Puestos"(id_puesto)
            )
        ''')
        conn.commit()
        print("[OK] Tabla 'Empleados' creada")
    except sqlite3.OperationalError as e:
        if "already exists" in str(e).lower():
            print("[INFO] Tabla 'Empleados' ya existe")
        else:
            print(f"[ERROR] {e}")
    
    # Crear Asistencias con comillas dobles
    print("[INFO] Creando tabla 'Asistencias'...")
    try:
        cursor.execute('''
            CREATE TABLE "Asistencias" (
                id_asistencia INTEGER PRIMARY KEY AUTOINCREMENT,
                id_empleado INTEGER,
                fecha DATE,
                hora_entrada TIME,
                hora_salida TIME,
                observaciones TEXT,
                FOREIGN KEY (id_empleado) REFERENCES "Empleados"(id_empleado)
            )
        ''')
        conn.commit()
        print("[OK] Tabla 'Asistencias' creada")
    except sqlite3.OperationalError as e:
        if "already exists" in str(e).lower():
            print("[INFO] Tabla 'Asistencias' ya existe")
        else:
            print(f"[ERROR] {e}")
    
    # Verificar todas las tablas
    print("\n" + "=" * 70)
    print("VERIFICACION FINAL:")
    print("=" * 70)
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    todas = [row[0] for row in cursor.fetchall() if row[0] != 'sqlite_sequence']
    
    tablas_requeridas = ['Departamentos', 'Puestos', 'Empleados', 'Contratos', 
                        'Asistencias', 'Capacitaciones', 'Evaluaciones', 
                        'Nomina', 'Vacaciones_Permisos']
    
    print(f"\nTotal de tablas: {len(todas)}")
    print("\nTablas requeridas:")
    for req in tablas_requeridas:
        if req in todas:
            cursor.execute(f'PRAGMA table_info("{req}")')
            cols = cursor.fetchall()
            print(f"  [OK] {req} ({len(cols)} columnas)")
        else:
            print(f"  [ERROR] {req} - NO EXISTE")
    
    print("\nTodas las tablas:")
    for tabla in todas:
        print(f"  - {tabla}")
    
    conn.close()
    
    print("\n[OK] Proceso completado!")
    print("\nAhora en DB Browser:")
    print("1. Cierra y vuelve a abrir DB Browser")
    print("2. O haz click en 'Refresh' (F5)")
    print("3. Deberias ver todas las tablas con mayusculas")
    
except sqlite3.OperationalError as e:
    if "locked" in str(e).lower():
        print("\n[ERROR] Base de datos bloqueada")
        print("Cierra DB Browser y ejecuta este script nuevamente")
    else:
        print(f"\n[ERROR] Error: {e}")
except Exception as e:
    print(f"\n[ERROR] Error: {e}")

