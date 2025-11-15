import sqlite3
import os
from typing import Optional

# Ruta de la base de datos
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'rrhh.db')

class Database:
    """Clase para manejar la conexión a SQLite"""
    
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
        
    def connect(self):
        """Establecer conexión a la base de datos"""
        try:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row  # Para obtener resultados como diccionarios
            # Habilitar foreign keys en SQLite
            self.connection.execute("PRAGMA foreign_keys = ON")
            print(f"[OK] Conexion exitosa a la base de datos: {self.db_path}")
            return self.connection
        except sqlite3.Error as e:
            print(f"[ERROR] Error al conectar a la base de datos: {e}")
            raise
    
    def disconnect(self):
        """Cerrar conexión a la base de datos"""
        if self.connection:
            self.connection.close()
            print("[OK] Conexion cerrada")
    
    def execute_query(self, query: str, params: tuple = ()):
        """Ejecutar una consulta SQL"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            return cursor
        except sqlite3.Error as e:
            print(f"[ERROR] Error al ejecutar query: {e}")
            self.connection.rollback()
            raise
    
    def fetch_all(self, query: str, params: tuple = ()):
        """Obtener todos los resultados de una consulta"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            # Convertir Row objects a diccionarios
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            print(f"[ERROR] Error al obtener datos: {e}")
            raise
    
    def fetch_one(self, query: str, params: tuple = ()):
        """Obtener un solo resultado de una consulta"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            print(f"[ERROR] Error al obtener datos: {e}")
            raise
    
    def create_tables(self):
        """Crear las tablas necesarias para el sistema de RRHH"""
        try:
            # Tabla de usuarios
            self.execute_query('''
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre VARCHAR(100) NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    rol VARCHAR(50) DEFAULT 'empleado',
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    activo BOOLEAN DEFAULT 1
                )
            ''')
            
            # Tabla de departamentos
            self.execute_query('''
                CREATE TABLE IF NOT EXISTS departamentos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre VARCHAR(100) NOT NULL,
                    descripcion TEXT,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    activo BOOLEAN DEFAULT 1
                )
            ''')
            
            # Tabla de empleados
            self.execute_query('''
                CREATE TABLE IF NOT EXISTS empleados (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre VARCHAR(100) NOT NULL,
                    apellido VARCHAR(100) NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    telefono VARCHAR(20),
                    departamento_id INTEGER,
                    puesto VARCHAR(100),
                    fecha_ingreso DATE,
                    salario DECIMAL(10, 2),
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    activo BOOLEAN DEFAULT 1,
                    FOREIGN KEY (departamento_id) REFERENCES departamentos(id)
                )
            ''')
            
            # Tabla de asistencias
            self.execute_query('''
                CREATE TABLE IF NOT EXISTS asistencias (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    empleado_id INTEGER NOT NULL,
                    fecha DATE NOT NULL,
                    hora_entrada TIME,
                    hora_salida TIME,
                    estado VARCHAR(50) DEFAULT 'presente',
                    observaciones TEXT,
                    FOREIGN KEY (empleado_id) REFERENCES empleados(id)
                )
            ''')
            
            # Tabla de notificaciones
            self.execute_query('''
                CREATE TABLE IF NOT EXISTS notificaciones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario_id INTEGER,
                    titulo VARCHAR(200) NOT NULL,
                    mensaje TEXT NOT NULL,
                    tipo VARCHAR(50) DEFAULT 'info',
                    leido BOOLEAN DEFAULT 0,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
                )
            ''')
            
            # Tabla de Departamentos (nueva estructura)
            self.execute_query('''
                CREATE TABLE IF NOT EXISTS Departamentos (
                    id_departamento INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre_departamento VARCHAR(100) NOT NULL,
                    descripcion TEXT
                )
            ''')
            
            # Tabla de Puestos
            self.execute_query('''
                CREATE TABLE IF NOT EXISTS Puestos (
                    id_puesto INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre_puesto VARCHAR(100) NOT NULL,
                    nivel VARCHAR(50),
                    salario_base DECIMAL(10,2)
                )
            ''')
            
            # Tabla de Empleados (nueva estructura)
            self.execute_query('''
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
            
            # Tabla de Contratos
            self.execute_query('''
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
            ''')
            
            # Tabla de Asistencias (nueva estructura)
            self.execute_query('''
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
            
            # Tabla de Capacitaciones
            self.execute_query('''
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
            ''')
            
            # Tabla de Evaluaciones
            self.execute_query('''
                CREATE TABLE IF NOT EXISTS Evaluaciones (
                    id_evaluacion INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_empleado INTEGER,
                    fecha DATE,
                    evaluador VARCHAR(100),
                    puntaje INTEGER,
                    observaciones TEXT,
                    FOREIGN KEY (id_empleado) REFERENCES Empleados(id_empleado)
                )
            ''')
            
            # Tabla de Nómina
            self.execute_query('''
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
            ''')
            
            # Tabla de Vacaciones y Permisos
            self.execute_query('''
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
            
            print("[OK] Tablas creadas exitosamente")
            
        except sqlite3.Error as e:
            print(f"[ERROR] Error al crear tablas: {e}")
            raise


# Instancia global de la base de datos
db = Database()

def get_db():
    """Función helper para obtener la conexión a la base de datos"""
    if not db.connection:
        db.connect()
        db.create_tables()
    return db

def init_db():
    """Inicializar la base de datos"""
    db.connect()
    db.create_tables()
    return db

