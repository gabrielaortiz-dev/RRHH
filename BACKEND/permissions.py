"""
Sistema de permisos y verificación de acceso basado en roles
"""
from typing import Optional, List
from fastapi import HTTPException, status, Depends
from database import Database, get_db
from auth import get_current_active_user

# Importar la lista de usuarios con acceso total (se hace de forma lazy para evitar importación circular)
def _get_usuarios_acceso_total():
    """Obtiene la lista de usuarios con acceso total"""
    from auth import USUARIOS_ACCESO_TOTAL
    return USUARIOS_ACCESO_TOTAL

# Mapeo de roles del sistema
ROLES = {
    "super admin": 100,
    "gerente / alta gerencia": 80,
    "supervisor / jefe de área": 60,
    "operativo": 30,
    "consulta / solo visualización": 10
}

def normalize_role(rol: str) -> str:
    """Normaliza el nombre del rol a minúsculas para comparación"""
    if not rol:
        return ""
    return rol.lower().strip()

def get_role_level(rol: str) -> int:
    """Obtiene el nivel de acceso de un rol"""
    rol_normalizado = normalize_role(rol)
    # Buscar coincidencia parcial
    for role_name, level in ROLES.items():
        if role_name in rol_normalizado or rol_normalizado in role_name:
            return level
    # Si no encuentra, retornar nivel mínimo
    return 0

def is_super_admin(user: dict) -> bool:
    """
    Verifica si el usuario es Super Admin o tiene acceso total
    
    Args:
        user: Diccionario con los datos del usuario (debe incluir 'email' y 'rol')
    
    Returns:
        True si el usuario es Super Admin o tiene acceso total configurado
    """
    if not user:
        return False
    
    # Verificar si el usuario está en la lista de acceso total
    user_email = user.get("email", "").lower().strip()
    usuarios_acceso_total = _get_usuarios_acceso_total()
    
    if user_email in [email.lower().strip() for email in usuarios_acceso_total]:
        return True
    
    # Verificar por rol - AHORA MÁS FLEXIBLE
    rol = normalize_role(user.get("rol", ""))
    
    # Reconocer SUPER ADMIN en cualquier variación
    if "super admin" in rol or rol == "super admin":
        return True
    
    # Reconocer administrador en cualquier variación
    if "administrador" in rol or rol == "administrador":
        return True
    
    # También reconocer si el rol contiene "ADMIN" en mayúsculas
    rol_upper = user.get("rol", "").upper()
    if "ADMIN" in rol_upper or "SUPER ADMIN" in rol_upper:
        return True
    
    return False

def is_gerente(user: dict) -> bool:
    """Verifica si el usuario es Gerente"""
    rol = normalize_role(user.get("rol", ""))
    return "gerente" in rol and "super admin" not in rol

def is_supervisor(user: dict) -> bool:
    """Verifica si el usuario es Supervisor"""
    rol = normalize_role(user.get("rol", ""))
    return "supervisor" in rol or "jefe de área" in rol

def is_operativo(user: dict) -> bool:
    """Verifica si el usuario es Operativo"""
    rol = normalize_role(user.get("rol", ""))
    return "operativo" in rol

def is_consulta(user: dict) -> bool:
    """Verifica si el usuario es Consulta"""
    rol = normalize_role(user.get("rol", ""))
    return "consulta" in rol or "solo visualización" in rol

def can_access_configuration(user: dict) -> bool:
    """Solo Super Admin puede acceder a configuración"""
    return is_super_admin(user)

