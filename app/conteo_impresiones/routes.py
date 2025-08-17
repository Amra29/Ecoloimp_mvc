from flask import render_template, flash, redirect, url_for, request, current_app, jsonify, abort
from flask_login import login_required, current_user
from sqlalchemy import desc, func, or_
from datetime import datetime, timedelta, date
from sqlalchemy.orm import joinedload
from app.extensions import db
from app.conteo_impresiones import bp
from app.models import Conteo, Equipo, Sucursal, Cliente, Tecnico, Usuario, Visita, Permiso, Solicitud
from app.conteo_impresiones.forms import ConteoImpresionForm
from app.decorators import admin_required, tecnico_required, permisos_requeridos

def _configurar_opciones_formulario(form):
    """Configura las opciones dinámicas del formulario de conteo."""
    # Obtener listas para los select
    clientes = Cliente.query.filter_by(activo=True).order_by(Cliente.nombre).all()
    form.cliente_id.choices = [(0, 'Seleccione un cliente')] + [(c.id, c.nombre) for c in clientes]
    
    # Cargar sucursales basadas en el cliente seleccionado
    if 'cliente_id' in request.form and request.form['cliente_id']:
        sucursales = Sucursal.query.filter_by(
            cliente_id=request.form['cliente_id'],
            activa=True
        ).order_by(Sucursal.nombre).all()
        form.sucursal_id.choices = [(0, 'Seleccione una sucursal')] + [(s.id, f"{s.nombre} - {s.ciudad}") for s in sucursales]
    else:
        form.sucursal_id.choices = [(0, 'Seleccione un cliente primero')]
    
    # Cargar equipos (impresoras) basados en la sucursal seleccionada
    if 'sucursal_id' in request.form and request.form['sucursal_id']:
        equipos = Equipo.query.filter(
            Equipo.sucursal_id == request.form['sucursal_id'],
            Equipo.estado != 'baja',
            Equipo.tipo.in_(['impresora', 'multifuncional'])  # Solo equipos que pueden tener contadores
        ).order_by(Equipo.modelo).all()
        form.equipo_id.choices = [(0, 'Seleccione un equipo')] + [(e.id, f"{e.marca} {e.modelo} - {e.numero_serie}") for e in equipos]
    else:
        form.equipo_id.choices = [(0, 'Seleccione una sucursal primero')]

def _cargar_ultimo_conteo(equipo_id):
    """Carga el último conteo registrado para un equipo."""
    if not equipo_id:
        return None
    return Conteo.query.filter_by(equipo_id=equipo_id)\
                     .order_by(desc(Conteo.fecha_conteo))\
                     .first()

