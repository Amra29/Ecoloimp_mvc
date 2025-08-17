"""
Script para inicializar la base de datos y crear las tablas necesarias.
"""
import os
import sys
from app.app_factory import create_app
from app.extensions import db

# Importar todos los modelos para asegurar que estén registrados con SQLAlchemy
from app.models import *

def init_database():
    # Crear la aplicación
    app = create_app()
    
    with app.app_context():
        try:
            # Verificar si las tablas ya existen
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            if existing_tables and 'alembic_version' in existing_tables:
                print("Eliminando tablas existentes...")
                db.drop_all()
            
            # Crear todas las tablas
            print("Creando tablas...")
            db.create_all()
            db.session.commit()  # Asegurarse de que los cambios se guarden
            print("¡Tablas creadas exitosamente!")
            
            # Verificar que las tablas se crearon
            inspector = inspect(db.engine)
            created_tables = inspector.get_table_names()
            print("\nTablas creadas:")
            for table in created_tables:
                print(f"- {table}")
            
            # Crear usuario administrador por defecto si no existe
            from app.models import Usuario, Admin
            admin = Usuario.query.filter_by(email='admin@servicio.com').first()
            if not admin:
                print("\nCreando usuario administrador por defecto...")
                admin = Admin(
                    nombre='Administrador',
                    email='admin@servicio.com',
                    telefono='1234567890',
                    activo=True
                )
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                
                print("\n¡Base de datos inicializada exitosamente!")
                print("\nCredenciales de administrador:")
                print(f"Email: admin@servicio.com")
                print(f"Contraseña: admin123")
            else:
                print("\nEl usuario administrador ya existe en la base de datos.")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"\nError al inicializar la base de datos: {str(e)}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    init_database()
