from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

config_bp = Blueprint('config', __name__, url_prefix='/config')

@config_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        # procesar cambios de configuración global
        flash('Configuración actualizada.')
        return redirect(url_for('config.index'))
    return render_template('config/index.html')