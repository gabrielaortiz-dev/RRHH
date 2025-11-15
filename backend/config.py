"""
Configuración de la aplicación Flask por entornos.
Maneja las variables de entorno para desarrollo, producción y testing.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno desde archivo .env
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)


class Config:
    """Configuración base compartida por todos los entornos."""
    
    # Directorio base de la aplicación
    BASE_DIR = Path(__file__).parent
    
    # Configuración de la base de datos
    DATABASE_DIR = BASE_DIR / 'database'
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'rrhh.db')
    DATABASE_PATH = DATABASE_DIR / DATABASE_NAME
    
    # Configuración de seguridad
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Configuración de CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:4200').split(',')
    
    # Configuración del servidor
    HOST = os.getenv('HOST', '127.0.0.1')
    PORT = int(os.getenv('PORT', 5000))
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Configuración de logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'app.log')
    
    # Configuración de JWT (si se implementa autenticación)
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))  # 1 hora
    
    # Configuración de paginación
    ITEMS_PER_PAGE = int(os.getenv('ITEMS_PER_PAGE', 10))
    
    @staticmethod
    def init_app(app):
        """Inicializa la aplicación con la configuración."""
        # Asegurar que el directorio de la base de datos existe
        Config.DATABASE_DIR.mkdir(exist_ok=True)


class DevelopmentConfig(Config):
    """Configuración para el entorno de desarrollo."""
    
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    
    # En desarrollo, permitir más orígenes CORS
    CORS_ORIGINS = ['http://localhost:4200', 'http://127.0.0.1:4200', 'http://localhost:3000']


class ProductionConfig(Config):
    """Configuración para el entorno de producción."""
    
    DEBUG = False
    LOG_LEVEL = 'WARNING'
    
    # En producción, usar SECRET_KEY obligatorio
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY or SECRET_KEY == 'dev-secret-key-change-in-production':
        raise ValueError(
            "SECRET_KEY debe estar configurada en producción. "
            "Establece la variable de entorno SECRET_KEY."
        )
    
    # CORS más restrictivo en producción
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '').split(',')
    if not CORS_ORIGINS or CORS_ORIGINS == ['']:
        raise ValueError(
            "CORS_ORIGINS debe estar configurada en producción. "
            "Establece la variable de entorno CORS_ORIGINS."
        )


class TestingConfig(Config):
    """Configuración para el entorno de testing."""
    
    DEBUG = True
    TESTING = True
    
    # Base de datos de prueba en memoria o archivo temporal
    DATABASE_NAME = 'test_rrhh.db'
    DATABASE_PATH = Path('/tmp') / DATABASE_NAME
    
    # CORS permisivo para testing
    CORS_ORIGINS = ['*']


# Diccionario de configuraciones disponibles
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config():
    """
    Obtiene la configuración según el entorno actual.
    
    Returns:
        Config: Clase de configuración correspondiente al entorno
    """
    env = os.getenv('FLASK_ENV', 'development').lower()
    return config.get(env, config['default'])

