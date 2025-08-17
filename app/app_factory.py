"""
Módulo para la creación de la aplicación Flask.
"""
from flask import Flask
from config import Config
import os

# Importar extensiones inicializadas
from .extensions import db, login_manager, csrf, migrate, init_extensions
from . import cli

def create_app(config_class=Config):
    """Crea y configura la aplicación Flask."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Asegurar que el directorio de instancia exista
    os.makedirs(app.instance_path, exist_ok=True)
    
    # Configurar directorio para subidas
    upload_folder = os.path.join(app.instance_path, 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = upload_folder

    # Inicializar extensiones
    init_extensions(app)
    
    # Register context processors
    from app.utils.context_processors import inject_template_vars
    app.context_processor(inject_template_vars)
    
    # Configurar Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Debe iniciar sesión para acceder a esta página.'
    login_manager.login_message_category = 'info'
    login_manager.session_protection = 'strong'

    # Registrar blueprints
    register_blueprints(app)
    
    # Registrar comandos CLI
    cli.init_app(app)
    
    # Configurar manejador de usuarios para Flask-Login
    from app.models.models import Usuario
    
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(Usuario, int(user_id))
    
    return app

def register_blueprints(app):
    """Registra todos los blueprints de la aplicación."""
    # Importar blueprints
    from app.controllers.main import main_bp
    from app.controllers.auth import auth_bp
    from app.conteo_impresiones import bp as conteo_impresiones_bp
    from app.controllers.facturas import facturas_bp
    from app.controllers.servicios import servicios_bp
    from app.controllers.tecnicos import tecnicos_bp
    from app.controllers.tecnico_old import tecnico_bp
    from app.controllers.tecnico_dashboard import tecnico_dashboard_bp
    from app.controllers.usuarios import usuarios_bp
    from app.controllers.partes import partes_bp
    from app.controllers.reportes import reportes_bp
    from app.controllers.admin import admin_bp
    from app.controllers.admin_permisos import permisos_bp
    from app.controllers.solicitudes import solicitudes_bp
    from app.controllers.clientes import clientes_bp
    from app.controllers.asignaciones import asignaciones_bp
    from app.controllers.test import test_bp
    from app.controllers.equipos import equipos_bp

    # Registrar blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(conteo_impresiones_bp, url_prefix='/conteo_impresiones')
    app.register_blueprint(facturas_bp, url_prefix='/facturas')
    app.register_blueprint(servicios_bp, url_prefix='/servicios')
    app.register_blueprint(tecnicos_bp, url_prefix='/tecnicos')
    app.register_blueprint(tecnico_bp, url_prefix='/tecnico')
    app.register_blueprint(tecnico_dashboard_bp, url_prefix='/tecnico-dashboard')
    app.register_blueprint(usuarios_bp, url_prefix='/usuarios')
    app.register_blueprint(partes_bp, url_prefix='/partes')
    app.register_blueprint(reportes_bp, url_prefix='/reportes')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(permisos_bp, url_prefix='/admin/permisos')
    app.register_blueprint(solicitudes_bp, url_prefix='/solicitudes')
    app.register_blueprint(clientes_bp, url_prefix='/clientes')
    app.register_blueprint(asignaciones_bp, url_prefix='/asignaciones')
    app.register_blueprint(test_bp, url_prefix='/test')
    app.register_blueprint(equipos_bp, url_prefix='/equipos')
