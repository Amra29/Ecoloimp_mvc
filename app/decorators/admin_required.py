from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user, login_required

def admin_required(f):
    """
    Decorador que verifica si el usuario actual es administrador o superadmin.
    Si no tiene permisos, redirige a la página de inicio.
    """
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not (hasattr(current_user, 'is_admin') and current_user.is_admin()) and \
           not (hasattr(current_user, 'is_superadmin') and current_user.is_superadmin()):
            flash('No tienes permiso para acceder a esta sección. Se requiere rol de Administrador.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function
