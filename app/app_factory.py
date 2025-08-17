"""
Módulo para la creación y configuración de la aplicación Flask.

Este módulo proporciona una fábrica de aplicaciones que configura e inicializa
la aplicación Flask con todas sus extensiones, blueprints y manejadores de errores.
"""
import os
from flask import Flask
from config import Config

# Importar extensiones
from .extensions import db, login_manager, csrf, migrate, init_extensions
from . import cli


def create_app(config_class=Config):
    """
    Crea y configura la aplicación Flask.
    
    Args:
        config_class: Clase de configuración que hereda de Config
        
    Returns:
        Flask: Instancia de la aplicación Flask configurada
    """
    # Crear la aplicación Flask
    app = Flask(__name__)
    
    # Cargar configuración
    app.config.from_object(config_class)
    
    # Configuración de directorios
    _configure_directories(app)
    
    # Inicializar extensiones
    init_extensions(app)
    
    # Configurar contexto de la aplicación
    _configure_app_context(app)
    
    # Configurar manejadores de errores
    _configure_error_handlers(app)
    
    # Registrar blueprints
    from app.controllers import register_blueprints
    register_blueprints(app)
    
    # Registrar comandos CLI personalizados
    cli.init_app(app)
    
    return app


def _configure_directories(app):
    """Configura los directorios necesarios para la aplicación."""
    # Asegurar que el directorio de instancia exista
    os.makedirs(app.instance_path, exist_ok=True)
    
    # Configurar directorio para subidas de archivos
    upload_folder = os.path.join(app.instance_path, 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = upload_folder
    
    # Crear directorio para archivos temporales
    temp_folder = os.path.join(app.instance_path, 'temp')
    os.makedirs(temp_folder, exist_ok=True)
    app.config['TEMP_FOLDER'] = temp_folder


def _configure_app_context(app):
    """Configura el contexto de la aplicación."""
    # Configurar Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Debe iniciar sesión para acceder a esta página.'
    login_manager.login_message_category = 'info'
    login_manager.session_protection = 'strong'
    
    # Registrar procesadores de contexto
    from app.utils.context_processors import inject_template_vars
    app.context_processor(inject_template_vars)
    
    # Configurar manejador de usuarios para Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.models import Usuario
        return db.session.get(Usuario, int(user_id))


def _configure_error_handlers(app):
    """Configura los manejadores de errores globales."""
    # Importar manejadores de errores
    from app.controllers.error_handlers import register_error_handlers
    
    # Registrar manejadores de errores personalizados
    register_error_handlers(app)
    
    # Configurar logging
    if not app.debug and not app.testing:
        import logging
        from logging.handlers import RotatingFileHandler
        
        # Crear directorio de logs si no existe
        log_dir = os.path.join(app.root_path, '..', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        # Configurar el manejador de archivos rotativos
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, 'app.log'),
            maxBytes=10240,
            backupCount=10
        )
        
        # Configurar el formato del log
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        
        # Configurar el nivel de log
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        # Establecer el nivel de log de la aplicación
        app.logger.setLevel(logging.INFO)
        app.logger.info('Inicio de la aplicación')
