"""
Módulo para comandos personalizados de Flask CLI.
"""
import click
from flask import current_app
from flask.cli import with_appcontext
from .extensions import db

def init_app(app):
    """Registra los comandos personalizados en la aplicación Flask."""
    app.cli.add_command(init_db_command)
    app.cli.add_command(init_permissions_command)
    app.cli.add_command(reset_db_command)

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Inicializa la base de datos y crea las tablas."""
    try:
        db.create_all()
        click.echo('Base de datos inicializada correctamente.')
    except Exception as e:
        click.echo(f'Error al inicializar la base de datos: {str(e)}', err=True)
        raise

@click.command('init-permissions')
@with_appcontext
def init_permissions_command():
    """Inicializa los permisos del sistema."""
    try:
        # Importar aquí para evitar importación circular
        from app.controllers.auth import init_permisos
        
        # Asegurarse de que las tablas existan
        db.create_all()
        
        # Inicializar permisos
        init_permisos()
        click.echo('Permisos inicializados correctamente.')
    except Exception as e:
        click.echo(f'Error al inicializar los permisos: {str(e)}', err=True)
        raise

@click.command('reset-db')
@with_appcontext
def reset_db_command():
    """Elimina y recrea todas las tablas de la base de datos."""
    if click.confirm('¿Estás seguro de que deseas eliminar todas las tablas de la base de datos? Esto no se puede deshacer.'):
        try:
            db.drop_all()
            db.create_all()
            click.echo('Base de datos reinicializada correctamente.')
        except Exception as e:
            click.echo(f'Error al reinicializar la base de datos: {str(e)}', err=True)
            raise
