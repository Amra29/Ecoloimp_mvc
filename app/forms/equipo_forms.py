from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Length, Optional, NumberRange
from app.models.models import Equipo, Cliente

class EquipoForm(FlaskForm):
    """Formulario para crear y editar equipos."""
    cliente_id = SelectField('Cliente', coerce=int, validators=[
        DataRequired(message='Seleccione un cliente')
    ])
    
    tipo = StringField('Tipo de Equipo', validators=[
        DataRequired(message='El tipo de equipo es obligatorio'),
        Length(max=50, message='El tipo no puede tener más de 50 caracteres')
    ])
    
    marca = StringField('Marca', validators=[
        DataRequired(message='La marca es obligatoria'),
        Length(max=50, message='La marca no puede tener más de 50 caracteres')
    ])
    
    modelo = StringField('Modelo', validators=[
        DataRequired(message='El modelo es obligatorio'),
        Length(max=50, message='El modelo no puede tener más de 50 caracteres')
    ])
    
    numero_serie = StringField('Número de Serie', validators=[
        Optional(),
        Length(max=50, message='El número de serie no puede tener más de 50 caracteres')
    ])
    
    contador_actual = IntegerField('Contador Actual', validators=[
        Optional(),
        NumberRange(min=0, message='El contador no puede ser negativo')
    ])
    
    ubicacion = StringField('Ubicación', validators=[
        Optional(),
        Length(max=100, message='La ubicación no puede tener más de 100 caracteres')
    ])
    
    notas = TextAreaField('Notas', validators=[
        Optional(),
        Length(max=500, message='Las notas no pueden tener más de 500 caracteres')
    ])
    
    activo = BooleanField('Equipo Activo', default=True)
    
    def __init__(self, *args, **kwargs):
        super(EquipoForm, self).__init__(*args, **kwargs)
        # Cargar la lista de clientes activos
        self.cliente_id.choices = [(c.id, f"{c.nombre} {c.apellido}") 
                                 for c in Cliente.query.filter_by(activo=True).order_by(Cliente.nombre).all()]


class BuscarEquipoForm(FlaskForm):
    """Formulario para buscar equipos."""
    buscar = StringField('Buscar', validators=[
        Optional(),
        Length(max=100, message='La búsqueda no puede tener más de 100 caracteres')
    ])
    
    tipo = SelectField('Tipo de Equipo', choices=[
        ('', 'Todos los tipos'),
        ('impresora', 'Impresora'),
        ('escaner', 'Escáner'),
        ('fotocopiadora', 'Fotocopiadora'),
        ('multifuncional', 'Multifuncional'),
        ('otro', 'Otro')
    ], default='')
    
    estado = SelectField('Estado', choices=[
        ('todos', 'Todos'),
        ('activos', 'Solo activos'),
        ('inactivos', 'Solo inactivos'
    )], default='activos')
    
    ordenar_por = SelectField('Ordenar por', choices=[
        ('marca', 'Marca (A-Z)'),
        ('-marca', 'Marca (Z-A)'),
        ('modelo', 'Modelo (A-Z)'),
        ('-modelo', 'Modelo (Z-A)'),
        ('cliente', 'Cliente (A-Z)'),
        ('-cliente', 'Cliente (Z-A)')
    ], default='marca')
    
    submit = SubmitField('Buscar')
