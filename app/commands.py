"""
Comandos personalizados de Flask para la gestión de la aplicación.
"""
import click
from flask import current_app
from flask.cli import with_appcontext
from app.extensions import db
from app.models.models import Permiso, RolPermiso
from app.controllers.auth import init_permisos


def init_app(app):
    """Registra los comandos personalizados en la aplicación Flask."""
    app.cli.add_command(init_db_command)
    app.cli.add_command(init_permissions_command)


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Inicializa la base de datos y crea las tablas."""
    try:
        db.create_all()
        click.echo('Base de datos inicializada correctamente.')
    except Exception as e:
        click.echo(f'Error al inicializar la base de datos: {str(e)}', err=True)


@click.command('init-permissions')
@with_appcontext
def init_permissions_command():
    """Inicializa los permisos del sistema."""
    try:
        init_permisos()
        click.echo('Permisos inicializados correctamente.')
    except Exception as e:
        click.echo(f'Error al inicializar los permisos: {str(e)}', err=True)


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
