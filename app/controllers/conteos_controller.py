from flask import Blueprint, request, render_template, redirect, url_for, flash
from app.models.models import db, Conteo, Equipo, Usuario
from flask_login import login_required, current_user

conteos_bp = Blueprint('conteos', __name__, url_prefix='/conteos')

@conteos_bp.route('/')
@login_required
def listar():
    conteos = Conteo.query.order_by(Conteo.fecha_conteo.desc()).limit(100).all()
    return render_template('conteos/listar.html', conteos=conteos)

@conteos_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    equipos = Equipo.query.all()
    if request.method == 'POST':
        equipo_id = request.form['equipo_id']
        impresiones = request.form['impresiones']
        escaneos = request.form['escaneos']
        copias = request.form['copias']
        observaciones = request.form['observaciones']
        conteo = Conteo(
            equipo_id=equipo_id,
            tecnico_id=current_user.id,
            impresiones=impresiones,
            escaneos=escaneos,
            copias=copias,
            observaciones=observaciones
        )
        db.session.add(conteo)
        db.session.commit()
        flash('Conteo registrado correctamente.')
        return redirect(url_for('conteos.listar'))
    return render_template('conteos/nuevo.html', equipos=equipos)