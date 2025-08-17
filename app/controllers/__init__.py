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

# Importar los controladores para que se registren los blueprints
from . import admin, auth, clientes, equipos, facturas, partes, pedidos_piezas, reportes, solicitudes, tecnicos, asignaciones, tecnico_dashboard
from .test import test_bp
