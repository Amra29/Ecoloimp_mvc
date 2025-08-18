from flask import Blueprint, render_template
from flask_login import login_required

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/inicio')
@login_required
def inicio():
    return render_template('dashboard/inicio.html')