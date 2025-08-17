"""
Controlador para el panel de control del técnico

Este módulo maneja las rutas relacionadas con el panel de control de los técnicos,
incluyendo la visualización de asignaciones, pedidos de piezas y otras funcionalidades
específicas para técnicos.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from flask_login import current_user
from sqlalchemy import func
from app.models.models import db, Asignacion, PedidoPieza
from app.decorators import role_required, permission_required

# Crear blueprint
tecnico_dashboard_bp = Blueprint('tecnico_dashboard', __name__, 
                               template_folder='../../templates/tecnico',
                               url_prefix='/tecnico')

@tecnico_dashboard_bp.route('/dashboard')
@role_required('tecnico', 'admin')
@permission_required('ver_dashboard_tecnico')
def dashboard():
    """
    Muestra el panel de control del técnico con estadísticas y resúmenes.
    
    Requiere el rol de 'tecnico' o 'admin' y el permiso 'ver_dashboard_tecnico'.
    """
    try:
        # Obtener estadísticas de asignaciones
        estadisticas = {
            'asignaciones_pendientes': Asignacion.query.filter_by(
                tecnico_id=current_user.id,
                estado='asignada'
            ).count(),
            'asignaciones_proceso': Asignacion.query.filter_by(
                tecnico_id=current_user.id,
                estado='en_proceso'
            ).count(),
            'asignaciones_completadas': Asignacion.query.filter_by(
                tecnico_id=current_user.id,
                estado='completada'
            ).count(),
            'pedidos_pendientes': PedidoPieza.query.filter_by(
                tecnico_id=current_user.id,
                estado='pendiente'
            ).count()
        }
        
        # Obtener últimas asignaciones
        ultimas_asignaciones = Asignacion.query.filter_by(
            tecnico_id=current_user.id
        ).order_by(Asignacion.fecha_asignacion.desc()).limit(5).all()
        
        return render_template('dashboard.html',
                            tecnico=current_user,
                            estadisticas=estadisticas,
                            ultimas_asignaciones=ultimas_asignaciones)
    except Exception as e:
        current_app.logger.error(f'Error en dashboard técnico: {str(e)}')
        flash('Ocurrió un error al cargar el panel de control.', 'error')
        return redirect(url_for('main.index'))

@tecnico_dashboard_bp.route('/asignaciones')
@role_required('tecnico', 'admin')
@permission_required('ver_asignaciones')
def mis_asignaciones():
    """
    Muestra las asignaciones del técnico actual.
    
    Requiere el rol de 'tecnico' o 'admin' y el permiso 'ver_asignaciones'.
    """
    try:
        # Obtener todas las asignaciones del técnico ordenadas por prioridad y fecha
        asignaciones = Asignacion.query.filter_by(
            tecnico_id=current_user.id
        ).order_by(
            Asignacion.prioridad.desc(),
            Asignacion.fecha_asignacion.desc()
        ).all()
        
        return render_template('asignaciones/lista.html',
                            asignaciones=asignaciones)
    except Exception as e:
        current_app.logger.error(f'Error al cargar asignaciones: {str(e)}')
        flash('Ocurrió un error al cargar las asignaciones.', 'error')
        return redirect(url_for('tecnico_dashboard.dashboard'))

@tecnico_dashboard_bp.route('/pedidos')
@role_required('tecnico', 'admin')
@permission_required('ver_pedidos')
def mis_pedidos():
    """
    Muestra los pedidos de piezas realizados por el técnico actual.
    
    Requiere el rol de 'tecnico' o 'admin' y el permiso 'ver_pedidos'.
    """
    try:
        # Obtener los pedidos del técnico ordenados por fecha descendente
        pedidos = PedidoPieza.query.filter_by(
            tecnico_id=current_user.id
        ).order_by(
            PedidoPieza.fecha_solicitud.desc()
        ).all()
        
        return render_template('pedidos/lista.html',
                            pedidos=pedidos)
    except Exception as e:
        current_app.logger.error(f'Error al cargar pedidos: {str(e)}')
        flash('Ocurrió un error al cargar los pedidos de piezas.', 'error')
        return redirect(url_for('tecnico_dashboard.dashboard'))

@tecnico_dashboard_bp.route('/inventario')
@role_required('tecnico', 'admin')
@permission_required('ver_inventario')
def ver_inventario():
    """
    Muestra el inventario de piezas disponibles.
    
    Requiere el rol de 'tecnico' o 'admin' y el permiso 'ver_inventario'.
    """
    try:
        # Implementar lógica para obtener el inventario
        # inventario = Pieza.query.filter_by(disponible=True).all()
        return render_template('inventario/lista.html')
    except Exception as e:
        current_app.logger.error(f'Error al cargar inventario: {str(e)}')
        flash('Ocurrió un error al cargar el inventario.', 'error')
        return redirect(url_for('tecnico_dashboard.dashboard'))

@tecnico_dashboard_bp.route('/solicitar_pieza', methods=['GET', 'POST'])
@role_required('tecnico', 'admin')
@permission_required('solicitar_piezas')
def solicitar_pieza():
    """
    Permite al técnico solicitar una pieza del inventario.
    
    Requiere el rol de 'tecnico' o 'admin' y el permiso 'solicitar_piezas'.
    """
    if request.method == 'POST':
        try:
            # Procesar el formulario de solicitud de pieza
            # Implementar lógica de validación y creación del pedido
            flash('Solicitud de pieza enviada correctamente.', 'success')
            return redirect(url_for('tecnico_dashboard.mis_pedidos'))
        except Exception as e:
            current_app.logger.error(f'Error al solicitar pieza: {str(e)}')
            flash('Ocurrió un error al procesar la solicitud.', 'error')
    
    # Mostrar formulario de solicitud
    return render_template('pedidos/solicitar.html')
