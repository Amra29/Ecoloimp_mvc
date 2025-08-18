from flask import Blueprint, request, render_template, redirect, url_for, flash
from app.models.models import db, Equipo, Cliente
from flask_login import login_required

equipos_bp = Blueprint('equipos', __name__, url_prefix='/equipos')

@equipos_bp.route('/')
@login_required
def listar():
    equipos = Equipo.query.all()
    return render_template('equipos/listar.html', equipos=equipos)

@equipos_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    clientes = Cliente.query.all()
    if request.method == 'POST':
        marca = request.form['marca']
        modelo = request.form['modelo']
        numero_serie = request.form['numero_serie']
        ubicacion = request.form['ubicacion']
        cliente_id = request.form['cliente_id']
        equipo = Equipo(marca=marca, modelo=modelo, numero_serie=numero_serie, ubicacion=ubicacion, cliente_id=cliente_id)
        db.session.add(equipo)
        db.session.commit()
        flash('Equipo creado correctamente.')
        return redirect(url_for('equipos.listar'))
    return render_template('equipos/nuevo.html', clientes=clientes)

@equipos_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    equipo = Equipo.query.get_or_404(id)
    clientes = Cliente.query.all()
    if request.method == 'POST':
        equipo.marca = request.form['marca']
        equipo.modelo = request.form['modelo']
        equipo.numero_serie = request.form['numero_serie']
        equipo.ubicacion = request.form['ubicacion']
        equipo.cliente_id = request.form['cliente_id']
        db.session.commit()
        flash('Equipo actualizado correctamente.')
        return redirect(url_for('equipos.listar'))
    return render_template('equipos/editar.html', equipo=equipo, clientes=clientes)

@equipos_bp.route('/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar(id):
    equipo = Equipo.query.get_or_404(id)
    db.session.delete(equipo)
    db.session.commit()
    flash('Equipo eliminado correctamente.')
    return redirect(url_for('equipos.listar'))