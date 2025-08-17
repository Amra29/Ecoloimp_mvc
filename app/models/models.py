"""
Modelos de la base de datos para el sistema de servicio técnico y conteo de impresiones.
"""
from datetime import datetime
from sqlalchemy.orm import validates
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func

# Usar la instancia de SQLAlchemy desde extensions.py
from app.extensions import db

# ============================================
# Modelos de Permisos y Roles
# ============================================

class Permiso(db.Model):
    """Modelo para almacenar los permisos disponibles en el sistema"""
    __tablename__ = 'permisos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(64), unique=True, nullable=False)
    descripcion = db.Column(db.String(255))
    categoria = db.Column(db.String(64), index=True)  # Para agrupar permisos
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    roles = db.relationship('RolPermiso', back_populates='permiso', 
                           cascade='all, delete-orphan')
    usuarios = db.relationship('UsuarioPermiso', back_populates='permiso', 
                              cascade='all, delete-orphan')
                              
    def __repr__(self):
        return f'<Permiso {self.nombre}>'


class RolPermiso(db.Model):
    """Tabla de unión entre roles y permisos"""
    __tablename__ = 'roles_permisos'
    
    id = db.Column(db.Integer, primary_key=True)
    rol = db.Column(db.String(50), nullable=False, index=True)
    permiso_id = db.Column(db.Integer, db.ForeignKey('permisos.id', ondelete='CASCADE'), nullable=False)
    fecha_asignacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    permiso = db.relationship('Permiso', back_populates='roles')
    
    __table_args__ = (
        db.UniqueConstraint('rol', 'permiso_id', name='uq_rol_permiso'),
        {'sqlite_autoincrement': True}
    )
    
    @classmethod
    def asignar_permiso_rol(cls, rol, permiso_nombre):
        """Asigna un permiso a un rol si no existe ya la relación"""
        permiso = Permiso.query.filter_by(nombre=permiso_nombre).first()
        if not permiso:
            permiso = Permiso(nombre=permiso_nombre, 
                           descripcion=f'Permiso asignado al rol {rol}')
            db.session.add(permiso)
            db.session.flush()  # Para obtener el ID del permiso
            
        # Verificar si ya existe la relación
        if not cls.query.filter_by(rol=rol, permiso_id=permiso.id).first():
            rol_permiso = cls(rol=rol, permiso_id=permiso.id)
            db.session.add(rol_permiso)
            return True
        return False
        
    @classmethod
    def quitar_permiso_rol(cls, rol, permiso_nombre):
        """Elimina un permiso de un rol"""
        permiso = Permiso.query.filter_by(nombre=permiso_nombre).first()
        if permiso:
            rol_permiso = cls.query.filter_by(rol=rol, permiso_id=permiso.id).first()
            if rol_permiso:
                db.session.delete(rol_permiso)
                return True
        return False
    
    def __repr__(self):
        return f'<RolPermiso {self.rol} - {self.permiso.nombre}>'


class UsuarioPermiso(db.Model):
    """Tabla de unión entre usuarios y permisos"""
    __tablename__ = 'usuarios_permisos'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)
    permiso_id = db.Column(db.Integer, db.ForeignKey('permisos.id', ondelete='CASCADE'), nullable=False)
    fecha_asignacion = db.Column(db.DateTime, default=datetime.utcnow)
    asignado_por = db.Column(db.Integer, db.ForeignKey('usuarios.id'))  # Usuario que asignó el permiso
    notas = db.Column(db.Text, nullable=True)  # Notas adicionales sobre la asignación
    
    # Relaciones
    usuario = db.relationship('Usuario', foreign_keys=[usuario_id], back_populates='permisos_usuario')
    permiso = db.relationship('Permiso', back_populates='usuarios')
    
    __table_args__ = (
        db.UniqueConstraint('usuario_id', 'permiso_id', name='uq_usuario_permiso'),
        {'sqlite_autoincrement': True}
    )
    
    @classmethod
    def asignar_permiso_usuario(cls, usuario_id, permiso_nombre, asignado_por_id=None, notas=None):
        """Asigna un permiso a un usuario si no lo tiene ya"""
        from app import db
        
        usuario = Usuario.query.get(usuario_id)
        if not usuario:
            return False, "Usuario no encontrado"
            
        permiso = Permiso.query.filter_by(nombre=permiso_nombre).first()
        if not permiso:
            permiso = Permiso(nombre=permiso_nombre, 
                           descripcion=f'Permiso asignado manualmente a usuario {usuario_id}')
            db.session.add(permiso)
            db.session.flush()  # Para obtener el ID del permiso
        
        # Verificar si ya tiene el permiso
        if cls.query.filter_by(usuario_id=usuario_id, permiso_id=permiso.id).first():
            return False, "El usuario ya tiene este permiso asignado"
            
        # Asignar el permiso
        usuario_permiso = cls(
            usuario_id=usuario_id,
            permiso_id=permiso.id,
            asignado_por=asignado_por_id,
            notas=notas
        )
        db.session.add(usuario_permiso)
        return True, "Permiso asignado correctamente"
        
    @classmethod
    def quitar_permiso_usuario(cls, usuario_id, permiso_nombre):
        """Elimina un permiso de un usuario"""
        permiso = Permiso.query.filter_by(nombre=permiso_nombre).first()
        if not permiso:
            return False, "Permiso no encontrado"
            
        usuario_permiso = cls.query.filter_by(
            usuario_id=usuario_id, 
            permiso_id=permiso.id
        ).first()
        
        if not usuario_permiso:
            return False, "El usuario no tiene este permiso asignado"
            
        db.session.delete(usuario_permiso)
        return True, "Permiso eliminado correctamente"
    
    def __repr__(self):
        return f'<UsuarioPermiso {self.usuario_id} - {self.permiso.nombre}>'


# ============================================
# Modelos de Autenticación y Usuarios
# ============================================

