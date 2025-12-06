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
        # Si ya hay una conexión activa, verificar que esté válida
        if self.connection:
            try:
                # Verificar que la conexión esté activa
                self.connection.execute("SELECT 1")
                return self.connection
            except (sqlite3.Error, AttributeError):
                # La conexión está cerrada o inválida, crear una nueva
                try:
                    self.connection.close()
                except:
                    pass
                self.connection = None
        
        try:
            # Agregar timeout para evitar bloqueos (20 segundos)
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False, timeout=20.0)
            self.connection.row_factory = sqlite3.Row  # Para obtener resultados como diccionarios
            # Habilitar WAL mode para permitir lecturas concurrentes
            self.connection.execute("PRAGMA journal_mode=WAL")
            # Habilitar foreign keys en SQLite
            self.connection.execute("PRAGMA foreign_keys = ON")
            print(f"[OK] Conexion exitosa a la base de datos: {self.db_path}")
            return self.connection
        except sqlite3.Error as e:
            print(f"[ERROR] Error al conectar a la base de datos: {e}")
            self.connection = None
            raise
    
    def disconnect(self):
        """Cerrar conexión a la base de datos"""
        if self.connection:
            self.connection.close()
            print("[OK] Conexion cerrada")
    
    def execute_query(self, query: str, params: tuple = (), max_retries: int = 3):
        """Ejecutar una consulta SQL con reintentos para manejar bloqueos"""
        import time
        
        for intento in range(max_retries):
            try:
                # Asegurar conexión activa
                if not self.connection:
                    self.connect()
                else:
                    # Verificar que la conexión esté activa
                    try:
                        self.connection.execute("SELECT 1")
                    except (sqlite3.Error, AttributeError):
                        # Reconectar si la conexión se perdió
                        self.connect()
                
                cursor = self.connection.cursor()
                cursor.execute(query, params)
                self.connection.commit()
                return cursor
                
            except sqlite3.OperationalError as e:
                error_msg = str(e).lower()
                if "locked" in error_msg and intento < max_retries - 1:
                    # Esperar antes de reintentar (backoff exponencial)
                    wait_time = (intento + 1) * 0.5
                    print(f"[ADVERTENCIA] Base de datos bloqueada, reintentando en {wait_time}s... (intento {intento + 1}/{max_retries})")
                    time.sleep(wait_time)
                    # Cerrar y reconectar
                    try:
                        if self.connection:
                            self.connection.close()
                    except:
                        pass
                    self.connection = None
                    continue
                else:
                    print(f"[ERROR] Error al ejecutar query: {e}")
                    if self.connection:
                        try:
                            self.connection.rollback()
                        except:
                            pass
                    raise
            except sqlite3.Error as e:
                print(f"[ERROR] Error al ejecutar query: {e}")
                if self.connection:
                    try:
                        self.connection.rollback()
                    except:
                        pass
                raise
        
        # Si llegamos aquí, todos los reintentos fallaron
        raise sqlite3.OperationalError("Base de datos bloqueada después de múltiples intentos")
    
    def fetch_all(self, query: str, params: tuple = ()):
        """Obtener todos los resultados de una consulta"""
        # Asegurar conexión activa
        if not self.connection:
            self.connect()
        else:
            # Verificar que la conexión esté activa
            try:
                self.connection.execute("SELECT 1")
            except (sqlite3.Error, AttributeError):
                # Reconectar si la conexión se perdió
                self.connect()
        
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
        # Asegurar conexión activa
        if not self.connection:
            self.connect()
        else:
            # Verificar que la conexión esté activa
            try:
                self.connection.execute("SELECT 1")
            except (sqlite3.Error, AttributeError):
                # Reconectar si la conexión se perdió
                self.connect()
        
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
        # Asegurar conexión activa
        if not self.connection:
            self.connect()
        else:
            # Verificar que la conexión esté activa
            try:
                self.connection.execute("SELECT 1")
            except (sqlite3.Error, AttributeError):
                # Reconectar si la conexión se perdió
                self.connect()
        
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
            
            # Tabla de Contratos (estructura completa)
            self.execute_query('''
                CREATE TABLE IF NOT EXISTS Contratos (
                    id_contrato INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_empleado INTEGER NOT NULL,
                    
                    -- Datos del Empleador
                    empresa_nombre VARCHAR(200),
                    empresa_representante_legal VARCHAR(200),
                    empresa_rtn VARCHAR(50),
                    empresa_direccion TEXT,
                    empresa_telefono VARCHAR(20),
                    empresa_email VARCHAR(100),
                    
                    -- Datos del Trabajador
                    trabajador_nombre_completo VARCHAR(200),
                    trabajador_dni VARCHAR(50),
                    trabajador_nacionalidad VARCHAR(100),
                    trabajador_estado_civil VARCHAR(50),
                    trabajador_direccion TEXT,
                    trabajador_telefono VARCHAR(20),
                    trabajador_email VARCHAR(100),
                    
                    -- Datos del Puesto
                    nombre_puesto VARCHAR(100),
                    descripcion_puesto TEXT,
                    id_departamento INTEGER,
                    jefe_inmediato VARCHAR(200),
                    
                    -- Condiciones de Trabajo
                    tipo_contrato VARCHAR(50),
                    jornada_laboral_dias VARCHAR(100),
                    horario_entrada TIME,
                    horario_salida TIME,
                    tiempo_descanso VARCHAR(100),
                    lugar_trabajo TEXT,
                    
                    -- Remuneración
                    salario_base DECIMAL(10,2),
                    forma_pago VARCHAR(50),
                    metodo_pago VARCHAR(50),
                    bonificaciones TEXT,
                    comisiones TEXT,
                    incentivos TEXT,
                    deducciones TEXT,
                    
                    -- Duración
                    fecha_inicio DATE NOT NULL,
                    fecha_fin DATE,
                    periodo_prueba_dias INTEGER,
                    
                    -- Derechos y Obligaciones
                    derechos_empleado TEXT,
                    obligaciones_empleado TEXT,
                    derechos_empleador TEXT,
                    obligaciones_empleador TEXT,
                    
                    -- Beneficios Legales
                    vacaciones_anuales INTEGER,
                    aguinaldo BOOLEAN DEFAULT 1,
                    prestaciones_sociales TEXT,
                    dias_feriados TEXT,
                    permisos_ley TEXT,
                    
                    -- Confidencialidad
                    clausula_confidencialidad TEXT,
                    politica_datos TEXT,
                    no_competencia TEXT,
                    
                    -- Terminación
                    causas_terminacion TEXT,
                    tiempo_preaviso INTEGER,
                    pago_prestaciones TEXT,
                    
                    -- Cláusulas Adicionales
                    politica_uniformes TEXT,
                    uso_vehiculos TEXT,
                    trabajo_remoto TEXT,
                    politica_horas_extras TEXT,
                    uso_sistemas TEXT,
                    
                    -- Campos adicionales del sistema
                    condiciones TEXT,
                    estado VARCHAR(50) DEFAULT 'activo',
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    fecha_modificacion DATETIME,
                    
                    FOREIGN KEY (id_empleado) REFERENCES Empleados(id_empleado),
                    FOREIGN KEY (id_departamento) REFERENCES Departamentos(id_departamento)
                )
            ''')
            
            # Intentar agregar nuevas columnas si la tabla ya existe (migración)
            try:
                # Verificar si las nuevas columnas existen, si no, agregarlas
                cursor = self.connection.cursor()
                cursor.execute("PRAGMA table_info(Contratos)")
                columnas_existentes = [col[1] for col in cursor.fetchall()]
                
                nuevas_columnas = [
                    ("empresa_nombre", "VARCHAR(200)"),
                    ("empresa_representante_legal", "VARCHAR(200)"),
                    ("empresa_rtn", "VARCHAR(50)"),
                    ("empresa_direccion", "TEXT"),
                    ("empresa_telefono", "VARCHAR(20)"),
                    ("empresa_email", "VARCHAR(100)"),
                    ("trabajador_nombre_completo", "VARCHAR(200)"),
                    ("trabajador_dni", "VARCHAR(50)"),
                    ("trabajador_nacionalidad", "VARCHAR(100)"),
                    ("trabajador_estado_civil", "VARCHAR(50)"),
                    ("trabajador_direccion", "TEXT"),
                    ("trabajador_telefono", "VARCHAR(20)"),
                    ("trabajador_email", "VARCHAR(100)"),
                    ("nombre_puesto", "VARCHAR(100)"),
                    ("descripcion_puesto", "TEXT"),
                    ("id_departamento", "INTEGER"),
                    ("jefe_inmediato", "VARCHAR(200)"),
                    ("jornada_laboral_dias", "VARCHAR(100)"),
                    ("horario_entrada", "TIME"),
                    ("horario_salida", "TIME"),
                    ("tiempo_descanso", "VARCHAR(100)"),
                    ("lugar_trabajo", "TEXT"),
                    ("salario_base", "DECIMAL(10,2)"),
                    ("forma_pago", "VARCHAR(50)"),
                    ("metodo_pago", "VARCHAR(50)"),
                    ("bonificaciones", "TEXT"),
                    ("comisiones", "TEXT"),
                    ("incentivos", "TEXT"),
                    ("deducciones", "TEXT"),
                    ("periodo_prueba_dias", "INTEGER"),
                    ("derechos_empleado", "TEXT"),
                    ("obligaciones_empleado", "TEXT"),
                    ("derechos_empleador", "TEXT"),
                    ("obligaciones_empleador", "TEXT"),
                    ("vacaciones_anuales", "INTEGER"),
                    ("aguinaldo", "BOOLEAN DEFAULT 1"),
                    ("prestaciones_sociales", "TEXT"),
                    ("dias_feriados", "TEXT"),
                    ("permisos_ley", "TEXT"),
                    ("clausula_confidencialidad", "TEXT"),
                    ("politica_datos", "TEXT"),
                    ("no_competencia", "TEXT"),
                    ("causas_terminacion", "TEXT"),
                    ("tiempo_preaviso", "INTEGER"),
                    ("pago_prestaciones", "TEXT"),
                    ("politica_uniformes", "TEXT"),
                    ("uso_vehiculos", "TEXT"),
                    ("trabajo_remoto", "TEXT"),
                    ("politica_horas_extras", "TEXT"),
                    ("uso_sistemas", "TEXT"),
                    ("estado", "VARCHAR(50) DEFAULT 'activo'"),
                    ("fecha_creacion", "DATETIME DEFAULT CURRENT_TIMESTAMP"),
                    ("fecha_modificacion", "DATETIME")
                ]
                
                for columna, tipo in nuevas_columnas:
                    if columna not in columnas_existentes:
                        try:
                            self.execute_query(f"ALTER TABLE Contratos ADD COLUMN {columna} {tipo}")
                        except Exception as e:
                            # Ignorar si la columna ya existe o hay otro error
                            pass
            except Exception as e:
                # Si hay error en la migración, continuar
                pass
            
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
            
            # Tabla de Roles del Sistema (vinculados a Puestos)
            self.execute_query('''
                CREATE TABLE IF NOT EXISTS Roles (
                    id_rol INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre VARCHAR(50) UNIQUE NOT NULL,
                    descripcion TEXT,
                    id_puesto INTEGER,
                    nivel_acceso INTEGER DEFAULT 1,
                    es_sistema BOOLEAN DEFAULT 0,
                    activo BOOLEAN DEFAULT 1,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    fecha_modificacion DATETIME,
                    FOREIGN KEY (id_puesto) REFERENCES Puestos(id_puesto)
                )
            ''')
            
            # Tabla de Permisos (acciones que se pueden realizar)
            self.execute_query('''
                CREATE TABLE IF NOT EXISTS Permisos (
                    id_permiso INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre VARCHAR(100) UNIQUE NOT NULL,
                    descripcion TEXT,
                    modulo VARCHAR(50) NOT NULL,
                    accion VARCHAR(50) NOT NULL,
                    codigo VARCHAR(100) UNIQUE NOT NULL,
                    activo BOOLEAN DEFAULT 1,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de Roles_Permisos (relación muchos a muchos)
            self.execute_query('''
                CREATE TABLE IF NOT EXISTS Roles_Permisos (
                    id_rol_permiso INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_rol INTEGER NOT NULL,
                    id_permiso INTEGER NOT NULL,
                    concedido BOOLEAN DEFAULT 1,
                    fecha_asignacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (id_rol) REFERENCES Roles(id_rol) ON DELETE CASCADE,
                    FOREIGN KEY (id_permiso) REFERENCES Permisos(id_permiso) ON DELETE CASCADE,
                    UNIQUE(id_rol, id_permiso)
                )
            ''')
            
            # Tabla de Usuarios_Roles (un usuario puede tener múltiples roles)
            self.execute_query('''
                CREATE TABLE IF NOT EXISTS Usuarios_Roles (
                    id_usuario_rol INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario_id INTEGER NOT NULL,
                    id_rol INTEGER NOT NULL,
                    es_principal BOOLEAN DEFAULT 0,
                    fecha_asignacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    fecha_expiracion DATETIME,
                    activo BOOLEAN DEFAULT 1,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
                    FOREIGN KEY (id_rol) REFERENCES Roles(id_rol) ON DELETE CASCADE,
                    UNIQUE(usuario_id, id_rol)
                )
            ''')
            
            # Tabla de Permisos Especiales de Usuario (permisos específicos por usuario)
            self.execute_query('''
                CREATE TABLE IF NOT EXISTS Usuarios_Permisos (
                    id_usuario_permiso INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario_id INTEGER NOT NULL,
                    id_permiso INTEGER NOT NULL,
                    concedido BOOLEAN DEFAULT 1,
                    razon TEXT,
                    fecha_asignacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    fecha_expiracion DATETIME,
                    asignado_por INTEGER,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
                    FOREIGN KEY (id_permiso) REFERENCES Permisos(id_permiso) ON DELETE CASCADE,
                    FOREIGN KEY (asignado_por) REFERENCES usuarios(id),
                    UNIQUE(usuario_id, id_permiso)
                )
            ''')
            
            # Tabla de Historial de Cambios de Roles
            self.execute_query('''
                CREATE TABLE IF NOT EXISTS Historial_Roles (
                    id_historial INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario_id INTEGER NOT NULL,
                    id_rol_anterior INTEGER,
                    id_rol_nuevo INTEGER,
                    motivo TEXT,
                    realizado_por INTEGER,
                    fecha_cambio DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
                    FOREIGN KEY (id_rol_anterior) REFERENCES Roles(id_rol),
                    FOREIGN KEY (id_rol_nuevo) REFERENCES Roles(id_rol),
                    FOREIGN KEY (realizado_por) REFERENCES usuarios(id)
                )
            ''')
            
            # Insertar roles del sistema por defecto (solo si no existen)
            try:
                # Verificar si ya existen roles
                roles_existentes = self.fetch_all("SELECT COUNT(*) as count FROM Roles")
                if roles_existentes[0]['count'] == 0:
                    # Roles predeterminados del sistema
                    roles_default = [
                        ('administrador', 'Acceso total al sistema - Control completo', None, 100, 1),
                        ('rrhh', 'Gestión de Recursos Humanos - Empleados, nómina, documentos', None, 80, 1),
                        ('supervisor', 'Supervisor de departamento - Gestión de equipo y reportes', None, 60, 1),
                        ('empleado', 'Empleado estándar - Acceso básico', None, 20, 1),
                        ('invitado', 'Acceso de solo lectura', None, 10, 1)
                    ]
                    
                    for rol in roles_default:
                        self.execute_query("""
                            INSERT INTO Roles (nombre, descripcion, id_puesto, nivel_acceso, es_sistema)
                            VALUES (?, ?, ?, ?, ?)
                        """, rol)
                    
                    print("[OK] Roles del sistema creados")
            except Exception as e:
                print(f"[INFO] Los roles ya existen o error al crearlos: {e}")
            
            # Insertar permisos del sistema por defecto
            try:
                permisos_existentes = self.fetch_all("SELECT COUNT(*) as count FROM Permisos")
                if permisos_existentes[0]['count'] == 0:
                    # Permisos predeterminados
                    permisos_default = [
                        # Usuarios
                        ('Ver usuarios', 'Visualizar lista de usuarios', 'usuarios', 'ver', 'usuarios.ver'),
                        ('Crear usuarios', 'Crear nuevos usuarios', 'usuarios', 'crear', 'usuarios.crear'),
                        ('Editar usuarios', 'Modificar usuarios existentes', 'usuarios', 'editar', 'usuarios.editar'),
                        ('Eliminar usuarios', 'Desactivar o eliminar usuarios', 'usuarios', 'eliminar', 'usuarios.eliminar'),
                        ('Gestionar roles', 'Asignar y gestionar roles de usuarios', 'usuarios', 'roles', 'usuarios.roles'),
                        
                        # Empleados
                        ('Ver empleados', 'Visualizar lista de empleados', 'empleados', 'ver', 'empleados.ver'),
                        ('Crear empleados', 'Registrar nuevos empleados', 'empleados', 'crear', 'empleados.crear'),
                        ('Editar empleados', 'Modificar información de empleados', 'empleados', 'editar', 'empleados.editar'),
                        ('Eliminar empleados', 'Desactivar empleados', 'empleados', 'eliminar', 'empleados.eliminar'),
                        
                        # Departamentos
                        ('Ver departamentos', 'Visualizar departamentos', 'departamentos', 'ver', 'departamentos.ver'),
                        ('Gestionar departamentos', 'Crear y editar departamentos', 'departamentos', 'gestionar', 'departamentos.gestionar'),
                        
                        # Puestos
                        ('Ver puestos', 'Visualizar puestos', 'puestos', 'ver', 'puestos.ver'),
                        ('Gestionar puestos', 'Crear y editar puestos', 'puestos', 'gestionar', 'puestos.gestionar'),
                        
                        # Contratos
                        ('Ver contratos', 'Visualizar contratos', 'contratos', 'ver', 'contratos.ver'),
                        ('Crear contratos', 'Generar nuevos contratos', 'contratos', 'crear', 'contratos.crear'),
                        ('Editar contratos', 'Modificar contratos', 'contratos', 'editar', 'contratos.editar'),
                        ('Eliminar contratos', 'Anular contratos', 'contratos', 'eliminar', 'contratos.eliminar'),
                        
                        # Asistencias
                        ('Ver asistencias', 'Visualizar registros de asistencia', 'asistencias', 'ver', 'asistencias.ver'),
                        ('Registrar asistencias', 'Registrar entradas y salidas', 'asistencias', 'registrar', 'asistencias.registrar'),
                        ('Editar asistencias', 'Modificar registros de asistencia', 'asistencias', 'editar', 'asistencias.editar'),
                        
                        # Nómina
                        ('Ver nómina', 'Visualizar información de nómina', 'nomina', 'ver', 'nomina.ver'),
                        ('Crear nómina', 'Generar nómina', 'nomina', 'crear', 'nomina.crear'),
                        ('Editar nómina', 'Modificar nómina', 'nomina', 'editar', 'nomina.editar'),
                        ('Aprobar nómina', 'Aprobar pagos de nómina', 'nomina', 'aprobar', 'nomina.aprobar'),
                        
                        # Vacaciones
                        ('Ver vacaciones', 'Visualizar solicitudes de vacaciones', 'vacaciones', 'ver', 'vacaciones.ver'),
                        ('Solicitar vacaciones', 'Crear solicitudes de vacaciones', 'vacaciones', 'solicitar', 'vacaciones.solicitar'),
                        ('Aprobar vacaciones', 'Aprobar o rechazar vacaciones', 'vacaciones', 'aprobar', 'vacaciones.aprobar'),
                        
                        # Capacitaciones
                        ('Ver capacitaciones', 'Visualizar capacitaciones', 'capacitaciones', 'ver', 'capacitaciones.ver'),
                        ('Gestionar capacitaciones', 'Crear y editar capacitaciones', 'capacitaciones', 'gestionar', 'capacitaciones.gestionar'),
                        
                        # Evaluaciones
                        ('Ver evaluaciones', 'Visualizar evaluaciones', 'evaluaciones', 'ver', 'evaluaciones.ver'),
                        ('Crear evaluaciones', 'Realizar evaluaciones de desempeño', 'evaluaciones', 'crear', 'evaluaciones.crear'),
                        ('Editar evaluaciones', 'Modificar evaluaciones', 'evaluaciones', 'editar', 'evaluaciones.editar'),
                        
                        # Documentos
                        ('Ver documentos', 'Visualizar documentos', 'documentos', 'ver', 'documentos.ver'),
                        ('Subir documentos', 'Cargar nuevos documentos', 'documentos', 'subir', 'documentos.subir'),
                        ('Eliminar documentos', 'Eliminar documentos', 'documentos', 'eliminar', 'documentos.eliminar'),
                        
                        # Reportes
                        ('Ver reportes', 'Visualizar reportes', 'reportes', 'ver', 'reportes.ver'),
                        ('Generar reportes', 'Crear reportes personalizados', 'reportes', 'generar', 'reportes.generar'),
                        ('Exportar reportes', 'Exportar reportes a PDF/Excel', 'reportes', 'exportar', 'reportes.exportar'),
                        
                        # Configuración
                        ('Ver configuración', 'Ver configuración del sistema', 'configuracion', 'ver', 'configuracion.ver'),
                        ('Modificar configuración', 'Cambiar configuración del sistema', 'configuracion', 'modificar', 'configuracion.modificar'),
                        
                        # Auditoría
                        ('Ver auditoría', 'Visualizar logs de auditoría', 'auditoria', 'ver', 'auditoria.ver'),
                    ]
                    
                    for permiso in permisos_default:
                        self.execute_query("""
                            INSERT INTO Permisos (nombre, descripcion, modulo, accion, codigo)
                            VALUES (?, ?, ?, ?, ?)
                        """, permiso)
                    
                    print("[OK] Permisos del sistema creados")
            except Exception as e:
                print(f"[INFO] Los permisos ya existen o error al crearlos: {e}")
            
            # Asignar permisos a roles del sistema
            try:
                # Obtener IDs de roles
                rol_admin = self.fetch_one("SELECT id_rol FROM Roles WHERE nombre = 'administrador'")
                rol_rrhh = self.fetch_one("SELECT id_rol FROM Roles WHERE nombre = 'rrhh'")
                rol_supervisor = self.fetch_one("SELECT id_rol FROM Roles WHERE nombre = 'supervisor'")
                rol_empleado = self.fetch_one("SELECT id_rol FROM Roles WHERE nombre = 'empleado'")
                
                if rol_admin:
                    # Administrador tiene TODOS los permisos
                    permisos = self.fetch_all("SELECT id_permiso FROM Permisos")
                    for permiso in permisos:
                        try:
                            self.execute_query("""
                                INSERT OR IGNORE INTO Roles_Permisos (id_rol, id_permiso)
                                VALUES (?, ?)
                            """, (rol_admin['id_rol'], permiso['id_permiso']))
                        except:
                            pass
                
                if rol_rrhh:
                    # RRHH tiene casi todos los permisos excepto configuración del sistema
                    permisos_rrhh = self.fetch_all("""
                        SELECT id_permiso FROM Permisos 
                        WHERE modulo NOT IN ('configuracion', 'auditoria')
                           OR codigo = 'auditoria.ver'
                    """)
                    for permiso in permisos_rrhh:
                        try:
                            self.execute_query("""
                                INSERT OR IGNORE INTO Roles_Permisos (id_rol, id_permiso)
                                VALUES (?, ?)
                            """, (rol_rrhh['id_rol'], permiso['id_permiso']))
                        except:
                            pass
                
                if rol_supervisor:
                    # Supervisor tiene permisos de gestión de su equipo
                    permisos_supervisor = self.fetch_all("""
                        SELECT id_permiso FROM Permisos 
                        WHERE accion IN ('ver', 'editar', 'aprobar', 'registrar', 'crear')
                          AND modulo IN ('empleados', 'asistencias', 'vacaciones', 'evaluaciones', 'reportes')
                    """)
                    for permiso in permisos_supervisor:
                        try:
                            self.execute_query("""
                                INSERT OR IGNORE INTO Roles_Permisos (id_rol, id_permiso)
                                VALUES (?, ?)
                            """, (rol_supervisor['id_rol'], permiso['id_permiso']))
                        except:
                            pass
                
                if rol_empleado:
                    # Empleado solo puede ver su información
                    permisos_empleado = self.fetch_all("""
                        SELECT id_permiso FROM Permisos 
                        WHERE accion = 'ver' OR codigo IN ('vacaciones.solicitar', 'asistencias.registrar')
                    """)
                    for permiso in permisos_empleado:
                        try:
                            self.execute_query("""
                                INSERT OR IGNORE INTO Roles_Permisos (id_rol, id_permiso)
                                VALUES (?, ?)
                            """, (rol_empleado['id_rol'], permiso['id_permiso']))
                        except:
                            pass
                
                print("[OK] Permisos asignados a roles")
            except Exception as e:
                print(f"[INFO] Error al asignar permisos a roles: {e}")
            
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

