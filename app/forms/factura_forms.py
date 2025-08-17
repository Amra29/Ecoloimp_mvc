from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DecimalField, DateField, HiddenField, SubmitField
from wtforms.validators import DataRequired, Optional, Length, NumberRange
from datetime import datetime

class FacturaForm(FlaskForm):
    """Formulario para crear y editar facturas."""
    cliente_id = SelectField('Cliente', coerce=int, validators=[
        DataRequired(message='Seleccione un cliente')
    ])
    
    numero_factura = StringField('Número de Factura', validators=[
        DataRequired(message='El número de factura es obligatorio'),
        Length(max=20, message='El número de factura no puede tener más de 20 caracteres')
    ])
    
    fecha_emision = DateField('Fecha de Emisión', format='%Y-%m-%d', default=datetime.utcnow,
                            validators=[DataRequired(message='La fecha de emisión es obligatoria')])
    
    fecha_vencimiento = DateField('Fecha de Vencimiento', format='%Y-%m-%d',
                                 validators=[DataRequired(message='La fecha de vencimiento es obligatoria')])
    
    concepto = TextAreaField('Concepto', validators=[
        DataRequired(message='El concepto es obligatorio'),
        Length(max=500, message='El concepto no puede tener más de 500 caracteres')
    ])
    
    subtotal = DecimalField('Subtotal', places=2, validators=[
        DataRequired(message='El subtotal es obligatorio'),
        NumberRange(min=0, message='El subtotal no puede ser negativo')
    ])
    
    impuestos = DecimalField('Impuestos', places=2, default=0.0, validators=[
        Optional(),
        NumberRange(min=0, message='Los impuestos no pueden ser negativos')
    ])
    
    descuento = DecimalField('Descuento', places=2, default=0.0, validators=[
        Optional(),
        NumberRange(min=0, message='El descuento no puede ser negativo')
    ])
    
    total = DecimalField('Total', places=2, validators=[
        DataRequired(message='El total es obligatorio'),
        NumberRange(min=0, message='El total no puede ser negativo')
    ])
    
    estado = SelectField('Estado', choices=[
        ('pendiente', 'Pendiente de pago'),
        ('pagada', 'Pagada'),
        ('vencida', 'Vencida'),
        ('anulada', 'Anulada')
    ], validators=[DataRequired(message='El estado es obligatorio')])
    
    notas = TextAreaField('Notas Adicionales', validators=[
        Optional(),
        Length(max=1000, message='Las notas no pueden tener más de 1000 caracteres')
    ])
    
    submit = SubmitField('Guardar Factura')


class LineaFacturaForm(FlaskForm):
    """Formulario para las líneas de factura."""
    descripcion = StringField('Descripción', validators=[
        DataRequired(message='La descripción es obligatoria'),
        Length(max=255, message='La descripción no puede tener más de 255 caracteres')
    ])
    
    cantidad = DecimalField('Cantidad', places=2, default=1.0, validators=[
        DataRequired(message='La cantidad es obligatoria'),
        NumberRange(min=0.01, message='La cantidad debe ser mayor a cero')
    ])
    
    precio_unitario = DecimalField('Precio Unitario', places=2, validators=[
        DataRequired(message='El precio unitario es obligatorio'),
        NumberRange(min=0, message='El precio no puede ser negativo')
    ])
    
    impuesto = DecimalField('Impuesto (%)', places=2, default=0.0, validators=[
        Optional(),
        NumberRange(min=0, max=100, message='El impuesto debe estar entre 0 y 100%')
    ])
    
    descuento = DecimalField('Descuento', places=2, default=0.0, validators=[
        Optional(),
        NumberRange(min=0, message='El descuento no puede ser negativo')
    ])
    
    total = DecimalField('Total', places=2, validators=[
        DataRequired(message='El total es obligatorio'),
        NumberRange(min=0, message='El total no puede ser negativo')
    ])
    
    # Campos ocultos para referencias
    factura_id = HiddenField()
    orden_servicio_id = HiddenField()
    
    def __init__(self, *args, **kwargs):
        super(LineaFacturaForm, self).__init__(*args, **kwargs)
        # Inicializar el total si no está definido
        if not self.total.data and self.precio_unitario.data and self.cantidad.data:
            self.total.data = self.precio_unitario.data * self.cantidad.data
            if self.descuento.data:
                self.total.data -= self.descuento.data
            if self.impuesto.data:
                self.total.data *= (1 + (self.impuesto.data / 100))
