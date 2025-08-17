from flask_wtf import FlaskForm
from wtforms import (
    SelectField, TextAreaField, DateField, SubmitField, HiddenField,
    StringField, BooleanField
)
from wtforms.validators import DataRequired, Optional, Length, ValidationError
from datetime import datetime, timedelta

class AsignacionForm(FlaskForm):
    """Formulario para crear y editar asignaciones de trabajo."""
    tecnico_id = SelectField('Técnico', coerce=int, validators=[
        DataRequired(message='Seleccione un técnico')
    ])
    
    solicitud_id = SelectField('Solicitud', coerce=int, validators=[
        DataRequired(message='Seleccione una solicitud')
    ])
    
    fecha_asignacion = DateField('Fecha de Asignación', format='%Y-%m-%d',
                               default=datetime.utcnow,
                               validators=[DataRequired(message='La fecha de asignación es obligatoria')])
    
    fecha_limite = DateField('Fecha Límite', format='%Y-%m-%d',
                           default=(datetime.utcnow() + timedelta(days=7)).date(),
                           validators=[DataRequired(message='La fecha límite es obligatoria')])
    
    prioridad = SelectField('Prioridad', choices=[
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente')
    ], default='media', validators=[DataRequired(message='La prioridad es obligatoria')])
    
    estado = SelectField('Estado', choices=[
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada')
    ], default='pendiente', validators=[DataRequired(message='El estado es obligatorio')])
    
    notas = TextAreaField('Notas', validators=[
        Optional(),
        Length(max=1000, message='Las notas no pueden tener más de 1000 caracteres')
    ])
    
    submit = SubmitField('Guardar Asignación')
    
    def __init__(self, *args, **kwargs):
        super(AsignacionForm, self).__init__(*args, **kwargs)
        # Inicializar las opciones de técnico y solicitud
        self._populate_choices()
    
    def _populate_choices(self):
        """Poblar las opciones de técnico y solicitud desde la base de datos."""
        from app.models.models import Usuario, SolicitudServicio
        
        # Obtener técnicos activos
        tecnicos = Usuario.query.filter_by(activo=True, rol='tecnico')\
                              .order_by(Usuario.nombre, Usuario.apellido).all()
        self.tecnico_id.choices = [(t.id, f"{t.nombre} {t.apellido}") for t in tecnicos]
        
        # Obtener solicitudes pendientes o asignadas
        solicitudes = SolicitudServicio.query.filter(
            (SolicitudServicio.estado == 'pendiente') | 
            (SolicitudServicio.estado == 'asignada')
        ).order_by(SolicitudServicio.fecha_solicitud.desc()).all()
        
        self.solicitud_id.choices = [
            (s.id, f"#{s.id} - {s.cliente.nombre} - {s.equipo.marca} {s.equipo.modelo}")
            for s in solicitudes
        ]
        
        if not self.solicitud_id.choices:
            self.solicitud_id.choices = [('', 'No hay solicitudes disponibles')]
    
    def validate_fecha_limite(self, field):
        """Validar que la fecha límite no sea anterior a la fecha de asignación."""
        if field.data and field.data < self.fecha_asignacion.data:
                    raise ValidationError('La fecha límite no puede ser anterior a la fecha de asignación')


class BuscarAsignacionForm(FlaskForm):
    """Formulario para buscar y filtrar asignaciones."""
    from wtforms import StringField, BooleanField, SubmitField
    buscar = StringField('Buscar', validators=[
        Optional(),
        Length(max=100, message='La búsqueda no puede tener más de 100 caracteres')
    ])
    
    estado = SelectField('Estado', choices=[
        ('todos', 'Todas'),
        ('pendiente', 'Pendientes'),
        ('en_proceso', 'En Proceso'),
        ('completada', 'Completadas'),
        ('cancelada', 'Canceladas')
    ], default='pendiente')
    
    prioridad = SelectField('Prioridad', choices=[
        ('', 'Todas'),
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente')
    ], default='')
    
    tecnico_id = SelectField('Técnico', coerce=int, default=0)
    
    fecha_desde = DateField('Desde', format='%Y-%m-%d', validators=[Optional()])
    fecha_hasta = DateField('Hasta', format='%Y-%m-%d', validators=[Optional()])
    
    submit = SubmitField('Buscar')
    
    def __init__(self, *args, **kwargs):
        super(BuscarAsignacionForm, self).__init__(*args, **kwargs)
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


class CompletarAsignacionForm(FlaskForm):
    """Formulario para marcar una asignación como completada."""
    trabajo_realizado = TextAreaField('Trabajo Realizado', validators=[
        DataRequired(message='Por favor describa el trabajo realizado'),
        Length(min=10, message='La descripción debe tener al menos 10 caracteres')
    ])
    
    observaciones = TextAreaField('Observaciones', validators=[
        Optional(),
        Length(max=1000, message='Las observaciones no pueden tener más de 1000 caracteres')
    ])
    
    requiere_aprobacion = BooleanField('Requiere Aprobación', default=False)
    
    submit = SubmitField('Marcar como Completada')
