"""
Módulo principal de la aplicación.

Este módulo exporta la aplicación Flask creada por la fábrica de aplicaciones.
"""
from app.app_factory import create_app

# Crear la aplicación Flask
app = create_app()

# Importar modelos para asegurar que están registrados con SQLAlchemy
# Esto es necesario para que Flask-Migrate pueda detectar los modelos
from app.models.models import (  # noqa: F401, E402
    Usuario, Sucursal, Tecnico, Admin, Cliente,
    Solicitud, Servicio, Asignacion, Reporte, Parte,
    PedidoPieza, Factura, Equipo, Visita, Conteo, Permiso, RolPermiso, SuperAdmin
)
