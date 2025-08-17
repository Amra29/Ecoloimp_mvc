"""
Controlador para la gestión de permisos del sistema.
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app.models.models import db, Permiso, RolPermiso, Usuario
from app.forms.permiso_forms import BuscarPermisoForm, AsignarPermisoForm, RolForm
from app.decorators.permisos import permiso_requerido

# Crear blueprint
permisos_bp = Blueprint('admin_permisos', __name__, url_prefix='/admin/permisos')

# Categorías para organizar los permisos en la interfaz
CATEGORIAS_PERMISOS = {
    'Administración': ['admin_todo', 'gestionar_usuarios', 'gestionar_permisos', 'ver_reportes', 'exportar_datos'],
    'Clientes': ['gestionar_clientes', 'ver_clientes', 'crear_clientes', 'editar_clientes', 'eliminar_clientes'],
    'Equipos': ['gestionar_equipos', 'ver_equipos', 'crear_equipos', 'editar_equipos', 'eliminar_equipos'],
    'Conteos': ['gestionar_conteos', 'ver_conteos', 'crear_conteos', 'editar_conteos', 'editar_conteos_propios', 'eliminar_conteos'],
    'Visitas': ['gestionar_visitas', 'ver_visitas', 'crear_visitas', 'editar_visitas', 'eliminar_visitas', 'registrar_visitas'],
    'Reportes': ['ver_reportes', 'generar_reportes', 'exportar_datos'],
    'Inventario': ['gestionar_inventario', 'ver_inventario', 'crear_inventario', 'editar_inventario', 'eliminar_inventario'],
    'Facturación': ['gestionar_facturas', 'ver_facturas', 'crear_facturas', 'anular_facturas', 'generar_notas_credito']
}

def organizar_permisos_por_categoria():
    """Organiza los permisos por categoría para mostrarlos en la interfaz"""
    todos_permisos = {p.nombre: p for p in Permiso.query.all()}
    permisos_por_categoria = {}
    
    for categoria, permisos in CATEGORIAS_PERMISOS.items():
        permisos_filtrados = []
        for permiso_nombre in permisos:
            if permiso_nombre in todos_permisos:
                permisos_filtrados.append(todos_permisos[permiso_nombre])
        
        if permisos_filtrados:  # Solo agregar categorías con permisos existentes
            permisos_por_categoria[categoria] = sorted(
                permisos_filtrados, 
                key=lambda x: x.nombre
            )
    
    return permisos_por_categoria

@permisos_bp.route('/')
@login_required
@permiso_requerido('gestionar_permisos')
def listar_permisos():
    """Lista todos los permisos del sistema"""
    form_busqueda = BuscarPermisoForm()
    
    # Obtener parámetros de búsqueda
    busqueda = request.args.get('buscar', '')
    rol_filtro = request.args.get('rol', '')
    
    # Consulta base
    query = Permiso.query
    
    # Aplicar filtros
    if busqueda:
        query = query.filter(
            (Permiso.nombre.ilike(f'%{busqueda}%')) |
            (Permiso.descripcion.ilike(f'%{busqueda}%'))
        )
    
    if rol_filtro:
        query = query.join(RolPermiso).filter(RolPermiso.rol == rol_filtro)
    
    # Ordenar y obtener todos los permisos
    permisos = query.order_by(Permiso.nombre).all()
    
    # Obtener roles únicos para el formulario de asignación
    roles = db.session.query(RolPermiso.rol).distinct().all()
    roles = [r[0] for r in roles]
    
    # Agregar roles del sistema que podrían no tener permisos aún
    roles_sistema = ['administrador', 'tecnico', 'cliente', 'recepcion', 'gerencia']
    for rol in roles_sistema:
        if rol not in roles:
            roles.append(rol)
    
    # Organizar permisos por categoría para la vista
    permisos_por_categoria = organizar_permisos_por_categoria()
    
    return render_template(
        'admin/permisos/listar.html',
        permisos=permisos,
        form_busqueda=form_busqueda,
        roles=roles,
        titulo='Gestión de Permisos',
        categorias_permisos=permisos_por_categoria,
        active_page='permisos'
    )

@permisos_bp.route('/asignar', methods=['POST'])
@login_required
@permiso_requerido('gestionar_permisos')
def asignar_permiso():
    """Asigna o remueve permisos a un rol"""
    if request.method == 'POST':
        try:
            data = request.get_json()
            rol = data.get('rol')
            permisos_ids = data.get('permisos', [])
            
            if not rol:
                return jsonify({'error': 'Rol no especificado'}), 400
            
            # Obtener los permisos actuales del rol
            permisos_actuales = RolPermiso.query.filter_by(rol=rol).all()
            permisos_actuales_ids = {rp.permiso_id for rp in permisos_actuales}
            
            # Convertir a enteros
            try:
                permisos_nuevos_ids = {int(pid) for pid in permisos_ids}
            except (ValueError, TypeError):
                return jsonify({'error': 'IDs de permisos inválidos'}), 400
            
            # Determinar permisos a agregar y eliminar
            agregar_ids = permisos_nuevos_ids - permisos_actuales_ids
            eliminar_ids = permisos_actuales_ids - permisos_nuevos_ids
            
            # Realizar cambios en la base de datos
            try:
                # Eliminar permisos
                if eliminar_ids:
                    RolPermiso.query.filter(
                        RolPermiso.rol == rol,
                        RolPermiso.permiso_id.in_(eliminar_ids)
                    ).delete(synchronize_session=False)
                
                # Agregar nuevos permisos
                for pid in agregar_ids:
                    # Verificar que el permiso exista
                    if not Permiso.query.get(pid):
                        continue
                    
                    # Verificar que no exista ya la relación
                    if not RolPermiso.query.filter_by(rol=rol, permiso_id=pid).first():
                        nuevo_permiso = RolPermiso(rol=rol, permiso_id=pid)
                        db.session.add(nuevo_permiso)
                
                db.session.commit()
                return jsonify({
                    'message': 'Permisos actualizados correctamente',
                    'agregados': len(agregar_ids),
                    'eliminados': len(eliminar_ids)
                })
                
            except Exception as e:
                db.session.rollback()
                return jsonify({'error': f'Error al actualizar permisos: {str(e)}'}), 500
                
        except Exception as e:
            return jsonify({'error': f'Error en la solicitud: {str(e)}'}), 400
    
    return jsonify({'error': 'Método no permitido'}), 405

@permisos_bp.route('/roles')
@login_required
@permiso_requerido('gestionar_permisos')
def listar_roles():
    """Lista todos los roles y sus permisos"""
    # Obtener todos los roles únicos
    roles_result = db.session.query(RolPermiso.rol).distinct().all()
    roles = [r[0] for r in roles_result]
    
    # Agregar roles del sistema que podrían no tener permisos aún
    roles_sistema = ['administrador', 'tecnico', 'cliente', 'recepcion', 'gerencia']
    for rol in roles_sistema:
        if rol not in roles:
            roles.append(rol)
    
    # Obtener permisos por rol
    roles_permisos = {}
    for rol in roles:
        permisos = db.session.query(Permiso).join(RolPermiso).filter(
            RolPermiso.rol == rol
        ).all()
        roles_permisos[rol] = permisos
    
    # Organizar todos los permisos por categoría
    permisos_por_categoria = organizar_permisos_por_categoria()
    
    # Obtener todos los permisos para el formulario de nuevo rol
    todos_los_permisos = Permiso.query.order_by(Permiso.nombre).all()
    
    return render_template(
        'admin/permisos/roles.html',
        roles_permisos=roles_permisos,
        permisos_por_categoria=permisos_por_categoria,
        todos_los_permisos=todos_los_permisos,
        titulo='Roles y Permisos',
        active_page='roles'
    )

@permisos_bp.route('/crear-rol', methods=['GET', 'POST'])
@login_required
@permiso_requerido('gestionar_permisos')
@permiso_requerido('gestionar_roles')
def crear_rol():
    """Crea un nuevo rol en el sistema"""
    form = RolForm()
    
    # Cargar opciones de permisos
    form.permisos.choices = [(p.id, f"{p.nombre} - {p.descripcion or 'Sin descripción'}") 
                            for p in Permiso.query.order_by(Permiso.nombre).all()]
    
    if form.validate_on_submit():
        nombre_rol = form.nombre.data.lower().replace(' ', '_')
        
        # Verificar si el rol ya existe
        if RolPermiso.query.filter_by(rol=nombre_rol).first():
            flash('Ya existe un rol con ese nombre', 'error')
            return redirect(url_for('admin_permisos.listar_roles'))
        
        try:
            # Crear las relaciones de permisos
            for permiso_id in form.permisos.data:
                permiso = Permiso.query.get(permiso_id)
                if permiso:
                    rol_permiso = RolPermiso(rol=nombre_rol, permiso_id=permiso_id)
                    db.session.add(rol_permiso)
            
            db.session.commit()
            flash(f'Rol "{nombre_rol}" creado correctamente', 'success')
            return redirect(url_for('admin_permisos.listar_roles'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear el rol: {str(e)}', 'error')
    
    return render_template('admin/permisos/crear_rol.html', form=form, titulo='Crear Nuevo Rol')

@permisos_bp.route('/eliminar-rol/<string:rol>', methods=['POST'])
@login_required
@permiso_requerido('gestionar_permisos')
@permiso_requerido('gestionar_roles')
def eliminar_rol(rol):
    """Elimina un rol del sistema"""
    # Prevenir eliminación de roles del sistema
    roles_protegidos = ['administrador', 'tecnico', 'cliente']
    if rol in roles_protegidos:
        flash('No se pueden eliminar los roles del sistema', 'error')
        return redirect(url_for('admin_permisos.listar_roles'))
    
    # Verificar si hay usuarios con este rol
    usuarios_con_rol = Usuario.query.filter_by(tipo=rol).count()
    if usuarios_con_rol > 0:
        flash(f'No se puede eliminar el rol porque tiene {usuarios_con_rol} usuario(s) asignado(s)', 'error')
        return redirect(url_for('admin_permisos.listar_roles'))
    
    try:
        # Eliminar todas las relaciones de permisos para este rol
        RolPermiso.query.filter_by(rol=rol).delete()
        db.session.commit()
        flash(f'Rol "{rol}" eliminado correctamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el rol: {str(e)}', 'error')
    
    return redirect(url_for('admin_permisos.listar_roles'))

# API para obtener permisos de un rol (para AJAX)
@permisos_bp.route('/api/permisos-rol/<rol>')
@login_required
@permiso_requerido('gestionar_permisos')
def api_permisos_rol(rol):
    """API para obtener los permisos de un rol específico"""
    try:
        # Crear la condición para verificar si el permiso está asignado al rol
        condicion = db.exists().where(
            (RolPermiso.permiso_id == Permiso.id) & 
            (RolPermiso.rol == rol)
        )
        
        # Consulta para obtener los permisos con su estado de asignación
        permisos = db.session.query(
            Permiso.id,
            Permiso.nombre,
            Permiso.descripcion,
            db.case([(condicion, True)], else_=False).label('tiene_permiso')
        ).all()
        
        return jsonify([{
            'id': p.id,
            'nombre': p.nombre,
            'descripcion': p.descripcion or '',
            'tiene_permiso': p.tiene_permiso
        } for p in permisos])
    except Exception as e:
        return jsonify({'error': str(e)}), 500
