from flask import Blueprint, request, render_template, redirect, url_for, flash
from app.models.models import db, Solicitud, Cliente, Equipo, Usuario
from flask_login import login_required, current_user

solicitudes_bp = Blueprint('solicitudes', __name__, url_prefix='/solicitudes')

@solicitudes_bp.route('/')
@login_required
def listar():
    solicitudes = Solicitud.query.order_by(Solicitud.fecha_creacion.desc()).limit(100).all()
    return render_template('solicitudes/listar.html', solicitudes=solicitudes)

@solicitudes_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    clientes = Cliente.query.all()
    equipos = Equipo.query.all()
    tecnicos = Usuario.query.filter_by(rol='tecnico').all()
    if request.method == 'POST':
        cliente_id = request.form['cliente_id']
        equipo_id = request.form.get('equipo_id')
        descripcion = request.form['descripcion']
        tecnico_id = request.form.get('tecnico_id')
        solicitud = Solicitud(
            cliente_id=cliente_id,
            equipo_id=equipo_id,
            usuario_id=current_user.id,
            descripcion=descripcion,
            tecnico_id=tecnico_id
        )
        db.session.add(solicitud)
        db.session.commit()
        flash('Solicitud creada correctamente.')
        return redirect(url_for('solicitudes.listar'))
    return render_template('solicitudes/nuevo.html', clientes=clientes, equipos=equipos, tecnicos=tecnicos)

@solicitudes_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    solicitud = Solicitud.query.get_or_404(id)
    clientes = Cliente.query.all()
    equipos = Equipo.query.all()
    tecnicos = Usuario.query.filter_by(rol='tecnico').all()
    if request.method == 'POST':
        solicitud.cliente_id = request.form['cliente_id']
        solicitud.equipo_id = request.form.get('equipo_id')
        solicitud.descripcion = request.form['descripcion']
        solicitud.tecnico_id = request.form.get('tecnico_id')
        db.session.commit()
        flash('Solicitud actualizada correctamente.')
        return redirect(url_for('solicitudes.listar'))
    return render_template('solicitudes/editar.html', solicitud=solicitud, clientes=clientes, equipos=equipos, tecnicos=tecnicos)

@solicitudes_bp.route('/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar(id):
    solicitud = Solicitud.query.get_or_404(id)
    db.session.delete(solicitud)
    db.session.commit()
    flash('Solicitud eliminada correctamente.')
    return redirect(url_for('solicitudes.listar'))