class Usuario(db.Model, UserMixin):
    """
    Modelo base para todos los usuarios del sistema Ecoloimp.
    Usa herencia de tabla única con discriminador.
    """
    __tablename__ = 'usuarios'
    
    # Sistema de roles jerárquico
    ROLES = {
        'superadmin': {'name': 'Super Administrador', 'level': 3},
        'admin': {'name': 'Administrador', 'level': 2},
        'tecnico': {'name': 'Técnico', 'level': 1},
        'usuario': {'name': 'Usuario', 'level': 0}
    }
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128))
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20), nullable=True)
    direccion = db.Column(db.Text, nullable=True)
    activo = db.Column(db.Boolean, default=True, nullable=False)
    rol = db.Column(db.String(20), nullable=False, default='tecnico')  # 'superadmin', 'admin', 'tecnico'
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_acceso = db.Column(db.DateTime, nullable=True)
    fecha_nacimiento = db.Column(db.Date, nullable=True)
    genero = db.Column(db.String(20), nullable=True)
    foto_perfil = db.Column(db.String(255), nullable=True)
    
    # Campos de auditoría
    creado_por = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    actualizado_por = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    fecha_actualizacion = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relaciones
    permisos_usuario = db.relationship('UsuarioPermiso', 
                                     foreign_keys='UsuarioPermiso.usuario_id',
                                     back_populates='usuario', 
                                     cascade='all, delete-orphan')
    
    # Relaciones de auditoría
    creado_por_usuario = db.relationship('Usuario', 
                                       foreign_keys=[creado_por], 
                                       remote_side=[id],
                                       post_update=True)
    actualizado_por_usuario = db.relationship('Usuario', 
                                            foreign_keys=[actualizado_por],
                                            remote_side=[id],
                                            post_update=True)
    
    # Propiedades calculadas
    @property
    def nombre_completo(self):
        """Devuelve el nombre completo del usuario"""
        return f"{self.nombre} {self.apellido}"
    
    @property
    def rol_display(self):
        """Devuelve el nombre legible del rol"""
        return self.ROLES.get(self.rol, self.rol.capitalize())
    
    # Métodos de autenticación
    def set_password(self, password):
        """Establece la contraseña del usuario"""
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        """Verifica si la contraseña es correcta"""
        return check_password_hash(self.password_hash, password)
    
    def get_auth_token(self, expires_in=3600):
        """Genera un token JWT para autenticación por API"""
        from app import app
        return jwt.encode(
            {'user_id': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256'
        )
    
    @staticmethod
    def verify_auth_token(token):
        """Verifica un token JWT y devuelve el usuario"""
        from app import app
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])
            return Usuario.query.get(data['user_id'])
        except:
            return None
            
    def is_admin(self):
        """
        Check if the user has admin or superadmin role.
        
        Returns:
            bool: True if user is admin or superadmin, False otherwise
        """
        return self.ROLES.get(self.rol, {}).get('level', 0) >= self.ROLES['admin']['level']
        
    def is_tecnico(self):
        """
        Check if the user has at least tecnico role.
        
        Returns:
            bool: True if user is tecnico, admin or superadmin, False otherwise
        """
        return self.ROLES.get(self.rol, {}).get('level', 0) >= self.ROLES['tecnico']['level']
        
    def get_id(self):
        return str(self.id)
        
    def is_active(self):
        return self.activo
        
    def has_role(self, *roles):
        """
        Check if user has any of the specified roles or a higher role.
        
        Args:
            *roles: Role names to check
            
        Returns:
            bool: True if user has at least one of the specified roles or higher
        """
        user_level = self.ROLES.get(self.rol, {}).get('level', 0)
        for role in roles:
            role_level = self.ROLES.get(role, {}).get('level', -1)
            if user_level >= role_level:
                return True
        return False
        
    def is_superadmin(self):
        """
        Check if user is a superadmin.
        
        Returns:
            bool: True if user is superadmin, False otherwise
        """
        return self.rol == 'superadmin'
        
    # Alias methods for backward compatibility
    es_admin = is_admin
    es_tecnico = is_tecnico
    es_superadmin = is_superadmin
    tiene_rol = has_role
    
    def tiene_permiso(self, permiso_nombre):
        """
        Verifica si el usuario tiene un permiso específico, ya sea por su rol o por asignación directa.
        
        Args:
            permiso_nombre (str): El nombre del permiso a verificar
            
        Returns:
            bool: True si el usuario tiene el permiso, False en caso contrario
        """
        # Superadmin tiene todos los permisos
        if self.es_superadmin():
            return True
            
        # Verificar si el permiso está asignado directamente al usuario
        if any(p.permiso.nombre == permiso_nombre for p in self.permisos_usuario):
            return True
            
        # Verificar si el permiso está asignado al rol del usuario
        from app import db
        from sqlalchemy import and_
        
        permiso = db.session.query(RolPermiso).join(Permiso).filter(
            and_(
                RolPermiso.rol == self.rol,
                Permiso.nombre == permiso_nombre
            )
        ).first()
        
        return permiso is not None
    
    def tiene_permisos(self, *permisos, todos=True):
        """
        Verifica si el usuario tiene los permisos especificados.
        
        Args:
            *permisos: Nombres de permisos a verificar
            todos (bool): Si es True (default), requiere que el usuario tenga todos los permisos.
                         Si es False, requiere que el usuario tenga al menos uno de los permisos.
        
        Returns:
            bool: True si se cumplen las condiciones de los permisos, False en caso contrario.
            
        Notas:
            - Los superadministradores siempre tienen todos los permisos.
            - Los permisos se pueden asignar directamente al usuario o a su rol.
        """
        # Superadmin tiene todos los permisos
        if self.es_superadmin():
            return True
            
        if not permisos:
            return False
            
        # Verificar permisos según el modo (todos/cualquiera)
        if todos:
            return all(self.tiene_permiso(p) for p in permisos)
        return any(self.tiene_permiso(p) for p in permisos)
    
    def obtener_permisos(self):
        """
        Obtiene todos los permisos del usuario, incluyendo los asignados directamente
        y los heredados de su rol.
        
        Returns:
            set: Conjunto de nombres de permisos únicos que tiene el usuario.
            
        Notas:
            - Los permisos directos del usuario tienen prioridad sobre los del rol.
            - Los superadministradores tienen implícitamente todos los permisos.
        """
        # Si es superadmin, devolver todos los permisos existentes
        if self.es_superadmin():
            return {p.nombre for p in Permiso.query.all()}
        
        # Obtener permisos directos del usuario
        permisos_directos = {up.permiso.nombre for up in self.permisos_usuario}
        
        # Obtener permisos del rol (solo si el usuario tiene un rol válido)
        permisos_rol = set()
        if self.rol:
            permisos_rol = {p[0] for p in db.session.query(Permiso.nombre)
                          .join(RolPermiso, Permiso.id == RolPermiso.permiso_id)
                          .filter(RolPermiso.rol == self.rol)
                          .all()}
        
        # Devolver la unión de permisos directos y del rol
        return permisos_directos.union(permisos_rol)
    
    def obtener_permisos_por_categoria(self):
        """
        Obtiene los permisos del usuario agrupados por categoría.
        
        Returns:
            dict: Un diccionario donde las claves son las categorías de permisos y los valores
                 son listas de tuplas (permiso, fecha_asignacion, es_directo).
        """
        from collections import defaultdict
        
        # Inicializar diccionario para agrupar por categoría
        permisos_por_categoria = defaultdict(list)
        
        # Si es superadmin, obtener todos los permisos existentes
        if self.es_superadmin():
            todos_los_permisos = Permiso.query.all()
            for permiso in todos_los_permisos:
                permisos_por_categoria[permiso.categoria or 'Sin categoría'].append(
                    (permiso, None, False)  # (permiso, fecha, es_directo)
                )
            return dict(permisos_por_categoria)
        
        # Obtener permisos directos del usuario
        permisos_directos = db.session.query(
            Permiso, 
            UsuarioPermiso.fecha_asignacion
        ).join(UsuarioPermiso).filter(
            UsuarioPermiso.usuario_id == self.id
        ).all()
        
        # Procesar permisos directos
        for permiso, fecha_asignacion in permisos_directos:
            categoria = permiso.categoria or 'Sin categoría'
            permisos_por_categoria[categoria].append(
                (permiso, fecha_asignacion, True)  # es_directo=True
            )
        
        # Obtener permisos del rol (si el usuario tiene un rol)
        if self.rol:
            permisos_rol = db.session.query(Permiso).join(RolPermiso).filter(
                RolPermiso.rol == self.rol
            ).all()
            
            # Procesar permisos del rol (solo si no están ya en los directos)
            permisos_directos_set = {p.id for p, _ in permisos_directos}
            for permiso in permisos_rol:
                if permiso.id not in permisos_directos_set:  # Evitar duplicados
                    categoria = permiso.categoria or 'Sin categoría'
                    permisos_por_categoria[categoria].append(
                        (permiso, None, False)  # es_directo=False
                    )
        
        # Convertir defaultdict a dict regular para evitar comportamientos inesperados
        return dict(permisos_por_categoria)
        
    # Otros métodos...
    
    def tiene_permiso_objeto(self, objeto, accion):
        """
        Verifica si el usuario tiene permiso para realizar una acción sobre un objeto específico.
        
        Args:
            objeto (str): Tipo de objeto sobre el que se realiza la acción (ej: 'usuario', 'equipo')
            accion (str): Acción a realizar sobre el objeto (ej: 'crear', 'editar', 'eliminar')
            
        Returns:
            bool: True si el usuario tiene el permiso, False en caso contrario
        """
        # Construir el nombre del permiso (ej: 'usuario_editar')
        permiso = f"{objeto}_{accion}".lower()
        return self.tiene_permiso(permiso)
        
    def puede_ver(self, recurso):
        """
        Verifica si el usuario puede ver un recurso específico.
        
        Args:
            recurso (str): Nombre del recurso a verificar
            
        Returns:
            bool: True si el usuario tiene permiso para ver el recurso
        """
        return self.tiene_permiso_objeto(recurso, 'ver')
        
    def puede_editar(self, recurso):
        """
        Verifica si el usuario puede editar un recurso específico.
        
        Args:
            recurso (str): Nombre del recurso a verificar
            
        Returns:
            bool: True si el usuario tiene permiso para editar el recurso
        """
        return self.tiene_permiso_objeto(recurso, 'editar')
        
    def puede_eliminar(self, recurso):
        """
        Verifica si el usuario puede eliminar un recurso específico.
        
        Args:
            recurso (str): Nombre del recurso a verificar
            
        Returns:
            bool: True si el usuario tiene permiso para eliminar el recurso
        """
        return self.tiene_permiso_objeto(recurso, 'eliminar')
        
    def puede_crear(self, recurso):
        """
        Verifica si el usuario puede crear un nuevo recurso del tipo especificado.
        
        Args:
            recurso (str): Nombre del recurso a verificar
            
        Returns:
            bool: True si el usuario tiene permiso para crear el recurso
        """
        return self.tiene_permiso_objeto(recurso, 'crear')
            
    def __repr__(self):
        return f'<Usuario {self.email} ({self.rol})>'
        
    def agregar_permiso(self, nombre_permiso):
        """Agrega un permiso al rol del usuario"""
        if not self.tiene_permiso(nombre_permiso):
            permiso = Permiso.query.filter_by(nombre=nombre_permiso).first()
            if not permiso:
                permiso = Permiso(nombre=nombre_permiso, descripcion=f'Permiso para {nombre_permiso}')
                db.session.add(permiso)
                db.session.commit()
                
            rol_permiso = RolPermiso(rol=self.rol, permiso_id=permiso.id)
            db.session.add(rol_permiso)
            db.session.commit()
            return True
        return False


