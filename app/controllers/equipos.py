"""
Controlador para la gestión de equipos (impresoras, multifuncionales, etc.)
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models.models import db, Equipo, Cliente, Sucursal, Conteo
from app.forms import EquipoForm, BuscarEquipoForm
from datetime import datetime

# Crear blueprint
equipos_bp = Blueprint('equipos', __name__, url_prefix='/equipos')


@equipos_bp.route('/')
@login_required
def listar():
    """Lista todos los equipos con opciones de filtrado"""
    form = BuscarEquipoForm()
    
    # Inicializar consulta
    query = Equipo.query
    
    # Aplicar filtros si se envió el formulario
    if request.args.get('buscar'):
        if form.numero_serie.data:
            query = query.filter(Equipo.numero_serie.ilike(f'%{form.numero_serie.data}%'))
        if form.marca.data:
            query = query.filter(Equipo.marca.ilike(f'%{form.marca.data}%'))
        if form.modelo.data:
            query = query.filter(Equipo.modelo.ilike(f'%{form.modelo.data}%'))
        if form.tipo.data:
            query = query.filter(Equipo.tipo == form.tipo.data)
        if form.estado.data:
            query = query.filter(Equipo.estado == form.estado.data)
    
    # Ordenar por fecha de registro descendente
    equipos = query.order_by(Equipo.fecha_registro.desc()).all()
    
    return render_template('equipos/listar.html', 
                         equipos=equipos, 
                         form=form,
                         titulo='Listado de Equipos')


@equipos_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    """Crea un nuevo equipo"""
    form = EquipoForm()
    
    # Cargar opciones de clientes y sucursales
    form.cliente_id.choices = [(c.id, c.nombre) for c in Cliente.query.order_by('nombre').all()]
    form.sucursal_id.choices = [(s.id, f"{s.nombre} - {s.ciudad}") 
                               for s in Sucursal.query.order_by('nombre').all()]
    
    if form.validate_on_submit():
        try:
            equipo = Equipo(
                numero_serie=form.numero_serie.data.upper(),
                cliente_id=form.cliente_id.data,
                sucursal_id=form.sucursal_id.data if form.sucursal_id.data != '0' else None,
                marca=form.marca.data,
                modelo=form.modelo.data,
                tipo=form.tipo.data,
                area=form.area.data,
                ubicacion_detalle=form.ubicacion_detalle.data,
                propiedad=form.propiedad.data,
                estado=form.estado.data,
                fecha_instalacion=form.fecha_instalacion.data,
                notas=form.notas.data
            )
            
            db.session.add(equipo)
            db.session.commit()
            
            flash(f'Equipo {equipo.numero_serie} registrado correctamente.', 'success')
            return redirect(url_for('equipos.detalle', id=equipo.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar el equipo: {str(e)}', 'error')
    
    return render_template('equipos/form.html', 
                         form=form, 
                         titulo='Nuevo Equipo')


@equipos_bp.route('/<int:id>')
@login_required
def detalle(id):
    """Muestra los detalles de un equipo"""
    equipo = Equipo.query.get_or_404(id)
    conteos = Conteo.query.filter_by(equipo_id=id).order_by(Conteo.fecha_conteo.desc()).limit(5).all()
    return render_template('equipos/detalle.html', 
                         equipo=equipo, 
                         conteos=conteos)


@equipos_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    """Edita un equipo existente"""
    equipo = Equipo.query.get_or_404(id)
    form = EquipoForm(obj=equipo)
    
    # Cargar opciones de clientes y sucursales
    form.cliente_id.choices = [(c.id, c.nombre) for c in Cliente.query.order_by('nombre').all()]
    form.sucursal_id.choices = [(s.id, f"{s.nombre} - {s.ciudad}") 
                               for s in Sucursal.query.order_by('nombre').all()]
    
    if form.validate_on_submit():
        try:
            equipo.numero_serie = form.numero_serie.data.upper()
            equipo.cliente_id = form.cliente_id.data
            equipo.sucursal_id = form.sucursal_id.data if form.sucursal_id.data != '0' else None
            equipo.marca = form.marca.data
            equipo.modelo = form.modelo.data
            equipo.tipo = form.tipo.data
            equipo.area = form.area.data
            equipo.ubicacion_detalle = form.ubicacion_detalle.data
            equipo.propiedad = form.propiedad.data
            equipo.estado = form.estado.data
            equipo.fecha_instalacion = form.fecha_instalacion.data
            equipo.notas = form.notas.data
            
            db.session.commit()
            flash('Equipo actualizado correctamente.', 'success')
            return redirect(url_for('equipos.detalle', id=equipo.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el equipo: {str(e)}', 'error')
    
    return render_template('equipos/form.html', 
                         form=form, 
                         equipo=equipo,
                         titulo='Editar Equipo')


@equipos_bp.route('/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar(id):
    """Elimina un equipo (borrado lógico)"""
    if not current_user.is_admin():
        flash('No tiene permiso para realizar esta acción.', 'error')
        return redirect(url_for('equipos.listar'))
    
    equipo = Equipo.query.get_or_404(id)
    
    try:
        # Verificar si hay conteos asociados
        if Conteo.query.filter_by(equipo_id=id).count() > 0:
            flash('No se puede eliminar el equipo porque tiene conteos registrados.', 'error')
        else:
            db.session.delete(equipo)
            db.session.commit()
            flash('Equipo eliminado correctamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el equipo: {str(e)}', 'error')
    
    return redirect(url_for('equipos.listar'))


@equipos_bp.route('/buscar-ajax')
@login_required
def buscar_ajax():
    """Búsqueda de equipos para AJAX (usado en formularios)"""
    query = request.args.get('q', '').strip()
    
    if len(query) < 2:
        return jsonify([])
    
    # Buscar por número de serie, marca o modelo
    resultados = Equipo.query.filter(
        (Equipo.numero_serie.ilike(f'%{query}%')) |
        (Equipo.marca.ilike(f'%{query}%')) |
        (Equipo.modelo.ilike(f'%{query}%'))
    ).limit(10).all()
    
    # Formatear resultados para Select2
    data = [{
        'id': eq.id,
        'text': f"{eq.numero_serie} - {eq.marca} {eq.modelo} ({eq.tipo})"
    } for eq in resultados]
    
    return jsonify(data)
