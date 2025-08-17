"""
Controlador para la gestión de conteos de impresoras
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from app.models.models import db, Conteo, Equipo, Visita
from app.forms import ConteoForm, BuscarConteoForm

# Crear blueprint
conteos_bp = Blueprint('conteos', __name__, url_prefix='/conteos')


@conteos_bp.route('/')
@login_required
def listar():
    """Lista todos los conteos con opciones de filtrado"""
    form = BuscarConteoForm()
    
    # Inicializar consulta
    query = Conteo.query.join(Equipo).join(Visita)
    
    # Si es técnico, solo mostrar sus conteos
    if current_user.is_tecnico():
        query = query.filter(Visita.tecnico.has(usuario_id=current_user.id))
    
    # Aplicar filtros
    if request.args.get('buscar'):
        if form.equipo_id.data:
            query = query.filter(Conteo.equipo_id == form.equipo_id.data)
        if form.fecha_desde.data:
            query = query.filter(Conteo.fecha_conteo >= form.fecha_desde.data)
        if form.fecha_hasta.data:
            # Añadir 1 día a la fecha hasta para incluir todo el día
            fecha_hasta = form.fecha_hasta.data + timedelta(days=1)
            query = query.filter(Conteo.fecha_conteo <= fecha_hasta)
    else:
        # Por defecto, mostrar solo conteos del mes actual
        hoy = datetime.now().date()
        primer_dia_mes = hoy.replace(day=1)
        query = query.filter(Conteo.fecha_conteo >= primer_dia_mes)
    
    # Ordenar por fecha descendente
    query = query.order_by(Conteo.fecha_conteo.desc())
    
    # Paginación
    page = request.args.get('page', 1, type=int)
    por_pagina = 20
    conteos = query.paginate(page=page, per_page=por_pagina, error_out=False)
    
    return render_template('conteos/listar.html', 
                         conteos=conteos,
                         form=form,
                         titulo='Registro de Conteos')


@conteos_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    """Crea un nuevo registro de conteo"""
    form = ConteoForm()
    
    # Cargar opciones de selección
    _cargar_opciones_formulario(form)
    
    # Si se está creando desde una visita, precargar datos
    visita_id = request.args.get('visita_id')
    equipo_id = request.args.get('equipo_id')
    
    if visita_id:
        visita = Visita.query.get(visita_id)
        if visita:
            form.visita_id.data = visita.id
            if not equipo_id and visita.equipos:
                equipo_id = visita.equipos[0].id
    
    if equipo_id:
        equipo = Equipo.query.get(equipo_id)
        if equipo:
            form.equipo_id.data = equipo.id
            # Obtener el último conteo para este equipo
            ultimo_conteo = Conteo.query.filter_by(equipo_id=equipo.id)\
                .order_by(Conteo.fecha_conteo.desc()).first()
            
            if ultimo_conteo:
                form.contador_anterior_impresiones.data = ultimo_conteo.contador_actual_impresiones
                form.contador_anterior_escaneos.data = ultimo_conteo.contador_actual_escaneos
    
    if form.validate_on_submit():
        try:
            # Calcular diferencias
            dif_impresiones = form.contador_actual_impresiones.data - form.contador_anterior_impresiones.data
            dif_escaneos = form.contador_actual_escaneos.data - form.contador_anterior_escaneos.data
            
            # Crear registro de conteo
            conteo = Conteo(
                equipo_id=form.equipo_id.data,
                visita_id=form.visita_id.data if form.visita_id.data != '0' else None,
                fecha_conteo=form.fecha_conteo.data,
                contador_anterior_impresiones=form.contador_anterior_impresiones.data,
                contador_actual_impresiones=form.contador_actual_impresiones.data,
                diferencia_impresiones=dif_impresiones if dif_impresiones > 0 else 0,
                contador_anterior_escaneos=form.contador_anterior_escaneos.data,
                contador_actual_escaneos=form.contador_actual_escaneos.data,
                diferencia_escaneos=dif_escaneos if dif_escaneos > 0 else 0,
                estado_equipo=form.estado_equipo.data,
                observaciones=form.observaciones.data,
                registrado_por=current_user.id
            )
            
            # Actualizar contadores del equipo
            equipo = Equipo.query.get(form.equipo_id.data)
            if equipo:
                equipo.ultimo_conteo_impresiones = form.contador_actual_impresiones.data
                equipo.ultimo_conteo_escaneos = form.contador_actual_escaneos.data
                equipo.ultimo_conteo_fecha = form.fecha_conteo.data
                equipo.estado = form.estado_equipo.data
            
            db.session.add(conteo)
            db.session.commit()
            
            flash('Conteo registrado correctamente.', 'success')
            
            # Redirigir según el origen
            if form.visita_id.data and form.visita_id.data != '0':
                return redirect(url_for('visitas.detalle', id=form.visita_id.data))
            elif equipo:
                return redirect(url_for('equipos.detalle', id=equipo.id))
            else:
                return redirect(url_for('conteos.listar'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar el conteo: {str(e)}', 'error')
    
    return render_template('conteos/form.html', 
                         form=form, 
                         titulo='Nuevo Conteo')


@conteos_bp.route('/<int:id>')
@login_required
def detalle(id):
    """Muestra los detalles de un conteo"""
    conteo = Conteo.query.get_or_404(id)
    return render_template('conteos/detalle.html', conteo=conteo)


@conteos_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    """Edita un registro de conteo existente"""
    conteo = Conteo.query.get_or_404(id)
    
    # Verificar permisos (solo admin o el usuario que lo creó)
    if not current_user.is_admin() and conteo.registrado_por != current_user.id:
        flash('No tiene permiso para editar este conteo.', 'error')
        return redirect(url_for('conteos.listar'))
    
    form = ConteoForm(obj=conteo)
    
    # Cargar opciones de selección
    _cargar_opciones_formulario(form, conteo.equipo_id, conteo.visita_id)
    
    if form.validate_on_submit():
        try:
            # Calcular diferencias
            dif_impresiones = form.contador_actual_impresiones.data - form.contador_anterior_impresiones.data
            dif_escaneos = form.contador_actual_escaneos.data - form.contador_anterior_escaneos.data
            
            # Actualizar conteo
            conteo.equipo_id = form.equipo_id.data
            conteo.visita_id = form.visita_id.data if form.visita_id.data != '0' else None
            conteo.fecha_conteo = form.fecha_conteo.data
            conteo.contador_anterior_impresiones = form.contador_anterior_impresiones.data
            conteo.contador_actual_impresiones = form.contador_actual_impresiones.data
            conteo.diferencia_impresiones = dif_impresiones if dif_impresiones > 0 else 0
            conteo.contador_anterior_escaneos = form.contador_anterior_escaneos.data
            conteo.contador_actual_escaneos = form.contador_actual_escaneos.data
            conteo.diferencia_escaneos = dif_escaneos if dif_escaneos > 0 else 0
            conteo.estado_equipo = form.estado_equipo.data
            conteo.observaciones = form.observaciones.data
            
            # Actualizar contadores del equipo
            equipo = Equipo.query.get(form.equipo_id.data)
            if equipo:
                equipo.ultimo_conteo_impresiones = form.contador_actual_impresiones.data
                equipo.ultimo_conteo_escaneos = form.contador_actual_escaneos.data
                equipo.ultimo_conteo_fecha = form.fecha_conteo.data
                equipo.estado = form.estado_equipo.data
            
            db.session.commit()
            
            flash('Conteo actualizado correctamente.', 'success')
            
            # Redirigir según el origen
            if conteo.visita_id:
                return redirect(url_for('visitas.detalle', id=conteo.visita_id))
            elif equipo:
                return redirect(url_for('equipos.detalle', id=equipo.id))
            else:
                return redirect(url_for('conteos.listar'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el conteo: {str(e)}', 'error')
    
    return render_template('conteos/form.html', 
                         form=form, 
                         conteo=conteo,
                         titulo='Editar Conteo')


@conteos_bp.route('/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar(id):
    """Elimina un registro de conteo"""
    if not current_user.is_admin():
        flash('No tiene permiso para realizar esta acción.', 'error')
        return redirect(url_for('conteos.listar'))
    
    conteo = Conteo.query.get_or_404(id)
    
    try:
        equipo_id = conteo.equipo_id
        db.session.delete(conteo)
        
        # Actualizar el equipo con el último conteo disponible
        if equipo_id:
            ultimo_conteo = Conteo.query.filter(
                Conteo.equipo_id == equipo_id,
                Conteo.id != id  # Excluir el conteo que se está eliminando
            ).order_by(Conteo.fecha_conteo.desc()).first()
            
            equipo = Equipo.query.get(equipo_id)
            if equipo:
                if ultimo_conteo:
                    equipo.ultimo_conteo_impresiones = ultimo_conteo.contador_actual_impresiones
                    equipo.ultimo_conteo_escaneos = ultimo_conteo.contador_actual_escaneos
                    equipo.ultimo_conteo_fecha = ultimo_conteo.fecha_conteo
                else:
                    # Si no hay más conteos, limpiar los campos
                    equipo.ultimo_conteo_impresiones = None
                    equipo.ultimo_conteo_escaneos = None
                    equipo.ultimo_conteo_fecha = None
        
        db.session.commit()
        flash('Conteo eliminado correctamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el conteo: {str(e)}', 'error')
    
    return redirect(url_for('conteos.listar'))


def _cargar_opciones_formulario(form, equipo_id=None, visita_id=None):
    """Carga las opciones de los selectores en el formulario"""
    # Cargar equipos activos
    form.equipo_id.choices = [(eq.id, f"{eq.numero_serie} - {eq.marca} {eq.modelo}") 
                             for eq in Equipo.query.filter_by(activo=True).order_by('numero_serie').all()]
    
    # Cargar visitas recientes (últimos 30 días)
    fecha_limite = datetime.now().date() - timedelta(days=30)
    visitas = Visita.query.filter(Visita.fecha_visita >= fecha_limite)\
        .order_by(Visita.fecha_visita.desc()).all()
    
    form.visita_id.choices = [(0, 'Ninguna')] + \
                           [(v.id, f"{v.fecha_visita.strftime('%d/%m/%Y')} - {v.tipo_visita}") 
                            for v in visitas]
    
    # Establecer valores por defecto si se proporcionan
    if equipo_id:
        form.equipo_id.data = equipo_id
    if visita_id:
        form.visita_id.data = visita_id
    
    return form