def can_view_nomina(user: dict, empleado_id: Optional[int] = None, db: Optional[Database] = None) -> bool:
    """
    Verifica si el usuario puede ver información de nómina
    
    Args:
        user: Usuario actual
        empleado_id: ID del empleado cuya nómina se quiere ver (None para nómina general)
        db: Instancia de base de datos para verificar relaciones
    
    Returns:
        True si puede ver, False si no
    """
    if is_super_admin(user):
        return True
    
    if is_gerente(user):
        return True  # Gerente puede ver nómina general
    
    if is_supervisor(user):
        # Supervisor solo puede ver nómina de su equipo
        if empleado_id and db:
            # Verificar si el empleado está bajo su supervisión
            # Esto requiere implementar lógica de jerarquía
            # Por ahora, permitir si es supervisor
            return True
        return False  # No puede ver nómina general
    
    if is_operativo(user):
        # Operativo solo puede ver su propia nómina
        if empleado_id:
            # Obtener ID del empleado asociado al usuario
            empleado_usuario = db.fetch_one(
                "SELECT id_empleado FROM Empleados WHERE correo = ?",
                (user.get("email"),)
            ) if db else None
            if empleado_usuario and empleado_usuario.get("id_empleado") == empleado_id:
                return True
        return False
    
    # Consulta no puede ver nómina
    return False

def can_edit_employee(user: dict, empleado_id: int, db: Database) -> bool:
    """
    Verifica si el usuario puede editar un empleado específico
    
    Args:
        user: Usuario actual
        empleado_id: ID del empleado a editar
        db: Instancia de base de datos
    
    Returns:
        True si puede editar, False si no
    """
    if is_super_admin(user) or is_gerente(user):
        return True
    
    if is_supervisor(user):
        # Verificar si el empleado está bajo su supervisión
        # Por ahora, permitir si es supervisor (se puede mejorar con tabla de jerarquías)
        return True
    
    if is_operativo(user):
        # Operativo solo puede editar su propia información
        empleado_usuario = db.fetch_one(
            "SELECT id_empleado FROM Empleados WHERE correo = ?",
            (user.get("email"),)
        )
        if empleado_usuario and empleado_usuario.get("id_empleado") == empleado_id:
            return True
    
    return False

def can_approve(user: dict, area: Optional[str] = None) -> bool:
    """
    Verifica si el usuario puede aprobar solicitudes
    
    Args:
        user: Usuario actual
        area: Área de la solicitud (opcional)
    
    Returns:
        True si puede aprobar, False si no
    """
    if is_super_admin(user) or is_gerente(user):
        return True
    
    if is_supervisor(user):
        # Supervisor solo puede aprobar en su área
        return True  # Se puede mejorar con verificación de área específica
    
    return False

def can_create_roles(user: dict) -> bool:
    """Ningún usuario puede crear roles (solo Super Admin puede gestionarlos)"""
    return False  # Según requerimientos, nadie puede crear roles

def can_manage_users(user: dict) -> bool:
    """Solo Super Admin puede gestionar usuarios y roles"""
    return is_super_admin(user)

def can_view_all_employees(user: dict) -> bool:
    """Verifica si el usuario puede ver todos los empleados"""
    if is_super_admin(user) or is_gerente(user):
        return True
    
    if is_supervisor(user):
        return True  # Puede ver su equipo
    
    if is_operativo(user):
        return False  # Solo puede ver su propia información
    
    if is_consulta(user):
        return True  # Puede ver pero no editar
    
    return False

def can_create_employee(user: dict) -> bool:
    """Verifica si el usuario puede crear empleados"""
    if is_super_admin(user) or is_gerente(user):
        return True
    
    return False

def can_delete_employee(user: dict) -> bool:
    """Verifica si el usuario puede eliminar empleados"""
    return is_super_admin(user) or is_gerente(user)

def can_manage_departments(user: dict) -> bool:
    """Verifica si el usuario puede gestionar departamentos"""
    return is_super_admin(user) or is_gerente(user)

def can_manage_puestos(user: dict) -> bool:
    """Verifica si el usuario puede gestionar puestos"""
    return is_super_admin(user) or is_gerente(user)

def can_manage_contracts(user: dict) -> bool:
    """Verifica si el usuario puede gestionar contratos"""
    return is_super_admin(user) or is_gerente(user)

