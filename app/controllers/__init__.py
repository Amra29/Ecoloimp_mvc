"""
Módulo de controladores de la aplicación.

Este módulo importa y registra todos los blueprints de la aplicación,
asegurando que todas las rutas estén disponibles.
"""
from flask import Flask
from app.decorators import role_required, permission_required

# Importar blueprints
from .admin import admin_bp
from .auth import auth_bp
from .clientes import clientes_bp
from .equipos import equipos_bp
from .facturas import facturas_bp
from .partes import partes_bp
from .pedidos_piezas import pedidos_bp
from .reportes import reportes_bp
from .solicitudes import solicitudes_bp
from .tecnicos import tecnicos_bp
from .asignaciones import asignaciones_bp
from .tecnico_dashboard import tecnico_dashboard_bp

# Importar controladores para asegurar el registro de blueprints
from . import (
    admin, 
    auth, 
    clientes, 
    equipos, 
    facturas, 
    partes, 
    pedidos_piezas, 
    reportes, 
    solicitudes, 
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
