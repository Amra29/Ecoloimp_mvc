from functools import wraps
from flask import flash, redirect, url_for, abort, current_app
from flask_login import current_user, login_required

def permiso_requerido(nombre_permiso):
    """
    Decorador para verificar si un usuario tiene un permiso específico.
    Si no tiene el permiso, redirige a la página de inicio.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
                
            if not current_user.tiene_permiso(nombre_permiso):
                flash('No tienes permiso para acceder a esta página.', 'error')
                return redirect(url_for('main.index'))
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def permiso_requerido_api(nombre_permiso):
    """
    Versión del decorador para APIs que devuelve un error 403 en lugar de redirigir.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return {'error': 'No autenticado'}, 401
                
            if not current_user.tiene_permiso(nombre_permiso):
                return {'error': 'Permiso denegado'}, 403
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator
