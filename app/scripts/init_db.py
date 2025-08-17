"""
Script para inicializar la base de datos y aplicar migraciones.

Este script crea la base de datos, ejecuta las migraciones y carga datos iniciales.
"""
import os
import sys

# Asegurarse de que el directorio raíz del proyecto esté en el path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

def init_db():
    """Inicializa la base de datos y aplica migraciones."""
    from app import create_app, db
    from flask_migrate import upgrade, migrate, init, stamp
    
    # Crear la aplicación Flask
    app = create_app()
    
    with app.app_context():
        print("Inicializando la base de datos...")
        
        # Crear todas las tablas
        print("Creando tablas...")
        db.create_all()
        
        # Inicializar migraciones si no existen
        migrations_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'migrations')
        if not os.path.exists(migrations_dir):
            print("Inicializando migraciones...")
            init()
        
        # Marcar la base de datos como actualizada con la migración inicial
        print("Aplicando migraciones...")
        stamp()
        migrate(message='Initial migration')
        upgrade()
        
        print("¡Base de datos inicializada exitosamente!")
        return True

if __name__ == '__main__':
    init_db()
