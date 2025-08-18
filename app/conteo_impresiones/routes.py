from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import Conteo, Equipo, Cliente, Usuario
from datetime import datetime

bp = Blueprint('conteo_impresiones', __name__, url_prefix='/conteo_impresiones')

@bp.route('/', methods=['GET'])
def index():
    """
    Página principal del módulo de conteo de impresiones.
    Muestra un listado de los últimos conteos realizados, con filtros por fecha y cliente.
    """
    page = request.args.get('page', 1, type=int)
    cliente_id = request.args.get('cliente_id', type=int)
    fecha_desde = request.args.get('fecha_desde')
    fecha_hasta = request.args.get('fecha_hasta')

    # Construir consulta base
    query = Conteo.query.join(Equipo).options(
        db.joinedload(Conteo.equipo),
        db.joinedload(Conteo.tecnico)
    )

    # Filtro por cliente
    if cliente_id:
        query = query.filter(Equipo.cliente_id == cliente_id)

    # Filtro por fecha desde
    if fecha_desde:
        try:
            fecha_desde_dt = datetime.strptime(fecha_desde, '%Y-%m-%d')
            query = query.filter(Conteo.fecha_conteo >= fecha_desde_dt)
        except ValueError:
            flash("Fecha desde inválida.", "danger")

    # Filtro por fecha hasta
    if fecha_hasta:
        try:
            fecha_hasta_dt = datetime.strptime(fecha_hasta, '%Y-%m-%d')
            query = query.filter(Conteo.fecha_conteo <= fecha_hasta_dt)
        except ValueError:
            flash("Fecha hasta inválida.", "danger")

    conteos = query.order_by(Conteo.fecha_conteo.desc()).paginate(page=page, per_page=25)

    # Totales y promedios
    total_impresiones = sum(c.impresiones_desde_ultimo for c in conteos.items)
    total_escaneos = sum(c.escaneos_desde_ultimo for c in conteos.items)
    total_copias = sum(c.copias_desde_ultimo for c in conteos.items)
    promedio_diario = None
    if conteos.total > 0:
        dias = (conteos.items[0].fecha_conteo - conteos.items[-1].fecha_conteo).days or 1
        promedio_diario = {
            "impresiones": total_impresiones / dias,
            "escaneos": total_escaneos / dias,
            "copias": total_copias / dias
        }

    clientes = Cliente.query.order_by(Cliente.nombre).all()

    return render_template(
        "conteo_impresiones/historial.html",
        conteos=conteos.items,
        total_impresiones=total_impresiones,
        total_escaneos=total_escaneos,
        total_copias=total_copias,
        promedio_diario=promedio_diario,
        clientes=clientes
    )