@bp.route('/')
@login_required
@permisos_requeridos('ver_conteos')
def index():
    """
    Página principal del módulo de conteo de impresiones.
    Muestra un listado de los últimos conteos realizados.
    """
    # Obtener parámetros de filtrado
    page = request.args.get('page', 1, type=int)
    cliente_id = request.args.get('cliente_id', type=int)
    fecha_desde = request.args.get('fecha_desde')
    fecha_hasta = request.args.get('fecha_hasta')
    
    # Construir consulta base
    query = Conteo.query.join(Equipo).options(
        db.joinedload(Conteo.equipo),
        db.joinedload(Conteo.tecnico)
    )
    
    # Aplicar filtros
    if cliente_id:
        query = query.filter(Equipo.cliente_id == cliente_id)
        
    if fecha_desde:
        try:
            fecha_desde_dt = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
            query = query.filter(Conteo.fecha_conteo >= fecha_desde_dt)
        except ValueError:
            flash('Formato de fecha desde inválido', 'error')
    
    if fecha_hasta:
        try:
            fecha_hasta_dt = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
            query = query.filter(Conteo.fecha_conteo <= fecha_hasta_dt)
        except ValueError:
            flash('Formato de fecha hasta inválido', 'error')
    
    # Si es técnico, solo ver sus propios conteos
    if current_user.is_tecnico():
        query = query.filter(Conteo.tecnico_id == current_user.id)
    
    # Ordenar y paginar
    conteos = query.order_by(Conteo.fecha_conteo.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    # Obtener lista de clientes para el filtro
    clientes = Cliente.query.filter_by(activo=True).order_by(Cliente.nombre).all()
    
    return render_template('conteo_impresiones/index.html', 
                         conteos=conteos,
                         clientes=clientes,
                         filtros={
                             'cliente_id': cliente_id,
                             'fecha_desde': fecha_desde,
                             'fecha_hasta': fecha_hasta
                         })

@bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
@permisos_requeridos('crear_conteo')
def nuevo_conteo():
    """
    Crear un nuevo registro de conteo de impresiones.
    
    Los técnicos pueden registrar nuevos conteos para equipos existentes.
    El sistema calcula automáticamente las diferencias con el último conteo.
    """
    form = ConteoImpresionForm()
    
    # Configurar opciones de formulario
    _configurar_opciones_formulario(form)
    
    # Si es una solicitud POST, validar y procesar el formulario
    if form.validate_on_submit():
        try:
            # Obtener datos del formulario
            equipo_id = form.equipo_id.data
            contador_impresiones = form.contador_impresiones.data
            contador_escaneos = form.contador_escaneos.data
            contador_copias = form.contador_copias.data
            estado_equipo = form.estado_equipo.data
            requiere_mantenimiento = form.requiere_mantenimiento.data
            problemas_detectados = form.problemas_detectados.data
            observaciones = form.observaciones.data
            
            # Obtener el equipo y verificar permisos
            equipo = Equipo.query.get_or_404(equipo_id)
            
            # Verificar que el técnico tenga permiso para este cliente
            if not current_user.is_admin() and not current_user.puede_ver_cliente(equipo.cliente_id):
                flash('No tiene permiso para registrar conteos en este cliente', 'error')
                return redirect(url_for('conteo_impresiones.index'))
            
            # Obtener el último conteo para este equipo
            ultimo_conteo = Conteo.query.filter_by(equipo_id=equipo_id)\
                                     .order_by(desc(Conteo.fecha_conteo))\
                                     .first()
            
            # Crear nuevo registro de conteo
            nuevo_conteo = Conteo(
                equipo_id=equipo_id,
                visita_id=form.visita_id.data or None,
                tecnico_id=current_user.id,
                fecha_conteo=datetime.utcnow().date(),
                contador_impresion_actual=contador_impresiones,
                contador_escaneo_actual=contador_escaneos,
                contador_copias_actual=contador_copias,
                contador_impresion_anterior=ultimo_conteo.contador_impresion_actual if ultimo_conteo else 0,
                contador_escaneo_anterior=ultimo_conteo.contador_escaneo_actual if ultimo_conteo else 0,
                contador_copias_anterior=ultimo_conteo.contador_copias_actual if ultimo_conteo else 0,
                estado_equipo=estado_equipo,
                requiere_mantenimiento=requiere_mantenimiento,
                problemas_detectados=problemas_detectados if requiere_mantenimiento else None,
                observaciones=observaciones,
                registrado_por=current_user.id
            )
            
            # Calcular diferencias
            nuevo_conteo.calcular_diferencias()
            
            # Actualizar información del equipo
            equipo.ultimo_conteo_impresiones = contador_impresiones
            equipo.ultimo_conteo_escaneos = contador_escaneos
            equipo.ultimo_conteo_copias = contador_copias
            equipo.ultimo_conteo_fecha = datetime.utcnow()
            
            # Actualizar estado del equipo si es necesario
            if requiere_mantenimiento:
                equipo.estado = 'en_mantenimiento'
                equipo.fecha_ultimo_mantenimiento = datetime.utcnow().date()
                # Calcular próxima fecha de mantenimiento (30 días después)
                equipo.fecha_proximo_mantenimiento = datetime.utcnow().date() + timedelta(days=30)
            
            # Guardar cambios en la base de datos
            db.session.add(nuevo_conteo)
            db.session.add(equipo)
            db.session.commit()
            
            flash('Conteo registrado exitosamente', 'success')
            
            # Redirigir según el origen
            if form.visita_id.data:
                return redirect(url_for('visitas.detalle', id=form.visita_id.data))
            return redirect(url_for('conteo_impresiones.detalle', id=nuevo_conteo.id))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error al guardar el conteo: {str(e)}", exc_info=True)
            flash('Ocurrió un error al guardar el conteo. Por favor, intente nuevamente.', 'error')
    
    # Cargar datos iniciales si se proporciona un equipo_id
    equipo_id = request.args.get('equipo_id')
    if equipo_id and not form.is_submitted():
        equipo = Equipo.query.get(equipo_id)
        if equipo:
            form.equipo_id.data = equipo.id
            form.cliente_id.data = equipo.cliente_id
            form.sucursal_id.data = equipo.sucursal_id
            
            # Cargar último conteo para este equipo
            ultimo_conteo = Conteo.query.filter_by(equipo_id=equipo.id)\
                                     .order_by(desc(Conteo.fecha_conteo))\
                                     .first()
            
            if ultimo_conteo:
                form.contador_impresiones_anterior.data = ultimo_conteo.contador_impresion_actual
                form.contador_escaneos_anterior.data = ultimo_conteo.contador_escaneo_actual
                form.contador_copias_anterior.data = ultimo_conteo.contador_copias_actual
    
    return render_template('conteo_impresiones/nuevo.html', 
                         form=form,
                         titulo='Nuevo Conteo de Impresiones')

@bp.route('/<int:id>')
@login_required
@permisos_requeridos('ver_conteos')
def ver_conteo(id):
    """Ver los detalles de un conteo específico"""
    # Cargar el conteo con todas las relaciones necesarias
    conteo = Conteo.query.options(
        joinedload(Conteo.equipo).joinedload(Equipo.cliente),
        joinedload(Conteo.tecnico),
        joinedload(Conteo.usuario_registro),
        joinedload(Conteo.visita)
    ).get_or_404(id)
    
    # Verificar permisos - solo admin o el técnico que lo creó pueden ver
    if not current_user.is_admin() and conteo.registrado_por != current_user.id:
        abort(403)
    
    # Obtener estadísticas de uso
    hoy = date.today()
    primer_dia_mes = hoy.replace(day=1)
    
    # Conteos del mes actual para este equipo
    conteos_mes = Conteo.query.filter(
        Conteo.equipo_id == conteo.equipo_id,
        Conteo.fecha_conteo >= primer_dia_mes,
        Conteo.fecha_conteo <= hoy
    ).order_by(Conteo.fecha_conteo).all()
    
    # Calcular totales del mes
    total_impresiones = sum(c.diferencia_impresiones for c in conteos_mes)
    total_escaneos = sum(c.diferencia_escaneos for c in conteos_mes)
    total_copias = sum(c.diferencia_copias for c in conteos_mes)
    
    return render_template('conteo_impresiones/ver.html', 
                         conteo=conteo,
                         total_impresiones=total_impresiones,
                         total_escaneos=total_escaneos,
                         total_copias=total_copias,
                         conteos_mes=conteos_mes)

@bp.route('/historial/equipo/<int:equipo_id>')
@login_required
@permisos_requeridos('ver_conteos', 'ver_reportes')
def historial_equipo(equipo_id):
    """
    Ver el historial de conteos para un equipo específico
    
    Permite filtrar por rango de fechas y muestra estadísticas de uso.
    """
    # Obtener parámetros de filtrado
    fecha_desde = request.args.get('fecha_desde')
    fecha_hasta = request.args.get('fecha_hasta')
    
    # Validar fechas
    try:
        fecha_inicio = datetime.strptime(fecha_desde, '%Y-%m-%d').date() if fecha_desde else None
        fecha_fin = datetime.strptime(fecha_hasta, '%Y-%m-%d').date() if fecha_hasta else None
    except ValueError:
        flash('Formato de fecha inválido. Use YYYY-MM-DD', 'error')
        fecha_inicio = fecha_fin = None
    
    # Obtener el equipo con su cliente
    equipo = Equipo.query.options(
        joinedload(Equipo.cliente),
        joinedload(Equipo.sucursal)
    ).get_or_404(equipo_id)
    
    # Verificar permisos - solo admin o técnicos asignados pueden ver
    if not current_user.is_admin() and not current_user.puede_ver_cliente(equipo.cliente_id):
        abort(403)
    
    # Construir consulta base
    query = Conteo.query.filter_by(equipo_id=equipo_id)
    
    # Aplicar filtros de fecha si existen
    if fecha_inicio and fecha_fin:
        query = query.filter(Conteo.fecha_conteo.between(fecha_inicio, fecha_fin))
    
    # Obtener conteos ordenados por fecha
    conteos = query.options(
        joinedload(Conteo.tecnico),
        joinedload(Conteo.usuario_registro)
    ).order_by(Conteo.fecha_conteo.desc()).all()
    
    # Calcular estadísticas
    total_impresiones = sum(c.diferencia_impresiones for c in conteos)
    total_escaneos = sum(c.diferencia_escaneos for c in conteos)
    total_copias = sum(c.diferencia_copias for c in conteos)
    
    # Obtener conteo más reciente
    ultimo_conteo = conteos[0] if conteos else None
    
    # Obtener promedio diario si hay suficientes datos
    promedio_diario = None
    if len(conteos) > 1 and fecha_inicio and fecha_fin:
        dias = (fecha_fin - fecha_inicio).days or 1
        promedio_diario = {
            'impresiones': round(total_impresiones / dias, 2),
            'escaneos': round(total_escaneos / dias, 2),
            'copias': round(total_copias / dias, 2)
        }
    
    return render_template(
        'conteo_impresiones/historial.html',
        equipo=equipo,
        conteos=conteos,
        ultimo_conteo=ultimo_conteo,
        total_impresiones=total_impresiones,
        total_escaneos=total_escaneos,
        total_copias=total_copias,
        promedio_diario=promedio_diario,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta
    )

@bp.route('/api/sucursales/<int:cliente_id>')
@login_required
def get_sucursales(cliente_id):
    """API para obtener sucursales de un cliente (AJAX)"""
    sucursales = Sucursal.query.filter_by(
        cliente_id=cliente_id,
        activa=True
    ).order_by(Sucursal.nombre).all()
    
    sucursales_json = [{
        'id': s.id,
        'nombre': f"{s.nombre} - {s.ciudad}"
    } for s in sucursales]
    
    return {'sucursales': sucursales_json}

@bp.route('/api/equipos/<int:sucursal_id>')
@login_required
def get_equipos(sucursal_id):
    """
    API para obtener equipos (impresoras) de una sucursal (AJAX)
    
    Devuelve información detallada de los equipos de impresión de una sucursal,
    incluyendo el último conteo registrado y estadísticas de uso.
    """
    # Verificar que el usuario tenga acceso a esta sucursal
    if not current_user.is_admin():
        sucursal = Sucursal.query.get_or_404(sucursal_id)
        if not current_user.puede_ver_cliente(sucursal.cliente_id):
            return jsonify({'error': 'No autorizado'}), 403
    
    # Obtener equipos activos de la sucursal
    equipos = Equipo.query.filter(
        Equipo.sucursal_id == sucursal_id,
        Equipo.estado == 'activo',
        Equipo.tipo.in_(['impresora', 'multifuncional'])
    ).order_by(Equipo.modelo).all()
    
    # Obtener el último conteo para cada equipo
    equipos_con_info = []
    for equipo in equipos:
        # Obtener último conteo con información del técnico
        ultimo_conteo = Conteo.query.options(
            joinedload(Conteo.tecnico)
        ).filter_by(
            equipo_id=equipo.id
        ).order_by(Conteo.fecha_conteo.desc()).first()
        
        # Calcular días desde el último conteo
        dias_desde_ultimo = None
        if ultimo_conteo and ultimo_conteo.fecha_conteo:
            dias_desde_ultimo = (date.today() - ultimo_conteo.fecha_conteo).days
        
        # Obtener estadísticas del mes actual
        hoy = date.today()
        primer_dia_mes = hoy.replace(day=1)
        
        conteos_mes = Conteo.query.filter(
            Conteo.equipo_id == equipo.id,
            Conteo.fecha_conteo >= primer_dia_mes,
            Conteo.fecha_conteo <= hoy
        ).all()
        
        # Calcular totales del mes
        total_impresiones = sum(c.diferencia_impresiones for c in conteos_mes)
        total_escaneos = sum(c.diferencia_escaneos for c in conteos_mes)
        total_copias = sum(c.diferencia_copias for c in conteos_mes)
        
        equipos_con_info.append({
            'id': equipo.id,
            'nombre': f"{equipo.marca} {equipo.modelo}",
            'numero_serie': equipo.numero_serie,
            'ubicacion': equipo.ubicacion_detalle or 'No especificada',
            'ultimo_conteo': {
                'fecha': ultimo_conteo.fecha_conteo.strftime('%d/%m/%Y') if ultimo_conteo else 'Nunca',
                'impresiones': ultimo_conteo.contador_impresion_actual if ultimo_conteo else 0,
                'escaneos': ultimo_conteo.contador_escaneo_actual if ultimo_conteo else 0,
                'copias': ultimo_conteo.contador_copias_actual if ultimo_conteo else 0,
                'tecnico': ultimo_conteo.tecnico.nombre if ultimo_conteo and ultimo_conteo.tecnico else 'N/A',
                'estado': ultimo_conteo.estado_equipo if ultimo_conteo else 'desconocido',
                'requiere_mantenimiento': ultimo_conteo.requiere_mantenimiento if ultimo_conteo else False
            },
            'estadisticas_mes': {
                'impresiones': total_impresiones,
                'escaneos': total_escaneos,
                'copias': total_copias,
                'promedio_diario': {
                    'impresiones': round(total_impresiones / hoy.day, 2) if hoy.day > 0 else 0,
                    'escaneos': round(total_escaneos / hoy.day, 2) if hoy.day > 0 else 0,
                    'copias': round(total_copias / hoy.day, 2) if hoy.day > 0 else 0
                }
            },
            'dias_desde_ultimo_conteo': dias_desde_ultimo,
            'necesita_conteo': not ultimo_conteo or dias_desde_ultimo > 7,
            'estado': equipo.estado
        })
    
    return jsonify({
        'equipos': equipos_con_info,
        'total': len(equipos_con_info),
        'fecha_consulta': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
