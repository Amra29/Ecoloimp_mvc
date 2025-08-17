from flask_wtf import FlaskForm
from wtforms import (
    StringField, TextAreaField, SelectField, DecimalField, 
    DateField, BooleanField, SubmitField, HiddenField
)
from wtforms.validators import DataRequired, Optional, Length, NumberRange, ValidationError
from datetime import datetime

class ServicioForm(FlaskForm):
    """Formulario para crear y editar servicios."""
    nombre = StringField('Nombre del Servicio', validators=[
        DataRequired(message='El nombre del servicio es obligatorio'),
        Length(min=3, max=100, message='El nombre debe tener entre 3 y 100 caracteres')
    ])
    
    descripcion = TextAreaField('Descripción', validators=[
        DataRequired(message='La descripción es obligatoria'),
        Length(min=10, message='La descripción debe tener al menos 10 caracteres')
    ])
    
    tipo_servicio = SelectField('Tipo de Servicio', choices=[
        ('preventivo', 'Mantenimiento Preventivo'),
        ('correctivo', 'Mantenimiento Correctivo'),
        ('instalacion', 'Instalación'),
        ('capacitacion', 'Capacitación'),
        ('reparacion', 'Reparación'),
        ('otro', 'Otro')
    ], validators=[DataRequired(message='Seleccione el tipo de servicio')])
    
    categoria = SelectField('Categoría', choices=[
        ('hardware', 'Hardware'),
        ('software', 'Software'),
        ('redes', 'Redes'),
        ('seguridad', 'Seguridad'),
        ('otros', 'Otros')
    ], validators=[DataRequired(message='Seleccione una categoría')])
    
    precio_base = DecimalField('Precio Base', validators=[
        DataRequired(message='El precio base es obligatorio'),
        NumberRange(min=0, message='El precio no puede ser negativo')
    ])
    
    duracion_estimada = StringField('Duración Estimada', validators=[
        DataRequired(message='La duración estimada es obligatoria'),
        Length(max=50, message='La duración no puede tener más de 50 caracteres')
    ])
    
    garantia = StringField('Garantía', validators=[
        Optional(),
        Length(max=100, message='La garantía no puede tener más de 100 caracteres')
    ])
    
    activo = BooleanField('Servicio Activo', default=True)
    
    # Campos para seguimiento interno
    codigo = StringField('Código de Servicio', validators=[
        Optional(),
        Length(max=20, message='El código no puede tener más de 20 caracteres')
    ])
    
    notas_internas = TextAreaField('Notas Internas', validators=[
        Optional(),
        Length(max=500, message='Las notas no pueden tener más de 500 caracteres')
    ])
    
    submit = SubmitField('Guardar Servicio')
    
    def __init__(self, *args, **kwargs):
        super(ServicioForm, self).__init__(*args, **kwargs)
        # Si estamos creando un nuevo servicio, generar un código automático
        if not self.codigo.data and not hasattr(self, 'obj'):
            from datetime import datetime
            from random import randint
            prefix = 'SERV-'
            date_str = datetime.now().strftime('%Y%m%d')
            random_str = str(randint(1000, 9999))
            self.codigo.data = f"{prefix}{date_str}-{random_str}"


class BuscarServicioForm(FlaskForm):
    """Formulario para buscar y filtrar servicios."""
    buscar = StringField('Buscar', validators=[
        Optional(),
        Length(max=100, message='La búsqueda no puede tener más de 100 caracteres')
    ])
    
    tipo_servicio = SelectField('Tipo de Servicio', choices=[
        ('', 'Todos los tipos'),
        ('preventivo', 'Mantenimiento Preventivo'),
        ('correctivo', 'Mantenimiento Correctivo'),
        ('instalacion', 'Instalación'),
        ('capacitacion', 'Capacitación'),
        ('reparacion', 'Reparación'),
        ('otro', 'Otro')
    ], default='')
    
    categoria = SelectField('Categoría', choices=[
        ('', 'Todas las categorías'),
        ('hardware', 'Hardware'),
        ('software', 'Software'),
        ('redes', 'Redes'),
        ('seguridad', 'Seguridad'),
        ('otros', 'Otros')
    ], default='')
    
    estado = SelectField('Estado', choices=[
        ('todos', 'Todos'),
        ('activos', 'Solo activos'),
        ('inactivos', 'Solo inactivos'
    )], default='activos')
    
    ordenar_por = SelectField('Ordenar por', choices=[
        ('nombre', 'Nombre (A-Z)'),
        ('-nombre', 'Nombre (Z-A)'),
        ('precio', 'Precio (menor a mayor)'),
        ('-precio', 'Precio (mayor a menor)')
    ], default='nombre')
    
    submit = SubmitField('Buscar')


class ItemServicioForm(FlaskForm):
    """Formulario para agregar un ítem de servicio a una factura o cotización."""
    servicio_id = SelectField('Servicio', coerce=int, validators=[
        DataRequired(message='Seleccione un servicio')
    ])
    
    cantidad = DecimalField('Cantidad', default=1, validators=[
        DataRequired(message='La cantidad es obligatoria'),
        NumberRange(min=0.01, message='La cantidad debe ser mayor a cero')
    ])
    
    precio_unitario = DecimalField('Precio Unitario', validators=[
        DataRequired(message='El precio unitario es obligatorio'),
        NumberRange(min=0, message='El precio no puede ser negativo')
    ])
    
    descuento = DecimalField('Descuento %', default=0, validators=[
        Optional(),
        NumberRange(min=0, max=100, message='El descuento debe estar entre 0 y 100%')
    ])
    
    descripcion = TextAreaField('Descripción Adicional', validators=[
        Optional(),
        Length(max=500, message='La descripción no puede tener más de 500 caracteres')
    ])
    
    submit = SubmitField('Agregar Servicio')
    
    def __init__(self, *args, **kwargs):
        super(ItemServicioForm, self).__init__(*args, **kwargs)
        # Cargar servicios activos
        from app.models.models import Servicio
        servicios = Servicio.query.filter_by(activo=True).order_by(Servicio.nombre).all()
        self.servicio_id.choices = [(s.id, f"{s.nombre} - ${s.precio_base}") for s in servicios]
