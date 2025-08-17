from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, Length

class LoginForm(FlaskForm):
    """Formulario para el inicio de sesión de usuarios."""
    email = StringField('Correo Electrónico', validators=[
        DataRequired(message='El correo electrónico es obligatorio'),
        Email(message='Ingrese un correo electrónico válido')
    ])
    
    password = PasswordField('Contraseña', validators=[
        DataRequired(message='La contraseña es obligatoria'),
        Length(min=6, message='La contraseña debe tener al menos 6 caracteres')
    ])
    
    remember_me = BooleanField('Recordar sesión')
