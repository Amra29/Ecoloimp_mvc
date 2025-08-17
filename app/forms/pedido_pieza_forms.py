from flask_wtf import FlaskForm
from wtforms import (
    SelectField, IntegerField, TextAreaField, StringField, DateField,
    SelectMultipleField, SubmitField, HiddenField, BooleanField, DecimalField
)
from wtforms.validators import DataRequired, Optional, NumberRange, ValidationError, Length
from datetime import datetime

class PedidoPiezaForm(FlaskForm):
    """Formulario para crear y editar pedidos de piezas."""
    tecnico_id = SelectField('Técnico', coerce=int, validators=[
        DataRequired(message='Seleccione un técnico')
    ])
    
    fecha_solicitud = HiddenField('Fecha de Solicitud', default=datetime.utcnow)
    
    fecha_requerida = SelectField('Fecha Requerida', choices=[
        ('inmediato', 'Lo antes posible'),
        ('1_dia', 'En 1 día hábil'),
        ('2_dias', 'En 2 días hábiles'),
        ('3_dias', 'En 3 días hábiles'),
        ('especifica', 'Especificar fecha...')
    ], default='1_dia')
    
    fecha_especifica = HiddenField('Fecha Específica')
    
    prioridad = SelectField('Prioridad', choices=[
        ('normal', 'Normal'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente')
    ], default='normal')
    
    notas = TextAreaField('Notas', validators=[
        Optional(),
        Length(max=500, message='Las notas no pueden tener más de 500 caracteres')
    ])
    
    # Campos para los ítems del pedido
    pieza_id = SelectField('Pieza', coerce=int, validators=[
        DataRequired(message='Seleccione una pieza')
    ])
    
    cantidad = IntegerField('Cantidad', default=1, validators=[
        DataRequired(message='La cantidad es obligatoria'),
        NumberRange(min=1, message='La cantidad debe ser al menos 1')
    ])
    
    descripcion = TextAreaField('Descripción Adicional', validators=[
        Optional(),
        Length(max=200, message='La descripción no puede tener más de 200 caracteres')
    ])
    
    submit = SubmitField('Solicitar Piezas')
    
    def __init__(self, *args, **kwargs):
        super(PedidoPiezaForm, self).__init__(*args, **kwargs)
        self._cargar_opciones()
    
    def _cargar_opciones(self):
        """Cargar las opciones de técnicos y piezas desde la base de datos."""
        from app.models.models import Usuario, Pieza
        
        # Cargar técnicos activos
        tecnicos = Usuario.query.filter_by(activo=True, rol='tecnico')\
                              .order_by(Usuario.nombre, Usuario.apellido).all()
        self.tecnico_id.choices = [(t.id, f"{t.nombre} {t.apellido}") for t in tecnicos]
        
        # Cargar piezas activas
        piezas = Pieza.query.filter_by(activo=True)\
                          .order_by(Pieza.nombre).all()
        self.pieza_id.choices = [(p.id, f"{p.nombre} - Stock: {p.stock}") for p in piezas]


class AprobarPedidoPiezaForm(FlaskForm):
    """Formulario para aprobar o rechazar pedidos de piezas."""
    estado = SelectField('Acción', choices=[
        ('aprobado', 'Aprobar Pedido'),
        ('rechazado', 'Rechazar Pedido')
    ], validators=[DataRequired()])
    
    motivo_rechazo = TextAreaField('Motivo del Rechazo', validators=[
        Optional(),
        Length(max=500, message='El motivo no puede tener más de 500 caracteres')
    ])
    
    notas_aprobacion = TextAreaField('Notas de Aprobación', validators=[
        Optional(),
        Length(max=500, message='Las notas no pueden tener más de 500 caracteres')
    ])
    
    submit = SubmitField('Confirmar')
    
    def validate_motivo_rechazo(self, field):
        """Validar que se proporcione un motivo si se rechaza el pedido."""
        if self.estado.data == 'rechazado' and not field.data:
            raise ValidationError('Por favor proporcione un motivo para el rechazo')


class EntregarPiezaForm(FlaskForm):
    """Formulario para registrar la entrega de piezas a los técnicos."""
    cantidad_entregada = IntegerField('Cantidad Entregada', validators=[
        DataRequired(message='La cantidad entregada es obligatoria'),
        NumberRange(min=1, message='La cantidad debe ser al menos 1')
    ])
    
    fecha_entrega = HiddenField('Fecha de Entrega', default=datetime.utcnow)
    
    notas_entrega = TextAreaField('Notas de Entrega', validators=[
        Optional(),
        Length(max=500, message='Las notas no pueden tener más de 500 caracteres')
    ])
    
    submit = SubmitField('Registrar Entrega')


class BuscarPedidoPiezaForm(FlaskForm):
    """Formulario para buscar y filtrar pedidos de piezas."""
    buscar = StringField('Buscar', validators=[
        Optional(),
        Length(max=100, message='La búsqueda no puede tener más de 100 caracteres')
    ])
    
    estado = SelectField('Estado', choices=[
        ('todos', 'Todos los estados'),
        ('pendiente', 'Pendientes'),
        ('aprobado', 'Aprobados'),
        ('rechazado', 'Rechazados'),
        ('entregado', 'Entregados'),
        ('cancelado', 'Cancelados')
    ], default='pendiente')
    
    prioridad = SelectField('Prioridad', choices=[
        ('', 'Todas'),
        ('normal', 'Normal'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente')
    ], default='')
    
    tecnico_id = SelectField('Técnico', coerce=int, default=0)
    
    fecha_desde = DateField('Desde', format='%Y-%m-%d', validators=[Optional()])
    fecha_hasta = DateField('Hasta', format='%Y-%m-%d', validators=[Optional()])
    
    submit = SubmitField('Buscar')
    
    def __init__(self, *args, **kwargs):
        super(BuscarPedidoPiezaForm, self).__init__(*args, **kwargs)
        # Cargar la lista de técnicos para el filtro
        from app.models.models import Usuario
        tecnicos = Usuario.query.filter_by(activo=True, rol='tecnico')\
                              .order_by(Usuario.nombre, Usuario.apellido).all()
        self.tecnico_id.choices = [(0, 'Todos los técnicos')] + \
                                 [(t.id, f"{t.nombre} {t.apellido}") for t in tecnicos]
    
    def validate_fecha_hasta(self, field):
        """Validar que la fecha hasta no sea anterior a la fecha desde."""
        if field.data and self.fecha_desde.data and field.data < self.fecha_desde.data:
            raise ValidationError('La fecha "hasta" no puede ser anterior a la fecha "desde"')
