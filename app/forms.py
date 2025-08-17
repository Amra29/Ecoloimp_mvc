from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, FloatField, IntegerField, BooleanField, PasswordField, DateField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional, InputRequired


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember_me = BooleanField('Recordarme', default=False)


class UsuarioForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    telefono = StringField('Teléfono', validators=[Length(max=20)])
    rol = SelectField('Rol',
                      choices=[('usuario', 'Usuario'), ('tecnico', 'Técnico'), ('administrador', 'Administrador')])
    password = PasswordField('Contraseña', validators=[Optional(), Length(min=6, max=20)])


class ClienteForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[Email(), Optional()])
    telefono = StringField('Teléfono', validators=[DataRequired(), Length(max=20)])
    direccion = TextAreaField('Dirección')
    tipo_cliente = SelectField('Tipo de Cliente', choices=[('particular', 'Particular'), ('empresa', 'Empresa')])


class EquipoForm(FlaskForm):
    """Formulario para crear o editar un equipo."""
    numero_serie = StringField('Número de Serie', validators=[DataRequired(), Length(max=50)])
    marca = StringField('Marca', validators=[DataRequired(), Length(max=50)])
    modelo = StringField('Modelo', validators=[DataRequired(), Length(max=100)])
    tipo = SelectField('Tipo', choices=[
        ('impresora', 'Impresora'),
        ('multifuncional', 'Multifuncional'),
        ('escaner', 'Escáner'),
        ('otro', 'Otro')
    ], validators=[DataRequired()])
    fecha_instalacion = DateField('Fecha de Instalación', format='%Y-%m-%d', validators=[Optional()])
    contador_inicial = IntegerField('Contador Inicial', validators=[Optional(), NumberRange(min=0)])
    cliente_id = SelectField('Cliente', coerce=int, validators=[DataRequired()])
    sucursal_id = SelectField('Sucursal', coerce=int, validators=[Optional()])
    ubicacion = StringField('Ubicación', validators=[Length(max=200), Optional()])
    notas = TextAreaField('Notas', validators=[Optional()])


class BuscarEquipoForm(FlaskForm):
    """Formulario para buscar equipos."""
    numero_serie = StringField('Número de Serie', validators=[Optional()])
    marca = StringField('Marca', validators=[Optional()])
    modelo = StringField('Modelo', validators=[Optional()])
    tipo = SelectField('Tipo', choices=[
        ('', 'Todos'),
        ('impresora', 'Impresora'),
        ('multifuncional', 'Multifuncional'),
        ('escaner', 'Escáner'),
        ('otro', 'Otro')
    ], validators=[Optional()])
    cliente_id = SelectField('Cliente', coerce=int, validators=[Optional()])
    sucursal_id = SelectField('Sucursal', coerce=int, validators=[Optional()])


class ServicioForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(min=2, max=100)])
    descripcion = TextAreaField('Descripción')
    precio_base = FloatField('Precio Base', validators=[DataRequired(), NumberRange(min=0)])
    categoria = StringField('Categoría', validators=[Length(max=50)])


class TecnicoForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()], 
                       description='Se usará para iniciar sesión')
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6)],
                           description='Mínimo 6 caracteres')
    telefono = StringField('Teléfono', validators=[DataRequired(), Length(max=20)])
    especialidad = StringField('Especialidad', validators=[Length(max=100)])
    habilidades = TextAreaField('Habilidades', 
                              description='Lista de habilidades separadas por comas')
    notas = TextAreaField('Notas',
                        description='Observaciones adicionales sobre el técnico')
    activo = BooleanField('Activo', default=True)
    fecha_ingreso = StringField('Fecha de Ingreso', validators=[Optional()],
                              description='Formato: AAAA-MM-DD')
    
    def validate_email(self, field):
        # Verificar si el correo ya está en uso por otro usuario
        from app.models.models import Usuario
        if Usuario.query.filter(Usuario.email == field.data.lower(), 
                              Usuario.id != getattr(self, '_obj_id', None)).first():
            raise ValidationError('Este correo electrónico ya está en uso')
    
    def __init__(self, *args, **kwargs):
        # Guardar el ID del objeto si se está editando
        if 'obj' in kwargs and kwargs['obj'] is not None:
            self._obj_id = kwargs['obj'].id
        super(TecnicoForm, self).__init__(*args, **kwargs)


class SolicitudForm(FlaskForm):
    cliente_id = SelectField('Cliente', coerce=int, validators=[DataRequired()])
    servicio_id = SelectField('Servicio', coerce=int, validators=[DataRequired()])
    descripcion_problema = TextAreaField('Descripción del Problema', validators=[DataRequired()])
    prioridad = SelectField('Prioridad',
                            choices=[('baja', 'Baja'), ('media', 'Media'), ('alta', 'Alta'), ('urgente', 'Urgente')])
    estado = SelectField('Estado',
                         choices=[('pendiente', 'Pendiente'), ('asignada', 'Asignada'),
                                  ('en_proceso', 'En Proceso'), ('completada', 'Completada'),
                                  ('cancelada', 'Cancelada')])


