"""
Módulo para inicializar las extensiones de Flask.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate

# Inicializar extensiones
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
migrate = Migrate()

def init_extensions(app):
    """Inicializa las extensiones con la aplicación Flask."""
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    
    # Configurar SQLite en modo WAL para mejor concurrencia
    with app.app_context():
        if app.config.get('SQLALCHEMY_DATABASE_URI', '').startswith('sqlite'):
            from sqlalchemy import event
            @event.listens_for(db.engine, 'connect')
            def set_sqlite_pragma(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                cursor.execute('PRAGMA journal_mode=WAL')
                cursor.execute('PRAGMA synchronous=NORMAL')
                cursor.execute('PRAGMA foreign_keys=ON')
                cursor.close()
