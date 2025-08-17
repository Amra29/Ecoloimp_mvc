#!/usr/bin/env python3
"""
Script de configuración inicial para la base de datos de Ecoloimp.
Crea las tablas, roles, permisos y un usuario administrador por defecto.
"""
import os
import sys
from datetime import datetime

# Agregar el directorio raíz al path para poder importar la aplicación
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.models import (
    Usuario, Rol, Permiso, RolPermiso, 
    SuperAdmin, Admin, Tecnico, Cliente, 
    Equipo, Visita, Conteo, Inventario
)

def create_tables():
    """Crea todas las tablas en la base de datos."""
    print("Creando tablas en la base de datos...")
    db.create_all()
    print("Tablas creadas exitosamente.")

def create_initial_roles():
    """Crea los roles iniciales del sistema."""
    print("\nCreando roles iniciales...")
    
    roles = [
        {
            'nombre': 'superadmin',
            'descripcion': 'Super Administrador del sistema con acceso total',
            'nivel': 1000
        },
        {
            'nombre': 'admin',
            'descripcion': 'Administrador con acceso a la gestión del sistema',
            'nivel': 500
        },
        {
            'nombre': 'tecnico',
            'descripcion': 'Técnico con acceso limitado a sus funciones',
            'nivel': 100
        }
    ]
    
    for rol_data in roles:
        if not Rol.query.filter_by(nombre=rol_data['nombre']).first():
            rol = Rol(
                nombre=rol_data['nombre'],
                descripcion=rol_data['descripcion'],
                nivel=rol_data['nivel']
            )
            db.session.add(rol)
    
    db.session.commit()
    print("Roles iniciales creados exitosamente.")

def create_initial_permissions():
    """Crea los permisos iniciales del sistema."""
    print("\nCreando permisos iniciales...")
    
    # Categorías de permisos
    categorias = [
        'sistema', 'usuarios', 'clientes', 'equipos', 'visitas', 
        'conteos', 'reportes', 'inventario', 'configuracion'
    ]
    
    # Permisos del sistema
    permisos = [
        # Sistema
        ('sistema.admin', 'Acceso total al sistema', 'sistema'),
        ('sistema.configurar', 'Configurar parámetros del sistema', 'sistema'),
        ('sistema.backup', 'Realizar copias de seguridad', 'sistema'),
        
        # Usuarios
        ('usuarios.ver', 'Ver lista de usuarios', 'usuarios'),
        ('usuarios.crear', 'Crear nuevos usuarios', 'usuarios'),
        ('usuarios.editar', 'Editar usuarios existentes', 'usuarios'),
        ('usuarios.eliminar', 'Eliminar usuarios', 'usuarios'),
        ('usuarios.roles', 'Gestionar roles de usuario', 'usuarios'),
        
        # Clientes
        ('clientes.ver', 'Ver lista de clientes', 'clientes'),
        ('clientes.crear', 'Crear nuevos clientes', 'clientes'),
        ('clientes.editar', 'Editar clientes existentes', 'clientes'),
        ('clientes.eliminar', 'Eliminar clientes', 'clientes'),
        ('clientes.historial', 'Ver historial de clientes', 'clientes'),
        
        # Equipos
        ('equipos.ver', 'Ver lista de equipos', 'equipos'),
        ('equipos.ver_propios', 'Ver equipos asignados', 'equipos'),
        ('equipos.crear', 'Registrar nuevos equipos', 'equipos'),
        ('equipos.editar', 'Editar equipos existentes', 'equipos'),
        ('equipos.eliminar', 'Eliminar equipos', 'equipos'),
        ('equipos.mantenimiento', 'Gestionar mantenimientos', 'equipos'),
        
        # Visitas
        ('visitas.ver', 'Ver todas las visitas', 'visitas'),
        ('visitas.ver_propias', 'Ver visitas propias', 'visitas'),
        ('visitas.crear', 'Programar visitas', 'visitas'),
        ('visitas.editar', 'Editar visitas', 'visitas'),
        ('visitas.eliminar', 'Eliminar visitas', 'visitas'),
        ('visitas.registrar', 'Registrar visitas realizadas', 'visitas'),
        ('visitas.calendario', 'Ver calendario de visitas', 'visitas'),
        
        # Conteos
        ('conteos.ver', 'Ver todos los conteos', 'conteos'),
        ('conteos.ver_propios', 'Ver conteos propios', 'conteos'),
        ('conteos.crear', 'Registrar nuevos conteos', 'conteos'),
        ('conteos.editar', 'Editar conteos existentes', 'conteos'),
        ('conteos.eliminar', 'Eliminar conteos', 'conteos'),
        ('conteos.estadisticas', 'Ver estadísticas de conteos', 'conteos'),
        
        # Reportes
        ('reportes.ver', 'Ver reportes', 'reportes'),
        ('reportes.generar', 'Generar reportes personalizados', 'reportes'),
        ('reportes.exportar', 'Exportar datos a diferentes formatos', 'reportes'),
        
        # Inventario
        ('inventario.ver', 'Ver inventario', 'inventario'),
        ('inventario.gestionar', 'Gestionar inventario', 'inventario'),
        ('inventario.solicitar', 'Solicitar materiales', 'inventario'),
        ('inventario.aprobar', 'Aprobar solicitudes de materiales', 'inventario'),
        
        # Configuración
        ('configuracion.parametros', 'Configurar parámetros', 'configuracion'),
        ('configuracion.alertas', 'Gestionar alertas', 'configuracion')
    ]
    
    for nombre, descripcion, categoria in permisos:
        if not Permiso.query.filter_by(nombre=nombre).first():
            permiso = Permiso(
                nombre=nombre,
                descripcion=descripcion,
                categoria=categoria
            )
            db.session.add(permiso)
    
    db.session.commit()
    print("Permisos iniciales creados exitosamente.")

