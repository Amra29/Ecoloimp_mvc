"""
Decoradores para control de acceso basado en permisos.

Este módulo proporciona decoradores para verificar permisos específicos del usuario.
"""
from functools import wraps
from flask import flash, redirect, url_for, current_app, abort, request, jsonify
from flask_login import current_user, login_required

def permission_required(*permissions, require_all=True):
    """
    Decorador que verifica que el usuario tenga los permisos requeridos.
    
    Args:
        *permissions: Nombres de permisos requeridos.
        require_all (bool): Si es True (por defecto), requiere todos los permisos.
                          Si es False, requiere al menos uno de los permisos.
    
    Returns:
        function: Función decorada que verifica los permisos antes de ejecutar la vista.
        
    Uso:
        @bp.route('/editar_usuario/<int:user_id>')
        @login_required
        @permission_required('usuario_editar')
        def editar_usuario(user_id):
            return 'Editar usuario'
            
        @bp.route('/super_accion')
        @login_required
        @permission_required('permiso1', 'permiso2', require_all=False)
        def super_accion():
            return 'Acción que requiere permiso1 o permiso2'
    """
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return current_app.login_manager.unauthorized()
                
            # Superadmin tiene todos los permisos
            if hasattr(current_user, 'es_superadmin') and current_user.es_superadmin():
                return f(*args, **kwargs)
                
            # Verificar permisos
            if not permissions:
                return f(*args, **kwargs)
                
            # Usar el método tiene_permisos si está disponible
            if hasattr(current_user, 'tiene_permisos') and callable(current_user.tiene_permisos):
                has_permission = current_user.tiene_permisos(*permissions, todos=require_all)
            else:
                # Verificación manual como respaldo
                user_permissions = set()
                if hasattr(current_user, 'obtener_permisos') and callable(current_user.obtener_permisos):
                    user_permissions = current_user.obtener_permisos()
                
                if require_all:
                    has_permission = all(perm in user_permissions for perm in permissions)
                else:
                    has_permission = any(perm in user_permissions for perm in permissions)
            
            if not has_permission:
                if request.is_xhr or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({
                        'error': 'Permiso denegado',
                        'message': 'No tienes los permisos necesarios para realizar esta acción.'
                    }), 403
                
                flash('No tienes los permisos necesarios para acceder a esta página.', 'error')
                
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
                    
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def object_permission_required(permission, object_getter):
    """
    Decorador que verifica permisos sobre un objeto específico.
    
    Args:
        permission (str): Nombre del permiso requerido (ej: 'editar', 'eliminar').
        object_getter (function): Función que recibe los mismos argumentos que la vista
                                y devuelve el objeto sobre el que verificar permisos.
    
    Returns:
        function: Función decorada que verifica los permisos sobre el objeto.
        
    Uso:
        @bp.route('/documento/<int:doc_id>/editar')
        @login_required
        @object_permission_required('editar', lambda doc_id: Documento.query.get_or_404(doc_id))
        def editar_documento(doc_id, documento):
            # 'documento' es inyectado como argumento con el objeto ya cargado
            return render_template('editar_documento.html', documento=documento)
    """
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            # Obtener el objeto sobre el que verificar permisos
            obj = object_getter(*args, **kwargs)
            
            # Si el objeto tiene un método can, usarlo para verificar permisos
            if hasattr(obj, 'can') and callable(obj.can):
                if not obj.can(current_user, permission):
                    return _handle_permission_denied()
            # Si el usuario tiene un método can en el modelo
            elif hasattr(current_user, 'can') and callable(current_user.can):
                if not current_user.can(permission, obj):
                    return _handle_permission_denied()
            else:
                # Verificación manual como último recurso
                if not _check_object_permission(current_user, obj, permission):
                    return _handle_permission_denied()
            
            # Inyectar el objeto como argumento con nombre 'obj' si la función lo espera
            from inspect import signature
            sig = signature(f)
            if 'obj' in sig.parameters:
                kwargs['obj'] = obj
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def _check_object_permission(user, obj, permission):
    """
    Verifica si un usuario tiene un permiso sobre un objeto específico.
    
    Esta es una implementación básica que puede ser sobrescrita según las necesidades.
    """
    # Si el objeto tiene un propietario, verificar si el usuario es el propietario
    if hasattr(obj, 'usuario_id') and hasattr(user, 'id'):
        if obj.usuario_id == user.id:
            return True
    
    # Verificar si el usuario tiene el permiso directamente
    if hasattr(user, 'tiene_permiso') and callable(user.tiene_permiso):
        # Construir el nombre completo del permiso (ej: 'documento_editar')
        object_type = obj.__tablename__ if hasattr(obj, '__tablename__') else obj.__class__.__name__.lower()
        full_permission = f"{object_type}_{permission}"
        return user.tiene_permiso(full_permission)
        
    return False

def _handle_permission_denied():
    """Maneja el error de permiso denegado de manera consistente."""
    from flask import request
    
    if request.is_xhr or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'error': 'Permiso denegado',
            'message': 'No tienes permiso para realizar esta acción.'
        }), 403
    
    flash('No tienes permiso para realizar esta acción.', 'error')
    
    # Redirigir según el tipo de usuario
    from flask import current_app, url_for
    
    try:
        if hasattr(current_user, 'is_admin') and current_user.is_admin():
            return redirect(url_for('admin.dashboard'))
        elif hasattr(current_user, 'is_tecnico') and current_user.is_tecnico():
            return redirect(url_for('tecnico.dashboard'))
        return redirect(url_for('main.index'))
    except Exception as e:
        current_app.logger.error(f'Error en redirección: {str(e)}')
        return redirect(url_for('main.index'))
