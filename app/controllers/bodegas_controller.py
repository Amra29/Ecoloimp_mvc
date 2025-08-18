from flask import Blueprint, request, render_template, redirect, url_for, flash
from app.models.models import db, Bodega
from flask_login import login_required

bodegas_bp = Blueprint('bodegas', __name__, url_prefix='/bodegas')

@bodegas_bp.route('/')
@login_required
def listar():
    bodegas = Bodega.query.all()
    return render_template('bodegas/listar.html', bodegas=bodegas)

@bodegas_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    if request.method == 'POST':
        nombre = request.form['nombre']
        direccion = request.form['direccion']
        bodega = Bodega(nombre=nombre, direccion=direccion)
        db.session.add(bodega)
        db.session.commit()
        flash('Bodega creada correctamente.')
        return redirect(url_for('bodegas.listar'))
    return render_template('bodegas/nuevo.html')

@bodegas_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    bodega = Bodega.query.get_or_404(id)
    if request.method == 'POST':
        bodega.nombre = request.form['nombre']
        bodega.direccion = request.form['direccion']
        db.session.commit()
        flash('Bodega actualizada correctamente.')
        return redirect(url_for('bodegas.listar'))
    return render_template('bodegas/editar.html', bodega=bodega)

@bodegas_bp.route('/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar(id):
    bodega = Bodega.query.get_or_404(id)
    db.session.delete(bodega)
    db.session.commit()
    flash('Bodega eliminada correctamente.')
    return redirect(url_for('bodegas.listar'))