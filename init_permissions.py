"""
Script para inicializar permisos en la base de datos.
"""
from app.app_factory import create_app
from app.extensions import db
from app.models.models import Permiso, Usuario, Tecnico, Administrador

def init_permissions():
    """Inicializa los permisos en la base de datos."""
    app = create_app()
    
    with app.app_context():
        # Crear permisos básicos si no existen
        permisos = [
            ('ver_conteos', 'Ver conteos de impresiones'),
            ('crear_conteo', 'Crear nuevo conteo de impresiones'),
            ('editar_conteo', 'Editar conteo de impresiones existente'),
            ('eliminar_conteo', 'Eliminar conteo de impresiones'),
            ('ver_equipos', 'Ver equipos registrados'),
            ('gestionar_equipos', 'Gestionar (crear/editar/eliminar) equipos'),
            ('ver_usuarios', 'Ver lista de usuarios'),
            ('gestionar_usuarios', 'Gestionar (crear/editar/eliminar) usuarios'),
            ('ver_reportes', 'Ver reportes y estadísticas'),
            ('gestionar_permisos', 'Gestionar permisos y roles'),
            ('admin_todo', 'Acceso total al sistema (solo administradores)')
        ]
        
        for nombre, descripcion in permisos:
            if not Permiso.query.filter_by(nombre=nombre).first():
                permiso = Permiso(nombre=nombre, descripcion=descripcion)
                db.session.add(permiso)
        
        db.session.commit()
        
        # Crear un usuario administrador si no existe
        if not Usuario.query.filter_by(email='admin@ecoloimp.com').first():
            admin = Administrador(
                nombre='Administrador',
                email='admin@ecoloimp.com',
                telefono='1234567890',
                activo=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Usuario administrador creado con email: admin@ecoloimp.com y contraseña: admin123")
        
        print("¡Permisos inicializados exitosamente!")

if __name__ == '__main__':
    init_permissions()
