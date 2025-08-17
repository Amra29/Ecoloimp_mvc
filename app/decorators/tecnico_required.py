from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def tecnico_required(f):
    """
    Decorador que verifica si el usuario actual es un técnico.
    Si no es un técnico, redirige a la página de inicio.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
            
        # Verificar si el usuario es técnico, admin o superadmin
        if not current_user.is_tecnico() and not current_user.is_admin() and not current_user.is_superadmin():
            flash('No tienes permiso para acceder a esta sección. Se requiere rol de Técnico.', 'error')
            return redirect(url_for('main.index'))
            
        return f(*args, **kwargs)
    return decorated_function
