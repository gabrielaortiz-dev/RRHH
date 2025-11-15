"""
Script para crear todas las nuevas tablas en la base de datos
CIERRA DB Browser antes de ejecutar este script
"""
import sqlite3
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'rrhh.db')

print("=" * 70)
print("CREANDO TODAS LAS NUEVAS TABLAS")
print("=" * 70)
print()

try:
    print("[INFO] Conectando a la base de datos...")
    conn = sqlite3.connect(DATABASE_PATH, timeout=10.0)
    # Habilitar foreign keys
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    print("[OK] Conexion establecida")
    
    tablas_creadas = []
    tablas_existentes = []
    
    # Primero asegurar que Departamentos y Puestos existen
    print("\n[INFO] Verificando tablas base (Departamentos y Puestos)...")
    
    # Crear Departamentos si no existe
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Departamentos'")
    if not cursor.fetchone():
        print("[INFO] Creando tabla Departamentos...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Departamentos (
                id_departamento INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_departamento VARCHAR(100) NOT NULL,
                descripcion TEXT
            )
        ''')
        tablas_creadas.append("Departamentos")
    else:
        print("[INFO] Tabla Departamentos ya existe")
        tablas_existentes.append("Departamentos")
    
    # Crear Puestos si no existe
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Puestos'")
    if not cursor.fetchone():
        print("[INFO] Creando tabla Puestos...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Puestos (
                id_puesto INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_puesto VARCHAR(100) NOT NULL,
                nivel VARCHAR(50),
                salario_base DECIMAL(10,2)
            )
        ''')
        tablas_creadas.append("Puestos")
    else:
        print("[INFO] Tabla Puestos ya existe")
        tablas_existentes.append("Puestos")
    
    # Lista de tablas a crear
    tablas_nuevas = [
        ("Empleados", '''
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
        '''),
        ("Contratos", '''
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
        '''),
        ("Asistencias", '''
            CREATE TABLE IF NOT EXISTS Asistencias (
                id_asistencia INTEGER PRIMARY KEY AUTOINCREMENT,
                id_empleado INTEGER,
                fecha DATE,
                hora_entrada TIME,
                hora_salida TIME,
                observaciones TEXT,
                FOREIGN KEY (id_empleado) REFERENCES Empleados(id_empleado)
            )
        '''),
        ("Capacitaciones", '''
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
        '''),
        ("Evaluaciones", '''
            CREATE TABLE IF NOT EXISTS Evaluaciones (
                id_evaluacion INTEGER PRIMARY KEY AUTOINCREMENT,
                id_empleado INTEGER,
                fecha DATE,
                evaluador VARCHAR(100),
                puntaje INTEGER,
                observaciones TEXT,
                FOREIGN KEY (id_empleado) REFERENCES Empleados(id_empleado)
            )
        '''),
        ("Nomina", '''
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
        '''),
        ("Vacaciones_Permisos", '''
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
        ''')
    ]
    
    print("\n[INFO] Creando nuevas tablas...")
    for nombre_tabla, sql in tablas_nuevas:
        try:
            # Verificar si existe
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{nombre_tabla}'")
            if cursor.fetchone():
                print(f"  [INFO] Tabla '{nombre_tabla}' ya existe")
                tablas_existentes.append(nombre_tabla)
            else:
                print(f"  [INFO] Creando tabla '{nombre_tabla}'...")
                cursor.execute(sql)
                tablas_creadas.append(nombre_tabla)
                print(f"  [OK] Tabla '{nombre_tabla}' creada")
        except sqlite3.Error as e:
            print(f"  [ERROR] Error al crear tabla '{nombre_tabla}': {e}")
    
    conn.commit()
    
    # Listar todas las tablas
    print("\n" + "=" * 70)
    print("RESUMEN DE TABLAS:")
    print("=" * 70)
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    todas_las_tablas = cursor.fetchall()
    
    print(f"\nTotal de tablas en la base de datos: {len(todas_las_tablas)}")
    print("\nTablas creadas en esta ejecucion:")
    for tabla in tablas_creadas:
        print(f"  [OK] {tabla}")
    
    if tablas_existentes:
        print("\nTablas que ya existian:")
        for tabla in tablas_existentes:
            print(f"  [INFO] {tabla}")
    
    print("\nTodas las tablas:")
    for tabla in todas_las_tablas:
        if tabla[0] != 'sqlite_sequence':
            print(f"  - {tabla[0]}")
    
    conn.close()
    
    print("\n" + "=" * 70)
    print("[OK] PROCESO COMPLETADO")
    print("=" * 70)
    print("\nAhora puedes:")
    print("1. Abrir DB Browser for SQLite")
    print("2. Abre la base de datos rrhh.db")
    print("3. Ve a la pestaña 'Database Structure'")
    print("4. Haz click en 'Refresh' (F5)")
    print("5. Deberias ver todas las nuevas tablas en la lista")
    
except sqlite3.OperationalError as e:
    if "locked" in str(e).lower():
        print("\n[ERROR] La base de datos esta BLOQUEADA")
        print("\nINSTRUCCIONES:")
        print("1. CIERRA DB Browser for SQLite COMPLETAMENTE")
        print("2. Deten el servidor FastAPI si esta corriendo")
        print("3. Ejecuta este script nuevamente: python crear_todas_las_tablas.py")
    else:
        print(f"\n[ERROR] Error de SQLite: {e}")
except Exception as e:
    print(f"\n[ERROR] Error: {e}")

