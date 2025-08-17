"""
Script para crear todas las tablas de la base de datos.
"""
from app.app_factory import create_app
from app.extensions import db
from app.models.models import *  # Importar todos los modelos

def create_tables():
    """Crea todas las tablas en la base de datos."""
    app = create_app()
    with app.app_context():
        # Eliminar todas las tablas existentes
        db.drop_all()
        # Crear todas las tablas
        db.create_all()
        print("¡Todas las tablas han sido creadas exitosamente!")

if __name__ == '__main__':
    create_tables()
