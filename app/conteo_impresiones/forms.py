from flask_wtf import FlaskForm
from wtforms import (
    StringField, IntegerField, TextAreaField, 
    SelectField, BooleanField, SubmitField, HiddenField,
    DecimalField, FloatField
)
from wtforms.validators import DataRequired, NumberRange, Optional, ValidationError
from wtforms.fields import DateField, TimeField
from datetime import datetime, date

class ConteoImpresionForm(FlaskForm):
    """
    Formulario para registrar un nuevo conteo de impresiones.
    
    Este formulario permite a los técnicos registrar los contadores de impresiones,
    escaneos y copias de los equipos, así como reportar problemas o necesidades de mantenimiento.
    """
    # Campos ocultos para cargar dinámicamente
    cliente_id = SelectField('Cliente', coerce=int, validators=[DataRequired()], 
                           render_kw={
                               'class': 'form-control select2',
                               'data-placeholder': 'Seleccione un cliente',
                               'onchange': 'cargarSucursales()'
                           })
    
    sucursal_id = SelectField('Sucursal', coerce=int, validators=[DataRequired()],
                            render_kw={
                                'class': 'form-control select2',
                                'data-placeholder': 'Seleccione una sucursal',
                                'onchange': 'cargarEquipos()'
                            })
    
    equipo_id = SelectField('Equipo', coerce=int, validators=[DataRequired()],
                          render_kw={
                              'class': 'form-control select2',
                              'data-placeholder': 'Seleccione un equipo',
                              'onchange': 'cargarUltimoConteo()'
                          })
    
    # Información del equipo (solo lectura)
    equipo_info = StringField('Información del equipo', 
                            render_kw={'class': 'form-control', 'readonly': True})
    
    # Contadores anteriores (solo lectura)
    contador_impresiones_anterior = IntegerField(
        'Contador anterior', 
        render_kw={'class': 'form-control', 'readonly': True, 'min': 0}
    )
    
    contador_escaneos_anterior = IntegerField(
        'Escaneos anteriores', 
        render_kw={'class': 'form-control', 'readonly': True, 'min': 0}
    )
    
    contador_copias_anterior = IntegerField(
        'Copias anteriores', 
        render_kw={'class': 'form-control', 'readonly': True, 'min': 0}
    )
    
    # Fecha del último conteo (solo lectura)
    fecha_ultimo_conteo = StringField(
        'Fecha último conteo', 
        render_kw={'class': 'form-control', 'readonly': True}
    )
    
    # Contadores actuales
    contador_impresiones_actual = IntegerField(
        'Contador actual', 
        validators=[
            DataRequired(message='El contador de impresiones es obligatorio'),
            NumberRange(min=0, message='El contador no puede ser negativo')
        ],
        render_kw={
            'class': 'form-control',
            'min': 0,
            'onchange': 'calcularDiferencia()'
        }
    )
    
    contador_escaneos_actual = IntegerField(
        'Escaneos actuales', 
        validators=[
            DataRequired(message='El contador de escaneos es obligatorio'),
            NumberRange(min=0, message='El contador no puede ser negativo')
        ],
        default=0,
        render_kw={
            'class': 'form-control',
            'min': 0,
            'onchange': 'calcularDiferencia()'
        }
    )
    
    contador_copias_actual = IntegerField(
        'Copias actuales', 
        validators=[
            Optional(),
            NumberRange(min=0, message='El contador no puede ser negativo')
        ],
        default=0,
        render_kw={
            'class': 'form-control',
            'min': 0,
            'onchange': 'calcularDiferencia()'
        }
    )
    
    # Diferencias calculadas (solo lectura)
    diferencia_impresiones = IntegerField(
        'Diferencia',
        render_kw={'class': 'form-control', 'readonly': True}
    )
    
    diferencia_escaneos = IntegerField(
        'Diferencia',
        render_kw={'class': 'form-control', 'readonly': True}
    )
    
    diferencia_copias = IntegerField(
        'Diferencia',
        render_kw={'class': 'form-control', 'readonly': True}
    )
    
    # Estado del equipo
    estado_equipo = SelectField(
        'Estado del equipo',
        choices=[
            ('operativo', 'Operativo'),
            ('con_fallas', 'Con fallas'),
            ('fuera_de_servicio', 'Fuera de servicio')
        ],
        default='operativo',
        render_kw={'class': 'form-control'}
    )
    
    # Mantenimiento
    requiere_mantenimiento = BooleanField(
        '¿Requiere mantenimiento?', 
        default=False,
        render_kw={
            'onchange': 'toggleMantenimiento()'
        }
    )
    
    problemas_detectados = TextAreaField(
        'Problemas detectados',
        validators=[],
        render_kw={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Describa los problemas encontrados',
            'disabled': True
        }
    )
    
    # Observaciones
    observaciones = TextAreaField(
        'Observaciones', 
        validators=[Optional()],
        render_kw={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Ingrese cualquier observación adicional'
        }
    )
    
    # Campos ocultos
    visita_id = HiddenField('Visita ID')
    
    # Botones
    submit = SubmitField(
        'Guardar conteo',
        render_kw={'class': 'btn btn-primary'}
    )
    
    cancelar = SubmitField(
        'Cancelar',
        render_kw={
            'class': 'btn btn-secondary',
            'formnovalidate': 'formnovalidate',
            'onclick': 'window.history.back(); return false;'
        }
    )
    
    def __init__(self, *args, **kwargs):
        super(ConteoImpresionForm, self).__init__(*args, **kwargs)
        # Inicializar opciones vacías
        self.cliente_id.choices = [(0, 'Seleccione un cliente')]
        self.sucursal_id.choices = [(0, 'Seleccione una sucursal')]
        self.equipo_id.choices = [(0, 'Seleccione un equipo')]
    
    def validate_contador_impresiones_actual(self, field):
        """Valida que el contador actual sea mayor o igual al anterior."""
        if (hasattr(self, 'contador_impresiones_anterior') and 
            self.contador_impresiones_anterior.data is not None and
            field.data < self.contador_impresiones_anterior.data):
            
            # Permitir si el usuario confirma que es un reinicio de contador
            if not getattr(self, 'confirmar_reinicio', False):
                raise ValidationError(
                    f'El contador actual ({field.data}) no puede ser menor que el anterior ' \
                    f'({self.contador_impresiones_anterior.data}). Si el contador fue reiniciado, ' \
                    'marque la opción de reinicio de contador.'
                )
    
    def validate_requiere_mantenimiento(self, field):
        """Valida que si requiere mantenimiento, se especifiquen los problemas."""
        if field.data and not self.problemas_detectados.data.strip():
            raise ValidationError('Debe especificar los problemas detectados cuando se requiere mantenimiento')
    
    def validate_fecha_conteo(self, field):
        """Valida que la fecha del conteo no sea futura."""
        if field.data and field.data > date.today():
            raise ValidationError('La fecha del conteo no puede ser futura')
    
    def validate(self, **kwargs):
        """Validación cruzada de campos."""
        # Validación estándar del formulario
        if not super().validate():
            return False
            
        # Validar que al menos un contador tenga un valor mayor a cero
        if (self.contador_impresiones_actual.data == 0 and 
            self.contador_escaneos_actual.data == 0 and 
            self.contador_copias_actual.data == 0):
            
            msg = 'Al menos un contador debe tener un valor mayor a cero'
            self.contador_impresiones_actual.errors.append(msg)
            self.contador_escaneos_actual.errors.append(msg)
            self.contador_copias_actual.errors.append(msg)
            return False
            
        return True
