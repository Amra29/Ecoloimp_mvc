from flask import Blueprint, request, render_template, redirect, url_for, flash
from app.models.models import db, PedidoItem, Pedido, InventarioItem
from flask_login import login_required

pedido_items_bp = Blueprint('pedido_items', __name__, url_prefix='/pedido_items')

@pedido_items_bp.route('/')
@login_required
def listar():
    pedido_items = PedidoItem.query.all()
    return render_template('pedido_items/listar.html', pedido_items=pedido_items)

@pedido_items_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    pedidos = Pedido.query.all()
    inventario_items = InventarioItem.query.all()
    if request.method == 'POST':
        pedido_id = request.form['pedido_id']
        inventario_item_id = request.form['inventario_item_id']
        cantidad = request.form['cantidad']
        pedido_item = PedidoItem(
            pedido_id=pedido_id,
            inventario_item_id=inventario_item_id,
            cantidad=cantidad
        )
        db.session.add(pedido_item)
        db.session.commit()
        flash('Ítem de pedido creado correctamente.')
        return redirect(url_for('pedido_items.listar'))
    return render_template('pedido_items/nuevo.html', pedidos=pedidos, inventario_items=inventario_items)

@pedido_items_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    pedido_item = PedidoItem.query.get_or_404(id)
    pedidos = Pedido.query.all()
    inventario_items = InventarioItem.query.all()
    if request.method == 'POST':
        pedido_item.pedido_id = request.form['pedido_id']
        pedido_item.inventario_item_id = request.form['inventario_item_id']
        pedido_item.cantidad = request.form['cantidad']
        db.session.commit()
        flash('Ítem de pedido actualizado correctamente.')
        return redirect(url_for('pedido_items.listar'))
    return render_template('pedido_items/editar.html', pedido_item=pedido_item, pedidos=pedidos, inventario_items=inventario_items)

@pedido_items_bp.route('/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar(id):
    pedido_item = PedidoItem.query.get_or_404(id)
    db.session.delete(pedido_item)
    db.session.commit()
    flash('Ítem de pedido eliminado correctamente.')
    return redirect(url_for('pedido_items.listar'))