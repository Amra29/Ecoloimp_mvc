from flask import Blueprint

bp = Blueprint('conteo_impresiones', __name__)

from app.conteo_impresiones import routes
