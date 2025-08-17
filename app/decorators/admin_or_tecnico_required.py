from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user, login_required

def _tiene_acceso_admin_o_tecnico(u):
    """Determina si el usuario tiene rol admin, superadmin o técnico, usando helpers del modelo cuando existan."""
    # Preferir métodos agregados en el modelo que ya contemplan variantes
    try:
        if hasattr(u, 'tiene_rol') and callable(getattr(u, 'tiene_rol')):
            if u.tiene_rol('admin', 'superadmin', 'tecnico'):
                return True
        # Métodos alternativos
        if hasattr(u, 'es_admin') and callable(getattr(u, 'es_admin')) and u.es_admin():
            return True
        if hasattr(u, 'es_superadmin') and callable(getattr(u, 'es_superadmin')) and u.es_superadmin():
            return True
        if hasattr(u, 'es_tecnico') and callable(getattr(u, 'es_tecnico')) and u.es_tecnico():
            return True
        # Métodos con prefijo is_ (compatibilidad)
        if hasattr(u, 'is_superadmin') and callable(getattr(u, 'is_superadmin')) and u.is_superadmin():
            return True
        if hasattr(u, 'is_admin') and callable(getattr(u, 'is_admin')) and u.is_admin():
            return True
        if hasattr(u, 'is_tecnico') and callable(getattr(u, 'is_tecnico')) and u.is_tecnico():
            return True
    except Exception:
        pass
    return False

def admin_or_tecnico_required(f):
    """
    Decorador que verifica si el usuario actual es administrador, técnico o superadmin.
    Si no tiene permisos, redirige a la página de inicio.
    """
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not _tiene_acceso_admin_o_tecnico(current_user):
            flash('No tienes permiso para acceder a esta sección. Se requiere rol de Administrador o Técnico.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function
