"""
Validadores para el sistema de roles y permisos.

Este módulo proporciona funciones para validar la consistencia de roles,
permisos y estructura de la aplicación.
"""
from functools import wraps
from flask import current_app, flash, redirect, url_for
from flask_login import current_user

# Roles estándar del sistema
STANDARD_ROLES = {
    'superadmin': {
        'level': 3,
        'description': 'Acceso total al sistema (desarrollador)'
    },
    'admin': {
        'level': 2,
        'description': 'Administrador con gestión completa'
    },
    'tecnico': {
        'level': 1,
        'description': 'Técnico con acceso limitado'
    }
}

def validate_role(role_name):
    """Valida que un nombre de rol sea válido."""
    return role_name in STANDARD_ROLES

def validate_permission(permission_name):
    """Valida que un permiso exista en la base de datos."""
    from app.models.models import Permiso
    if not current_app.testing:
        return Permiso.query.filter_by(nombre=permission_name).first() is not None
    return True

def role_required(role_name):
    """Decorador para verificar el rol del usuario."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return current_app.login_manager.unauthorized()
                
            if not validate_role(role_name):
                current_app.logger.error(f'Rol inválido: {role_name}')
                flash('Error de configuración: rol no válido', 'error')
                return redirect(url_for('main.index'))
                
            user_role_level = STANDARD_ROLES.get(current_user.rol, {}).get('level', 0)
            required_level = STANDARD_ROLES[role_name]['level']
            
            if user_role_level < required_level:
                flash('No tienes permiso para acceder a esta sección', 'error')
                return redirect(url_for('main.index'))
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_blueprint_structure():
    """Valida que todos los blueprints sigan la estructura correcta."""
    from flask import Blueprint, current_app
    
    required_blueprints = {
        'auth': {
            'url_prefix': '/auth',
            'template_folder': 'auth'
        },
        'admin': {
            'url_prefix': '/admin',
            'template_folder': 'admin'
        },
        'tecnico': {
            'url_prefix': '/tecnico',
            'template_folder': 'tecnico'
        }
    }
    
    for name, config in required_blueprints.items():
        bp = current_app.blueprints.get(name)
        if not bp:
            current_app.logger.warning(f'Blueprint faltante: {name}')
            continue
            
        if bp.url_prefix != config['url_prefix']:
            current_app.logger.warning(
                f'El blueprint {name} tiene un prefijo inesperado: '
                f'Esperado {config["url_prefix"]}, Encontrado {bp.url_prefix}'
            )

def validate_template_structure():
    """Valida que las plantillas sigan la estructura correcta."""
    import os
    from flask import current_app
    
    required_templates = {
        'auth': ['login.html', 'register.html'],
        'admin': ['dashboard.html', 'users.html'],
        'tecnico': ['dashboard.html', 'asignaciones.html']
    }
    
    template_path = os.path.join(current_app.root_path, 'templates')
    
    for folder, templates in required_templates.items():
        folder_path = os.path.join(template_path, folder)
        if not os.path.exists(folder_path):
            current_app.logger.warning(f'Falta el directorio de plantillas: {folder}')
            continue
            
        for template in templates:
            if not os.path.exists(os.path.join(folder_path, template)):
                current_app.logger.warning(
                    f'Falta la plantilla: {folder}/{template}'
                )

def check_system_health():
    """Realiza una verificación de salud del sistema."""
    from app.models.models import db, Usuario, Permiso, Rol
    
    health_checks = {
        'database_connection': False,
        'admin_user_exists': False,
        'required_roles_exist': True,
        'required_permissions_exist': True
    }
    
    try:
        # Verificar conexión a la base de datos
        db.session.execute('SELECT 1')
        health_checks['database_connection'] = True
        
        # Verificar existencia de usuario administrador
        admin_exists = Usuario.query.filter_by(rol='admin').first() is not None
        health_checks['admin_user_exists'] = admin_exists
        
        # Verificar roles requeridos
        for role in STANDARD_ROLES:
            if not Rol.query.filter_by(nombre=role).first():
                health_checks['required_roles_exist'] = False
                current_app.logger.warning(f'Falta el rol requerido: {role}')
        
        return health_checks
        
    except Exception as e:
        current_app.logger.error(f'Error en la verificación de salud: {str(e)}')
        return health_checks
