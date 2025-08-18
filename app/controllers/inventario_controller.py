from flask import Blueprint, request, render_template, redirect, url_for, flash
from app.models.models import db, InventarioItem, Bodega
from flask_login import login_required

inventario_bp = Blueprint('inventario', __name__, url_prefix='/inventario')

@inventario_bp.route('/')
@login_required
def listar():
    items = InventarioItem.query.all()
    return render_template('inventario/listar.html', items=items)

@inventario_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    bodegas = Bodega.query.all()
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        cantidad = request.form['cantidad']
        ubicacion_id = request.form['ubicacion_id']
        codigo_barras = request.form['codigo_barras']
        item = InventarioItem(
            nombre=nombre, descripcion=descripcion, cantidad=cantidad,
            ubicacion_id=ubicacion_id, codigo_barras=codigo_barras
        )
        db.session.add(item)
        db.session.commit()
        flash('Ítem de inventario creado correctamente.')
        return redirect(url_for('inventario.listar'))
    return render_template('inventario/nuevo.html', bodegas=bodegas)

@inventario_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    item = InventarioItem.query.get_or_404(id)
    bodegas = Bodega.query.all()
    if request.method == 'POST':
        item.nombre = request.form['nombre']
        item.descripcion = request.form['descripcion']
        item.cantidad = request.form['cantidad']
        item.ubicacion_id = request.form['ubicacion_id']
        item.codigo_barras = request.form['codigo_barras']
        db.session.commit()
        flash('Ítem actualizado correctamente.')
        return redirect(url_for('inventario.listar'))
    return render_template('inventario/editar.html', item=item, bodegas=bodegas)

@inventario_bp.route('/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar(id):
    item = InventarioItem.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('Ítem eliminado correctamente.')
    return redirect(url_for('inventario.listar'))