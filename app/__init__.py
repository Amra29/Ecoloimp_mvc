"""
Módulo principal de la aplicación.

Este módulo exporta la aplicación Flask creada por la fábrica de aplicaciones
y configura los componentes principales de la aplicación.
"""
import os
from typing import Optional

from flask import Flask

from .app_factory import create_app

# Create the Flask application instance
app: Flask = create_app(os.getenv('FLASK_ENV') or 'development')

# Import models to ensure they are registered with SQLAlchemy
# This is necessary for Flask-Migrate to detect the models
# Note: These imports must come after app creation to avoid circular imports
from .models.models import (  # noqa: F401, E402
    Usuario, Sucursal, Tecnico, Admin, Cliente,
    Solicitud, Servicio, Asignacion, Reporte, Parte,
    PedidoPieza, Factura, Equipo, Visita, Conteo, Permiso, RolPermiso, SuperAdmin
)

def init_app(app: Optional[Flask] = None) -> Flask:
    """Initialize the application.
    
    This function is used by the application factory pattern and WSGI servers.
    
    Args:
        app: Optional Flask application instance. If not provided, creates a new one.
        
    Returns:
        The configured Flask application instance.
    """
    if app is None:
        app = create_app(os.getenv('FLASK_ENV') or 'development')
    
    # Additional initialization can be added here
    
    return app

# This allows the application to be run directly with: python -m app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=app.debug)
