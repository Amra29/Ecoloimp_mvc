"""
Script para ejecutar migraciones de la base de datos usando Flask-Migrate
"""
import os
import sys
from flask import current_app
from flask_migrate import upgrade, migrate, init, stamp
from app import create_app, db
from app.models.models import Usuario, Tecnico  # Importar modelos para que se registren

def run_migrations():
    """Ejecuta las migraciones de la base de datos"""
    print("Iniciando migraciones de la base de datos con Flask-Migrate...")
    
    # Crear la aplicación Flask
    app = create_app()
    
    with app.app_context():
        # Directorio de migraciones
        migrations_dir = os.path.join(os.path.dirname(__file__), 'migrations')
        
        # Si no existe el directorio de migraciones, inicializarlo
        if not os.path.exists(migrations_dir):
            print("Inicializando el directorio de migraciones...")
            try:
                init()
                print("Directorio de migraciones creado exitosamente.")
            except Exception as e:
                print(f"Error al inicializar el directorio de migraciones: {e}")
                return False
        
        # Ejecutar migraciones
        try:
            # Crear una migración inicial si es necesario
            print("Creando migración inicial...")
            migrate(message="Migración inicial")
            
            # Aplicar migraciones pendientes
            print("Aplicando migraciones...")
            upgrade()
            
            # Si hay migraciones personalizadas, ejecutarlas después
            from app.migrations import run_migrations as run_custom_migrations
            run_custom_migrations()
            
            print("Migraciones completadas exitosamente.")
            return True
            
        except Exception as e:
            print(f"Error durante las migraciones: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    run_migrations()
