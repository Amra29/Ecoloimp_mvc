from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, TextAreaField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Optional, ValidationError
from app.models.models import Usuario, Tecnico

class TecnicoForm(FlaskForm):
    """Formulario para crear y editar técnicos."""
    nombre = StringField('Nombres', validators=[
        DataRequired(message='El nombre es obligatorio'),
        Length(min=2, max=50, message='El nombre debe tener entre 2 y 50 caracteres')
    ])
    
    apellido = StringField('Apellidos', validators=[
        DataRequired(message='El apellido es obligatorio'),
        Length(min=2, max=50, message='El apellido debe tener entre 2 y 50 caracteres')
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
    
    especialidad = SelectField('Especialidad', choices=[
        ('general', 'Técnico General'),
        ('impresoras', 'Impresoras'),
        ('computadoras', 'Computadoras'),
        ('redes', 'Redes'),
        ('software', 'Software'),
        ('electronica', 'Electrónica'),
        ('otro', 'Otra Especialidad')
    ], validators=[DataRequired(message='La especialidad es obligatoria')])
    
    nivel = SelectField('Nivel', choices=[
        ('junior', 'Técnico Junior'),
        ('semi_senior', 'Técnico Semi-Senior'),
        ('senior', 'Técnico Senior'),
        ('especialista', 'Especialista')
    ], default='junior')
    
    activo = BooleanField('Técnico Activo', default=True)
    
    # Campos de autenticación (solo para creación)
    username = StringField('Nombre de Usuario', validators=[
        Optional(),
        Length(min=4, max=50, message='El nombre de usuario debe tener entre 4 y 50 caracteres')
    ])
    
    password = PasswordField('Contraseña', validators=[
        Optional(),
        Length(min=8, message='La contraseña debe tener al menos 8 caracteres')
    ])
    
    confirm_password = PasswordField('Confirmar Contraseña', validators=[
        EqualTo('password', message='Las contraseñas no coinciden')
    ])
    
    # Campos ocultos para seguimiento
    es_nuevo = HiddenField(default='true')
    
    submit = SubmitField('Guardar Técnico')
    
    def __init__(self, *args, **kwargs):
        super(TecnicoForm, self).__init__(*args, **kwargs)
        # Si estamos editando un técnico existente, marcar como no nuevo
        if 'obj' in kwargs and kwargs['obj']:
            self.es_nuevo.data = 'false'
    
    def validate_email(self, field):
        """Validar que el email no esté en uso por otro usuario."""
        if self.es_nuevo.data == 'true' or (hasattr(self, 'obj') and self.obj and self.obj.email != field.data):
            if Usuario.query.filter_by(email=field.data).first():
                raise ValidationError('Este correo electrónico ya está en uso por otro usuario')
    
    def validate_username(self, field):
        """Validar que el nombre de usuario no esté en uso."""
        if field.data and (self.es_nuevo.data == 'true' or 
                          (hasattr(self, 'obj') and self.obj and self.obj.username != field.data)):
            if Usuario.query.filter_by(username=field.data).first():
                raise ValidationError('Este nombre de usuario ya está en uso')


class BuscarTecnicoForm(FlaskForm):
    """Formulario para buscar técnicos."""
    buscar = StringField('Buscar', validators=[
        Optional(),
        Length(max=100, message='La búsqueda no puede tener más de 100 caracteres')
    ])
    
    estado = SelectField('Estado', choices=[
        ('todos', 'Todos'),
        ('activos', 'Solo activos'),
        ('inactivos', 'Solo inactivos'
    )], default='activos')
    
    especialidad = SelectField('Especialidad', choices=[
        ('', 'Todas las especialidades'),
        ('general', 'General'),
        ('impresoras', 'Impresoras'),
        ('computadoras', 'Computadoras'),
        ('redes', 'Redes'),
        ('software', 'Software'),
        ('electronica', 'Electrónica'),
        ('otro', 'Otra Especialidad')
    ], default='')
    
    nivel = SelectField('Nivel', choices=[
        ('', 'Todos los niveles'),
        ('junior', 'Junior'),
        ('semi_senior', 'Semi-Senior'),
        ('senior', 'Senior'),
        ('especialista', 'Especialista')
    ], default='')
    
    ordenar_por = SelectField('Ordenar por', choices=[
        ('nombre', 'Nombre (A-Z)'),
        ('-nombre', 'Nombre (Z-A)'),
        ('fecha_registro', 'Fecha de registro (más recientes)'),
        ('-fecha_registro', 'Fecha de registro (más antiguos)')
    ], default='nombre')
    
    submit = SubmitField('Buscar')
