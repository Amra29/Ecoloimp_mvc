from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, HiddenField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Optional, Length, Email
from datetime import datetime, timedelta

class SolicitudForm(FlaskForm):
    """Formulario para crear y editar solicitudes de servicio."""
    cliente_id = SelectField('Cliente', coerce=int, validators=[
        DataRequired(message='Seleccione un cliente')
    ])
    
    equipo_id = SelectField('Equipo', coerce=int, validators=[
        DataRequired(message='Seleccione un equipo')
    ])
    
    tipo_servicio = SelectField('Tipo de Servicio', choices=[
        ('preventivo', 'Mantenimiento Preventivo'),
        ('correctivo', 'Mantenimiento Correctivo'),
        ('instalacion', 'Instalación'),
        ('capacitacion', 'Capacitación'),
        ('otro', 'Otro')
    ], validators=[DataRequired(message='Seleccione el tipo de servicio')])
    
    descripcion = TextAreaField('Descripción del Problema/Solicitud', validators=[
        DataRequired(message='La descripción es obligatoria'),
        Length(min=10, max=1000, message='La descripción debe tener entre 10 y 1000 caracteres')
    ])
    
    prioridad = SelectField('Prioridad', choices=[
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('critica', 'Crítica')
    ], default='media', validators=[DataRequired(message='Seleccione la prioridad')])
    
    fecha_solicitud = DateField('Fecha de Solicitud', format='%Y-%m-%d', 
                              default=datetime.utcnow,
                              validators=[DataRequired(message='La fecha de solicitud es obligatoria')])
    
    fecha_requerida = DateField('Fecha Requerida', format='%Y-%m-%d',
                              default=(datetime.utcnow() + timedelta(days=7)).date(),
                              validators=[DataRequired(message='La fecha requerida es obligatoria')])
    
    contacto_nombre = StringField('Persona de Contacto', validators=[
        DataRequired(message='El nombre de contacto es obligatorio'),
        Length(max=100, message='El nombre no puede tener más de 100 caracteres')
    ])
    
    contacto_telefono = StringField('Teléfono de Contacto', validators=[
        DataRequired(message='El teléfono de contacto es obligatorio'),
        Length(max=20, message='El teléfono no puede tener más de 20 caracteres')
    ])
    
    contacto_email = StringField('Email de Contacto', validators=[
        Optional(),
        Email(message='Ingrese un correo electrónico válido'),
        Length(max=120, message='El correo electrónico no puede tener más de 120 caracteres')
    ])
    
    direccion_servicio = TextAreaField('Dirección del Servicio', validators=[
        Optional(),
        Length(max=500, message='La dirección no puede tener más de 500 caracteres')
    ])
    
    notas_adicionales = TextAreaField('Notas Adicionales', validators=[
        Optional(),
        Length(max=1000, message='Las notas no pueden tener más de 1000 caracteres')
    ])
    
    submit = SubmitField('Guardar Solicitud')
    
    def __init__(self, *args, **kwargs):
        super(SolicitudForm, self).__init__(*args, **kwargs)
        # Inicializar las opciones de cliente y equipo
        self._populate_choices()
    
    def _populate_choices(self):
        """Poblar las opciones de cliente y equipo desde la base de datos."""
        from app.models.models import Cliente, Equipo
        
        # Obtener clientes activos
        self.cliente_id.choices = [(c.id, f"{c.nombre} {c.apellido}") 
                                 for c in Cliente.query.filter_by(activo=True).order_by(Cliente.nombre).all()]
        
        # Si hay un cliente seleccionado, cargar sus equipos
        if self.cliente_id.data:
            self._load_equipos(self.cliente_id.data)
        else:
            self.equipo_id.choices = [('', 'Seleccione un cliente primero')]
    
    def _load_equipos(self, cliente_id):
        """Cargar los equipos de un cliente específico."""
        from app.models.models import Equipo
        
        self.equipo_id.choices = [(e.id, f"{e.marca} {e.modelo} - {e.numero_serie or 'Sin serie'}")
                                 for e in Equipo.query.filter_by(cliente_id=cliente_id, activo=True)
                                 .order_by(Equipo.marca, Equipo.modelo).all()]
        
        if not self.equipo_id.choices:
            self.equipo_id.choices = [('', 'Este cliente no tiene equipos registrados')]
            
    def validate_fecha_requerida(self, field):
        """Validar que la fecha requerida no sea anterior a la fecha de solicitud."""
        if field.data and field.data < self.fecha_solicitud.data:
            from wtforms.validators import ValidationError
            raise ValidationError('La fecha requerida no puede ser anterior a la fecha de solicitud')


class BuscarSolicitudForm(FlaskForm):
    """Formulario para buscar y filtrar solicitudes."""
    buscar = StringField('Buscar', validators=[
        Optional(),
        Length(max=100, message='La búsqueda no puede tener más de 100 caracteres')
    ])
    
    estado = SelectField('Estado', choices=[
        ('todos', 'Todos los estados'),
        ('pendiente', 'Pendientes'),
        ('asignada', 'Asignadas'),
        ('en_proceso', 'En Proceso'),
        ('completada', 'Completadas'),
        ('cancelada', 'Canceladas')
    ], default='pendiente')
    
    tipo_servicio = SelectField('Tipo de Servicio', choices=[
        ('', 'Todos los tipos'),
        ('preventivo', 'Mantenimiento Preventivo'),
        ('correctivo', 'Mantenimiento Correctivo'),
        ('instalacion', 'Instalación'),
        ('capacitacion', 'Capacitación'),
        ('otro', 'Otro')
    ], default='')
    
    prioridad = SelectField('Prioridad', choices=[
        ('', 'Todas'),
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('critica', 'Crítica')
    ], default='')
    
    fecha_desde = DateField('Desde', format='%Y-%m-%d', validators=[Optional()])
    fecha_hasta = DateField('Hasta', format='%Y-%m-%d', validators=[Optional()])
    
    submit = SubmitField('Buscar')
    
    def validate_fecha_hasta(self, field):
        """Validar que la fecha hasta no sea anterior a la fecha desde."""
        if field.data and self.fecha_desde.data and field.data < self.fecha_desde.data:
            from wtforms.validators import ValidationError
            raise ValidationError('La fecha "hasta" no puede ser anterior a la fecha "desde"')
