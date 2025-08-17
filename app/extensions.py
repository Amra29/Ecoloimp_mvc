"""
Flask extensions module.

This module initializes and configures all Flask extensions used in the application.
"""
import os
import logging
from typing import Optional, Dict, Any, Callable

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from flask_cors import CORS
from flask_debugtoolbar import DebugToolbarExtension

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
migrate = Migrate()
mail = Mail()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
cache = Cache(config={'CACHE_TYPE': 'simple'})
cors = CORS()
debug_toolbar = DebugToolbarExtension()


def init_extensions(app: Flask) -> None:
    """
    Initialize Flask extensions with the application.
    
    Args:
        app: The Flask application instance
    """
    # Initialize SQLAlchemy
    db.init_app(app)
    
    # Initialize Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    login_manager.session_protection = 'strong'
    
    # Initialize CSRF protection
    csrf.init_app(app)
    
    # Initialize Flask-Migrate
    migrate.init_app(app, db, render_as_batch=True)
    
    # Initialize Flask-Mail
    mail.init_app(app)
    
    # Initialize rate limiting (only in production)
    if not app.testing:
        limiter.init_app(app)
    
    # Initialize caching
    cache.init_app(app)
    
    # Initialize CORS if enabled
    if app.config.get('ENABLE_CORS', False):
        cors.init_app(app, resources={
            r"/*": {
                "origins": app.config.get('CORS_ORIGINS', '*'),
                "supports_credentials": True
            }
        })
    
    # Initialize debug toolbar in development
    if app.debug and not app.testing:
        debug_toolbar.init_app(app)
    
    # Configure SQLite for better concurrency
    _configure_sqlite(app)
    
    # Configure logging for SQLAlchemy
    _configure_sqlalchemy_logging(app)


def _configure_sqlite(app: Flask) -> None:
    """Configure SQLite for better concurrency."""
    if not app.config.get('SQLALCHEMY_DATABASE_URI', '').startswith('sqlite'):
        return
    
    from sqlalchemy import event
    
    @event.listens_for(db.engine, 'connect')
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute('PRAGMA journal_mode=WAL')
        cursor.execute('PRAGMA synchronous=NORMAL')
        cursor.execute('PRAGMA foreign_keys=ON')
        cursor.execute('PRAGMA busy_timeout=10000')
        cursor.close()


def _configure_sqlalchemy_logging(app: Flask) -> None:
    """Configure SQLAlchemy logging based on application config."""
    if app.config.get('SQLALCHEMY_ECHO'):
        # Enable SQL query logging
        logging.basicConfig()
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
        
        # Format SQL queries for better readability
        from sqlalchemy.engine import Engine
        from sqlalchemy import event
        
        @event.listens_for(Engine, "before_cursor_execute")
        def before_cursor_execute(conn, cursor, statement, params, context, executemany):
            conn.info.setdefault('query_start_time', []).append(time.time())
            app.logger.debug(f"SQL Query: {statement}")
            if params:
                app.logger.debug(f"Parameters: {params}")
        
        @event.listens_for(Engine, "after_cursor_execute")
        def after_cursor_execute(conn, cursor, statement, params, context, executemany):
            total = time.time() - conn.info['query_start_time'].pop(-1)
            app.logger.debug(f"Query completed in {total:.6f} seconds")


# Import time module for SQLAlchemy logging
import time
