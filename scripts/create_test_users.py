"""
Script para crear usuarios de prueba para Ecoloimp con diferentes roles.
"""
import sys
from app import create_app
from app.models.models import Usuario, db

def create_test_users():
    app = create_app()
    with app.app_context():
        # Verificar si ya existen usuarios de prueba
        if Usuario.query.filter_by(email='superadmin@ecoloimp.com').first():
            print("Los usuarios de prueba ya existen.")
            return

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
            print("Usuarios de prueba creados exitosamente:")
            print("1. Super Admin - superadmin@ecoloimp.com / SuperAdmin123!")
            print("2. Administrador - admin@ecoloimp.com / Admin123!")
            print("3. Técnico - tecnico@ecoloimp.com / Tecnico123!")
        except Exception as e:
            db.session.rollback()
            print(f"Error al crear usuarios de prueba: {str(e)}")

if __name__ == '__main__':
    create_test_users()
