"""
Sistema de migraciones para la base de datos
"""
import sqlite3
import os
from flask import current_app
from app.extensions import db
from sqlalchemy import or_

def get_db_path():
    """Obtiene la ruta de la base de datos"""
    db_uri = current_app.config['SQLALCHEMY_DATABASE_URI']
    if db_uri.startswith('sqlite:///'):
        return db_uri.replace('sqlite:///', '')
    return 'servicio_tecnico.db'

def check_column_exists(table_name, column_name):
    """Verifica si una columna existe en una tabla"""
    try:
        db_path = get_db_path()
        if not os.path.exists(db_path):
            return False

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [column[1] for column in cursor.fetchall()]

        conn.close()
        return column_name in columns
    except Exception as e:
        print(f"Error verificando columna: {e}")
        return False

def check_table_exists(table_name):
    """Verifica si una tabla existe"""
    try:
        db_path = get_db_path()
        if not os.path.exists(db_path):
            return False

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        result = cursor.fetchone()

        conn.close()
        return result is not None
    except Exception as e:
        print(f"Error verificando tabla: {e}")
        return False

def add_column_if_not_exists(table_name, column_name, column_type, default_value=None):
    """Agrega una columna si no existe"""
    try:
        if not check_table_exists(table_name):
            print(f"Tabla {table_name} no existe, se creará con db.create_all()")
            return False

        if not check_column_exists(table_name, column_name):
            db_path = get_db_path()
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            print(f"Agregando columna {column_name} a tabla {table_name}")

            # Construir la consulta ALTER TABLE
            alter_query = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
            if default_value is not None:
                alter_query += f" DEFAULT {default_value}"

            cursor.execute(alter_query)

            # Crear índice si es necesario
            if column_name == 'usuario_id':
                cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_{column_name} ON {table_name}({column_name})")

            conn.commit()
            conn.close()
            print(f"Columna {column_name} agregada exitosamente")
            return True
        else:
            print(f"Columna {column_name} ya existe en tabla {table_name}")
            return False
    except Exception as e:
        print(f"Error agregando columna: {e}")
        return False

def run_migrations():
    """Ejecuta todas las migraciones necesarias"""
    # No imprimir mensaje de inicio para mantener la salida limpia
    
    try:
        # Importar todos los modelos para que SQLAlchemy los registre
        # No necesitamos asignarlos a variables, solo importarlos para el registro
        from app.models.models import db  # Necesario para db.create_all()
        
        # Importar modelos para asegurar que están registrados con SQLAlchemy
        from app.models.models import (
            Usuario, Sucursal, Tecnico, Administrador, Cliente, 
            Solicitud, Servicio, Asignacion, Reporte, Parte, 
            PedidoPieza, Factura, Equipo, Visita, Conteo
        )
        
        # Crear todas las tablas con db.create_all()
        # SQLAlchemy maneja automáticamente las dependencias y el orden de creación
        db.create_all()
        
        # No es necesario verificar manualmente las tablas a menos que haya una razón específica
        # SQLAlchemy se encarga de crearlas si no existen
        

        print("Migraciones completadas exitosamente")
        return True
        
    except Exception as e:
        print(f"Error en migraciones: {e}")
        db.session.rollback()
        return False

def update_tecnico_model():
    """Método obsoleto - Mantenido para compatibilidad"""
    print("Actualización de modelo obsoleta - Usando herencia de SQLAlchemy")
    return True

def associate_existing_tecnicos():
    """Método obsoleto - Los técnicos ahora usan herencia de SQLAlchemy"""
    print("Asociación de técnicos obsoleta - Usando herencia de SQLAlchemy")
    return True