class SuperAdmin(Usuario):
    """
    Modelo para superadministradores de Ecoloimp.
    Tienen acceso completo a todas las funcionalidades del sistema.
    """
    __tablename__ = 'superadmins'
    
    id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), primary_key=True)
    
    # Campos específicos del superadministrador
    puede_crear_administradores = db.Column(db.Boolean, default=True)
    puede_eliminar_administradores = db.Column(db.Boolean, default=True)
    puede_ver_todos_los_datos = db.Column(db.Boolean, default=True)
    
    __mapper_args__ = {
        'polymorphic_identity': 'superadmin',
    }
    
    def __init__(self, **kwargs):
        super(SuperAdmin, self).__init__(**kwargs)
        self.rol = 'superadmin'
        # Asignar permisos por defecto
        self.asignar_permisos_por_defecto()
        
    def asignar_permisos_por_defecto(self):
        """Asigna los permisos por defecto para superadministradores"""
        permisos_superadmin = [
            'admin_todo',
            'gestionar_usuarios',
            'gestionar_roles',
            'ver_todos_los_datos',
            'configurar_sistema',
            'gestionar_clientes',
            'gestionar_equipos',
            'gestionar_visitas',
            'gestionar_conteos',
            'ver_reportes',
            'exportar_datos',
            'gestionar_backups'
        ]
        
        for permiso in permisos_superadmin:
            self.agregar_permiso(permiso)
    
    def __repr__(self):
        return f'<SuperAdmin {self.email}>'


