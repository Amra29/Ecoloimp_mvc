"""
Controlador para el panel de control del técnico
"""
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import func, and_
from app.models.models import db, Asignacion, PedidoPieza
from app.decorators import admin_or_tecnico_required

# Crear blueprint
tecnico_dashboard_bp = Blueprint('tecnico_dashboard', __name__)

@tecnico_dashboard_bp.route('/dashboard')
@login_required
@admin_or_tecnico_required
def dashboard():
    """Muestra el panel de control del técnico"""
    # Obtener estadísticas de asignaciones
    asignaciones_pendientes = Asignacion.query.filter_by(
        tecnico_id=current_user.id,
        estado='asignada'
    ).count()
    
    asignaciones_proceso = Asignacion.query.filter_by(
        tecnico_id=current_user.id,
        estado='en_proceso'
    ).count()
    
    asignaciones_completadas = Asignacion.query.filter_by(
        tecnico_id=current_user.id,
        estado='completada'
    ).count()
    
    # Obtener pedidos de piezas pendientes
    pedidos_pendientes = PedidoPieza.query.filter_by(
        tecnico_id=current_user.id,
        estado='pendiente'
    ).count()
    
    # Obtener últimas asignaciones
    ultimas_asignaciones = Asignacion.query.filter_by(
        tecnico_id=current_user.id
    ).order_by(Asignacion.fecha_asignacion.desc()).limit(5).all()
    
    return render_template('tecnico/dashboard.html',
                         tecnico=current_user,
                         asignaciones_pendientes=asignaciones_pendientes,
                         asignaciones_proceso=asignaciones_proceso,
                         asignaciones_completadas=asignaciones_completadas,
                         pedidos_pendientes=pedidos_pendientes,
                         ultimas_asignaciones=ultimas_asignaciones)

@tecnico_dashboard_bp.route('/mis_asignaciones')
@login_required
@admin_or_tecnico_required
def mis_asignaciones():
    """Redirige a la vista completa de asignaciones del blueprint legacy 'tecnico'"""
    return redirect(url_for('tecnico.mis_asignaciones'))

@tecnico_dashboard_bp.route('/solicitar_pieza', methods=['GET', 'POST'])
@login_required
@admin_or_tecnico_required
def solicitar_pieza():
    """Redirige a la vista de solicitud de pieza del blueprint legacy 'tecnico'"""
    return redirect(url_for('tecnico.solicitar_pieza'))

@tecnico_dashboard_bp.route('/ver_inventario')
@login_required
@admin_or_tecnico_required
def ver_inventario():
    """Redirige a la vista de inventario del blueprint legacy 'tecnico'"""
    return redirect(url_for('tecnico.ver_inventario'))

@tecnico_dashboard_bp.route('/mis_pedidos')
@login_required
@admin_or_tecnico_required
def mis_pedidos():
    """Redirige a la vista completa de pedidos del blueprint legacy 'tecnico'"""
    return redirect(url_for('tecnico.mis_pedidos'))