def assign_permissions_to_roles():
    """Asigna los permisos a los roles correspondientes."""
    print("\nAsignando permisos a roles...")
    
    # Obtener todos los roles y permisos
    superadmin_role = Rol.query.filter_by(nombre='superadmin').first()
    admin_role = Rol.query.filter_by(nombre='admin').first()
    tecnico_role = Rol.query.filter_by(nombre='tecnico').first()
    
    # Asignar todos los permisos al superadmin
    for permiso in Permiso.query.all():
        if not RolPermiso.query.filter_by(rol_id=superadmin_role.id, permiso_id=permiso.id).first():
            rol_permiso = RolPermiso(rol_id=superadmin_role.id, permiso_id=permiso.id)
            db.session.add(rol_permiso)
    
    # Asignar permisos al admin (todos excepto configuración del sistema)
    admin_permisos = Permiso.query.filter(
        ~Permiso.nombre.startswith('sistema.') | (Permiso.nombre == 'sistema.configurar')
    ).all()
    
    for permiso in admin_permisos:
        if not RolPermiso.query.filter_by(rol_id=admin_role.id, permiso_id=permiso.id).first():
            rol_permiso = RolPermiso(rol_id=admin_role.id, permiso_id=permiso.id)
            db.session.add(rol_permiso)
    
    # Asignar permisos al técnico
    tecnico_permisos = [
        'equipos.ver_propios', 'visitas.ver_propias', 'visitas.registrar',
        'conteos.ver_propios', 'conteos.crear', 'conteos.editar',
        'inventario.ver', 'inventario.solicitar', 'clientes.historial'
    ]
    
    for permiso_nombre in tecnico_permisos:
        permiso = Permiso.query.filter_by(nombre=permiso_nombre).first()
        if permiso and not RolPermiso.query.filter_by(rol_id=tecnico_role.id, permiso_id=permiso.id).first():
            rol_permiso = RolPermiso(rol_id=tecnico_role.id, permiso_id=permiso.id)
            db.session.add(rol_permiso)
    
    db.session.commit()
    print("Permisos asignados a roles exitosamente.")

def create_default_admin():
    """Crea un usuario administrador por defecto."""
    print("\nCreando usuario administrador por defecto...")
    
    email = "admin@ecoloimp.com"
    if not Usuario.query.filter_by(email=email).first():
        # Crear el usuario
        admin = SuperAdmin(
            nombre="Administrador Principal",
            email=email,
            password="admin123",  # Contraseña temporal, se debe cambiar en el primer inicio
            activo=True,
            rol_id=Rol.query.filter_by(nombre='superadmin').first().id,
            fecha_ingreso=datetime.utcnow().date()
        )
        
        db.session.add(admin)
        db.session.commit()
        print(f"Usuario administrador creado con email: {email} y contraseña: admin123")
    else:
        print("El usuario administrador ya existe.")

def main():
    """Función principal."""
    print("Iniciando configuración de la base de datos para Ecoloimp...")
    
    # Configurar la aplicación
    app = create_app()
    
    with app.app_context():
        # Crear tablas
        create_tables()
        
        # Crear roles
        create_initial_roles()
        
        # Crear permisos
        create_initial_permissions()
        
        # Asignar permisos a roles
        assign_permissions_to_roles()
        
        # Crear usuario administrador por defecto
        create_default_admin()
    
    print("\n¡Configuración de la base de datos completada con éxito!")
    print("Puedes iniciar sesión con las credenciales proporcionadas.")

if __name__ == "__main__":
    main()
