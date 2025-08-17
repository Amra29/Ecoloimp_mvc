from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user, login_required

def permisos_requeridos(*permisos):
    """
    Decorador que verifica si el usuario actual tiene los permisos requeridos.
    Si no tiene los permisos, redirige a la página de inicio.
    """
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
                
            # Verificar si el usuario tiene al menos uno de los permisos requeridos
            tiene_permiso = False
            for permiso in permisos:
                if hasattr(current_user, 'tiene_permiso') and current_user.tiene_permiso(permiso):
                    tiene_permiso = True
                    break
                
            # Si es superadmin, siempre tiene permiso
            if not tiene_permiso and hasattr(current_user, 'is_superadmin') and current_user.is_superadmin():
                tiene_permiso = True
                
            if not tiene_permiso:
                flash('No tienes los permisos necesarios para acceder a esta sección.', 'error')
                return redirect(url_for('main.index'))
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator
