"""
Formularios para la gestión de permisos y roles.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, HiddenField, BooleanField, SubmitField, SelectMultipleField
from wtforms.validators import DataRequired, Length, Optional

class BuscarPermisoForm(FlaskForm):
    """Formulario para buscar permisos"""
    buscar = StringField('Buscar', validators=[Optional(), Length(max=100)])
    submit = SubmitField('Buscar')

class AsignarPermisoForm(FlaskForm):
    """Formulario para asignar/remover permisos a roles"""
    permiso_id = HiddenField('ID Permiso', validators=[DataRequired()])
    rol = SelectField('Rol', validators=[DataRequired()])
    accion = HiddenField('Acción', validators=[DataRequired()])
    submit = SubmitField('Guardar')
    
    def __init__(self, *args, **kwargs):
        super(AsignarPermisoForm, self).__init__(*args, **kwargs)
        # Los roles se cargarán dinámicamente desde la base de datos
        self.rol.choices = []

class FiltroPermisosForm(FlaskForm):
    """Formulario para filtrar permisos"""
    rol = SelectField('Rol', validators=[Optional()])
    activo = SelectField('Estado', choices=[
        ('', 'Todos'),
        ('1', 'Activos'),
        ('0', 'Inactivos')
    ], validators=[Optional()])
    submit = SubmitField('Filtrar')

class PermisoForm(FlaskForm):
    """Formulario para crear/editar permisos"""
    nombre = StringField('Nombre', validators=[
        DataRequired(),
        Length(max=50, message='El nombre no puede tener más de 50 caracteres')
    ])
    descripcion = StringField('Descripción', validators=[
        DataRequired(),
        Length(max=200, message='La descripción no puede tener más de 200 caracteres')
    ])
    activo = BooleanField('Activo', default=True)
    submit = SubmitField('Guardar')

class RolForm(FlaskForm):
    """Formulario para crear/editar roles"""
    nombre = StringField('Nombre del Rol', validators=[
        DataRequired(),
        Length(max=30, message='El nombre del rol no puede tener más de 30 caracteres')
    ])
    descripcion = StringField('Descripción', validators=[
        Length(max=200, message='La descripción no puede tener más de 200 caracteres')
    ])
    permisos = SelectMultipleField('Permisos', coerce=int)
    submit = SubmitField('Guardar')
    
    def __init__(self, *args, **kwargs):
        super(RolForm, self).__init__(*args, **kwargs)
        # Los permisos se cargarán dinámicamente desde la base de datos
        self.permisos.choices = []
