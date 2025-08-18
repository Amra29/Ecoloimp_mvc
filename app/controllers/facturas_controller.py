from flask import Blueprint, request, render_template, redirect, url_for, flash
from app.models.models import db, Factura, Cliente
from flask_login import login_required

facturas_bp = Blueprint('facturas', __name__, url_prefix='/facturas')

@facturas_bp.route('/')
@login_required
def listar():
    facturas = Factura.query.order_by(Factura.fecha_emision.desc()).all()
    return render_template('facturas/listar.html', facturas=facturas)

@facturas_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    clientes = Cliente.query.all()
    if request.method == 'POST':
        cliente_id = request.form['cliente_id']
        monto_subtotal = request.form['monto_subtotal']
        monto_impuestos = request.form['monto_impuestos']
        monto_total = request.form['monto_total']
        factura = Factura(
            cliente_id=cliente_id,
            monto_subtotal=monto_subtotal,
            monto_impuestos=monto_impuestos,
            monto_total=monto_total
        )
        db.session.add(factura)
        db.session.commit()
        flash('Factura creada correctamente.')
        return redirect(url_for('facturas.listar'))
    return render_template('facturas/nuevo.html', clientes=clientes)