#!/usr/bin/env python3
"""
Script de inicialización para Ecoloimp.
Crea los roles por defecto (superadmin, admin, técnico) y asigna los permisos correspondientes.
"""
import os
import sys
from datetime import datetime

# Agregar el directorio raíz al path para poder importar la aplicación
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.app_factory import create_app
from app.extensions import db
from app.models.models import Permiso, RolPermiso, Usuario, SuperAdmin, Admin, Tecnico

def init_roles_and_permissions():
    """Inicializa los roles y permisos del sistema."""
    print("Inicializando roles y permisos...")
    
    # Categorías de permisos para mejor organización
    categorias_permisos = {
        'usuarios': 'Gestión de Usuarios',
        'roles': 'Gestión de Roles y Permisos',
        'conteos': 'Conteos de Impresiones',
        'equipos': 'Gestión de Equipos',
        'clientes': 'Gestión de Clientes',
        'visitas': 'Visitas Técnicas',
        'reportes': 'Reportes y Estadísticas',
        'inventario': 'Gestión de Inventario',
        'configuracion': 'Configuración del Sistema',
        'soporte': 'Soporte Técnico'
    }
    
    # Permisos del sistema organizados por categoría
    permisos = [
        # Permisos de administración del sistema
        ('admin_todo', 'Acceso total al sistema', 'configuracion'),
        ('gestionar_usuarios', 'Gestionar usuarios del sistema', 'usuarios'),
        ('gestionar_roles', 'Gestionar roles y permisos', 'roles'),
        ('configurar_sistema', 'Configurar parámetros del sistema', 'configuracion'),
        ('ver_todos_los_datos', 'Ver todos los datos del sistema', 'configuracion'),
        ('exportar_datos', 'Exportar datos del sistema', 'configuracion'),
        ('gestionar_backups', 'Gestionar copias de seguridad', 'configuracion'),
        
        # Permisos de gestión de clientes
        ('gestionar_clientes', 'Gestionar clientes', 'clientes'),
        ('ver_clientes', 'Ver lista de clientes', 'clientes'),
        ('crear_clientes', 'Crear nuevos clientes', 'clientes'),
        ('editar_clientes', 'Editar clientes existentes', 'clientes'),
        ('eliminar_clientes', 'Eliminar clientes', 'clientes'),
        
        # Permisos de gestión de equipos
        ('gestionar_equipos', 'Gestionar equipos', 'equipos'),
        ('ver_equipos', 'Ver lista de equipos', 'equipos'),
        ('crear_equipos', 'Registrar nuevos equipos', 'equipos'),
        ('editar_equipos', 'Editar equipos existentes', 'equipos'),
        ('eliminar_equipos', 'Eliminar equipos', 'equipos'),
        ('ver_equipos_asignados', 'Ver equipos asignados', 'equipos'),
        
        # Permisos de gestión de visitas
        ('gestionar_visitas', 'Gestionar visitas técnicas', 'visitas'),
        ('ver_visitas', 'Ver lista de visitas', 'visitas'),
        ('ver_visitas_propias', 'Ver visitas propias', 'visitas'),
        ('programar_visitas', 'Programar visitas técnicas', 'visitas'),
        ('registrar_visitas', 'Registrar visitas realizadas', 'visitas'),
        ('editar_visitas', 'Editar visitas programadas', 'visitas'),
        ('cancelar_visitas', 'Cancelar visitas', 'visitas'),
        ('actualizar_estado_visita', 'Actualizar estado de visitas', 'visitas'),
        
        # Permisos de conteo de impresiones
        ('gestionar_conteos', 'Gestionar conteos de impresiones', 'conteos'),
        ('ver_conteos', 'Ver todos los conteos', 'conteos'),
        ('ver_conteos_propios', 'Ver conteos propios', 'conteos'),
        ('crear_conteos', 'Registrar nuevos conteos', 'conteos'),
        ('editar_conteos', 'Editar conteos existentes', 'conteos'),
        ('editar_conteos_propios', 'Editar conteos propios', 'conteos'),
        ('eliminar_conteos', 'Eliminar conteos', 'conteos'),
        ('registrar_conteo_impresiones', 'Registrar conteo de impresiones', 'conteos'),
        
        # Permisos de reportes y análisis
        ('ver_reportes', 'Ver reportes del sistema', 'reportes'),
        ('generar_reportes', 'Generar reportes personalizados', 'reportes'),
        ('ver_estadisticas', 'Ver estadísticas', 'reportes'),
        ('ver_historial_cliente', 'Ver historial de cliente', 'reportes'),
        ('generar_informes_visitas', 'Generar informes de visitas', 'reportes'),
        
        # Permisos de gestión de inventario
        ('gestionar_inventario', 'Gestionar inventario', 'inventario'),
        ('ver_inventario', 'Ver inventario', 'inventario'),
        ('solicitar_materiales', 'Solicitar materiales', 'inventario'),
        ('aprobar_solicitudes', 'Aprobar solicitudes de materiales', 'inventario'),
        
        # Permisos de soporte
        ('gestionar_tickets_soporte', 'Gestionar tickets de soporte', 'soporte'),
        ('responder_tickets', 'Responder tickets de soporte', 'soporte'),
        ('ver_tickets_propios', 'Ver tickets propios', 'soporte')
    ]
    
    # Crear permisos si no existen
    permisos_creados = 0
    for nombre, descripcion, categoria in permisos:
        if not Permiso.query.filter_by(nombre=nombre).first():
            permiso = Permiso(
                nombre=nombre, 
                descripcion=descripcion,
                categoria=categoria
            )
            db.session.add(permiso)
            permisos_creados += 1
    
    db.session.commit()
    print(f"Se han creado {permisos_creados} permisos de un total de {len(permisos)}.")
    
    # Asignar permisos a roles
    roles_permisos = {
        # SuperAdmin: Todos los permisos
        'superadmin': [p[0] for p in permisos],
        
        # Admin: Permisos de gestión pero no de administración total
        'admin': [
            'gestionar_usuarios', 'gestionar_clientes', 'gestionar_equipos',
            'gestionar_visitas', 'gestionar_conteos', 'ver_reportes',
            'exportar_datos', 'configurar_parametros', 'gestionar_alertas',
            'ver_clientes', 'ver_equipos', 'crear_equipos', 'editar_equipos',
            'ver_visitas', 'programar_visitas', 'editar_visitas', 'cancelar_visitas',
            'ver_conteos', 'crear_conteos', 'editar_conteos', 'eliminar_conteos',
            'ver_estadisticas', 'ver_historial_cliente', 'generar_informes_visitas',
            'gestionar_inventario', 'ver_inventario', 'solicitar_materiales', 'aprobar_solicitudes',
            'generar_reportes', 'gestionar_tickets_soporte', 'responder_tickets'
        ],
        
        # Técnico: Permisos limitados a sus funciones
        'tecnico': [
            'ver_equipos_asignados', 'ver_visitas_propias', 'registrar_visitas',
            'ver_conteos_propios', 'crear_conteos', 'editar_conteos_propios',
            'registrar_conteo_impresiones', 'solicitar_materiales',
            'actualizar_estado_visita', 'ver_historial_cliente',
            'ver_tickets_propios', 'responder_tickets'
        ]
    }
    
    # Asignar permisos a roles
    total_asignaciones = 0
    for rol, permisos_rol in roles_permisos.items():
        # Eliminar asignaciones existentes para este rol
        RolPermiso.query.filter_by(rol=rol).delete()
        
        # Asignar nuevos permisos
        for nombre_permiso in permisos_rol:
            permiso = Permiso.query.filter_by(nombre=nombre_permiso).first()
            if permiso:
                rol_permiso = RolPermiso(rol=rol, permiso_id=permiso.id)
                db.session.add(rol_permiso)
                total_asignaciones += 1
    
    db.session.commit()
    print(f"Se han asignado {total_asignaciones} permisos a los roles.")

