from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, IntegerField, DateTimeField, SelectField
from wtforms.validators import DataRequired, Optional, NumberRange
from flask_wtf.file import FileField, FileAllowed, FileRequired
from werkzeug.utils import secure_filename
import os

# Configuración para manejar la subida de firmas
UPLOAD_FOLDER = os.path.join('app', 'static', 'uploads', 'signatures')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class ReporteForm(FlaskForm):
    trabajo_realizado = TextAreaField('Trabajo Realizado', validators=[DataRequired()])
    problemas_encontrados = TextAreaField('Problemas Encontrados', validators=[Optional()])
    solucion_aplicada = TextAreaField('Solución Aplicada', validators=[DataRequired()])
    recomendaciones = TextAreaField('Recomendaciones', validators=[Optional()])
    
    # Información del cliente
    cliente_satisfecho = BooleanField('Cliente Satisfecho', default=True)
    observaciones_cliente = TextAreaField('Observaciones del Cliente', validators=[Optional()])
    nombre_firma = StringField('Nombre para la Firma', validators=[DataRequired()])
    firma_archivo = FileField('Firma Digital', validators=[
        FileRequired(),
        FileAllowed(ALLOWED_EXTENSIONS, 'Solo se permiten imágenes (PNG, JPG, JPEG)!')
    ])
    
    # Información del servicio
    hora_inicio = DateTimeField('Hora de Inicio', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    hora_fin = DateTimeField('Hora de Finalización', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    
    # Firma digital (se manejará con JavaScript)
    firma_cliente = StringField('Firma del Cliente', validators=[DataRequired()])
    
    # Campos ocultos para el estado
    completado = BooleanField('Completado', default=True)
    aprobado_admin = BooleanField('Aprobado por Administración', default=False)
    
    # Campo para piezas utilizadas (se manejará dinámicamente con JavaScript)
    piezas_utilizadas = TextAreaField('Piezas Utilizadas', validators=[Optional()], render_kw={"rows": 3})


class AprobarReporteForm(FlaskForm):
    aprobado = BooleanField('Aprobar Reporte', default=False)
    observaciones = TextAreaField('Observaciones', validators=[Optional()])
    nombre_firma_admin = StringField('Nombre para la Firma', validators=[DataRequired()])
    firma_admin_archivo = FileField('Firma del Administrador', validators=[
        FileRequired(),
        FileAllowed(ALLOWED_EXTENSIONS, 'Solo se permiten imágenes (PNG, JPG, JPEG)!')
    ])
