"""
Script para verificar y crear TODAS las tablas necesarias
"""
import sqlite3
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'rrhh.db')

print("=" * 70)
print("VERIFICANDO Y CREANDO TODAS LAS TABLAS")
print("=" * 70)
print()

try:
    conn = sqlite3.connect(DATABASE_PATH, timeout=10.0)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    
    # Lista de todas las tablas que deben existir
    tablas_requeridas = {
        'Departamentos': '''
            CREATE TABLE IF NOT EXISTS Departamentos (
                id_departamento INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_departamento VARCHAR(100) NOT NULL,
                descripcion TEXT
            )
        ''',
        'Puestos': '''
            CREATE TABLE IF NOT EXISTS Puestos (
                id_puesto INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_puesto VARCHAR(100) NOT NULL,
                nivel VARCHAR(50),
                salario_base DECIMAL(10,2)
            )
        ''',
        'Empleados': '''
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
        ''',
        'Contratos': '''
            CREATE TABLE IF NOT EXISTS Contratos (
                id_contrato INTEGER PRIMARY KEY AUTOINCREMENT,
                id_empleado INTEGER,
                tipo_contrato VARCHAR(50),
                fecha_inicio DATE,
                fecha_fin DATE,
                salario DECIMAL(10,2),
                condiciones TEXT,
                FOREIGN KEY (id_empleado) REFERENCES Empleados(id_empleado)
            )
        ''',
        'Asistencias': '''
            CREATE TABLE IF NOT EXISTS Asistencias (
                id_asistencia INTEGER PRIMARY KEY AUTOINCREMENT,
                id_empleado INTEGER,
                fecha DATE,
                hora_entrada TIME,
                hora_salida TIME,
                observaciones TEXT,
                FOREIGN KEY (id_empleado) REFERENCES Empleados(id_empleado)
            )
        ''',
        'Capacitaciones': '''
            CREATE TABLE IF NOT EXISTS Capacitaciones (
                id_capacitacion INTEGER PRIMARY KEY AUTOINCREMENT,
                id_empleado INTEGER,
                nombre_curso VARCHAR(100),
                institucion VARCHAR(100),
                fecha_inicio DATE,
                fecha_fin DATE,
                certificado BOOLEAN,
                FOREIGN KEY (id_empleado) REFERENCES Empleados(id_empleado)
            )
        ''',
        'Evaluaciones': '''
            CREATE TABLE IF NOT EXISTS Evaluaciones (
                id_evaluacion INTEGER PRIMARY KEY AUTOINCREMENT,
                id_empleado INTEGER,
                fecha DATE,
                evaluador VARCHAR(100),
                puntaje INTEGER,
                observaciones TEXT,
                FOREIGN KEY (id_empleado) REFERENCES Empleados(id_empleado)
            )
        ''',
        'Nomina': '''
            CREATE TABLE IF NOT EXISTS Nomina (
                id_nomina INTEGER PRIMARY KEY AUTOINCREMENT,
                id_empleado INTEGER,
                mes INTEGER,
                anio INTEGER,
                salario_base DECIMAL(10,2),
                bonificaciones DECIMAL(10,2),
                deducciones DECIMAL(10,2),
                salario_neto DECIMAL(10,2),
                fecha_pago DATE,
                FOREIGN KEY (id_empleado) REFERENCES Empleados(id_empleado)
            )
        ''',
        'Vacaciones_Permisos': '''
            CREATE TABLE IF NOT EXISTS Vacaciones_Permisos (
                id_permiso INTEGER PRIMARY KEY AUTOINCREMENT,
                id_empleado INTEGER,
                tipo VARCHAR(50),
                fecha_solicitud DATE,
                fecha_inicio DATE,
                fecha_fin DATE,
                estado VARCHAR(20),
                observaciones TEXT,
                FOREIGN KEY (id_empleado) REFERENCES Empleados(id_empleado)
            )
        '''
    }
    
    # Obtener tablas existentes
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tablas_existentes = [row[0] for row in cursor.fetchall() if row[0] != 'sqlite_sequence']
    
    print(f"Tablas existentes actualmente: {len(tablas_existentes)}")
    for tabla in tablas_existentes:
        print(f"  - {tabla}")
    
    print("\n" + "=" * 70)
    print("CREANDO TABLAS REQUERIDAS:")
    print("=" * 70)
    
    tablas_creadas = []
    tablas_ya_existian = []
    
    for nombre_tabla, sql in tablas_requeridas.items():
        # Verificar si existe (case sensitive)
        if nombre_tabla in tablas_existentes:
            print(f"  [INFO] Tabla '{nombre_tabla}' ya existe")
            tablas_ya_existian.append(nombre_tabla)
        else:
            try:
                print(f"  [INFO] Creando tabla '{nombre_tabla}'...")
                cursor.execute(sql)
                tablas_creadas.append(nombre_tabla)
                print(f"  [OK] Tabla '{nombre_tabla}' creada exitosamente")
            except sqlite3.Error as e:
                print(f"  [ERROR] Error al crear '{nombre_tabla}': {e}")
    
    conn.commit()
    
    # Verificar todas las tablas finales
    print("\n" + "=" * 70)
    print("VERIFICACION FINAL:")
    print("=" * 70)
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    todas_las_tablas = [row[0] for row in cursor.fetchall() if row[0] != 'sqlite_sequence']
    
    print(f"\nTotal de tablas en la base de datos: {len(todas_las_tablas)}")
    print("\nTodas las tablas:")
    for tabla in todas_las_tablas:
        if tabla in tablas_requeridas:
            print(f"  [OK] {tabla} <-- Tabla requerida")
        else:
            print(f"  [INFO] {tabla} <-- Tabla adicional")
    
    # Verificar que todas las tablas requeridas existen
    print("\n" + "=" * 70)
    print("VERIFICACION DE TABLAS REQUERIDAS:")
    print("=" * 70)
    todas_existen = True
    for nombre_tabla in tablas_requeridas.keys():
        if nombre_tabla in todas_las_tablas:
            print(f"  [OK] {nombre_tabla} - EXISTE")
        else:
            print(f"  [ERROR] {nombre_tabla} - NO EXISTE")
            todas_existen = False
    
    conn.close()
    
    print("\n" + "=" * 70)
    if todas_existen:
        print("[OK] TODAS LAS TABLAS REQUERIDAS EXISTEN")
    else:
        print("[ERROR] FALTAN ALGUNAS TABLAS")
    print("=" * 70)
    
    print("\nINSTRUCCIONES:")
    print("1. Abre DB Browser for SQLite")
    print("2. Abre la base de datos rrhh.db")
    print("3. Ve a la pestaña 'Database Structure'")
    print("4. Haz click en 'Refresh' (F5)")
    print("5. Deberias ver todas las tablas en la lista")
    
except sqlite3.OperationalError as e:
    if "locked" in str(e).lower():
        print("\n[ERROR] La base de datos esta BLOQUEADA")
        print("\nCIERRA DB Browser y ejecuta este script nuevamente")
    else:
        print(f"\n[ERROR] Error de SQLite: {e}")
except Exception as e:
    print(f"\n[ERROR] Error: {e}")

