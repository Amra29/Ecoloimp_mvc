from functools import wraps
from flask import flash, redirect, url_for, current_app
from flask_login import current_user, login_required

def _tiene_acceso_admin_o_tecnico(user):
    """
    Verifica si el usuario tiene rol de técnico o superior (admin, superadmin).
    
    Args:
        user: Instancia del modelo Usuario
        
    Returns:
        bool: True si el usuario tiene rol de técnico o superior, False en caso contrario
    """
    if not user or not user.is_authenticated:
        return False
        
    # Usar el método estándar de verificación de roles
    if hasattr(user, 'is_tecnico') and callable(user.is_tecnico):
        return user.is_tecnico()
        
    # Método alternativo para compatibilidad
    if hasattr(user, 'tiene_rol') and callable(user.tiene_rol):
        return user.tiene_rol('tecnico', 'admin', 'superadmin')
        
    # Verificación directa como último recurso
    return hasattr(user, 'rol') and user.rol in ['tecnico', 'admin', 'superadmin']

def admin_or_tecnico_required(f):
    """
    Decorador que verifica si el usuario actual es técnico o tiene un rol superior.
    
    Este decorador debe usarse en rutas que requieran privilegios de técnico o superiores.
    Si el usuario no tiene los permisos necesarios, se redirige a la página de inicio
    con un mensaje de error.
    
    Uso:
        @tecnico_bp.route('/ruta')
        @login_required
        @admin_or_tecnico_required
        def vista_protegida():
            return 'Contenido protegido'
    """
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not _tiene_acceso_admin_o_tecnico(current_user):
            flash('Acceso denegado: Se requiere rol de Técnico o superior para acceder a esta sección.', 'error')
            # Intentar redirigir al dashboard del usuario o a la página principal
            try:
                if hasattr(current_user, 'is_admin') and current_user.is_admin():
                    return redirect(url_for('admin.dashboard'))
                return redirect(url_for('main.index'))
            except Exception as e:
                current_app.logger.error(f'Error en redirección: {str(e)}')
                return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function
