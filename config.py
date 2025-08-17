import os
from datetime import timedelta


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-servicio-tecnico-2024'

    # Base de datos SQLite en el directorio principal
    basedir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(basedir, "instance/servicio_tecnico.db")
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'sqlite:///{db_path}?check_same_thread=False'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'connect_args': {
            'timeout': 30,
            'check_same_thread': False
        }
    }

    # Configuración de sesiones
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)

    # Configuración de paginación
    POSTS_PER_PAGE = 10

    # Configuración de archivos
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