def create_default_admin():
    """Crea un usuario superadmin por defecto si no existe."""
    email = "superadmin@ecoloimp.com"
    if not Usuario.query.filter_by(email=email).first():
        superadmin = SuperAdmin(
            username="superadmin",
            email=email,
            nombre="Super",
            apellido="Administrador",
            activo=True,
            rol="superadmin",
            telefono="+1234567890",
            direccion="Oficina Principal",
            fecha_registro=datetime.utcnow()
        )
        superadmin.set_password("SuperAdmin123!")  # Contraseña temporal
        
        db.session.add(superadmin)
        db.session.commit()
        print(f"\nUsuario superadmin creado con éxito!")
        print(f"Email: {email}")
        print("Contraseña: SuperAdmin123! (cámbiala después del primer inicio de sesión)")
    else:
        print("El usuario superadmin ya existe.")

def create_default_admin_user():
    """Crea un usuario administrador por defecto si no existe."""
    email = "admin@ecoloimp.com"
    if not Usuario.query.filter_by(email=email).first():
        admin = Admin(
            username="admin",
            email=email,
            nombre="Administrador",
            apellido="Sistema",
            activo=True,
            rol="admin",
            telefono="+1234567891",
            direccion="Oficina Administrativa",
            fecha_registro=datetime.utcnow(),
            departamento="Administración"
        )
        admin.set_password("Admin123!")
        
        db.session.add(admin)
        db.session.commit()
        print(f"\nUsuario administrador creado con éxito!")
        print(f"Email: {email}")
        print("Contraseña: Admin123! (cámbiala después del primer inicio de sesión)")
    else:
        print("El usuario administrador ya existe.")

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        try:
            # Crear tablas si no existen
            print("Creando tablas de la base de datos...")
            db.create_all()
            
            # Inicializar roles y permisos
            init_roles_and_permissions()
            
            # Crear usuarios por defecto
            create_default_admin()
            create_default_admin_user()
            
            print("\n¡Configuración inicial de Ecoloimp completada con éxito!")
            print("Puedes iniciar sesión con las credenciales proporcionadas.")
            
        except Exception as e:
            db.session.rollback()
            print(f"\nError durante la inicialización: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