class Admin(Usuario):
    """
    Modelo para administradores de Ecoloimp.
    Gestionan el sistema pero con restricciones en comparación con los superadministradores.
    """
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), primary_key=True)
    
    # Campos específicos del administrador
    departamento = db.Column(db.String(100), nullable=False)
    puede_crear_tecnicos = db.Column(db.Boolean, default=True)
    puede_editar_tecnicos = db.Column(db.Boolean, default=True)
    puede_eliminar_tecnicos = db.Column(db.Boolean, default=False)
    puede_ver_todos_los_clientes = db.Column(db.Boolean, default=True)
    puede_ver_todos_los_equipos = db.Column(db.Boolean, default=True)
    
    __mapper_args__ = {
        'polymorphic_identity': 'admin',
    }
    
    def __init__(self, **kwargs):
        super(Admin, self).__init__(**kwargs)
        self.rol = 'admin'
        # Asignar permisos por defecto
        self.asignar_permisos_por_defecto()
    
    def asignar_permisos_por_defecto(self):
        """Asigna los permisos por defecto para administradores"""
        permisos_admin = [
            'gestionar_tecnicos',
            'gestionar_clientes',
            'gestionar_equipos',
            'gestionar_visitas',
            'gestionar_conteos',
            'ver_reportes',
            'exportar_datos',
            'aprobar_solicitudes',
            'configurar_parametros',
            'gestionar_alertas'
        ]
        
        for permiso in permisos_admin:
            self.agregar_permiso(permiso)
    
    @property
    def activo_admin(self):
        return self.activo
        
    @activo_admin.setter
    def activo_admin(self, value):
        self.activo = value
    
    def __repr__(self):
        return f'<Admin {self.email}>'


# ============================================
# Modelos del Sistema de Servicio Técnico
# ============================================

class Cliente(db.Model):
    """Modelo de cliente que recibe servicios técnicos."""
    __tablename__ = 'clientes'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    rfc = db.Column(db.String(20))
    direccion = db.Column(db.Text)
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(120))
    contacto_principal = db.Column(db.String(100))
    activo = db.Column(db.Boolean, default=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    notas = db.Column(db.Text)

    # Relaciones
    sucursales = db.relationship('Sucursal', back_populates='cliente', lazy=True, cascade='all, delete-orphan')
    equipos = db.relationship('Equipo', back_populates='cliente', lazy=True, cascade='all, delete-orphan')
    visitas = db.relationship('Visita', back_populates='cliente', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Cliente {self.nombre}>'


class Sucursal(db.Model):
    """Modelo de sucursales de los clientes."""
    __tablename__ = 'sucursales'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.Text, nullable=False)
    ciudad = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(120))
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    activa = db.Column(db.Boolean, default=True)

    # Relaciones
    cliente = db.relationship('Cliente', back_populates='sucursales')
    equipos = db.relationship('Equipo', back_populates='sucursal', lazy=True, cascade='all, delete-orphan')
    visitas = db.relationship('Visita', back_populates='sucursal', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Sucursal {self.nombre} - {self.ciudad}>'


class Servicio(db.Model):
    """Modelo de servicios ofrecidos."""
    __tablename__ = 'servicios'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    precio_base = db.Column(db.Float, nullable=False)
    categoria = db.Column(db.String(50))

    # Relaciones
    solicitudes = db.relationship('Solicitud', backref='servicio', lazy=True)

    def __repr__(self):
        return f'<Servicio {self.nombre}>'


class Tecnico(Usuario):
    """
    Modelo para técnicos de Ecoloimp.
    Realizan las visitas a clientes, conteos de impresiones y mantenimientos.
    """
    __tablename__ = 'tecnicos'
    
    id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), primary_key=True)
    
    # Información profesional
    especialidad = db.Column(db.String(100))
    habilidades = db.Column(db.Text)
    nivel_experiencia = db.Column(db.String(20))  # Junior, Intermedio, Senior
    
    # Información de contacto de emergencia
    contacto_emergencia_nombre = db.Column(db.String(100))
    contacto_emergencia_telefono = db.Column(db.String(20))
    contacto_emergencia_parentesco = db.Column(db.String(50))
    
    # Documentación
    numero_identificacion = db.Column(db.String(50))
    tipo_licencia = db.Column(db.String(20))
    vencimiento_licencia = db.Column(db.Date)
    seguro_social = db.Column(db.String(50))
    
    # Estado y fechas
    fecha_ingreso = db.Column(db.Date, default=datetime.utcnow().date)
    fecha_ultima_evaluacion = db.Column(db.Date)
    calificacion_evaluacion = db.Column(db.Float)
    
    # Ubicación
    ubicacion_actual = db.Column(db.String(200))
    ultima_ubicacion_conocida = db.Column(db.String(200))
    ultima_actualizacion_ubicacion = db.Column(db.DateTime)
    
    # Relaciones
    visitas = db.relationship('Visita', back_populates='tecnico', lazy=True, 
                             foreign_keys='Visita.tecnico_id',
                             order_by='desc(Visita.fecha_visita)')
    
    conteos = db.relationship('Conteo', back_populates='tecnico', lazy=True, 
                             foreign_keys='Conteo.tecnico_id',
                             order_by='desc(Conteo.fecha_conteo)')
    
    asignaciones = db.relationship('Asignacion', back_populates='tecnico', lazy=True,
                                 order_by='desc(Asignacion.fecha_asignacion)')
    
    __mapper_args__ = {
        'polymorphic_identity': 'tecnico',
    }
    
    def __init__(self, **kwargs):
        super(Tecnico, self).__init__(**kwargs)
        self.rol = 'tecnico'
        # Asignar permisos por defecto
        self.asignar_permisos_por_defecto()
    
    def asignar_permisos_por_defecto(self):
        """Asigna los permisos por defecto para técnicos"""
        permisos_tecnico = [
            'ver_conteos_propios',
            'crear_conteos',
            'editar_conteos_propios',
            'ver_equipos_asignados',
            'ver_visitas_propias',
            'crear_visitas',
            'reportar_incidentes',
            'solicitar_materiales',
            'ver_calendario',
            'actualizar_estado_visita',
            'registrar_conteo_impresiones',
            'ver_historial_cliente',
            'generar_informes_visitas'
        ]
        
        for permiso in permisos_tecnico:
            self.agregar_permiso(permiso)
    
    @property
    def activo_tecnico(self):
        return self.activo
        
    @activo_tecnico.setter
    def activo_tecnico(self, value):
        self.activo = value
    
    def obtener_estadisticas(self):
        """Obtiene estadísticas del técnico"""
        from sqlalchemy import func
        
        return {
            'total_visitas': self.visitas.count(),
            'visitas_mes_actual': self.visitas.filter(
                func.date_trunc('month', Visita.fecha_visita) == func.date_trunc('month', func.current_date())
            ).count(),
            'conteos_realizados': self.conteos.count(),
            'promedio_calificacion': self.calificacion_evaluacion or 0.0
        }
    
    def __repr__(self):
        return f'<Tecnico {self.nombre} ({self.especialidad or "Sin especialidad"})>'


