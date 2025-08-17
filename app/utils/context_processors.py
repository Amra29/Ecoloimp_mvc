from flask import current_app
from flask_login import current_user
from app.models import Solicitud

def inject_template_vars():
    """Make common template variables available to all templates."""
    def solicitudes_pendientes():
        if not hasattr(current_user, 'is_authenticated') or not current_user.is_authenticated:
            return 0
        if current_user.is_admin() or current_user.is_tecnico():
            return Solicitud.query.filter_by(estado='pendiente').count()
        return 0
    
    return dict(
        solicitudes_pendientes=solicitudes_pendientes
    )
