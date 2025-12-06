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

# Esquema de seguridad HTTP Bearer
security = HTTPBearer()


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
    except JWTError:
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Database = Depends(get_db)
) -> dict:
    """
    Dependencia de FastAPI para obtener el usuario actual desde el token JWT
    
    Args:
        credentials: Credenciales HTTP Bearer del request
        db: Instancia de la base de datos
    
    Returns:
        Diccionario con los datos del usuario autenticado
    
    Raises:
        HTTPException: Si el token es inválido o el usuario no existe
    """
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id: int = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verificar que el usuario existe y está activo
    usuario = db.fetch_one(
        "SELECT id, nombre, email, rol, activo FROM usuarios WHERE id = ? AND activo = 1",
        (user_id,)
    )
    
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado o inactivo",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
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