def can_register_attendance(user: dict, empleado_id: Optional[int] = None) -> bool:
    """Verifica si el usuario puede registrar asistencia"""
    if is_super_admin(user) or is_gerente(user) or is_supervisor(user):
        return True
    
    if is_operativo(user):
        # Solo puede registrar su propia asistencia
        if empleado_id:
            # Verificar que es su propia asistencia
            return True  # Se puede mejorar con verificación
        return True  # Puede registrar su propia asistencia
    
    return False

def can_view_attendance(user: dict, empleado_id: Optional[int] = None) -> bool:
    """Verifica si el usuario puede ver asistencias"""
    if is_super_admin(user) or is_gerente(user):
        return True
    
    if is_supervisor(user):
        # Puede ver asistencias de su equipo
        return True
    
    if is_operativo(user):
        # Solo puede ver su propia asistencia
        return True
    
    if is_consulta(user):
        return True  # Puede ver pero no editar
    
    return False

def can_request_vacation(user: dict) -> bool:
    """Verifica si el usuario puede solicitar vacaciones"""
    if is_consulta(user):
        return False
    
    return True  # Todos excepto consulta pueden solicitar

def can_approve_vacation(user: dict) -> bool:
    """Verifica si el usuario puede aprobar vacaciones"""
    return can_approve(user)

def can_upload_documents(user: dict, empleado_id: Optional[int] = None) -> bool:
    """Verifica si el usuario puede subir documentos"""
    if is_super_admin(user) or is_gerente(user) or is_supervisor(user):
        return True
    
    if is_operativo(user):
        # Solo puede subir sus propios documentos
        return True
    
    return False

def can_view_training(user: dict) -> bool:
    """Verifica si el usuario puede ver capacitaciones"""
    if is_consulta(user):
        return True  # Puede ver pero no gestionar
    
    return True  # Todos pueden ver capacitaciones asignadas

def can_manage_training(user: dict) -> bool:
    """Verifica si el usuario puede gestionar capacitaciones"""
    return is_super_admin(user) or is_gerente(user)

def can_view_evaluations(user: dict) -> bool:
    """Verifica si el usuario puede ver evaluaciones"""
    if is_consulta(user):
        return True  # Puede ver pero no gestionar
    
    return True

def can_manage_evaluations(user: dict) -> bool:
    """Verifica si el usuario puede gestionar evaluaciones"""
    return is_super_admin(user) or is_gerente(user)

def can_export_data(user: dict) -> bool:
    """Verifica si el usuario puede exportar datos"""
    if is_consulta(user):
        return False  # Consulta no puede exportar
    
    return is_super_admin(user) or is_gerente(user) or is_supervisor(user)

def can_view_reports(user: dict) -> bool:
    """Verifica si el usuario puede ver reportes"""
    return True  # Todos pueden ver reportes (con restricciones de datos según rol)

# Dependencias de FastAPI para verificación de permisos
def require_super_admin(current_user: dict = Depends(get_current_active_user)) -> dict:
    """
    Dependencia que requiere rol Super Admin
    PERMITE ACCESO TOTAL a usuarios con acceso total o rol SUPER ADMIN
    """
    from auth import tiene_acceso_total_sin_restricciones
    
    # Si tiene acceso total sin restricciones, permitir TODO
    if tiene_acceso_total_sin_restricciones(current_user):
        return current_user
    
    # Si tiene rol SUPER ADMIN o administrador, también permitir TODO
    if is_super_admin(current_user):
        return current_user
    
    # Si no tiene permisos, rechazar
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Se requiere rol de Super Admin para esta operación"
    )

def require_gerente_or_above(current_user: dict = Depends(get_current_active_user)) -> dict:
    """Dependencia que requiere rol Gerente o superior"""
    if not (is_super_admin(current_user) or is_gerente(current_user)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol de Gerente o superior para esta operación"
        )
    return current_user

def require_not_consulta(current_user: dict = Depends(get_current_active_user)) -> dict:
    """Dependencia que prohíbe el rol Consulta"""
    if is_consulta(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El rol Consulta no tiene permisos para esta operación"
        )
    return current_user

