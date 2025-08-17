"""
Decoradores para control de acceso basado en roles.

Este módulo proporciona decoradores para verificar los permisos del usuario basados en roles.
"""
from functools import wraps
from flask import flash, redirect, url_for, current_app, abort, request
from flask_login import current_user, login_required

def role_required(*roles):
    """
    Decorador que verifica que el usuario tenga al menos uno de los roles requeridos.
    
    Args:
        *roles: Nombres de roles requeridos. Si se especifica 'any', cualquier usuario autenticado tiene acceso.
    
    Returns:
        function: Función decorada que verifica los roles antes de ejecutar la vista.
        
    Uso:
        @bp.route('/admin')
        @login_required
        @role_required('admin', 'superadmin')
        def admin_panel():
            return 'Panel de administración'
            
        @bp.route('/profile')
        @login_required
        @role_required('any')  # Cualquier usuario autenticado
        def profile():
            return 'Perfil de usuario'
    """
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            # Si no hay roles requeridos o 'any' está en los roles, permitir acceso
            if not roles or 'any' in roles:
                return f(*args, **kwargs)
                
            # Verificar si el usuario tiene al menos uno de los roles requeridos
            if not current_user.is_authenticated:
                return current_app.login_manager.unauthorized()
                
            # Usar el método tiene_rol si está disponible
            if hasattr(current_user, 'tiene_rol') and callable(current_user.tiene_rol):
                if current_user.tiene_rol(*roles):
                    return f(*args, **kwargs)
            # Verificación directa de roles como respaldo
            elif hasattr(current_user, 'rol') and current_user.rol in roles:
                return f(*args, **kwargs)
                
            # Si llega aquí, el usuario no tiene los roles necesarios
            if request.is_xhr or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return {'error': 'No autorizado'}, 403
                
            flash('No tienes permiso para acceder a esta página.', 'error')
            
            # Redirigir según el tipo de usuario
            try:
                if hasattr(current_user, 'is_admin') and current_user.is_admin():
                    return redirect(url_for('admin.dashboard'))
                elif hasattr(current_user, 'is_tecnico') and current_user.is_tecnico():
                    return redirect(url_for('tecnico.dashboard'))
                return redirect(url_for('main.index'))
            except Exception as e:
                current_app.logger.error(f'Error en redirección: {str(e)}')
                return redirect(url_for('main.index'))
                
        return decorated_function
    return decorator

def admin_required(f):
    """
    Decorador que verifica que el usuario sea administrador o superadministrador.
    
    Uso:
        @bp.route('/admin')
        @login_required
        @admin_required
        def admin_panel():
            return 'Panel de administración'
    """
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            if request.is_xhr or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return {'error': 'No autorizado'}, 403
                
            flash('Acceso restringido a administradores.', 'error')
            try:
                if hasattr(current_user, 'is_tecnico') and current_user.is_tecnico():
                    return redirect(url_for('tecnico.dashboard'))
                return redirect(url_for('main.index'))
            except Exception as e:
                current_app.logger.error(f'Error en redirección: {str(e)}')
                return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def superadmin_required(f):
    """
    Decorador que verifica que el usuario sea superadministrador.
    
    Uso:
        @bp.route('/superadmin')
        @login_required
        @superadmin_required
        def superadmin_panel():
            return 'Panel de superadministrador'
    """
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not (hasattr(current_user, 'es_superadmin') and current_user.es_superadmin()):
            if request.is_xhr or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return {'error': 'No autorizado'}, 403
                
            flash('Acceso restringido a superadministradores.', 'error')
            try:
                if hasattr(current_user, 'is_admin') and current_user.is_admin():
                    return redirect(url_for('admin.dashboard'))
                elif hasattr(current_user, 'is_tecnico') and current_user.is_tecnico():
                    return redirect(url_for('tecnico.dashboard'))
                return redirect(url_for('main.index'))
            except Exception as e:
                current_app.logger.error(f'Error en redirección: {str(e)}')
                return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function