class Solicitud(db.Model):
    __tablename__ = 'solicitudes'

    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    servicio_id = db.Column(db.Integer, db.ForeignKey('servicios.id'), nullable=False)
    descripcion_problema = db.Column(db.Text, nullable=False)
    prioridad = db.Column(db.String(20), default='media')
    estado = db.Column(db.String(20), default='pendiente')
    fecha_solicitud = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_limite = db.Column(db.DateTime)

    # Relaciones
    asignaciones = db.relationship('Asignacion', backref='solicitud', lazy=True)
    facturas = db.relationship('Factura', backref='solicitud', lazy=True)

    def __repr__(self):
        return f'<Solicitud {self.id}>'


class Asignacion(db.Model):
    """Modelo de asignaciones de técnicos a solicitudes."""
    __tablename__ = 'asignaciones'

    id = db.Column(db.Integer, primary_key=True)
    solicitud_id = db.Column(db.Integer, db.ForeignKey('solicitudes.id'), nullable=False)
    tecnico_id = db.Column(db.Integer, db.ForeignKey('tecnicos.id'), nullable=False)
    
    # Relación con Técnico
    tecnico = db.relationship('Tecnico', back_populates='asignaciones')
    fecha_asignacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_inicio = db.Column(db.DateTime)
    fecha_finalizacion = db.Column(db.DateTime)
    estado = db.Column(db.String(20), default='asignada')
    observaciones = db.Column(db.Text)
    tiempo_estimado = db.Column(db.Integer)
    tiempo_real = db.Column(db.Integer)

    # Relaciones
    reportes = db.relationship('Reporte', backref='asignacion', lazy=True, cascade='all, delete-orphan', passive_deletes=True)
    pedidos_piezas = db.relationship('PedidoPieza', backref='asignacion', lazy=True, cascade='all, delete-orphan', passive_deletes=True)

    def __repr__(self):
        return f'<Asignacion {self.id}>'


class Reporte(db.Model):
    """Modelo de reportes de servicio."""
    __tablename__ = 'reportes'

    id = db.Column(db.Integer, primary_key=True)
    asignacion_id = db.Column(db.Integer, db.ForeignKey('asignaciones.id', ondelete='CASCADE'), nullable=False)
    tecnico_id = db.Column(db.Integer, db.ForeignKey('tecnicos.id'), nullable=False)
    fecha_reporte = db.Column(db.DateTime, default=datetime.utcnow)

    trabajo_realizado = db.Column(db.Text, nullable=False)
    problemas_encontrados = db.Column(db.Text)
    solucion_aplicada = db.Column(db.Text)
    recomendaciones = db.Column(db.Text)
    piezas_utilizadas = db.Column(db.Text)

    estado_inicial = db.Column(db.String(50))
    estado_final = db.Column(db.String(50))

    hora_inicio = db.Column(db.DateTime)
    hora_fin = db.Column(db.DateTime)
    tiempo_total = db.Column(db.Integer)

    cliente_satisfecho = db.Column(db.Boolean, default=True)
    observaciones_cliente = db.Column(db.Text)
    firma_cliente = db.Column(db.Text)
    nombre_firma = db.Column(db.String(100))

    completado = db.Column(db.Boolean, default=False)
    aprobado_admin = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Reporte {self.id}>'


class Parte(db.Model):
    """Modelo de partes y repuestos."""
    __tablename__ = 'partes'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    descripcion = db.Column(db.Text)
    precio = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    stock_minimo = db.Column(db.Integer, default=5)
    proveedor = db.Column(db.String(100))
    activo = db.Column(db.Boolean, default=True)

    # Relaciones
    pedidos = db.relationship('PedidoPieza', backref='parte', lazy=True)

    @property
    def stock_bajo(self):
        """Indica si el stock est· por debajo del mÌnimo"""
        return self.stock <= self.stock_minimo

    def __repr__(self):
        return f'<Parte {self.nombre}>'


class PedidoPieza(db.Model):
    """Modelo de pedidos de piezas."""
    __tablename__ = 'pedidos_piezas'

    id = db.Column(db.Integer, primary_key=True)
    tecnico_id = db.Column(db.Integer, db.ForeignKey('tecnicos.id'), nullable=False)
    parte_id = db.Column(db.Integer, db.ForeignKey('partes.id'), nullable=False)
    asignacion_id = db.Column(db.Integer, db.ForeignKey('asignaciones.id'), nullable=True)

    cantidad_solicitada = db.Column(db.Integer, nullable=False)
    cantidad_aprobada = db.Column(db.Integer, default=0)

    motivo = db.Column(db.Text, nullable=False)
    urgencia = db.Column(db.String(20), default='normal')

    estado = db.Column(db.String(20), default='pendiente')

    fecha_pedido = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_aprobacion = db.Column(db.DateTime)
    fecha_entrega = db.Column(db.DateTime)

    observaciones_admin = db.Column(db.Text)

    def __repr__(self):
        return f'<PedidoPieza {self.id}>'


