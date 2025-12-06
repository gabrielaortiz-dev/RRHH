"""
Modelos Pydantic para validación de datos
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

# Modelo para crear un nuevo usuario
class UsuarioCreate(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100, description="Nombre completo del usuario")
    email: EmailStr = Field(..., description="Email único del usuario")
    password: str = Field(..., min_length=6, max_length=255, description="Contraseña del usuario")
    rol: str = Field(default="empleado", description="Rol del usuario (administrador, supervisor, empleado)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "nombre": "Juan Pérez",
                "email": "juan.perez@empresa.com",
                "password": "password123",
                "rol": "empleado"
            }
        }

# Modelo para actualizar un usuario existente
class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6, max_length=255)
    rol: Optional[str] = None
    activo: Optional[bool] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "nombre": "Juan Pérez Actualizado",
                "email": "juan.nuevo@empresa.com",
                "rol": "supervisor"
            }
        }

# Modelo de respuesta de usuario (sin password)
class UsuarioResponse(BaseModel):
    id: int
    nombre: str
    email: str
    rol: str
    fecha_creacion: str
    activo: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "nombre": "Juan Pérez",
                "email": "juan.perez@empresa.com",
                "rol": "empleado",
                "fecha_creacion": "2025-11-15 14:53:12",
                "activo": 1
            }
        }

# Modelo para login
class UsuarioLogin(BaseModel):
    email: EmailStr
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "admin@rrhh.com",
                "password": "admin123"
            }
        }

# Modelo para crear departamento
class DepartamentoCreate(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100)
    descripcion: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "nombre": "Tecnología",
                "descripcion": "Departamento de desarrollo y sistemas"
            }
        }

# Modelo para actualizar departamento
class DepartamentoUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    descripcion: Optional[str] = None
    activo: Optional[bool] = None

# Modelo para crear empleado
class EmpleadoCreate(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100)
    apellido: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    telefono: Optional[str] = None
    departamento_id: int
    puesto: str
    fecha_ingreso: str
    salario: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "nombre": "María",
                "apellido": "García",
                "email": "maria.garcia@empresa.com",
                "telefono": "555-1234",
                "departamento_id": 1,
                "puesto": "Analista",
                "fecha_ingreso": "2025-01-15",
                "salario": 35000.00
            }
        }

# Modelo para actualizar empleado
class EmpleadoUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    email: Optional[EmailStr] = None
    telefono: Optional[str] = None
    departamento_id: Optional[int] = None
    puesto: Optional[str] = None
    fecha_ingreso: Optional[str] = None
    salario: Optional[float] = None
    activo: Optional[bool] = None

# ============================================================================
#                           MODELOS DE CONTRATOS
# ============================================================================

# Modelo para crear un contrato completo
class ContratoCreate(BaseModel):
    id_empleado: int = Field(..., description="ID del empleado")
    
    # Datos del Empleador
    empresa_nombre: Optional[str] = Field(None, description="Nombre legal de la empresa")
    empresa_representante_legal: Optional[str] = Field(None, description="Representante legal de la empresa")
    empresa_rtn: Optional[str] = Field(None, description="Número de identificación tributaria (RTN)")
    empresa_direccion: Optional[str] = Field(None, description="Dirección de la empresa")
    empresa_telefono: Optional[str] = Field(None, description="Teléfono de la empresa")
    empresa_email: Optional[str] = Field(None, description="Correo electrónico de la empresa")
    
    # Datos del Trabajador
    trabajador_nombre_completo: Optional[str] = Field(None, description="Nombre completo del trabajador")
    trabajador_dni: Optional[str] = Field(None, description="Documento de identidad (DNI)")
    trabajador_nacionalidad: Optional[str] = Field(None, description="Nacionalidad del trabajador")
    trabajador_estado_civil: Optional[str] = Field(None, description="Estado civil")
    trabajador_direccion: Optional[str] = Field(None, description="Dirección del trabajador")
    trabajador_telefono: Optional[str] = Field(None, description="Teléfono del trabajador")
    trabajador_email: Optional[str] = Field(None, description="Correo electrónico del trabajador")
    
    # Datos del Puesto
    nombre_puesto: Optional[str] = Field(None, description="Nombre del puesto")
    descripcion_puesto: Optional[str] = Field(None, description="Descripción de funciones y responsabilidades")
    id_departamento: Optional[int] = Field(None, description="ID del departamento")
    jefe_inmediato: Optional[str] = Field(None, description="Nombre del jefe inmediato")
    
    # Condiciones de Trabajo
    tipo_contrato: str = Field(..., description="Tipo: tiempo_indefinido, tiempo_determinado, obra_proyecto, por_horas")
    jornada_laboral_dias: Optional[str] = Field(None, description="Días a trabajar (ej: Lunes a Viernes)")
    horario_entrada: Optional[str] = Field(None, description="Horario de entrada (HH:MM)")
    horario_salida: Optional[str] = Field(None, description="Horario de salida (HH:MM)")
    tiempo_descanso: Optional[str] = Field(None, description="Tiempo de descanso")
    lugar_trabajo: Optional[str] = Field(None, description="Lugar de trabajo")
    
    # Remuneración
    salario_base: float = Field(..., description="Salario base")
    forma_pago: Optional[str] = Field(None, description="Forma de pago: semanal, quincenal, mensual")
    metodo_pago: Optional[str] = Field(None, description="Método: transferencia, efectivo, cheque")
    bonificaciones: Optional[str] = Field(None, description="Bonificaciones adicionales")
    comisiones: Optional[str] = Field(None, description="Comisiones")
    incentivos: Optional[str] = Field(None, description="Incentivos")
    deducciones: Optional[str] = Field(None, description="Deducciones aplicables")
    
    # Duración
    fecha_inicio: str = Field(..., description="Fecha de inicio (YYYY-MM-DD)")
    fecha_fin: Optional[str] = Field(None, description="Fecha de fin (YYYY-MM-DD). Opcional para contratos permanentes")
    periodo_prueba_dias: Optional[int] = Field(None, description="Periodo de prueba en días")
    
    # Derechos y Obligaciones
    derechos_empleado: Optional[str] = Field(None, description="Derechos del empleado")
    obligaciones_empleado: Optional[str] = Field(None, description="Obligaciones del empleado")
    derechos_empleador: Optional[str] = Field(None, description="Derechos del empleador")
    obligaciones_empleador: Optional[str] = Field(None, description="Obligaciones del empleador")
    
    # Beneficios Legales
    vacaciones_anuales: Optional[int] = Field(None, description="Días de vacaciones anuales")
    aguinaldo: Optional[bool] = Field(True, description="Incluye aguinaldo/décimo tercer mes")
    prestaciones_sociales: Optional[str] = Field(None, description="Prestaciones sociales")
    dias_feriados: Optional[str] = Field(None, description="Días feriados")
    permisos_ley: Optional[str] = Field(None, description="Permisos de ley")
    
    # Confidencialidad
    clausula_confidencialidad: Optional[str] = Field(None, description="Cláusula de confidencialidad")
    politica_datos: Optional[str] = Field(None, description="Política de tratamiento de datos")
    no_competencia: Optional[str] = Field(None, description="Cláusula de no competencia")
    
    # Terminación
    causas_terminacion: Optional[str] = Field(None, description="Causas válidas de terminación")
    tiempo_preaviso: Optional[int] = Field(None, description="Tiempo de preaviso en días")
    pago_prestaciones: Optional[str] = Field(None, description="Pago de prestaciones")
    
    # Cláusulas Adicionales
    politica_uniformes: Optional[str] = Field(None, description="Política de uniformes")
    uso_vehiculos: Optional[str] = Field(None, description="Uso de vehículos o herramientas")
    trabajo_remoto: Optional[str] = Field(None, description="Trabajo remoto (si aplica)")
    politica_horas_extras: Optional[str] = Field(None, description="Política de horas extras")
    uso_sistemas: Optional[str] = Field(None, description="Uso de sistemas y equipos")
    
    # Campo adicional para compatibilidad
    salario: Optional[float] = Field(None, description="Salario (alias de salario_base)")
    condiciones: Optional[str] = Field(None, description="Condiciones adicionales del contrato")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id_empleado": 1,
                "empresa_nombre": "Empresa S.A.",
                "empresa_representante_legal": "Juan Pérez",
                "empresa_rtn": "1234567890123",
                "trabajador_nombre_completo": "María González",
                "trabajador_dni": "0801-1990-12345",
                "nombre_puesto": "Desarrollador Senior",
                "tipo_contrato": "tiempo_indefinido",
                "salario_base": 50000.00,
                "fecha_inicio": "2025-01-15"
            }
        }

# Modelo para actualizar un contrato
class ContratoUpdate(BaseModel):
    # Todos los campos son opcionales para actualización
    empresa_nombre: Optional[str] = None
    empresa_representante_legal: Optional[str] = None
    empresa_rtn: Optional[str] = None
    empresa_direccion: Optional[str] = None
    empresa_telefono: Optional[str] = None
    empresa_email: Optional[str] = None
    trabajador_nombre_completo: Optional[str] = None
    trabajador_dni: Optional[str] = None
    trabajador_nacionalidad: Optional[str] = None
    trabajador_estado_civil: Optional[str] = None
    trabajador_direccion: Optional[str] = None
    trabajador_telefono: Optional[str] = None
    trabajador_email: Optional[str] = None
    nombre_puesto: Optional[str] = None
    descripcion_puesto: Optional[str] = None
    id_departamento: Optional[int] = None
    jefe_inmediato: Optional[str] = None
    tipo_contrato: Optional[str] = None
    jornada_laboral_dias: Optional[str] = None
    horario_entrada: Optional[str] = None
    horario_salida: Optional[str] = None
    tiempo_descanso: Optional[str] = None
    lugar_trabajo: Optional[str] = None
    salario_base: Optional[float] = None
    salario: Optional[float] = None  # Alias
    forma_pago: Optional[str] = None
    metodo_pago: Optional[str] = None
    bonificaciones: Optional[str] = None
    comisiones: Optional[str] = None
    incentivos: Optional[str] = None
    deducciones: Optional[str] = None
    fecha_inicio: Optional[str] = None
    fecha_fin: Optional[str] = None
    periodo_prueba_dias: Optional[int] = None
    derechos_empleado: Optional[str] = None
    obligaciones_empleado: Optional[str] = None
    derechos_empleador: Optional[str] = None
    obligaciones_empleador: Optional[str] = None
    vacaciones_anuales: Optional[int] = None
    aguinaldo: Optional[bool] = None
    prestaciones_sociales: Optional[str] = None
    dias_feriados: Optional[str] = None
    permisos_ley: Optional[str] = None
    clausula_confidencialidad: Optional[str] = None
    politica_datos: Optional[str] = None
    no_competencia: Optional[str] = None
    causas_terminacion: Optional[str] = None
    tiempo_preaviso: Optional[int] = None
    pago_prestaciones: Optional[str] = None
    politica_uniformes: Optional[str] = None
    uso_vehiculos: Optional[str] = None
    trabajo_remoto: Optional[str] = None
    politica_horas_extras: Optional[str] = None
    uso_sistemas: Optional[str] = None
    condiciones: Optional[str] = None
    estado: Optional[str] = None

# ============================================================================
#                           MODELOS DE ASISTENCIAS
# ============================================================================

# Modelo para crear/registrar una asistencia
class AsistenciaCreate(BaseModel):
    id_empleado: int = Field(..., description="ID del empleado")
    fecha: str = Field(..., description="Fecha de la asistencia (YYYY-MM-DD)")
    hora_entrada: Optional[str] = Field(None, description="Hora de entrada (HH:MM:SS)")
    hora_salida: Optional[str] = Field(None, description="Hora de salida (HH:MM:SS)")
    observaciones: Optional[str] = Field(None, description="Justificaciones u observaciones")
    metodo_registro: Optional[str] = Field("manual", description="Método de registro: manual o biometrico")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id_empleado": 1,
                "fecha": "2025-01-15",
                "hora_entrada": "08:00:00",
                "hora_salida": "17:00:00",
                "observaciones": "Llegada puntual",
                "metodo_registro": "manual"
            }
        }

# Modelo para actualizar una asistencia
class AsistenciaUpdate(BaseModel):
    hora_entrada: Optional[str] = None
    hora_salida: Optional[str] = None
    observaciones: Optional[str] = None

# Modelo para reporte de asistencias por rango de fechas
class AsistenciaReporteRequest(BaseModel):
    id_empleado: Optional[int] = Field(None, description="ID del empleado (opcional, si no se proporciona se obtienen todos)")
    fecha_inicio: str = Field(..., description="Fecha de inicio del rango (YYYY-MM-DD)")
    fecha_fin: str = Field(..., description="Fecha de fin del rango (YYYY-MM-DD)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id_empleado": 1,
                "fecha_inicio": "2025-01-01",
                "fecha_fin": "2025-01-31"
            }
        }

# ============================================================================
#                           MODELOS DE NÓMINA
# ============================================================================

# Modelo para bonificación en nómina
class BonificacionItem(BaseModel):
    concepto: str
    tipo: Optional[str] = None
    monto: float
    descripcion: Optional[str] = None

# Modelo para deducción en nómina
class DeduccionItem(BaseModel):
    concepto: str
    tipo: Optional[str] = None
    monto: float
    descripcion: Optional[str] = None

# Modelo para crear nómina
class NominaCreate(BaseModel):
    id_empleado: int
    mes: int = Field(..., ge=1, le=12)
    anio: int = Field(..., ge=2000, le=2100)
    salario_base: float = Field(..., gt=0)
    bonificaciones: Optional[list[BonificacionItem]] = []
    deducciones: Optional[list[DeduccionItem]] = []
    fecha_pago: Optional[str] = None
    observaciones: Optional[str] = None

# Modelo para actualizar nómina
class NominaUpdate(BaseModel):
    salario_base: Optional[float] = None
    bonificaciones: Optional[list[BonificacionItem]] = None
    deducciones: Optional[list[DeduccionItem]] = None
    fecha_pago: Optional[str] = None
    estado: Optional[str] = None
    observaciones: Optional[str] = None

# Modelo para configuración de impuestos
class ConfigImpuestoCreate(BaseModel):
    nombre: str
    tipo: str
    porcentaje: Optional[float] = None
    monto_fijo: Optional[float] = None
    rango_minimo: Optional[float] = None
    rango_maximo: Optional[float] = None

# Modelo para configuración de deducciones
class ConfigDeduccionCreate(BaseModel):
    nombre: str
    tipo: str
    porcentaje: Optional[float] = None
    monto_fijo: Optional[float] = None
    aplica_a_todos: bool = False

# Modelo para configuración de beneficios
class ConfigBeneficioCreate(BaseModel):
    nombre: str
    tipo: str
    porcentaje: Optional[float] = None
    monto_fijo: Optional[float] = None
    aplica_a_todos: bool = False

# ============================================================================
#                    MODELOS DE VACACIONES Y PERMISOS
# ============================================================================

# Modelo para crear solicitud de vacaciones/permisos
class VacacionPermisoCreate(BaseModel):
    id_empleado: int
    tipo: str
    fecha_inicio: str
    fecha_fin: str
    motivo: Optional[str] = None
    observaciones: Optional[str] = None

# Modelo para actualizar solicitud
class VacacionPermisoUpdate(BaseModel):
    estado: Optional[str] = None
    motivo_rechazo: Optional[str] = None
    observaciones: Optional[str] = None

# Modelo para aprobar/rechazar
class VacacionPermisoAprobacion(BaseModel):
    aprobar: bool
    motivo: Optional[str] = None
    nivel: str = Field(..., description="jefe o rrhh")

# ============================================================================
#                           MODELOS DE DOCUMENTOS
# ============================================================================

# Modelo para subir documento
class DocumentoCreate(BaseModel):
    id_empleado: int
    tipo_documento: str
    categoria: Optional[str] = None
    descripcion: Optional[str] = None
    fecha_expiracion: Optional[str] = None

# Modelo para actualizar documento
class DocumentoUpdate(BaseModel):
    tipo_documento: Optional[str] = None
    categoria: Optional[str] = None
    descripcion: Optional[str] = None
    fecha_expiracion: Optional[str] = None
    estado: Optional[str] = None

# Modelo para permisos de documento
class DocumentoPermisoCreate(BaseModel):
    usuario_id: Optional[int] = None
    rol: Optional[str] = None
    puede_ver: bool = True
    puede_descargar: bool = False
    puede_eliminar: bool = False

# ============================================================================
#                           MODELOS DE PUESTOS
# ============================================================================

# Modelo para crear un puesto
class PuestoCreate(BaseModel):
    nombre_puesto: str = Field(..., min_length=2, max_length=100, description="Nombre del puesto")
    nivel: Optional[str] = Field(None, max_length=50, description="Nivel del puesto (Junior, Senior, etc.)")
    salario_base: Optional[float] = Field(None, ge=0, description="Salario base del puesto")
    
    class Config:
        json_schema_extra = {
            "example": {
                "nombre_puesto": "Desarrollador Senior",
                "nivel": "Senior",
                "salario_base": 45000.00
            }
        }

# Modelo para actualizar un puesto
class PuestoUpdate(BaseModel):
    nombre_puesto: Optional[str] = Field(None, min_length=2, max_length=100)
    nivel: Optional[str] = Field(None, max_length=50)
    salario_base: Optional[float] = Field(None, ge=0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "nombre_puesto": "Desarrollador Senior",
                "nivel": "Senior",
                "salario_base": 50000.00
            }
        }

# ============================================================================
#                           MODELOS DE CAPACITACIONES
# ============================================================================

# Modelo para crear una capacitación
class CapacitacionCreate(BaseModel):
    id_empleado: int = Field(..., description="ID del empleado")
    nombre_curso: str = Field(..., min_length=2, max_length=100, description="Nombre del curso o capacitación")
    institucion: Optional[str] = Field(None, max_length=100, description="Institución que imparte el curso")
    fecha_inicio: str = Field(..., description="Fecha de inicio (YYYY-MM-DD)")
    fecha_fin: Optional[str] = Field(None, description="Fecha de finalización (YYYY-MM-DD)")
    certificado: Optional[bool] = Field(False, description="Si obtuvo certificado")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id_empleado": 1,
                "nombre_curso": "Python Avanzado",
                "institucion": "Platzi",
                "fecha_inicio": "2025-01-01",
                "fecha_fin": "2025-03-01",
                "certificado": True
            }
        }

# Modelo para actualizar una capacitación
class CapacitacionUpdate(BaseModel):
    nombre_curso: Optional[str] = Field(None, min_length=2, max_length=100)
    institucion: Optional[str] = Field(None, max_length=100)
    fecha_inicio: Optional[str] = None
    fecha_fin: Optional[str] = None
    certificado: Optional[bool] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "nombre_curso": "Python Avanzado - Actualizado",
                "certificado": True
            }
        }

# ============================================================================
#                           MODELOS DE EVALUACIONES
# ============================================================================

# Modelo para crear una evaluación
class EvaluacionCreate(BaseModel):
    id_empleado: int = Field(..., description="ID del empleado evaluado")
    fecha: str = Field(..., description="Fecha de la evaluación (YYYY-MM-DD)")
    evaluador: str = Field(..., min_length=2, max_length=100, description="Nombre del evaluador")
    puntaje: int = Field(..., ge=0, le=100, description="Puntaje obtenido (0-100)")
    observaciones: Optional[str] = Field(None, description="Observaciones o comentarios de la evaluación")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id_empleado": 1,
                "fecha": "2025-01-15",
                "evaluador": "Carlos Gómez",
                "puntaje": 85,
                "observaciones": "Excelente desempeño en el último trimestre"
            }
        }

# Modelo para actualizar una evaluación
class EvaluacionUpdate(BaseModel):
    fecha: Optional[str] = None
    evaluador: Optional[str] = Field(None, min_length=2, max_length=100)
    puntaje: Optional[int] = Field(None, ge=0, le=100)
    observaciones: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "puntaje": 90,
                "observaciones": "Mejora significativa observada"
            }
        }

# ============================================================================
#                           MODELOS DE ROLES Y PERMISOS
# ============================================================================

# Modelo para crear un rol
class RolCreate(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=50, description="Nombre del rol")
    descripcion: Optional[str] = Field(None, description="Descripción del rol")
    id_puesto: Optional[int] = Field(None, description="ID del puesto vinculado (opcional)")
    nivel_acceso: int = Field(default=1, ge=1, le=100, description="Nivel de acceso (1-100)")
    permisos: Optional[list[int]] = Field(default=[], description="Lista de IDs de permisos a asignar")
    
    class Config:
        json_schema_extra = {
            "example": {
                "nombre": "gerente",
                "descripcion": "Gerente de departamento con acceso amplio",
                "id_puesto": 5,
                "nivel_acceso": 70,
                "permisos": [1, 2, 3, 5, 8]
            }
        }

# Modelo para actualizar un rol
class RolUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=50)
    descripcion: Optional[str] = None
    id_puesto: Optional[int] = None
    nivel_acceso: Optional[int] = Field(None, ge=1, le=100)
    activo: Optional[bool] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "descripcion": "Gerente de departamento - acceso actualizado",
                "nivel_acceso": 75
            }
        }

# Modelo para asignar permisos a un rol
class AsignarPermisosRol(BaseModel):
    permisos: list[int] = Field(..., description="Lista de IDs de permisos")
    reemplazar: bool = Field(default=False, description="Si es True, reemplaza todos los permisos. Si es False, agrega a los existentes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "permisos": [1, 2, 3, 5, 8, 10],
                "reemplazar": True
            }
        }

# Modelo para asignar rol a usuario
class AsignarRolUsuario(BaseModel):
    usuario_id: int = Field(..., description="ID del usuario")
    id_rol: int = Field(..., description="ID del rol a asignar")
    es_principal: bool = Field(default=True, description="Si es el rol principal del usuario")
    fecha_expiracion: Optional[str] = Field(None, description="Fecha de expiración del rol (YYYY-MM-DD)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "usuario_id": 5,
                "id_rol": 2,
                "es_principal": True
            }
        }

# Modelo para crear permisos personalizados
class PermisoCreate(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=100)
    descripcion: Optional[str] = None
    modulo: str = Field(..., max_length=50)
    accion: str = Field(..., max_length=50)
    codigo: str = Field(..., max_length=100, description="Código único (ej: empleados.crear)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "nombre": "Exportar empleados",
                "descripcion": "Permite exportar la lista de empleados a Excel",
                "modulo": "empleados",
                "accion": "exportar",
                "codigo": "empleados.exportar"
            }
        }

# Modelo para sincronizar empleado con usuario
class SincronizarEmpleadoUsuario(BaseModel):
    id_empleado: int = Field(..., description="ID del empleado")
    crear_usuario: bool = Field(default=False, description="Crear usuario si no existe")
    password_temporal: Optional[str] = Field(None, description="Contraseña temporal (si se crea usuario)")
    asignar_rol_automatico: bool = Field(default=True, description="Asignar rol basado en el puesto del empleado")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id_empleado": 10,
                "crear_usuario": True,
                "password_temporal": "Temporal123!",
                "asignar_rol_automatico": True
            }
        }

# Modelo para respuesta de permisos de usuario
class PermisosUsuarioResponse(BaseModel):
    usuario_id: int
    nombre_usuario: str
    roles: list[dict]
    permisos_rol: list[dict]
    permisos_especiales: list[dict]
    permisos_totales: list[str]

# ============================================================================
#                           MODELOS DE NOTIFICACIONES
# ============================================================================

# Modelo para crear una notificación
class NotificacionCreate(BaseModel):
    usuario_id: int = Field(..., description="ID del usuario destinatario")
    tipo: str = Field(..., description="Tipo: info, success, warning, error, approval, request, reminder, expiration")
    titulo: str = Field(..., min_length=1, max_length=200, description="Título de la notificación")
    mensaje: str = Field(..., min_length=1, max_length=1000, description="Mensaje descriptivo")
    modulo: Optional[str] = Field(None, max_length=50, description="Módulo relacionado")
    modulo_id: Optional[str] = Field(None, max_length=100, description="ID del elemento del módulo")
    redirect_url: Optional[str] = Field(None, max_length=500, description="URL de redirección")
    metadata: Optional[str] = Field(None, description="Datos adicionales en formato JSON")
    
    class Config:
        json_schema_extra = {
            "example": {
                "usuario_id": 1,
                "tipo": "info",
                "titulo": "Nueva solicitud de vacaciones",
                "mensaje": "Juan Pérez ha solicitado vacaciones del 1 al 5 de febrero",
                "modulo": "vacations",
                "modulo_id": "123",
                "redirect_url": "/vacaciones/123"
            }
        }

# Modelo para actualizar una notificación
class NotificacionUpdate(BaseModel):
    is_read: Optional[bool] = Field(None, description="Marcar como leída/no leída")
    read_at: Optional[str] = Field(None, description="Fecha de lectura")
    
    class Config:
        json_schema_extra = {
            "example": {
                "is_read": True
            }
        }

# Modelo para configuración de notificaciones de usuario
class NotificacionConfigCreate(BaseModel):
    usuario_id: int = Field(..., description="ID del usuario")
    email_notifications: bool = Field(default=True, description="Recibir notificaciones por email")
    enabled_types: Optional[str] = Field(None, description="Tipos habilitados (JSON array)")
    enabled_modules: Optional[str] = Field(None, description="Módulos habilitados (JSON array)")
    email: Optional[str] = Field(None, description="Email para notificaciones")
    
    class Config:
        json_schema_extra = {
            "example": {
                "usuario_id": 1,
                "email_notifications": True,
                "enabled_types": '["info", "success", "warning"]',
                "enabled_modules": '["employees", "vacations"]',
                "email": "usuario@empresa.com"
            }
        }

# Modelo para actualizar configuración de notificaciones
class NotificacionConfigUpdate(BaseModel):
    email_notifications: Optional[bool] = None
    enabled_types: Optional[str] = None
    enabled_modules: Optional[str] = None
    email: Optional[str] = None

