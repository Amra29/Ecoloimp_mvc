from flask import Blueprint, request, render_template, redirect, url_for, flash
from app.models.models import db, Mantenimiento, Equipo
from flask_login import login_required

mantenimientos_bp = Blueprint('mantenimientos', __name__, url_prefix='/mantenimientos')

@mantenimientos_bp.route('/')
@login_required
def listar():
    mantenimientos = Mantenimiento.query.order_by(Mantenimiento.fecha_mantenimiento.desc()).limit(100).all()
    return render_template('mantenimientos/listar.html', mantenimientos=mantenimientos)

@mantenimientos_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    equipos = Equipo.query.all()
    if request.method == 'POST':
        equipo_id = request.form['equipo_id']
        fecha_mantenimiento = request.form['fecha_mantenimiento']
        descripcion = request.form['descripcion']
        realizado = bool(request.form.get('realizado'))
        mantenimiento = Mantenimiento(
            equipo_id=equipo_id,
            fecha_mantenimiento=fecha_mantenimiento,
            descripcion=descripcion,
            realizado=realizado
        )
        db.session.add(mantenimiento)
        db.session.commit()
        flash('Mantenimiento registrado correctamente.')
        return redirect(url_for('mantenimientos.listar'))
    return render_template('mantenimientos/nuevo.html', equipos=equipos)

@mantenimientos_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    mantenimiento = Mantenimiento.query.get_or_404(id)
    equipos = Equipo.query.all()
    if request.method == 'POST':
        mantenimiento.equipo_id = request.form['equipo_id']
        mantenimiento.fecha_mantenimiento = request.form['fecha_mantenimiento']
        mantenimiento.descripcion = request.form['descripcion']
        mantenimiento.realizado = bool(request.form.get('realizado'))
        db.session.commit()
        flash('Mantenimiento actualizado correctamente.')
        return redirect(url_for('mantenimientos.listar'))
    return render_template('mantenimientos/editar.html', mantenimiento=mantenimiento, equipos=equipos)

@mantenimientos_bp.route('/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar(id):
    mantenimiento = Mantenimiento.query.get_or_404(id)
    db.session.delete(mantenimiento)
    db.session.commit()
    flash('Mantenimiento eliminado correctamente.')
    return redirect(url_for('mantenimientos.listar'))