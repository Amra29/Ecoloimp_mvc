"""
Controlador para la gestión de visitas técnicas
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from app.models.models import db, Visita, Equipo, Cliente, Sucursal, Tecnico, Conteo
from app.forms import VisitaForm, BuscarVisitaForm

# Crear blueprint
visitas_bp = Blueprint('visitas', __name__, url_prefix='/visitas')


@visitas_bp.route('/')
@login_required
def listar():
    """Lista todas las visitas con opciones de filtrado"""
    form = BuscarVisitaForm()
    
    # Inicializar consulta
    query = Visita.query
    
    # Si es técnico, solo mostrar sus visitas
    if current_user.is_tecnico():
        tecnico = Tecnico.query.filter_by(usuario_id=current_user.id).first()
        if tecnico:
            query = query.filter(Visita.tecnico_id == tecnico.id)
    
    # Aplicar filtros si se envió el formulario
    if request.args.get('buscar'):
        if form.estado.data:
            query = query.filter(Visita.estado == form.estado.data)
        if form.tipo_visita.data:
            query = query.filter(Visita.tipo_visita == form.tipo_visita.data)
        if form.fecha_desde.data:
            query = query.filter(Visita.fecha_visita >= form.fecha_desde.data)
        if form.fecha_hasta.data:
            # Añadir 1 día a la fecha hasta para incluir todo el día
            fecha_hasta = form.fecha_hasta.data + timedelta(days=1)
            query = query.filter(Visita.fecha_visita <= fecha_hasta)
    else:
        # Por defecto, mostrar solo visitas del mes actual
        hoy = datetime.now().date()
        primer_dia_mes = hoy.replace(day=1)
        query = query.filter(Visita.fecha_visita >= primer_dia_mes)
    
    # Ordenar por fecha de visita
    query = query.order_by(Visita.fecha_visita.desc())
    
    # Paginación
    page = request.args.get('page', 1, type=int)
    por_pagina = 15
    visitas = query.paginate(page=page, per_page=por_pagina, error_out=False)
    
    return render_template('visitas/listar.html', 
                         visitas=visitas,
                         form=form,
                         titulo='Visitas Técnicas')


@visitas_bp.route('/nueva', methods=['GET', 'POST'])
@login_required
def nueva():
    """Crea una nueva visita técnica"""
    form = VisitaForm()
    
    # Cargar opciones de selección
    _cargar_opciones_formulario(form)
    
    if form.validate_on_submit():
        try:
            visita = Visita(
                tecnico_id=form.tecnico_id.data,
                cliente_id=form.cliente_id.data,
                sucursal_id=form.sucursal_id.data if form.sucursal_id.data != '0' else None,
                tipo_visita=form.tipo_visita.data,
                fecha_visita=form.fecha_visita.data,
                hora_visita=form.hora_visita.data,
                estado=form.estado.data,
                observaciones=form.observaciones.data,
                creado_por=current_user.id
            )
            
            # Agregar equipos a la visita
            if form.equipos.data:
                equipos_ids = [int(id) for id in form.equipos.data.split(',') if id.isdigit()]
                equipos = Equipo.query.filter(Equipo.id.in_(equipos_ids)).all()
                visita.equipos = equipos
            
            db.session.add(visita)
            db.session.commit()
            
            flash('Visita técnica registrada correctamente.', 'success')
            return redirect(url_for('visitas.detalle', id=visita.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar la visita: {str(e)}', 'error')
    
    return render_template('visitas/form.html', 
                         form=form, 
                         titulo='Nueva Visita Técnica')


@visitas_bp.route('/<int:id>')
@login_required
def detalle(id):
    """Muestra los detalles de una visita técnica"""
    visita = Visita.query.get_or_404(id)
    
    # Verificar permisos (solo admin o el técnico asignado)
    if not current_user.is_admin() and \
       (not current_user.is_tecnico() or 
        not visita.tecnico or 
        visita.tecnico.usuario_id != current_user.id):
        flash('No tiene permiso para ver esta visita.', 'error')
        return redirect(url_for('visitas.listar'))
    
    # Obtener conteos realizados durante esta visita
    conteos = Conteo.query.filter_by(visita_id=id).all()
    
    return render_template('visitas/detalle.html', 
                         visita=visita,
                         conteos=conteos)


@visitas_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    """Edita una visita técnica existente"""
    visita = Visita.query.get_or_404(id)
    
    # Verificar permisos (solo admin o el técnico asignado)
    if not current_user.is_admin() and \
       (not current_user.is_tecnico() or 
        not visita.tecnico or 
        visita.tecnico.usuario_id != current_user.id):
        flash('No tiene permiso para editar esta visita.', 'error')
        return redirect(url_for('visitas.listar'))
    
    form = VisitaForm(obj=visita)
    
    # Cargar opciones de selección
    _cargar_opciones_formulario(form, visita.cliente_id, visita.sucursal_id)
    
    # Pre-seleccionar equipos
    if visita.equipos:
        form.equipos.data = ','.join(str(eq.id) for eq in visita.equipos)
    
    if form.validate_on_submit():
        try:
            visita.tecnico_id = form.tecnico_id.data
            visita.cliente_id = form.cliente_id.data
            visita.sucursal_id = form.sucursal_id.data if form.sucursal_id.data != '0' else None
            visita.tipo_visita = form.tipo_visita.data
            visita.fecha_visita = form.fecha_visita.data
            visita.hora_visita = form.hora_visita.data
            visita.estado = form.estado.data
            visita.observaciones = form.observaciones.data
            
            # Actualizar equipos de la visita
            if form.equipos.data:
                equipos_ids = [int(id) for id in form.equipos.data.split(',') if id.isdigit()]
                equipos = Equipo.query.filter(Equipo.id.in_(equipos_ids)).all()
                visita.equipos = equipos
            
            db.session.commit()
            flash('Visita técnica actualizada correctamente.', 'success')
            return redirect(url_for('visitas.detalle', id=visita.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar la visita: {str(e)}', 'error')
    
    return render_template('visitas/form.html', 
                         form=form, 
                         visita=visita,
                         titulo='Editar Visita Técnica')


@visitas_bp.route('/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar(id):
    """Elimina una visita técnica"""
    if not current_user.is_admin():
        flash('No tiene permiso para realizar esta acción.', 'error')
        return redirect(url_for('visitas.listar'))
    
    visita = Visita.query.get_or_404(id)
    
    try:
        # Verificar si hay conteos asociados
        if Conteo.query.filter_by(visita_id=id).count() > 0:
            flash('No se puede eliminar la visita porque tiene conteos registrados.', 'error')
        else:
            db.session.delete(visita)
            db.session.commit()
            flash('Visita técnica eliminada correctamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar la visita: {str(e)}', 'error')
    
    return redirect(url_for('visitas.listar'))


def _cargar_opciones_formulario(form, cliente_id=None, sucursal_id=None):
    """Carga las opciones de los selectores en el formulario"""
    # Cargar técnicos activos
    form.tecnico_id.choices = [(t.id, t.nombre) 
                             for t in Tecnico.query.filter_by(activo=True).order_by('nombre').all()]
    
    # Cargar clientes activos
    form.cliente_id.choices = [(0, 'Seleccione un cliente')] + \
                             [(c.id, c.nombre) 
                              for c in Cliente.query.filter_by(activo=True).order_by('nombre').all()]
    
    # Cargar sucursales según el cliente seleccionado o el predeterminado
    cliente_actual = cliente_id if cliente_id else (form.cliente_id.data if form.cliente_id.data else None)
    sucursales = []
    
    if cliente_actual:
        sucursales = Sucursal.query.filter_by(
            cliente_id=cliente_actual, 
            activo=True
        ).order_by('nombre').all()
    
    form.sucursal_id.choices = [(0, 'Seleccione una sucursal')] + \
                              [(s.id, f"{s.nombre} - {s.ciudad}") for s in sucursales]
    
    # Si hay una sucursal predeterminada, establecerla
    if sucursal_id:
        form.sucursal_id.data = sucursal_id
    
    return form
