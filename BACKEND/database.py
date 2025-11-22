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
            
            # Tabla de Nómina (expandida)
            self.execute_query('''
                CREATE TABLE IF NOT EXISTS Nomina (
                    id_nomina INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_empleado INTEGER,
                    mes INTEGER NOT NULL,
                    anio INTEGER NOT NULL,
                    periodo TEXT NOT NULL,
                    salario_base DECIMAL(10,2) NOT NULL,
                    total_bonificaciones DECIMAL(10,2) DEFAULT 0,
                    total_deducciones DECIMAL(10,2) DEFAULT 0,
                    salario_neto DECIMAL(10,2) NOT NULL,
                    fecha_pago DATE,
                    estado VARCHAR(20) DEFAULT 'pendiente',
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    fecha_modificacion DATETIME,
                    creado_por INTEGER,
                    modificado_por INTEGER,
                    observaciones TEXT,
                    FOREIGN KEY (id_empleado) REFERENCES Empleados(id_empleado),
                    FOREIGN KEY (creado_por) REFERENCES usuarios(id),
                    FOREIGN KEY (modificado_por) REFERENCES usuarios(id),
                    UNIQUE(id_empleado, mes, anio)
                )
            ''')
            
            # Tabla de Detalles de Bonificaciones en Nómina
            self.execute_query('''
                CREATE TABLE IF NOT EXISTS Nomina_Bonificaciones (
                    id_bonificacion INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_nomina INTEGER NOT NULL,
                    concepto VARCHAR(100) NOT NULL,
                    tipo VARCHAR(50),
                    monto DECIMAL(10,2) NOT NULL,
                    descripcion TEXT,
                    FOREIGN KEY (id_nomina) REFERENCES Nomina(id_nomina) ON DELETE CASCADE
                )
            ''')
            
            # Tabla de Detalles de Deducciones en Nómina
            self.execute_query('''
                CREATE TABLE IF NOT EXISTS Nomina_Deducciones (
                    id_deduccion INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_nomina INTEGER NOT NULL,
                    concepto VARCHAR(100) NOT NULL,
                    tipo VARCHAR(50),
                    monto DECIMAL(10,2) NOT NULL,
                    descripcion TEXT,
                    FOREIGN KEY (id_nomina) REFERENCES Nomina(id_nomina) ON DELETE CASCADE
                )
            ''')
            
            # Tabla de Configuración de Impuestos
            self.execute_query('''
                CREATE TABLE IF NOT EXISTS Config_Impuestos (
                    id_impuesto INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre VARCHAR(100) NOT NULL,
                    tipo VARCHAR(50) NOT NULL,
                    porcentaje DECIMAL(5,2),
                    monto_fijo DECIMAL(10,2),
                    rango_minimo DECIMAL(10,2),
                    rango_maximo DECIMAL(10,2),
                    activo BOOLEAN DEFAULT 1,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    fecha_modificacion DATETIME
                )
            ''')
            
            # Tabla de Configuración de Deducciones
            self.execute_query('''
                CREATE TABLE IF NOT EXISTS Config_Deducciones (
                    id_deduccion_config INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre VARCHAR(100) NOT NULL,
                    tipo VARCHAR(50) NOT NULL,
                    porcentaje DECIMAL(5,2),
                    monto_fijo DECIMAL(10,2),
                    aplica_a_todos BOOLEAN DEFAULT 0,
                    activo BOOLEAN DEFAULT 1,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    fecha_modificacion DATETIME
                )
            ''')
            
            # Tabla de Configuración de Beneficios
            self.execute_query('''
                CREATE TABLE IF NOT EXISTS Config_Beneficios (
                    id_beneficio INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre VARCHAR(100) NOT NULL,
                    tipo VARCHAR(50) NOT NULL,
                    porcentaje DECIMAL(5,2),
                    monto_fijo DECIMAL(10,2),
                    aplica_a_todos BOOLEAN DEFAULT 0,
                    activo BOOLEAN DEFAULT 1,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    fecha_modificacion DATETIME
                )
            ''')
            
            # Tabla de Auditoría de Nómina (trazabilidad)
            self.execute_query('''
                CREATE TABLE IF NOT EXISTS Nomina_Auditoria (
                    id_auditoria INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_nomina INTEGER NOT NULL,
                    accion VARCHAR(50) NOT NULL,
                    usuario_id INTEGER,
                    usuario_nombre VARCHAR(100),
                    campo_modificado VARCHAR(100),
                    valor_anterior TEXT,
                    valor_nuevo TEXT,
                    fecha_modificacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    ip_address VARCHAR(50),
                    FOREIGN KEY (id_nomina) REFERENCES Nomina(id_nomina),
                    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
                )
            ''')
            
            # Tabla de Vacaciones y Permisos (expandida)
            self.execute_query('''
                CREATE TABLE IF NOT EXISTS Vacaciones_Permisos (
                    id_permiso INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_empleado INTEGER NOT NULL,
                    tipo VARCHAR(50) NOT NULL,
                    fecha_solicitud DATE DEFAULT CURRENT_DATE,
                    fecha_inicio DATE NOT NULL,
                    fecha_fin DATE NOT NULL,
                    dias_solicitados INTEGER,
                    dias_disponibles INTEGER,
                    dias_usados INTEGER,
                    dias_acumulados INTEGER,
                    motivo TEXT,
                    estado VARCHAR(20) DEFAULT 'pendiente',
                    aprobado_por_jefe INTEGER,
                    aprobado_por_rrhh INTEGER,
                    fecha_aprobacion_jefe DATETIME,
                    fecha_aprobacion_rrhh DATETIME,
                    fecha_rechazo DATETIME,
                    motivo_rechazo TEXT,
                    observaciones TEXT,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    fecha_modificacion DATETIME,
                    FOREIGN KEY (id_empleado) REFERENCES Empleados(id_empleado),
                    FOREIGN KEY (aprobado_por_jefe) REFERENCES usuarios(id),
                    FOREIGN KEY (aprobado_por_rrhh) REFERENCES usuarios(id)
                )
            ''')
            
            # Tabla de Balance de Vacaciones por Empleado
            self.execute_query('''
                CREATE TABLE IF NOT EXISTS Balance_Vacaciones (
                    id_balance INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_empleado INTEGER NOT NULL,
                    anio INTEGER NOT NULL,
                    dias_totales INTEGER DEFAULT 0,
                    dias_usados INTEGER DEFAULT 0,
                    dias_disponibles INTEGER DEFAULT 0,
                    dias_acumulados INTEGER DEFAULT 0,
                    fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (id_empleado) REFERENCES Empleados(id_empleado),
                    UNIQUE(id_empleado, anio)
                )
            ''')
            
            # Tabla de Notificaciones de Vacaciones
            self.execute_query('''
                CREATE TABLE IF NOT EXISTS Notificaciones_Vacaciones (
                    id_notificacion INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_permiso INTEGER NOT NULL,
                    usuario_id INTEGER NOT NULL,
                    tipo_notificacion VARCHAR(50),
                    mensaje TEXT,
                    leida BOOLEAN DEFAULT 0,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (id_permiso) REFERENCES Vacaciones_Permisos(id_permiso),
                    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
                )
            ''')
            
            # Tabla de Documentos
            self.execute_query('''
                CREATE TABLE IF NOT EXISTS Documentos (
                    id_documento INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_empleado INTEGER,
                    nombre_archivo VARCHAR(255) NOT NULL,
                    nombre_original VARCHAR(255) NOT NULL,
                    tipo_documento VARCHAR(50) NOT NULL,
                    categoria VARCHAR(50),
                    ruta_archivo TEXT NOT NULL,
                    tamano_bytes INTEGER,
                    mime_type VARCHAR(100),
                    fecha_subida DATETIME DEFAULT CURRENT_TIMESTAMP,
                    fecha_expiracion DATE,
                    estado VARCHAR(20) DEFAULT 'activo',
                    subido_por INTEGER,
                    descripcion TEXT,
                    FOREIGN KEY (id_empleado) REFERENCES Empleados(id_empleado),
                    FOREIGN KEY (subido_por) REFERENCES usuarios(id)
                )
            ''')
            
            # Tabla de Permisos de Documentos
            self.execute_query('''
                CREATE TABLE IF NOT EXISTS Documentos_Permisos (
                    id_permiso_doc INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_documento INTEGER NOT NULL,
                    usuario_id INTEGER,
                    rol VARCHAR(50),
                    puede_ver BOOLEAN DEFAULT 1,
                    puede_descargar BOOLEAN DEFAULT 0,
                    puede_eliminar BOOLEAN DEFAULT 0,
                    FOREIGN KEY (id_documento) REFERENCES Documentos(id_documento) ON DELETE CASCADE,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
                )
            ''')
            
            # Tabla de Auditoría de Usuarios (mejorada)
            self.execute_query('''
                CREATE TABLE IF NOT EXISTS Usuarios_Auditoria (
                    id_auditoria INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario_id INTEGER,
                    accion VARCHAR(50) NOT NULL,
                    modulo VARCHAR(50),
                    detalles TEXT,
                    ip_address VARCHAR(50),
                    user_agent TEXT,
                    fecha_accion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
                )
            ''')
            
            # Tabla de Intentos de Login (para bloqueo de cuentas)
            self.execute_query('''
                CREATE TABLE IF NOT EXISTS Login_Intentos (
                    id_intento INTEGER PRIMARY KEY AUTOINCREMENT,
                    email VARCHAR(100) NOT NULL,
                    exitoso BOOLEAN DEFAULT 0,
                    ip_address VARCHAR(50),
                    user_agent TEXT,
                    fecha_intento DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de Configuración del Sistema
            self.execute_query('''
                CREATE TABLE IF NOT EXISTS Config_Sistema (
                    id_config INTEGER PRIMARY KEY AUTOINCREMENT,
                    clave VARCHAR(100) UNIQUE NOT NULL,
                    valor TEXT,
                    tipo VARCHAR(50),
                    descripcion TEXT,
                    categoria VARCHAR(50),
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    fecha_modificacion DATETIME
                )
            ''')
            
            # Tabla de Catálogos
            self.execute_query('''
                CREATE TABLE IF NOT EXISTS Catalogos (
                    id_catalogo INTEGER PRIMARY KEY AUTOINCREMENT,
                    tipo VARCHAR(50) NOT NULL,
                    codigo VARCHAR(50),
                    nombre VARCHAR(100) NOT NULL,
                    descripcion TEXT,
                    activo BOOLEAN DEFAULT 1,
                    orden INTEGER DEFAULT 0,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
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