class Notificacion(db.Model):
    """Modelo para notificaciones del sistema."""
    __tablename__ = 'notificaciones'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)
    titulo = db.Column(db.String(200), nullable=False)
    mensaje = db.Column(db.Text, nullable=False)
    tipo = db.Column(db.String(50))  # info, success, warning, error, etc.
    leida = db.Column(db.Boolean, default=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    url = db.Column(db.String(500))  # URL para redirigir al hacer clic en la notificación
    
    # Relación con el usuario
    usuario = db.relationship('Usuario', backref=db.backref('notificaciones', lazy=True, cascade='all, delete-orphan'))
    
    def __repr__(self):
        return f'<Notificacion {self.titulo} - {self.usuario.email}>'
    
    def marcar_como_leida(self):
        """Marca la notificación como leída."""
        self.leida = True
        db.session.commit()
    
    @classmethod
    def crear_notificacion(cls, usuario_id, titulo, mensaje, tipo='info', url=None):
        """Método de ayuda para crear una notificación."""
        notificacion = cls(
            usuario_id=usuario_id,
            titulo=titulo,
            mensaje=mensaje,
            tipo=tipo,
            url=url
        )
        db.session.add(notificacion)
        db.session.commit()
        return notificacion


class Factura(db.Model):
    """Modelo de facturas."""
    __tablename__ = 'facturas'

    id = db.Column(db.Integer, primary_key=True)
    numero_factura = db.Column(db.String(20), unique=True, nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    solicitud_id = db.Column(db.Integer, db.ForeignKey('solicitudes.id'), nullable=True)
    fecha_emision = db.Column(db.DateTime, default=datetime.utcnow)
    subtotal = db.Column(db.Float, nullable=False)
    impuestos = db.Column(db.Float, default=0)
    total = db.Column(db.Float, nullable=False)
    estado = db.Column(db.String(20), default='pendiente')
    fecha_vencimiento = db.Column(db.DateTime)
    observaciones = db.Column(db.Text)

    def __repr__(self):
        return f'<Factura {self.numero_factura}>'


# ============================================
# Modelos del Sistema de Conteo de Impresiones
# ============================================

class Equipo(db.Model):
    """Modelo de equipos (impresoras, multifuncionales, etc.)
    
    Este modelo representa los equipos de impresión que son monitoreados en el sistema,
    ya sean propiedad de Ecoloimp SA o de los clientes.
    """
    __tablename__ = 'equipos'
    
    # Identificación básica
    id = db.Column(db.Integer, primary_key=True)
    numero_serie = db.Column(db.String(100), unique=True, nullable=False, index=True)
    codigo_inventario = db.Column(db.String(50), unique=True, index=True, 
                                 comment='Código de inventario interno')
    
    # Relaciones con cliente y ubicación
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False, index=True)
    sucursal_id = db.Column(db.Integer, db.ForeignKey('sucursales.id'), nullable=True, index=True)
    
    # Información del equipo
    marca = db.Column(db.String(50), nullable=False)
    modelo = db.Column(db.String(100), nullable=False, index=True)
    tipo = db.Column(db.String(20), nullable=False, 
                    comment="Tipo de equipo: 'impresora', 'multifuncional', 'escaner', 'fax'")
    
    # Ubicación física
    area = db.Column(db.String(100), comment='Área o departamento donde está ubicado el equipo')
    ubicacion_detalle = db.Column(db.Text, comment='Detalles específicos de la ubicación')
    
    # Propiedad y estado
    propiedad = db.Column(db.String(20), default='ecoloimp', nullable=False,
                        comment="Propiedad: 'ecoloimp' o 'cliente'")
    estado = db.Column(db.String(20), default='activo', nullable=False,
                      comment="Estado: 'activo', 'inactivo', 'mantenimiento', 'baja'")
    
    # Contadores actuales (último registro)
    ultimo_conteo_impresiones = db.Column(db.BigInteger, default=0)
    ultimo_conteo_escaneos = db.Column(db.BigInteger, default=0)
    ultimo_conteo_copias = db.Column(db.BigInteger, default=0)
    ultimo_conteo_fecha = db.Column(db.DateTime, comment='Fecha del último conteo registrado')
    
    # Fechas importantes
    fecha_instalacion = db.Column(db.Date, comment='Fecha de instalación del equipo')
    fecha_ultimo_mantenimiento = db.Column(db.Date)
    fecha_proximo_mantenimiento = db.Column(db.Date)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Características técnicas
    color = db.Column(db.Boolean, default=False, comment='¿Es una impresora a color?')
    velocidad_impresion = db.Column(db.String(50), comment='Ej: 30 ppm')
    resolucion = db.Column(db.String(50), comment='Ej: 1200x1200 dpi')
    conexiones = db.Column(db.String(100), comment='Tipos de conexión: USB, Ethernet, WiFi')
    
    # Consumibles
    modelo_toner = db.Column(db.String(100), comment='Modelo de tóner o tinta compatible')
    modelo_tambor = db.Column(db.String(100), comment='Modelo de tambor compatible')
    capacidad_hojas = db.Column(db.Integer, comment='Capacidad del alimentador de hojas')
    
    # Información adicional
    numero_activo_fijo = db.Column(db.String(50), comment='Número de activo fijo del cliente')
    garantia_hasta = db.Column(db.Date)
    proveedor = db.Column(db.String(100))
    notas = db.Column(db.Text)
    
    # Relaciones
    cliente = db.relationship('Cliente', back_populates='equipos', foreign_keys=[cliente_id])
    sucursal = db.relationship('Sucursal', back_populates='equipos', foreign_keys=[sucursal_id])
    conteos = db.relationship('Conteo', back_populates='equipo', 
                             order_by='desc(Conteo.fecha_conteo)', 
                             lazy='dynamic',
                             cascade='all, delete-orphan',
                             foreign_keys='Conteo.equipo_id')
    
    # Métodos de utilidad
    def obtener_ultimo_conteo(self):
        """Devuelve el último registro de conteo para este equipo."""
        return self.conteos.first()
    
    def calcular_promedio_mensual(self, meses=6):
        """Calcula el promedio de impresiones por mes en los últimos N meses."""
        from sqlalchemy import func, extract
        from datetime import datetime, timedelta
        
        fecha_limite = datetime.utcnow() - timedelta(days=30*meses)
        
        # Obtener el primer conteo después de la fecha límite
        primer_conteo = (self.conteos
                        .filter(Conteo.fecha_conteo >= fecha_limite)
                        .order_by(Conteo.fecha_conteo)
                        .first())
        
        if not primer_conteo:
            return 0
            
        # Obtener el último conteo
        ultimo_conteo = self.obtener_ultimo_conteo()
        
        if not ultimo_conteo or not primer_conteo:
            return 0
            
        # Calcular días entre conteos
        dias = (ultimo_conteo.fecha_conteo - primer_conteo.fecha_conteo).days or 1
        
        # Calcular impresiones totales y promedio diario
        total_impresiones = (ultimo_conteo.contador_impresion_actual - 
                            primer_conteo.contador_impresion_anterior)
        promedio_diario = total_impresiones / dias
        
        # Devolver promedio mensual (30 días)
        return round(promedio_diario * 30)
    
    def necesita_mantenimiento(self):
        """Verifica si el equipo necesita mantenimiento basado en el uso."""
        if not self.fecha_ultimo_mantenimiento:
            return True
            
        if self.fecha_proximo_mantenimiento and \
           self.fecha_proximo_mantenimiento <= datetime.utcnow().date():
            return True
            
        # Verificar por cantidad de impresiones desde el último mantenimiento
        ultimo_mantenimiento = (self.conteos
                               .filter(Conteo.requiere_mantenimiento == False)
                               .order_by(Conteo.fecha_conteo.desc())
                               .first())
                               
        if ultimo_mantenimiento:
            ultimo_conteo = self.obtener_ultimo_conteo()
            if ultimo_conteo:
                impresiones_desde_mantenimiento = (
                    ultimo_conteo.contador_impresion_actual - 
                    ultimo_mantenimiento.contador_impresion_actual
                )
                # Supongamos que el mantenimiento se recomienda cada 50,000 impresiones
                if impresiones_desde_mantenimiento > 50000:
                    return True
        
        return False
    
    def __repr__(self):
        return f'<Equipo {self.marca} {self.modelo} - {self.numero_serie}>'


class Visita(db.Model):
    """Modelo para registrar las visitas técnicas a clientes."""
    __tablename__ = 'visitas'
    
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    sucursal_id = db.Column(db.Integer, db.ForeignKey('sucursales.id'), nullable=True)
    tecnico_id = db.Column(db.Integer, db.ForeignKey('tecnicos.id'), nullable=False)
    
    # Datos de la visita
    fecha_visita = db.Column(db.Date, nullable=False)
    hora_inicio = db.Column(db.Time)
    hora_fin = db.Column(db.Time)
    tipo_visita = db.Column(db.String(20), default='conteo')  # 'conteo', 'mantenimiento', 'instalacion'
    estado = db.Column(db.String(20), default='programada')  # 'programada', 'en_proceso', 'completada', 'cancelada'
    observaciones = db.Column(db.Text)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    cliente = db.relationship('Cliente', back_populates='visitas', foreign_keys=[cliente_id])
    sucursal = db.relationship('Sucursal', back_populates='visitas', foreign_keys=[sucursal_id])
    tecnico = db.relationship('Tecnico', back_populates='visitas', foreign_keys=[tecnico_id])
    conteos = db.relationship('Conteo', back_populates='visita', lazy=True, cascade='all, delete-orphan', foreign_keys='Conteo.visita_id')

    def __repr__(self):
        return f'<Visita {self.id} - {self.fecha_visita}>'


class Conteo(db.Model):
    """Modelo para registrar los conteos de impresiones, escaneos y copias.
    
    Este modelo registra el estado de los contadores de impresoras en un momento dado,
    permitiendo llevar un historial de uso para facturación, mantenimiento y análisis de tendencias.
    
    Atributos:
        equipo_id (int): ID del equipo al que pertenece el conteo
        visita_id (int, opcional): ID de la visita técnica asociada (si aplica)
        tecnico_id (int): ID del técnico que realizó el conteo
        fecha_conteo (date): Fecha en que se realizó el conteo
        contador_*_actual (int): Valores actuales de los contadores
        contador_*_anterior (int): Valores anteriores de los contadores
        diferencia_* (int): Diferencia calculada entre conteos actual y anterior
        estado_equipo (str): Estado del equipo durante el conteo
        requiere_mantenimiento (bool): Indica si el equipo necesita mantenimiento
        problemas_detectados (str): Descripción de problemas encontrados
        observaciones (str): Notas adicionales sobre el conteo
    """
    __tablename__ = 'conteos'
    
    # Constantes para estados del equipo
    ESTADO_OPERATIVO = 'operativo'
    ESTADO_CON_FALLAS = 'con_fallas'
    ESTADO_FUERA_SERVICIO = 'fuera_de_servicio'
    ESTADOS_EQUIPO = [
        (ESTADO_OPERATIVO, 'Operativo'),
        (ESTADO_CON_FALLAS, 'Con fallas'),
        (ESTADO_FUERA_SERVICIO, 'Fuera de servicio')
    ]
    
    # Límites razonables para los contadores (ajustar según necesidad)
    MAX_CONTADOR = 9999999  # Límite superior para cualquier contador
    MAX_DIFERENCIA_DIARIA = 10000  # Límite para detectar saltos inusuales
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Relaciones con otras tablas
    equipo_id = db.Column(db.Integer, db.ForeignKey('equipos.id', ondelete='CASCADE'), nullable=False, index=True)
    visita_id = db.Column(db.Integer, db.ForeignKey('visitas.id', ondelete='SET NULL'), nullable=True, index=True)
    tecnico_id = db.Column(db.Integer, db.ForeignKey('tecnicos.id'), nullable=False, index=True)
    
    # Fechas
    fecha_conteo = db.Column(db.Date, nullable=False, index=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Contadores actuales (lectura del equipo)
    contador_impresion_actual = db.Column(
        db.BigInteger, 
        nullable=False, 
        default=0,
        info={'label': 'Contador de impresiones actual'}
    )
    contador_escaneo_actual = db.Column(
        db.BigInteger, 
        nullable=False, 
        default=0,
        info={'label': 'Contador de escaneos actual'}
    )
    contador_copias_actual = db.Column(
        db.BigInteger, 
        nullable=False, 
        default=0,
        info={'label': 'Contador de copias actual'}
    )
    
    # Contadores anteriores (para calcular diferencias)
    contador_impresion_anterior = db.Column(
        db.BigInteger, 
        default=0,
        info={'label': 'Contador de impresiones anterior'}
    )
    contador_escaneo_anterior = db.Column(
        db.BigInteger, 
        default=0,
        info={'label': 'Contador de escaneos anterior'}
    )
    contador_copias_anterior = db.Column(
        db.BigInteger, 
        default=0,
        info={'label': 'Contador de copias anterior'}
    )
    
    # Diferencias calculadas
    diferencia_impresiones = db.Column(
        db.BigInteger, 
        default=0,
        info={'label': 'Diferencia de impresiones'}
    )
    diferencia_escaneos = db.Column(
        db.BigInteger, 
        default=0,
        info={'label': 'Diferencia de escaneos'}
    )
    diferencia_copias = db.Column(
        db.BigInteger, 
        default=0,
        info={'label': 'Diferencia de copias'}
    )
    
    # Estado del equipo
    estado_equipo = db.Column(
        db.String(20), 
        default=ESTADO_OPERATIVO,
        nullable=False,
        info={
            'label': 'Estado del equipo',
            'choices': [(estado, etiqueta) for estado, etiqueta in ESTADOS_EQUIPO],
            'default': ESTADO_OPERATIVO
        }
    )
    
    # Información adicional
    requiere_mantenimiento = db.Column(
        db.Boolean, 
        default=False,
        info={'label': '¿Requiere mantenimiento?'}
    )
    problemas_detectados = db.Column(
        db.Text,
        info={'label': 'Problemas detectados'}
    )
    observaciones = db.Column(
        db.Text,
        info={'label': 'Observaciones'}
    )
    
    # Auditoría
    registrado_por = db.Column(
        db.Integer, 
        db.ForeignKey('usuarios.id'), 
        nullable=False,
        info={'label': 'Registrado por'}
    )
    
    # Índices compuestos para mejorar el rendimiento de consultas comunes
    __table_args__ = (
        db.Index('idx_conteo_equipo_fecha', 'equipo_id', 'fecha_conteo'),
        db.Index('idx_conteo_tecnico_fecha', 'tecnico_id', 'fecha_conteo'),
    )
    
    # Relaciones
    equipo = db.relationship('Equipo', back_populates='conteos', foreign_keys=[equipo_id])
    visita = db.relationship('Visita', back_populates='conteos', foreign_keys=[visita_id])
    tecnico = db.relationship('Tecnico', back_populates='conteos', foreign_keys=[tecnico_id])
    usuario_registro = db.relationship('Usuario', foreign_keys=[registrado_por])
    
    @validates('contador_impresion_actual', 'contador_escaneo_actual', 'contador_copias_actual',
              'contador_impresion_anterior', 'contador_escaneo_anterior', 'contador_copias_anterior')
    def validar_contadores(self, key, value):
        """Valida que los contadores estén dentro de rangos razonables."""
        if value is None:
            return 0
            
        if not isinstance(value, (int, int)) or value < 0:
            raise ValueError(f"El valor del contador debe ser un número entero no negativo")
            
        if value > self.MAX_CONTADOR:
            raise ValueError(f"El valor del contador no puede exceder {self.MAX_CONTADOR}")
            
        return value
    
    @validates('estado_equipo')
    def validar_estado_equipo(self, key, estado):
        """Valida que el estado del equipo sea uno de los permitidos."""
        if estado not in dict(self.ESTADOS_EQUIPO):
            raise ValueError(f"Estado de equipo no válido. Debe ser uno de: {', '.join(dict(self.ESTADOS_EQUIPO).keys())}")
        return estado
    
    def calcular_diferencias(self):
        """
        Calcula las diferencias con el conteo anterior.
        
        Returns:
            dict: Diccionario con las diferencias calculadas
        """
        diferencias = {}
        
        # Calcular diferencias para cada tipo de contador
        for tipo in ['impresion', 'escaneo', 'copias']:
            actual = getattr(self, f'contador_{tipo}_actual', 0) or 0
            anterior = getattr(self, f'contador_{tipo}_anterior', 0) or 0
            
            # Validar que el contador actual no sea menor que el anterior
            if actual < anterior and actual > 0:
                # Podría ser un reinicio del contador o un error
                # En este caso, asumimos que es un reinicio y la diferencia es el valor actual
                diferencia = actual
            else:
                diferencia = max(0, actual - anterior)
            
            # Detectar saltos inusuales (posible error de entrada)
            if diferencia > self.MAX_DIFERENCIA_DIARIA and anterior > 0:
                # Podríamos registrar una advertencia o notificación
                pass
            
            setattr(self, f'diferencia_{tipo}s', diferencia)
            diferencias[tipo] = diferencia
        
        return diferencias
    
    def actualizar_estado_equipo(self):
        """Actualiza el estado del equipo basado en los contadores y problemas detectados."""
        if self.estado_equipo == self.ESTADO_FUERA_SERVICIO:
            self.requiere_mantenimiento = True
        elif self.estado_equipo == self.ESTADO_CON_FALLAS:
            self.requiere_mantenimiento = True
    
    def to_dict(self):
        """Convierte el objeto a un diccionario para serialización JSON."""
        return {
            'id': self.id,
            'equipo_id': self.equipo_id,
            'equipo_nombre': f"{self.equipo.marca} {self.equipo.modelo}" if self.equipo else '',
            'fecha_conteo': self.fecha_conteo.isoformat() if self.fecha_conteo else None,
            'contador_impresion_actual': self.contador_impresion_actual,
            'contador_escaneo_actual': self.contador_escaneo_actual,
            'contador_copias_actual': self.contador_copias_actual,
            'diferencia_impresiones': self.diferencia_impresiones,
            'diferencia_escaneos': self.diferencia_escaneos,
            'diferencia_copias': self.diferencia_copias,
            'estado_equipo': self.estado_equipo,
            'estado_equipo_display': dict(self.ESTADOS_EQUIPO).get(self.estado_equipo, ''),
            'requiere_mantenimiento': self.requiere_mantenimiento,
            'tecnico_nombre': self.tecnico.nombre if self.tecnico else '',
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None
        }
    
    @classmethod
    def obtener_ultimo_conteo_equipo(cls, equipo_id):
        """Obtiene el último conteo registrado para un equipo."""
        return cls.query.filter_by(equipo_id=equipo_id)\
                      .order_by(cls.fecha_conteo.desc())\
                      .first()
    
    @classmethod
    def obtener_conteos_rango_fechas(cls, fecha_inicio, fecha_fin, equipo_id=None):
        """Obtiene los conteos en un rango de fechas, opcionalmente filtrados por equipo."""
        query = cls.query.filter(
            cls.fecha_conteo.between(fecha_inicio, fecha_fin)
        )
        
        if equipo_id:
            query = query.filter_by(equipo_id=equipo_id)
            
        return query.order_by(cls.fecha_conteo.asc()).all()
    
    def __repr__(self):
        return f'<Conteo {self.id} - Equipo {self.equipo_id} - {self.fecha_conteo}>'
