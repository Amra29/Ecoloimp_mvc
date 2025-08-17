from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.models.models import db, Usuario, Tecnico, Permiso, RolPermiso
from app.forms import LoginForm
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

def init_permisos():
    """Inicializa los permisos por defecto en el sistema"""
    permisos_base = [
        # Permisos de administración
        ('admin_todo', 'Acceso total al sistema'),
        
        # Permisos de gestión de usuarios
        ('gestionar_usuarios', 'Gestionar usuarios del sistema'),
        ('ver_usuarios', 'Ver lista de usuarios'),
        ('crear_usuarios', 'Crear nuevos usuarios'),
        ('editar_usuarios', 'Editar usuarios existentes'),
        ('eliminar_usuarios', 'Eliminar usuarios'),
        
        # Permisos de gestión de clientes
        ('gestionar_clientes', 'Gestionar clientes'),
        ('ver_clientes', 'Ver lista de clientes'),
        ('crear_clientes', 'Crear nuevos clientes'),
        ('editar_clientes', 'Editar clientes existentes'),
        ('eliminar_clientes', 'Eliminar clientes'),
        
        # Permisos de gestión de equipos
        ('gestionar_equipos', 'Gestionar equipos'),
        ('ver_equipos', 'Ver lista de equipos'),
        ('crear_equipos', 'Agregar nuevos equipos'),
        ('editar_equipos', 'Editar equipos existentes'),
        ('eliminar_equipos', 'Eliminar equipos'),
        
        # Permisos de conteos
        ('gestionar_conteos', 'Gestionar conteos de impresiones'),
        ('ver_conteos', 'Ver lista de conteos'),
        ('crear_conteos', 'Registrar nuevos conteos'),
        ('editar_conteos', 'Editar conteos existentes'),
        ('editar_conteos_propios', 'Editar solo conteos propios'),
        ('eliminar_conteos', 'Eliminar conteos'),
        
        # Permisos de visitas técnicas
        ('gestionar_visitas', 'Gestionar visitas técnicas'),
        ('ver_visitas', 'Ver lista de visitas'),
        ('crear_visitas', 'Programar nuevas visitas'),
        ('editar_visitas', 'Editar visitas existentes'),
        ('eliminar_visitas', 'Eliminar visitas'),
        
        # Permisos de reportes
        ('ver_reportes', 'Ver reportes'),
        ('generar_reportes', 'Generar reportes'),
        ('exportar_datos', 'Exportar datos a diferentes formatos')
    ]
    
    # Crear permisos si no existen
    for permiso in permisos_base:
        if isinstance(permiso, tuple):
            nombre, descripcion = permiso
        else:
            nombre = permiso
            descripcion = f'Permiso para {nombre}'
            
        if not Permiso.query.filter_by(nombre=nombre).first():
            nuevo_permiso = Permiso(nombre=nombre, descripcion=descripcion)
            db.session.add(nuevo_permiso)
    
    # Asignar permisos a roles
    roles_permisos = {
        'admin': ['admin_todo'],
        'tecnico': [
            'ver_conteos', 'crear_conteos', 'editar_conteos_propios',
            'ver_equipos', 'ver_visitas', 'crear_visitas'
        ]
    }
    
    for rol, permisos in roles_permisos.items():
        for permiso in permisos:
            permiso_obj = Permiso.query.filter_by(nombre=permiso).first()
            if permiso_obj and not RolPermiso.query.filter_by(rol=rol, permiso_id=permiso_obj.id).first():
                rol_permiso = RolPermiso(rol=rol, permiso_id=permiso_obj.id)
                db.session.add(rol_permiso)
    
    try:
        db.session.commit()
        current_app.logger.info("Permisos inicializados correctamente")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error al inicializar permisos: {str(e)}")


# No inicializar permisos automáticamente al importar el módulo
# La inicialización se manejará a través de un comando Flask personalizado

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Maneja el inicio de sesión de usuarios"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        password = form.password.data

        # Buscar usuario por email
        usuario = Usuario.query.filter_by(email=email).first()

        # Verificar credenciales
        if usuario and usuario.check_password(password):
            # Verificar si el usuario está activo
            if not usuario.activo:
                flash('Su cuenta ha sido desactivada. Contacte al administrador.', 'error')
                return render_template('auth/login.html', form=form)
            
            # Iniciar sesión
            login_user(usuario, remember=form.remember_me.data)
            
            # Registrar el último acceso del usuario
            usuario.ultimo_acceso = db.func.now()
            db.session.commit()
            
            flash(f'Bienvenido {usuario.nombre}', 'success')

            # Redirigir según el rol del usuario
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            
            if usuario.is_admin():
                return redirect(url_for('admin.dashboard'))
            elif usuario.is_tecnico():
                return redirect(url_for('tecnico_dashboard.dashboard'))
            else:
                return redirect(url_for('main.index'))
        else:
            flash('Email o contraseña incorrectos', 'error')

    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """Cierra la sesión del usuario actual"""
    logout_user()
    flash('Sesión cerrada exitosamente', 'info')
    return redirect(url_for('auth.login'))
