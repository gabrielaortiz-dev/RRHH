"""
Paquete de modelos para el sistema de RRHH.
"""
from .user import User
from .empleado import Empleado
from .contrato import Contrato
from .asistencia import Asistencia
from .capacitacion import Capacitacion
from .evaluacion import Evaluacion
from .nomina import Nomina
from .vacacion_permiso import VacacionPermiso

__all__ = ['User', 'Empleado', 'Contrato', 'Asistencia', 
           'Capacitacion', 'Evaluacion', 'Nomina', 'VacacionPermiso']

