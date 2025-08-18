from flask import Blueprint, request, render_template, redirect, url_for, flash
from app.models.models import db, Cliente
from flask_login import login_required

clientes_bp = Blueprint('clientes', __name__, url_prefix='/clientes')

@clientes_bp.route('/')
@login_required
def listar():
    clientes = Cliente.query.all()
    return render_template('clientes/listar.html', clientes=clientes)

@clientes_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    if request.method == 'POST':
        nombre = request.form['nombre']
        contacto = request.form['contacto']
        email = request.form['email']
        telefono = request.form['telefono']
        direccion = request.form['direccion']
        cliente = Cliente(nombre=nombre, contacto=contacto, email=email, telefono=telefono, direccion=direccion)
        db.session.add(cliente)
        db.session.commit()
        flash('Cliente creado correctamente.')
        return redirect(url_for('clientes.listar'))
    return render_template('clientes/nuevo.html')

@clientes_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    cliente = Cliente.query.get_or_404(id)
    if request.method == 'POST':
        cliente.nombre = request.form['nombre']
        cliente.contacto = request.form['contacto']
        cliente.email = request.form['email']
        cliente.telefono = request.form['telefono']
        cliente.direccion = request.form['direccion']
        db.session.commit()
        flash('Cliente actualizado correctamente.')
        return redirect(url_for('clientes.listar'))
    return render_template('clientes/editar.html', cliente=cliente)

@clientes_bp.route('/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar(id):
    cliente = Cliente.query.get_or_404(id)
    db.session.delete(cliente)
    db.session.commit()
    flash('Cliente eliminado correctamente.')
    return redirect(url_for('clientes.listar'))