"""
Package para formularios de la aplicación.
"""
from .auth_forms import LoginForm
from .asignacion_forms import AsignacionForm, BuscarAsignacionForm, CompletarAsignacionForm
from .cliente_forms import ClienteForm, BuscarClienteForm
from .equipo_forms import EquipoForm, BuscarEquipoForm
from .factura_forms import FacturaForm, LineaFacturaForm
from .pedido_pieza_forms import (
    PedidoPiezaForm, AprobarPedidoPiezaForm, 
    EntregarPiezaForm, BuscarPedidoPiezaForm
)
from .servicio_forms import ServicioForm, BuscarServicioForm, ItemServicioForm
from .solicitud_forms import SolicitudForm, BuscarSolicitudForm
from .tecnico_forms import TecnicoForm, BuscarTecnicoForm
from .parte_forms import *
from .pedido_forms import *
from .permiso_forms import *
from .reporte_forms import *
from .usuario_forms import UsuarioForm

__all__ = [
    'LoginForm',
    'AsignacionForm',
    'BuscarAsignacionForm',
    'CompletarAsignacionForm',
    'ClienteForm',
    'BuscarClienteForm',
    'EquipoForm',
    'BuscarEquipoForm',
    'FacturaForm',
    'LineaFacturaForm',
    'PedidoPiezaForm',
    'AprobarPedidoPiezaForm',
    'EntregarPiezaForm',
    'BuscarPedidoPiezaForm',
    'ServicioForm',
    'BuscarServicioForm',
    'ItemServicioForm',
    'SolicitudForm',
    'BuscarSolicitudForm',
    'TecnicoForm',
    'BuscarTecnicoForm',
    'UsuarioForm',
    # Agrega aquí otras clases de formularios que necesites exportar
]

