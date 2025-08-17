from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.extensions import db
from app.models.models import Servicio
from app.forms import ServicioForm
from app.decorators import admin_required

servicios_bp = Blueprint('servicios', __name__)


@servicios_bp.route('/')
@login_required
def list():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    categoria = request.args.get('categoria', '')

    query = Servicio.query

    if search:
        query = query.filter(Servicio.nombre.contains(search))

    if categoria:
        query = query.filter_by(categoria=categoria)

    servicios = query.order_by(Servicio.nombre).paginate(
        page=page, per_page=10, error_out=False)

    # Obtener categorías para el filtro
    categorias = db.session.query(Servicio.categoria).distinct().filter(
        Servicio.categoria.isnot(None)).all()
    categorias = [cat[0] for cat in categorias if cat[0]]

    return render_template('servicios/list.html',
                           servicios=servicios,
                           search=search,
                           categoria_actual=categoria,
                           categorias=categorias)


@servicios_bp.route('/nuevo', methods=['GET', 'POST'])
@admin_required
def create():
    form = ServicioForm()
    if form.validate_on_submit():
        servicio = Servicio(
            nombre=form.nombre.data,
            descripcion=form.descripcion.data,
            precio_base=form.precio_base.data,
            categoria=form.categoria.data
        )
        db.session.add(servicio)
        db.session.commit()
        flash('Servicio creado exitosamente.', 'success')
        return redirect(url_for('servicios.list'))
    return render_template('servicios/form.html', form=form, title='Nuevo Servicio')


@servicios_bp.route('/<int:id>')
@login_required
def detail(id):
    servicio = Servicio.query.get_or_404(id)
    return render_template('servicios/detail.html', servicio=servicio)


@servicios_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit(id):
    servicio = Servicio.query.get_or_404(id)
    form = ServicioForm(obj=servicio)
    if form.validate_on_submit():
        servicio.nombre = form.nombre.data
        servicio.descripcion = form.descripcion.data
        servicio.precio_base = form.precio_base.data
        servicio.categoria = form.categoria.data
        db.session.commit()
        flash('Servicio actualizado exitosamente.', 'success')
        return redirect(url_for('servicios.detail', id=servicio.id))
    return render_template('servicios/form.html', form=form, title='Editar Servicio', servicio=servicio)


@servicios_bp.route('/eliminar/<int:id>', methods=['POST'])
@admin_required
def delete(id):
    servicio = Servicio.query.get_or_404(id)
    try:
        db.session.delete(servicio)
        db.session.commit()
        flash('Servicio eliminado exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('No se pudo eliminar el servicio. Asegúrese de que no esté siendo utilizado.', 'error')
    return redirect(url_for('servicios.list'))
