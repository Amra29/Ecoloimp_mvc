from flask import Blueprint, request, render_template, redirect, url_for, flash
from app.models.models import db, Reporte, Usuario
from flask_login import login_required, current_user

reportes_bp = Blueprint('reportes', __name__, url_prefix='/reportes')

@reportes_bp.route('/')
@login_required
def listar():
    reportes = Reporte.query.order_by(Reporte.fecha_generacion.desc()).limit(100).all()
    return render_template('reportes/listar.html', reportes=reportes)

@reportes_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    if request.method == 'POST':
        tipo = request.form['tipo']
        parametros = request.form['parametros']
        datos = request.form['datos']
        reporte = Reporte(
            usuario_id=current_user.id,
            tipo=tipo,
            parametros=parametros,
            datos=datos
        )
        db.session.add(reporte)
        db.session.commit()
        flash('Reporte creado correctamente.')
        return redirect(url_for('reportes.listar'))
    return render_template('reportes/nuevo.html')

@reportes_bp.route('/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar(id):
    reporte = Reporte.query.get_or_404(id)
    db.session.delete(reporte)
    db.session.commit()
    flash('Reporte eliminado correctamente.')
    return redirect(url_for('reportes.listar'))