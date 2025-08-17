from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Optional, ValidationError
from app.models.models import Cliente

class ClienteForm(FlaskForm):
    """Formulario para crear y editar clientes."""
    nombre = StringField('Nombre', validators=[
        DataRequired(message='El nombre es obligatorio'),
        Length(max=100, message='El nombre no puede tener más de 100 caracteres')
    ])
    
    apellido = StringField('Apellido', validators=[
        DataRequired(message='El apellido es obligatorio'),
        Length(max=100, message='El apellido no puede tener más de 100 caracteres')
    ])
    
    email = StringField('Correo Electrónico', validators=[
        DataRequired(message='El correo electrónico es obligatorio'),
        Email(message='Ingrese un correo electrónico válido'),
        Length(max=120, message='El correo electrónico no puede tener más de 120 caracteres')
    ])
    
    telefono = StringField('Teléfono', validators=[
        DataRequired(message='El teléfono es obligatorio'),
        Length(max=20, message='El teléfono no puede tener más de 20 caracteres')
    ])
    
    direccion = TextAreaField('Dirección', validators=[
        Optional(),
        Length(max=255, message='La dirección no puede tener más de 255 caracteres')
    ])
    
    ruc = StringField('RUC', validators=[
        Optional(),
        Length(max=20, message='El RUC no puede tener más de 20 caracteres')
    ])
    
    activo = BooleanField('Cliente Activo', default=True)
    
    def validate_email(self, field):
        """Valida que el email no esté en uso por otro cliente."""
        cliente = Cliente.query.filter_by(email=field.data).first()
        if cliente and (not hasattr(self, 'obj') or cliente.id != self.obj.id):
            raise ValidationError('Este correo electrónico ya está en uso por otro cliente')


class BuscarClienteForm(FlaskForm):
    """Formulario para buscar clientes."""
    buscar = StringField('Buscar', validators=[
        Optional(),
        Length(max=100, message='La búsqueda no puede tener más de 100 caracteres')
    ])
    
    filtro = SelectField('Filtrar por', choices=[
        ('todos', 'Todos los clientes'),
        ('activos', 'Solo activos'),
        ('inactivos', 'Solo inactivos')
    ], default='activos')
    
    ordenar_por = SelectField('Ordenar por', choices=[
        ('nombre', 'Nombre (A-Z)'),
        ('-nombre', 'Nombre (Z-A)'),
        ('fecha_registro', 'Fecha de registro (más recientes)'),
        ('-fecha_registro', 'Fecha de registro (más antiguos)')
    ], default='nombre')
    
    submit = SubmitField('Buscar')
