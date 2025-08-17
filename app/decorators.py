from functools import wraps
from flask import abort, redirect, url_for, flash, current_app, request
from flask_login import current_user
from functools import wraps

def permisos_requeridos(*permisos):
    """
    Decorador que verifica si el usuario tiene los permisos necesarios.
    
    Args:
        *permisos: Lista de permisos requeridos. Si está vacío, solo requiere autenticación.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                # Redirigir al login si no está autenticado
                return current_app.login_manager.unauthorized()
            
            # Si no se especifican permisos, solo se requiere autenticación
            if not permisos:
                return f(*args, **kwargs)
                
            # Verificar si el usuario tiene al menos uno de los permisos requeridos
            if not any(current_user.tiene_permiso(permiso) for permiso in permisos):
                # Si el usuario no tiene permisos, registrar el intento de acceso
                current_app.logger.warning(
                    f"Intento de acceso no autorizado a {request.path} "
                    f"por el usuario {current_user.email} "
                    f"(ID: {current_user.id}). Permisos requeridos: {', '.join(permisos)}"
                )
                # Mostrar mensaje al usuario
                flash('No tienes permiso para acceder a esta página.', 'error')
                # Redirigir a la página principal o a donde corresponda
                return redirect(url_for('main.index'))
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Acceso denegado. Se requieren permisos de administrador.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)

    return decorated_function


def tecnico_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not (current_user.is_tecnico() or current_user.is_admin()):
            flash('Acceso denegado. Se requieren permisos de técnico.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)

    return decorated_function


def admin_or_tecnico_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not (current_user.is_admin() or current_user.is_tecnico()):
            flash('Acceso denegado.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)

    return decorated_function


def can_edit_resource(resource_type):
    """Verifica si el usuario puede editar un tipo de recurso"""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))

            # Administrador puede editar todo
            if current_user.is_admin():
                return f(*args, **kwargs)

            # Técnico puede editar solo ciertos recursos
            if current_user.is_tecnico():
                allowed_resources = ['reportes', 'asignaciones_propias', 'pedidos_piezas']
                if resource_type in allowed_resources:
                    return f(*args, **kwargs)

            flash('No tiene permisos para realizar esta acción.', 'error')
            return redirect(url_for('main.index'))

        return decorated_function

    return decorator
