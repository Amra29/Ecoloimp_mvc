# This file makes the decorators directory a Python package
# Import decorators here to make them available directly from app.decorators
from .permisos import permiso_requerido, permiso_requerido_api
from .tecnico_required import tecnico_required
from .admin_required import admin_required
from .admin_or_tecnico_required import admin_or_tecnico_required
from .permisos_requeridos import permisos_requeridos

# New role-based and permission-based decorators
from .role_required import role_required, admin_required as new_admin_required, superadmin_required
from .permission_required import permission_required, object_permission_required

__all__ = [
    # Legacy decorators
    'permiso_requerido',
    'permiso_requerido_api',
    'admin_required',
    'tecnico_required',
    'admin_or_tecnico_required',
    'permisos_requeridos',
    
    # New decorators
    'role_required',
    'new_admin_required',
    'superadmin_required',
    'permission_required',
    'object_permission_required'
]
