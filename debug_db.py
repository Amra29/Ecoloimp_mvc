"""
Script para depuración de la base de datos.
"""
import os
import sys
from app.app_factory import create_app
from app.extensions import db

def debug_database():
    # Crear la aplicación
    app = create_app()
    
    with app.app_context():
        try:
            # Obtener la URL de la base de datos
            db_uri = app.config.get('SQLALCHEMY_DATABASE_URI')
            print(f"\n[INFO] Usando base de datos: {db_uri}")
            
            # Verificar si el archivo de base de datos existe
            if db_uri.startswith('sqlite'):
                db_path = db_uri.replace('sqlite:///', '')
                db_exists = os.path.exists(db_path)
                print(f"[INFO] Archivo de base de datos existe: {db_exists}")
                if db_exists:
                    print(f"[INFO] Tamaño del archivo: {os.path.getsize(db_path)} bytes")
            
            # Listar todas las tablas existentes usando el Inspector
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            print("\n[INFO] Tablas existentes en la base de datos:")
            tables = inspector.get_table_names()
            for table in tables:
                print(f"  - {table}")
            
            # Verificar si hay migraciones pendientes
            print("\n[INFO] Verificando migraciones pendientes...")
            from flask_migrate import upgrade, migrate
            migrate()
            
            # Intentar crear las tablas directamente
            print("\n[INFO] Intentando crear tablas...")
            db.create_all()
            
            # Volver a listar las tablas después de create_all
            print("\n[INFO] Tablas después de db.create_all():")
            inspector = inspect(db.engine)
            tables_after = inspector.get_table_names()
            for table in tables_after:
                print(f"  - {table}")
            
            # Verificar si las tablas de los modelos existen
            from app.models.models import Usuario, Admin, Cliente, Tecnico, SuperAdmin, Sucursal, \
                                        Servicio, Equipo, Conteo, Visita, Permiso, RolPermiso, \
                                        Solicitud, Asignacion, Reporte, Parte, PedidoPieza, Factura
            
            print("\n[INFO] Verificando tablas de modelos:")
            models = [Usuario, Admin, Cliente, Tecnico, SuperAdmin, Sucursal, 
                     Servicio, Equipo, Conteo, Visita, Permiso, RolPermiso,
                     Solicitud, Asignacion, Reporte, Parte, PedidoPieza, Factura]
            
            for model in models:
                table_name = model.__tablename__
                exists = db.engine.dialect.has_table(db.engine.connect(), table_name)
                print(f"  - {table_name}: {'EXISTE' if exists else 'NO EXISTE'}")
            
            return True
            
        except Exception as e:
            print(f"\n[ERROR] Error durante la depuración de la base de datos: {str(e)}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    print("=== Depuración de Base de Datos ===")
    if debug_database():
        print("\n[COMPLETADO] Depuración finalizada con éxito.")
    else:
        print("\n[ERROR] Ocurrió un error durante la depuración.")
        sys.exit(1)
