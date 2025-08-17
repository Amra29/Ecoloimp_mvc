from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, PasswordField
from wtforms.validators import DataRequired, Email, Length, Optional


class UsuarioForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    telefono = StringField('Teléfono', validators=[Optional(), Length(max=20)])
    rol = SelectField(
        'Rol',
        choices=[
            ('tecnico', 'Técnico'),
            ('admin', 'Administrador'),
            ('superadmin', 'Super Administrador')
        ],
        validators=[DataRequired()]
    )
    password = PasswordField('Contraseña', validators=[Optional(), Length(min=6, max=64)])
