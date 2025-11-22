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

# Modelo para crear un contrato
class ContratoCreate(BaseModel):
    id_empleado: int = Field(..., description="ID del empleado")
    tipo_contrato: str = Field(..., description="Tipo de contrato: temporal, permanente, honorarios")
    fecha_inicio: str = Field(..., description="Fecha de inicio del contrato (YYYY-MM-DD)")
    fecha_fin: Optional[str] = Field(None, description="Fecha de fin del contrato (YYYY-MM-DD). Opcional para contratos permanentes")
    salario: float = Field(..., description="Salario del contrato")
    condiciones: Optional[str] = Field(None, description="Condiciones adicionales del contrato")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id_empleado": 1,
                "tipo_contrato": "permanente",
                "fecha_inicio": "2025-01-15",
                "fecha_fin": None,
                "salario": 50000.00,
                "condiciones": "Contrato a tiempo completo con beneficios completos"
            }
        }

# Modelo para actualizar un contrato
class ContratoUpdate(BaseModel):
    tipo_contrato: Optional[str] = None
    fecha_inicio: Optional[str] = None
    fecha_fin: Optional[str] = None
    salario: Optional[float] = None
    condiciones: Optional[str] = None

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

