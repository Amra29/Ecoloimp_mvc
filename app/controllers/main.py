from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.models import db, Cliente, Tecnico, Visita, Equipo, Conteo, Asignacion, Solicitud
from datetime import datetime, timedelta

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
@login_required
def index():
    """Dashboard principal que se adapta según el rol del usuario"""
    if current_user.is_admin():
        return admin_dashboard()
    elif current_user.is_tecnico():
        return tecnico_dashboard()
    else:
        return user_dashboard()


def admin_dashboard():
    """Dashboard para administradores"""
    # Estadísticas generales
    total_clientes = Cliente.query.filter_by(activo=True).count()
    total_equipos = Equipo.query.count()
    total_tecnicos = Tecnico.query.filter_by(activo=True).count()
    
    # Últimas visitas
    ultimas_visitas = Visita.query.order_by(Visita.fecha_visita.desc()).limit(5).all()
    
    # Conteos recientes
    conteos_recientes = Conteo.query.order_by(Conteo.fecha_conteo.desc()).limit(5).all()

    return render_template('admin/dashboard.html',
                         total_clientes=total_clientes,
                         total_equipos=total_equipos,
                         total_tecnicos=total_tecnicos,
                         ultimas_visitas=ultimas_visitas,
                         conteos_recientes=conteos_recientes)


def tecnico_dashboard():
    """Dashboard para técnicos"""
    # Obtener el perfil del técnico asociado al usuario
    tecnico = Tecnico.query.filter_by(usuario_id=current_user.id).first()
    
    if not tecnico:
        flash('No se encontró el perfil de técnico asociado a su cuenta.', 'warning')
        return redirect(url_for('auth.logout'))

    # Estadísticas del técnico
    asignaciones_pendientes = Asignacion.query.filter_by(tecnico_id=tecnico.id, estado='asignada').count()
    asignaciones_proceso = Asignacion.query.filter_by(tecnico_id=tecnico.id, estado='en_proceso').count()
    # Obtener visitas programadas para el técnico
    hoy = datetime.now().date()
    proximas_visitas = Visita.query.filter(
        Visita.tecnico_id == tecnico.id,
        Visita.estado.in_(['programada', 'en_proceso']),
        Visita.fecha_visita >= hoy
    ).order_by(Visita.fecha_visita.asc()).limit(5).all()
    
    # Obtener conteos recientes del técnico
    conteos_recientes = Conteo.query.join(Visita).filter(
        Visita.tecnico_id == tecnico.id
    ).order_by(Conteo.fecha_conteo.desc()).limit(5).all()

    return render_template('tecnico/dashboard.html',
                         tecnico=tecnico,
                         proximas_visitas=proximas_visitas,
                         conteos_recientes=conteos_recientes,
                         hoy=hoy)


def user_dashboard():
    """Dashboard para usuarios normales"""
    # Estadísticas básicas
    total_clientes = Cliente.query.filter_by(activo=True).count()
    solicitudes_recientes = Solicitud.query.order_by(Solicitud.fecha_solicitud.desc()).limit(5).all()

    return render_template('user/dashboard.html',
                           total_clientes=total_clientes,
                           solicitudes_recientes=solicitudes_recientes)