class AsignacionForm(FlaskForm):
    solicitud_id = SelectField('Solicitud', coerce=int, validators=[DataRequired()])
    tecnico_id = SelectField('Técnico', coerce=int, validators=[DataRequired()])
    observaciones = TextAreaField('Observaciones')
    tiempo_estimado = IntegerField('Tiempo Estimado (horas)', validators=[Optional(), NumberRange(min=1)])
    estado = SelectField('Estado',
                         choices=[('asignada', 'Asignada'), ('en_proceso', 'En Proceso'), ('completada', 'Completada')])


class ParteForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(min=2, max=100)])
    codigo = StringField('Código', validators=[DataRequired(), Length(min=2, max=50)])
    descripcion = TextAreaField('Descripción')
    precio = FloatField('Precio', validators=[DataRequired(), NumberRange(min=0)])
    stock = IntegerField('Stock', validators=[NumberRange(min=0)])
    stock_minimo = IntegerField('Stock Mínimo', validators=[NumberRange(min=0)])
    proveedor = StringField('Proveedor', validators=[Length(max=100)])


class FacturaForm(FlaskForm):
    numero_factura = StringField('Número de Factura', validators=[DataRequired(), Length(max=20)])
    cliente_id = SelectField('Cliente', coerce=int, validators=[DataRequired()])
    solicitud_id = SelectField('Solicitud', coerce=int, validators=[Optional()])
    subtotal = FloatField('Subtotal', validators=[DataRequired(), NumberRange(min=0)])
    impuestos = FloatField('Impuestos', validators=[NumberRange(min=0)])
    total = FloatField('Total', validators=[DataRequired(), NumberRange(min=0)])
    estado = SelectField('Estado',
                         choices=[('pendiente', 'Pendiente'), ('pagada', 'Pagada'), ('vencida', 'Vencida')])
    observaciones = TextAreaField('Observaciones')


class ReporteForm(FlaskForm):
    trabajo_realizado = TextAreaField('Trabajo Realizado', validators=[DataRequired()])
    problemas_encontrados = TextAreaField('Problemas Encontrados')
    solucion_aplicada = TextAreaField('Solución Aplicada')
    recomendaciones = TextAreaField('Recomendaciones')
    piezas_utilizadas = TextAreaField('Piezas Utilizadas')

    estado_inicial = SelectField('Estado Inicial del Equipo',
                                 choices=[('funcionando', 'Funcionando'), ('dañado', 'Dañado'),
                                          ('inoperativo', 'Inoperativo')])
    estado_final = SelectField('Estado Final del Equipo',
                               choices=[('funcionando', 'Funcionando'), ('dañado', 'Dañado'),
                                        ('inoperativo', 'Inoperativo')])

    hora_inicio = StringField('Hora de Inicio (HH:MM)')
    hora_fin = StringField('Hora de Fin (HH:MM)')

    cliente_satisfecho = BooleanField('Cliente Satisfecho', default=True)
    observaciones_cliente = TextAreaField('Observaciones del Cliente')


class PedidoPiezaForm(FlaskForm):
    parte_id = SelectField('Pieza/Repuesto', coerce=int, validators=[DataRequired()])
    cantidad_solicitada = IntegerField('Cantidad Solicitada', validators=[DataRequired(), NumberRange(min=1)])
    motivo = TextAreaField('Motivo del Pedido', validators=[DataRequired()])
    urgencia = SelectField('Urgencia',
                           choices=[('baja', 'Baja'), ('normal', 'Normal'), ('alta', 'Alta'), ('urgente', 'Urgente')])
    asignacion_id = IntegerField('ID Asignación', validators=[Optional()])


class BuscarClienteForm(FlaskForm):
    busqueda = StringField('Buscar', validators=[InputRequired()], render_kw={"placeholder": "Nombre, email o teléfono"})
    tipo = SelectField('Tipo', choices=[
        ('todos', 'Todos'),
        ('particular', 'Particular'),
        ('empresa', 'Empresa')
    ], default='todos')


class BuscarTecnicoForm(FlaskForm):
    busqueda = StringField('Buscar', validators=[Optional()], render_kw={"placeholder": "Nombre, email o especialidad"})
    estado = SelectField('Estado', choices=[
        ('todos', 'Todos'),
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo')
    ], default='todos')


class AjusteStockForm(FlaskForm):
    nuevo_stock = IntegerField('Nuevo Stock', validators=[DataRequired(), NumberRange(min=0)])
    motivo = TextAreaField('Motivo del Ajuste', validators=[DataRequired()])
