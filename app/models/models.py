from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

# ------------------------
# USUARIOS Y ROLES
# ------------------------
class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    rol = db.Column(db.String(32), default='tecnico')  # superadmin, admin, tecnico
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    def tiene_permiso(self, permiso):
        permisos_por_rol = {
            "superadmin": {"*"},
            "admin": {"ver", "editar", "crear", "reportar", "facturar", "inventariar"},
            "tecnico": {"ver", "registrar_conteo", "solicitar_servicio"}
        }
        return permiso in permisos_por_rol.get(self.rol, set()) or "*" in permisos_por_rol.get(self.rol, set())

# ------------------------
# CLIENTES
# ------------------------
class Cliente(db.Model):
    __tablename__ = 'clientes'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(128), nullable=False)
    contacto = db.Column(db.String(128))
    email = db.Column(db.String(128))
    telefono = db.Column(db.String(32))
    direccion = db.Column(db.String(256))
    activo = db.Column(db.Boolean, default=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    equipos = db.relationship('Equipo', backref='cliente', lazy='dynamic')
    facturas = db.relationship('Factura', backref='cliente', lazy='dynamic')
    pedidos = db.relationship('Pedido', backref='cliente', lazy='dynamic')
    solicitudes = db.relationship('Solicitud', backref='cliente', lazy='dynamic')

# ------------------------
# EQUIPOS
# ------------------------
class Equipo(db.Model):
    __tablename__ = 'equipos'
    id = db.Column(db.Integer, primary_key=True)
    marca = db.Column(db.String(64), nullable=False)
    modelo = db.Column(db.String(64), nullable=False)
    numero_serie = db.Column(db.String(64), unique=True, nullable=False)
    ubicacion = db.Column(db.String(128))
    estado = db.Column(db.String(32), default='operativo')
    requiere_mantenimiento = db.Column(db.Boolean, default=False)
    ultimos_problemas = db.Column(db.String(256))
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    conteos = db.relationship('Conteo', backref='equipo', lazy='dynamic')
    mantenimientos = db.relationship('Mantenimiento', backref='equipo', lazy='dynamic')
    pedidos = db.relationship('Pedido', backref='equipo', lazy='dynamic')
    solicitudes = db.relationship('Solicitud', backref='equipo', lazy='dynamic')

# ------------------------
# CONTEO (Conteo de impresiones, escaneos, copias)
# ------------------------
class Conteo(db.Model):
    __tablename__ = 'conteos'
    id = db.Column(db.Integer, primary_key=True)
    fecha_conteo = db.Column(db.DateTime, default=datetime.utcnow)
    impresiones = db.Column(db.Integer, default=0)
    escaneos = db.Column(db.Integer, default=0)
    copias = db.Column(db.Integer, default=0)
    equipo_id = db.Column(db.Integer, db.ForeignKey('equipos.id'), nullable=False)
    tecnico_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    observaciones = db.Column(db.Text)
    tecnico = db.relationship('Usuario', backref='conteos_realizados')

# ------------------------
# FACTURACION
# ------------------------
class Factura(db.Model):
    __tablename__ = 'facturas'
    id = db.Column(db.Integer, primary_key=True)
    fecha_emision = db.Column(db.DateTime, default=datetime.utcnow)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    monto_subtotal = db.Column(db.Float, nullable=False)
    monto_impuestos = db.Column(db.Float, default=0)
    monto_total = db.Column(db.Float, nullable=False)
    estado = db.Column(db.String(32), default="pendiente")  # pendiente, pagada, anulada
    pedidos = db.relationship('Pedido', backref='factura', lazy='dynamic')

# ------------------------
# INVENTARIO
# ------------------------
class InventarioItem(db.Model):
    __tablename__ = 'inventario_items'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(128), nullable=False)
    descripcion = db.Column(db.String(256))
    cantidad = db.Column(db.Integer, default=0)
    ubicacion_id = db.Column(db.Integer, db.ForeignKey('bodegas.id'))
    codigo_barras = db.Column(db.String(32), unique=True)
    activo = db.Column(db.Boolean, default=True)
    pedidos_items = db.relationship('PedidoItem', backref='inventario_item', lazy='dynamic')

# ------------------------
# BODEGAS
# ------------------------
class Bodega(db.Model):
    __tablename__ = 'bodegas'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(128), nullable=False)
    direccion = db.Column(db.String(256))
    inventario = db.relationship('InventarioItem', backref='bodega', lazy='dynamic')

# ------------------------
# PEDIDOS
# ------------------------
class Pedido(db.Model):
    __tablename__ = 'pedidos'
    id = db.Column(db.Integer, primary_key=True)
    fecha_pedido = db.Column(db.DateTime, default=datetime.utcnow)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    equipo_id = db.Column(db.Integer, db.ForeignKey('equipos.id'))
    factura_id = db.Column(db.Integer, db.ForeignKey('facturas.id'))
    estado = db.Column(db.String(32), default="pendiente")  # pendiente, entregado, cancelado
    items = db.relationship('PedidoItem', backref='pedido', lazy='dynamic')

class PedidoItem(db.Model):
    __tablename__ = 'pedido_items'
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'), nullable=False)
    inventario_item_id = db.Column(db.Integer, db.ForeignKey('inventario_items.id'), nullable=False)
    cantidad = db.Column(db.Integer, default=1)

# ------------------------
# SOLICITUDES (Tickets de servicio)
# ------------------------
class Solicitud(db.Model):
    __tablename__ = 'solicitudes'
    id = db.Column(db.Integer, primary_key=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    equipo_id = db.Column(db.Integer, db.ForeignKey('equipos.id'))
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))  # quien la creó
    descripcion = db.Column(db.Text)
    estado = db.Column(db.String(32), default="abierta")  # abierta, en_proceso, cerrada, cancelada
    tecnico_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))  # asignado

# ------------------------
# MANTENIMIENTO
# ------------------------
class Mantenimiento(db.Model):
    __tablename__ = 'mantenimientos'
    id = db.Column(db.Integer, primary_key=True)
    equipo_id = db.Column(db.Integer, db.ForeignKey('equipos.id'), nullable=False)
    fecha_mantenimiento = db.Column(db.Date, nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    realizado = db.Column(db.Boolean, default=False)

# ------------------------
# REPORTES (Generación de reportes)
# ------------------------
class Reporte(db.Model):
    __tablename__ = 'reportes'
    id = db.Column(db.Integer, primary_key=True)
    fecha_generacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    tipo = db.Column(db.String(64))  # inventario, facturacion, conteo, solicitudes, etc.
    parametros = db.Column(db.String(256))
    datos = db.Column(db.Text)  # Puede ser JSON serializado, CSV, etc.