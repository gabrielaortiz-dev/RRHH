"""
Módulo para manejar la conexión a la base de datos SQLite.
"""
import sqlite3
import os
from contextlib import contextmanager
from pathlib import Path
from config import get_config

# Obtener configuración del entorno
config = get_config()

# Ruta de la base de datos desde la configuración
DB_DIR = config.DATABASE_DIR
DB_DIR.mkdir(exist_ok=True)
DB_PATH = config.DATABASE_PATH


def get_connection():
    """
    Crea y retorna una conexión a la base de datos SQLite.
    
    Returns:
        sqlite3.Connection: Conexión a la base de datos
    """
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row  # Permite acceder a las columnas por nombre
    return conn


@contextmanager
def get_db():
    """
    Context manager para manejar la conexión a la base de datos.
    Asegura que la conexión se cierre correctamente después de usarla.
    
    Yields:
        sqlite3.Connection: Conexión a la base de datos
    """
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """
    Inicializa la base de datos creando las tablas necesarias.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Tabla de usuarios
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabla de departamentos (actualizada con nombres en español)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Departamentos (
                id_departamento INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_departamento TEXT NOT NULL,
                descripcion TEXT
            )
        """)
        
        # Tabla de puestos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Puestos (
                id_puesto INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_puesto TEXT NOT NULL,
                nivel TEXT,
                salario_base REAL
            )
        """)
        
        # Tabla de empleados
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                department_id INTEGER,
                position TEXT,
                hire_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (department_id) REFERENCES departments(id)
            )
        """)
        
        # Tabla de asistencia
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL,
                date DATE NOT NULL,
                check_in TIME,
                check_out TIME,
                status TEXT DEFAULT 'present',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (employee_id) REFERENCES employees(id),
                UNIQUE(employee_id, date)
            )
        """)
        
        # Tabla de Empleados (nueva estructura con más campos)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Empleados (
                id_empleado INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                apellido TEXT NOT NULL,
                fecha_nacimiento DATE,
                genero TEXT,
                estado_civil TEXT,
                direccion TEXT,
                telefono TEXT,
                correo TEXT,
                fecha_ingreso DATE,
                estado TEXT,
                id_departamento INTEGER,
                id_puesto INTEGER,
                FOREIGN KEY (id_departamento) REFERENCES Departamentos(id_departamento),
                FOREIGN KEY (id_puesto) REFERENCES Puestos(id_puesto)
            )
        """)
        
        # Tabla de Contratos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Contratos (
                id_contrato INTEGER PRIMARY KEY AUTOINCREMENT,
                id_empleado INTEGER NOT NULL,
                tipo_contrato TEXT,
                fecha_inicio DATE,
                fecha_fin DATE,
                salario REAL,
                condiciones TEXT,
                FOREIGN KEY (id_empleado) REFERENCES Empleados(id_empleado)
            )
        """)
        
        # Tabla de Asistencias
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Asistencias (
                id_asistencia INTEGER PRIMARY KEY AUTOINCREMENT,
                id_empleado INTEGER NOT NULL,
                fecha DATE,
                hora_entrada TIME,
                hora_salida TIME,
                observaciones TEXT,
                FOREIGN KEY (id_empleado) REFERENCES Empleados(id_empleado)
            )
        """)
        
        # Tabla de Capacitaciones
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Capacitaciones (
                id_capacitacion INTEGER PRIMARY KEY AUTOINCREMENT,
                id_empleado INTEGER NOT NULL,
                nombre_curso TEXT,
                institucion TEXT,
                fecha_inicio DATE,
                fecha_fin DATE,
                certificado INTEGER DEFAULT 0,
                FOREIGN KEY (id_empleado) REFERENCES Empleados(id_empleado)
            )
        """)
        
        # Tabla de Evaluaciones
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Evaluaciones (
                id_evaluacion INTEGER PRIMARY KEY AUTOINCREMENT,
                id_empleado INTEGER NOT NULL,
                fecha DATE,
                evaluador TEXT,
                puntaje INTEGER,
                observaciones TEXT,
                FOREIGN KEY (id_empleado) REFERENCES Empleados(id_empleado)
            )
        """)
        
        # Tabla de Nómina
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Nomina (
                id_nomina INTEGER PRIMARY KEY AUTOINCREMENT,
                id_empleado INTEGER NOT NULL,
                mes INTEGER,
                anio INTEGER,
                salario_base REAL,
                bonificaciones REAL,
                deducciones REAL,
                salario_neto REAL,
                fecha_pago DATE,
                FOREIGN KEY (id_empleado) REFERENCES Empleados(id_empleado)
            )
        """)
        
        # Tabla de Vacaciones y Permisos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Vacaciones_Permisos (
                id_permiso INTEGER PRIMARY KEY AUTOINCREMENT,
                id_empleado INTEGER NOT NULL,
                tipo TEXT,
                fecha_solicitud DATE,
                fecha_inicio DATE,
                fecha_fin DATE,
                estado TEXT,
                observaciones TEXT,
                FOREIGN KEY (id_empleado) REFERENCES Empleados(id_empleado)
            )
        """)
        
        conn.commit()
        print("Base de datos inicializada correctamente.")


if __name__ == "__main__":
    init_db()

