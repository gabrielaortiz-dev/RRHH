"""
Crear las 3 tablas que faltan: Departamentos, Empleados, Asistencias
"""
import sqlite3
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'rrhh.db')

print("=" * 70)
print("CREANDO TABLAS FALTANTES")
print("=" * 70)
print()

try:
    conn = sqlite3.connect(DATABASE_PATH, timeout=10.0)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    
    # Crear Departamentos
    print("[INFO] Creando tabla Departamentos...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Departamentos (
            id_departamento INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_departamento VARCHAR(100) NOT NULL,
            descripcion TEXT
        )
    ''')
    print("[OK] Tabla Departamentos creada")
    
    # Crear Empleados
    print("[INFO] Creando tabla Empleados...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Empleados (
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
            FOREIGN KEY (id_departamento) REFERENCES Departamentos(id_departamento),
            FOREIGN KEY (id_puesto) REFERENCES Puestos(id_puesto)
        )
    ''')
    print("[OK] Tabla Empleados creada")
    
    # Crear Asistencias
    print("[INFO] Creando tabla Asistencias...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Asistencias (
            id_asistencia INTEGER PRIMARY KEY AUTOINCREMENT,
            id_empleado INTEGER,
            fecha DATE,
            hora_entrada TIME,
            hora_salida TIME,
            observaciones TEXT,
            FOREIGN KEY (id_empleado) REFERENCES Empleados(id_empleado)
        )
    ''')
    print("[OK] Tabla Asistencias creada")
    
    conn.commit()
    
    # Verificar
    print("\n" + "=" * 70)
    print("VERIFICACION:")
    print("=" * 70)
    
    tablas_requeridas = ['Departamentos', 'Empleados', 'Asistencias']
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    todas = [row[0] for row in cursor.fetchall() if row[0] != 'sqlite_sequence']
    
    for tabla in tablas_requeridas:
        if tabla in todas:
            cursor.execute(f"PRAGMA table_info({tabla})")
            cols = cursor.fetchall()
            print(f"[OK] {tabla} - EXISTE ({len(cols)} columnas)")
        else:
            print(f"[ERROR] {tabla} - NO EXISTE")
    
    print("\n" + "=" * 70)
    print("TODAS LAS TABLAS EN LA BASE DE DATOS:")
    print("=" * 70)
    for tabla in todas:
        print(f"  - {tabla}")
    
    conn.close()
    
    print("\n[OK] Proceso completado!")
    print("\nAhora:")
    print("1. Abre DB Browser")
    print("2. Refresca la vista (F5)")
    print("3. Deberias ver todas las tablas")
    
except sqlite3.OperationalError as e:
    if "locked" in str(e).lower():
        print("\n[ERROR] Base de datos bloqueada")
        print("Cierra DB Browser y ejecuta este script nuevamente")
    else:
        print(f"\n[ERROR] Error: {e}")
except Exception as e:
    print(f"\n[ERROR] Error: {e}")

