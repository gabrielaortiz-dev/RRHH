"""
Módulo de autenticación con JWT
Implementa autenticación basada en tokens JWT siguiendo buenas prácticas
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from database import get_db, Database

# Configuración de JWT
SECRET_KEY = "tu-clave-secreta-super-segura-cambiar-en-produccion"  # Cambiar en producción
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 horas

# Lista de emails con acceso total (sin importar el rol)
# Estos usuarios tienen acceso completo a TODO sin restricciones
# IMPORTANTE: Todos los usuarios con rol "SUPER ADMIN" también tienen acceso total automáticamente
USUARIOS_ACCESO_TOTAL = [
    "admin@rrhh.com",  # Usuario admin por defecto
    "admin@empresa.hn",  # Otro admin
    # CUALQUIER usuario con rol "SUPER ADMIN" tiene acceso total automáticamente
    # No necesitas agregarlos aquí, pero puedes agregar más si quieres
]

# Esquema de seguridad HTTP Bearer - Mejorado para manejar mejor los errores
security = HTTPBearer(auto_error=False)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un token JWT de acceso
    
    Args:
        data: Diccionario con los datos a incluir en el token (ej: {"sub": user_id})
        expires_delta: Tiempo de expiración del token. Si es None, usa el tiempo por defecto
    
    Returns:
        Token JWT codificado como string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """
    Verifica y decodifica un token JWT
    
    Args:
        token: Token JWT a verificar
    
    Returns:
        Diccionario con los datos del token si es válido, None si no lo es
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Error al verificar token JWT: {str(e)}")
        return None


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Database = Depends(get_db)
) -> dict:
    """
    Dependencia de FastAPI para obtener el usuario actual desde el token JWT
    
    Args:
        credentials: Credenciales HTTP Bearer del request (opcional si auto_error=False)
        db: Instancia de la base de datos
    
    Returns:
        Diccionario con los datos del usuario autenticado
    
    Raises:
        HTTPException: Si el token es inválido, no se proporciona, o el usuario no existe
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Verificar que se proporcionó un token
    if credentials is None:
        logger.warning("Intento de acceso sin token de autenticación")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    # Validar que el token no esté vacío
    if not token or not token.strip():
        logger.warning("Token vacío o inválido")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logger.debug(f"Token recibido: {token[:30]}... (longitud: {len(token)})")
    
    # Verificar y decodificar el token
    payload = verify_token(token)
    
    if payload is None:
        logger.warning("Token inválido o no se pudo decodificar")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logger.debug(f"Token decodificado correctamente. Payload: {payload}")
    
    # El estándar JWT requiere que 'sub' sea una cadena
    user_id_str = payload.get("sub")
    if user_id_str is None:
        logger.warning("Token no contiene 'sub' (user ID)")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token inválido: falta información de usuario",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Convertir sub (que es string) a int para la consulta
    try:
        user_id: int = int(user_id_str)
    except (ValueError, TypeError):
        logger.warning(f"Token contiene 'sub' inválido: {user_id_str}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token inválido: ID de usuario no válido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verificar que el usuario existe y está activo
    # IMPORTANTE: Siempre obtenemos el rol de la base de datos para asegurar que esté actualizado
    usuario = db.fetch_one(
        "SELECT id, nombre, email, rol, activo FROM usuarios WHERE id = ? AND activo = 1",
        (user_id,)
    )
    
    if usuario is None:
        logger.warning(f"Usuario con ID {user_id} no encontrado o inactivo")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario no encontrado o inactivo",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Asegurar que el rol viene de la base de datos, no del token JWT
    # Esto permite que los cambios de rol se reflejen inmediatamente sin necesidad de re-login
    logger.info(f"Usuario autenticado: {usuario['email']} (rol: {usuario['rol']})")
    return usuario


async def get_current_active_user(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Dependencia para verificar que el usuario está activo
    """
    if current_user.get("activo") != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )
    return current_user


def tiene_acceso_total_sin_restricciones(user: dict) -> bool:
    """
    Verifica si el usuario tiene acceso total SIN RESTRICCIONES
    Estos usuarios pueden hacer CUALQUIER cosa sin importar permisos
    
    Args:
        user: Diccionario con los datos del usuario (debe incluir 'email')
    
    Returns:
        True si el usuario tiene acceso total sin restricciones
    """
    if not user:
        return False
    
    user_email = user.get("email", "").lower().strip()
    
    # Verificar si está en la lista de acceso total
    if user_email in [email.lower().strip() for email in USUARIOS_ACCESO_TOTAL]:
        return True
    
    return False


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Database = Depends(get_db)
) -> Optional[dict]:
    """
    Dependencia de FastAPI para obtener el usuario actual desde el token JWT (opcional)
    No lanza error si no hay token, simplemente retorna None
    
    Args:
        credentials: Credenciales HTTP Bearer del request (opcional)
        db: Instancia de la base de datos
    
    Returns:
        Diccionario con los datos del usuario autenticado, o None si no hay token válido
    """
    # Si no hay credenciales, retornar None (no es un error)
    if credentials is None:
        return None
    
    token = credentials.credentials
    
    # Si el token está vacío, retornar None
    if not token or not token.strip():
        return None
    
    # Verificar y decodificar el token
    payload = verify_token(token)
    
    if payload is None:
        return None
    
    # Obtener el ID del usuario del token
    user_id_str = payload.get("sub")
    if user_id_str is None:
        return None
    
    # Convertir sub a int
    try:
        user_id: int = int(user_id_str)
    except (ValueError, TypeError):
        return None
    
    # Verificar que el usuario existe y está activo
    usuario = db.fetch_one(
        "SELECT id, nombre, email, rol, activo FROM usuarios WHERE id = ? AND activo = 1",
        (user_id,)
    )
    
    if usuario is None:
        return None
    
    return {
        "id": usuario["id"],
        "nombre": usuario["nombre"],
        "email": usuario["email"],
        "rol": usuario["rol"],
        "activo": usuario["activo"]
    }


def require_role(allowed_roles: list[str]):
    """
    Decorador/función para verificar roles de usuario
    
    Args:
        allowed_roles: Lista de roles permitidos
    
    Returns:
        Función de dependencia de FastAPI
    """
    async def role_checker(current_user: dict = Depends(get_current_active_user)) -> dict:
        user_role = current_user.get("rol", "").lower()
        if user_role not in [role.lower() for role in allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Se requiere uno de los siguientes roles: {', '.join(allowed_roles)}"
            )
        return current_user
    
    return role_checker

