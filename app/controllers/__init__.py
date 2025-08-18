"""
Módulo de controladores de la aplicación.

Este módulo importa y registra todos los blueprints de la aplicación,
asegurando que todas las rutas estén disponibles.
"""
from flask import Flask
from app.decorators import role_required, permission_required

# Importar blueprints
from .admin import admin_bp
from .auth_controller import auth_bp
from .clientes_controller import clientes_bp
from .equipos_controller import equipos_bp
from .facturas_controller import facturas_bp
from .partes import partes_bp
from .pedidos_controller import pedidos_bp
from .reportes_controller import reportes_bp
from .solicitudes_controller import solicitudes_bp
from .tecnicos import tecnicos_bp
from .asignaciones import asignaciones_bp
from .tecnico_dashboard import tecnico_dashboard_bp

# Importar controladores para asegurar el registro de blueprints
from . import (
    admin,
    auth_controller,
    clientes_controller,
    equipos_controller,
    facturas_controller,
    partes,
    pedidos_controller,
    reportes_controller,
    solicitudes_controller,
    tecnicos,
    asignaciones,
    tecnico_dashboard
)
from .test import test_bp  # Solo para desarrollo

# Lista de blueprints para registro
BLUEPRINTS = [
    admin_bp,
    auth_bp,
    clientes_bp,
    equipos_bp,
    facturas_bp,
    partes_bp,
    pedidos_bp,
    reportes_bp,
    solicitudes_bp,
    tecnicos_bp,
    asignaciones_bp,
    tecnico_dashboard_bp,
    test_bp  # Solo para desarrollo
]

def register_blueprints(app: Flask) -> None:
    """
    Registra todos los blueprints en la aplicación Flask.
    
    Args:
        app: Instancia de la aplicación Flask
    """
    for bp in BLUEPRINTS:
        app.register_blueprint(bp)
        
    # Registrar manejadores de errores
    from . import error_handlers
    error_handlers.register_error_handlers(app)
