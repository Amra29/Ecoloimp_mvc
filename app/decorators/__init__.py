# This file makes the decorators directory a Python package
# Import decorators here to make them available directly from app.decorators
from .permisos import permiso_requerido, permiso_requerido_api
from .tecnico_required import tecnico_required
from .admin_required import admin_required
from .admin_or_tecnico_required import admin_or_tecnico_required
from .permisos_requeridos import permisos_requeridos

__all__ = [
    'permiso_requerido',
    'permiso_requerido_api',
    'admin_required',
    'tecnico_required',
    'admin_or_tecnico_required',
    'permisos_requeridos'
]
