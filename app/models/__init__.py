# Importar todos los modelos para asegurar que estén registrados con SQLAlchemy
from .models import (
    # Modelos de autenticación y usuarios
    Usuario, Admin, Tecnico, SuperAdmin, 
    # Modelos de permisos
    Permiso, RolPermiso,
    # Modelos del sistema de servicio técnico
    Cliente, Sucursal, Servicio, Solicitud, Asignacion, 
    Reporte, Parte, PedidoPieza, Factura,
    # Modelos del sistema de conteo de impresiones
    Equipo, Visita, Conteo
)

# Hacer los modelos disponibles para importación directa desde app.models
__all__ = [
    'Usuario', 'Admin', 'Tecnico', 'SuperAdmin',
    'Permiso', 'RolPermiso',
    'Cliente', 'Sucursal', 'Servicio', 'Solicitud', 'Asignacion',
    'Reporte', 'Parte', 'PedidoPieza', 'Factura',
    'Equipo', 'Visita', 'Conteo'
]
