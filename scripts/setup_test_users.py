"""
Script para crear usuarios de prueba con diferentes roles en Ecoloimp.
"""
import os
import sys

# Asegurarse de que el directorio raíz esté en el PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models.models import Usuario, db

def create_test_users():
    # Crear la aplicación con la configuración adecuada
    app = create_app()
    
    with app.app_context():
        # Verificar si ya existen usuarios de prueba
        if Usuario.query.filter(Usuario.email.in_(['superadmin@ecoloimp.com', 'admin@ecoloimp.com', 'tecnico@ecoloimp.com'])).count() > 0:
            print("Los usuarios de prueba ya existen en la base de datos.")
            return

        print("Creando usuarios de prueba...")
        
        # Crear Super Admin
        superadmin = Usuario(
            username='superadmin',
            email='superadmin@ecoloimp.com',
            nombre='Super',
            apellido='Administrador',
            rol='superadmin',
            activo=True
        )
        superadmin.set_password('SuperAdmin123!')
        db.session.add(superadmin)

        # Crear Administrador
        admin = Usuario(
            username='admin',
            email='admin@ecoloimp.com',
            nombre='Admin',
            apellido='Ecoloimp',
            rol='admin',
            activo=True
        )
        admin.set_password('Admin123!')
        db.session.add(admin)

        # Crear Técnico
        tecnico = Usuario(
            username='tecnico',
            email='tecnico@ecoloimp.com',
            nombre='Técnico',
            apellido='Ecoloimp',
            rol='tecnico',
            activo=True
        )
        tecnico.set_password('Tecnico123!')
        db.session.add(tecnico)

        try:
            db.session.commit()
            print("\n¡Usuarios de prueba creados exitosamente!")
            print("\nCredenciales de acceso:")
            print("-" * 50)
            print("1. Super Administrador")
            print(f"   Email: superadmin@ecoloimp.com")
            print(f"   Contraseña: SuperAdmin123!")
            print("   Rol: Super Administrador (acceso total)")
            print("\n2. Administrador")
            print(f"   Email: admin@ecoloimp.com")
            print(f"   Contraseña: Admin123!")
            print("   Rol: Administrador (gestión de usuarios y clientes)")
            print("\n3. Técnico")
            print(f"   Email: tecnico@ecoloimp.com")
            print(f"   Contraseña: Tecnico123!")
            print("   Rol: Técnico (gestión de servicios y asignaciones)")
            print("-" * 50)
            print("\n¡Ahora puedes iniciar sesión con cualquiera de estas cuentas!")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error al crear usuarios de prueba: {str(e)}")
            raise e

if __name__ == '__main__':
    create_test_users()
