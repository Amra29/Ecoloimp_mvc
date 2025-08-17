"""
Application Factory for the Flask application.

This module provides a factory function that creates and configures the Flask application
with all its extensions, blueprints, error handlers, and other configurations.
"""
import os
import logging
import sys
import time
import warnings
from logging.handlers import RotatingFileHandler
import math
import pytz
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, Callable, Union, List, Tuple

from flask import Flask, jsonify, render_template, request, current_app, g, session, redirect, url_for
from flask.json.provider import DefaultJSONProvider
from flask_login import current_user
from werkzeug.exceptions import HTTPException, default_exceptions
from werkzeug.middleware.proxy_fix import ProxyFix
from markdown import markdown
from markupsafe import Markup

from .extensions import (
    db, login_manager, csrf, migrate, mail, limiter, cache, cors, debug_toolbar
)
from .middleware.security import init_app as init_security
from .utils.config import (
    get_env_variable, get_bool_env, get_int_env, get_list_env, get_path_env,
    ensure_directory_exists, ConfigError
)
from . import cli

# Filter out SQLAlchemy deprecation warnings
warnings.filterwarnings(
    'ignore',
    message='The default value of "max_length" will change from 50 to 255 in version 3.0.0',
    category=UserWarning,
    module='flask_sqlalchemy'
)

# Type aliases
ConfigType = Union[Dict[str, Any], str, None]
ErrorHandler = Callable[[Exception], Union[tuple, str, dict]]


def create_app(config_name: Optional[str] = None) -> Flask:
    """
    Create and configure the Flask application.
    
    This is the application factory function that creates, configures, and returns
    a Flask application instance. It handles all the necessary setup including:
    - Loading configuration from environment variables and config classes
    - Initializing Flask extensions
    - Registering blueprints and routes
    - Setting up error handlers and logging
    - Configuring the application context
    
    Args:
        config_name: The name of the configuration to use. If None, uses the
                    FLASK_ENV environment variable or 'development'.
    
    Returns:
        Flask: The configured Flask application instance.
        
    Raises:
        RuntimeError: If there's an error during application initialization.
    """
    start_time = time.time()
    
    try:
        # Determine configuration
        if config_name is None:
            config_name = os.getenv('FLASK_ENV', 'development')
        
        # Create the Flask application
        app = Flask(
            __name__,
            instance_relative_config=True,
            instance_path=str(Path.cwd() / 'instance')
        )
        
        # Apply configuration
        _configure_app(app, config_name)
        
        # Initialize logging early to capture all messages
        _configure_logging(app)
        
        # Log application startup
        app.logger.info(f'Starting application in {config_name} configuration')
        
        # Initialize security middleware
        init_security(app)
        
        # Initialize extensions
        _init_extensions(app)
        
        # Configure SQLAlchemy events
        _configure_sqlalchemy_events(app)
        
        # Register blueprints and routes
        _register_blueprints(app)
        
        # Register error handlers
        _register_error_handlers(app)
        
        # Register context processors
        _register_context_processors(app)
        
        # Register template filters
        _register_template_filters(app)
        
        # Register shell context
        _register_shell_context(app)
        
        # Register CLI commands
        _register_cli_commands(app)
        
        # Register teardown handlers
        _register_teardown_handlers(app)
        
        # Configure proxy if behind a reverse proxy
        if get_bool_env('USE_PROXY', False):
            app.wsgi_app = ProxyFix(
                app.wsgi_app,
                x_for=1,
                x_proto=1,
                x_host=1,
                x_prefix=1
            )
        
        # Ensure required directories exist
        _ensure_directories_exist(app)
        
        # Log successful initialization
        init_time = time.time() - start_time
        app.logger.info(f'Application initialized in {init_time:.2f} seconds')
        
        return app
        
    except Exception as e:
        # Try to log the error if logging is configured
        try:
            logging.critical('Failed to initialize application', exc_info=True)
        except:
            pass
            
        raise RuntimeError(f'Failed to create application: {str(e)}') from e


def _configure_app(app: Flask, config_name: str) -> None:
    """
    Configure the Flask application.
    
    This function loads configuration from multiple sources in the following order:
    1. Default configuration (hardcoded)
    2. Configuration class based on environment (development, testing, production)
    3. Instance configuration (instance/config.py)
    4. Environment variables (prefixed with FLASK_)
    5. .env file (loaded by python-dotenv)
    
    Args:
        app: The Flask application instance
        config_name: The name of the configuration to use (development, testing, production, etc.)
    """
    # Default configuration (lowest priority)
    app.config.update(
        # Application settings
        APP_NAME=get_env_variable('APP_NAME', 'Servicio Técnico'),
        SECRET_KEY=get_env_variable('SECRET_KEY', os.urandom(24).hex()),
        
        # Database settings
        SQLALCHEMY_DATABASE_URI=get_env_variable(
            'DATABASE_URL',
            f'sqlite:///{Path("instance") / "app.db"}'
        ),
        SQLALCHEMY_TRACK_MODIFICATIONS=get_bool_env('SQLALCHEMY_TRACK_MODIFICATIONS', False),
        SQLALCHEMY_ECHO=get_bool_env('SQLALCHEMY_ECHO', False),
        
        # Session settings
        SESSION_TYPE='filesystem',
        SESSION_COOKIE_NAME=get_env_variable('SESSION_COOKIE_NAME', 'ecoloim_session'),
        SESSION_COOKIE_SECURE=get_bool_env('SESSION_COOKIE_SECURE', False),
        SESSION_COOKIE_HTTPONLY=get_bool_env('SESSION_COOKIE_HTTPONLY', True),
        SESSION_COOKIE_SAMESITE=get_env_variable('SESSION_COOKIE_SAMESITE', 'Lax'),
        PERMANENT_SESSION_LIFETIME=get_int_env('PERMANENT_SESSION_LIFETIME', 8 * 60 * 60),  # 8 hours
        
        # Security settings
        SECURITY_PASSWORD_SALT=get_env_variable('SECURITY_PASSWORD_SALT', 'change-this-in-production'),
        SECURITY_PASSWORD_HASH='bcrypt',
        SECURITY_CONFIRMABLE=get_bool_env('SECURITY_CONFIRMABLE', False),
        SECURITY_RECOVERABLE=get_bool_env('SECURITY_RECOVERABLE', True),
        SECURITY_TRACKABLE=get_bool_env('SECURITY_TRACKABLE', True),
        SECURITY_CHANGEABLE=get_bool_env('SECURITY_CHANGEABLE', True),
        SECURITY_SEND_REGISTER_EMAIL=get_bool_env('SECURITY_SEND_REGISTER_EMAIL', False),
        
        # File uploads
        UPLOAD_FOLDER=get_path_env('UPLOAD_FOLDER', 'instance/uploads'),
        MAX_CONTENT_LENGTH=get_int_env('MAX_CONTENT_LENGTH', 16 * 1024 * 1024),  # 16MB
        ALLOWED_EXTENSIONS={'png', 'jpg', 'jpeg', 'gif', 'pdf'},
        
        # Email settings
        MAIL_SERVER=get_env_variable('MAIL_SERVER', 'smtp.gmail.com'),
        MAIL_PORT=get_int_env('MAIL_PORT', 587),
        MAIL_USE_TLS=get_bool_env('MAIL_USE_TLS', True),
        MAIL_USE_SSL=get_bool_env('MAIL_USE_SSL', False),
        MAIL_USERNAME=get_env_variable('MAIL_USERNAME', ''),
        MAIL_PASSWORD=get_env_variable('MAIL_PASSWORD', ''),
        MAIL_DEFAULT_SENDER=get_env_variable('MAIL_DEFAULT_SENDER', MAIL_USERNAME),
        
        # CORS settings
        CORS_ENABLED=get_bool_env('CORS_ENABLED', False),
        CORS_ORIGINS=get_list_env('CORS_ORIGINS', default=['*']),
        
        # Rate limiting
        RATELIMIT_DEFAULT=get_env_variable('RATELIMIT_DEFAULT', '200 per day, 50 per hour'),
        
        # Feature flags
        FEATURE_MAIL_ENABLED=get_bool_env('FEATURE_MAIL_ENABLED', False),
        FEATURE_REGISTRATION_ENABLED=get_bool_env('FEATURE_REGISTRATION_ENABLED', False),
    )
    
    # Load environment-specific configuration
    try:
        env_config = {
            'development': 'app.config.DevelopmentConfig',
            'testing': 'app.config.TestingConfig',
            'production': 'app.config.ProductionConfig',
            'staging': 'app.config.StagingConfig',
        }.get(config_name.lower())
        
        if env_config:
            app.config.from_object(env_config)
    except ImportError as e:
        app.logger.warning(f'Could not import {env_config}: {e}')
    
    # Load instance config if it exists (overrides all)
    instance_config = Path(app.instance_path) / 'config.py'
    if instance_config.exists():
        app.config.from_pyfile(str(instance_config))
    
    # Load environment variables (highest priority)
    app.config.from_prefixed_env()
    
    # Ensure SECRET_KEY is set
    if not app.config['SECRET_KEY'] or app.config['SECRET_KEY'] == 'dev-secret-key-change-this-in-production':
        app.logger.warning('Using default SECRET_KEY. This is not secure for production!')
    
    # Configure JSON provider for custom types
    class CustomJSONProvider(DefaultJSONProvider):
        def default(self, obj):
            if hasattr(obj, 'to_dict'):
                return obj.to_dict()
            if hasattr(obj, 'isoformat'):  # Handle datetime objects
                return obj.isoformat()
            return super().default(obj)
    
    app.json = CustomJSONProvider(app)
    # Configure directories
    _ensure_directories_exist(app)
    
    # Configure proxy if behind a reverse proxy
    if app.config.get('BEHIND_PROXY', False):
        from werkzeug.middleware.proxy_fix import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)


def _init_extensions(app: Flask) -> None:
    """
    Initialize and configure Flask extensions.
    
    This function initializes all Flask extensions used by the application
    and applies their configurations.
    
    Args:
        app: The Flask application instance
    """
    # Initialize SQLAlchemy
    db.init_app(app)
    
    # Initialize Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'info'
    login_manager.session_protection = 'strong'
    
    # Initialize Flask-Migrate
    migrate.init_app(app, db, render_as_batch=True)
    
    # Initialize Flask-WTF CSRF
    csrf.init_app(app)
    csrf.exempt('api.*')  # Exempt API routes from CSRF
    
    # Initialize Flask-Mail
    mail.init_app(app)
    
    # Initialize Flask-Limiter (only in production)
    if not app.testing and not app.debug:
        limiter.init_app(app)
    
    # Initialize Flask-Caching
    cache_config = {
        'CACHE_TYPE': 'simple',
        'CACHE_DEFAULT_TIMEOUT': 300,
        'CACHE_KEY_PREFIX': 'ecoloim_',
        'CACHE_THRESHOLD': 1000,
    }
    
    # Use Redis in production if available
    if app.config.get('REDIS_URL'):
        cache_config.update({
            'CACHE_TYPE': 'redis',
            'CACHE_REDIS_URL': app.config['REDIS_URL'],
            'CACHE_KEY_PREFIX': 'ecoloim_',
        })
    
    cache.init_app(app, config=cache_config)
    
    # Initialize CORS if enabled
    if app.config.get('CORS_ENABLED', False):
        cors.init_app(
            app,
            resources={r"/*": {"origins": app.config.get('CORS_ORIGINS', '*')}},
            supports_credentials=True
        )
    
    # Initialize Debug Toolbar in development
    if app.debug and not app.testing:
        debug_toolbar.init_app(app)
    
    # Configure SQLAlchemy events
    _configure_sqlalchemy_events(app)


def _register_blueprints(app: Flask) -> None:
    """
    Register Flask blueprints with the application.
    
    This function discovers and registers all blueprints from the application's
    modules. Blueprints should be defined in their respective modules with a 'bp'
    attribute.
    
    Args:
        app: The Flask application instance
    """
    # Import blueprints
    from . import (
        auth, main, admin, api, user, dashboard, reports, settings,
        conteo_impresiones, servicios, clientes, equipos, tickets
    )
    
    # Register blueprints with URL prefixes
    blueprints = [
        # Core
        (main.bp, ''),
        (auth.bp, '/auth'),
        (user.bp, '/user'),
        (dashboard.bp, '/dashboard'),
        
        # Features
        (admin.bp, '/admin'),
        (api.bp, '/api'),
        (reports.bp, '/reports'),
        (settings.bp, '/settings'),
        (conteo_impresiones.bp, '/conteo-impresiones'),
        (servicios.bp, '/servicios'),
        (clientes.bp, '/clientes'),
        (equipos.bp, '/equipos'),
        (tickets.bp, '/tickets'),
    ]
    
    for bp, url_prefix in blueprints:
        try:
            app.register_blueprint(bp, url_prefix=url_prefix)
            app.logger.debug(f'Registered blueprint: {bp.name} at {url_prefix or "/"}')
        except Exception as e:
            app.logger.error(f'Failed to register blueprint {bp.name}: {e}', exc_info=True)
    
    # Register API routes if they exist
    try:
        from .api import register_api_routes
        register_api_routes(app)
        app.logger.debug('API routes registered successfully')
    except ImportError as e:
        app.logger.debug(f'API routes not found: {e}')


def _configure_logging(app: Flask) -> None:
    """
    Configure logging for the application.
    
    This function sets up logging with the following features:
    - Console logging with color in development
    - File logging with rotation in production
    - Email notifications for errors in production
    - Custom log format with timestamps and log levels
    
    Args:
        app: The Flask application instance
    """
    import logging
    from logging.handlers import RotatingFileHandler, SMTPHandler
    import sys
    import os
    
    # Create logs directory if it doesn't exist
    logs_dir = Path('logs')
    logs_dir.mkdir(exist_ok=True)
    
    # Set the log level based on configuration
    log_level = app.config.get('LOG_LEVEL', 'INFO').upper()
    log_level = getattr(logging, log_level, logging.INFO)
    
    # Clear any existing handlers
    for handler in app.logger.handlers[:]:
        app.logger.removeHandler(handler)
    
    # Set the logger to not propagate to the root logger
    app.logger.propagate = False
    
    # Create formatters
    debug_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s [in %(pathname)s:%(lineno)d]'
    )
    
    production_formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )
    
    # Console handler (always enabled)
    if app.debug or app.testing:
        # Use colorlog for colored output in development
        try:
            import colorlog
            handler = colorlog.StreamHandler()
            handler.setFormatter(colorlog.ColoredFormatter(
                '%(log_color)s%(asctime)s %(levelname)-8s %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S',
                log_colors={
                    'DEBUG': 'cyan',
                    'INFO': 'green',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'red,bg_white',
                }
            ))
        except ImportError:
            handler = logging.StreamHandler()
            handler.setFormatter(debug_formatter)
    else:
        handler = logging.StreamHandler()
        handler.setFormatter(production_formatter)
    
    handler.setLevel(log_level)
    app.logger.addHandler(handler)
    
    # File handler (only in production)
    if not app.debug and not app.testing:
        file_handler = RotatingFileHandler(
            logs_dir / 'app.log',
            maxBytes=1024 * 1024 * 10,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(production_formatter)
        file_handler.setLevel(log_level)
        app.logger.addHandler(file_handler)
        
        # Error email handler (only in production)
        if app.config.get('MAIL_SERVER'):
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config.get('MAIL_PORT', 25)),
                fromaddr=app.config.get('MAIL_DEFAULT_SENDER'),
                toaddrs=app.config.get('ADMINS', []),
                subject=f"{app.config['APP_NAME']} Application Error",
                credentials=(
                    app.config.get('MAIL_USERNAME'),
                    app.config.get('MAIL_PASSWORD')
                ) if app.config.get('MAIL_USERNAME') else None,
                secure=() if app.config.get('MAIL_USE_TLS') else None
            )
            mail_handler.setLevel(logging.ERROR)
            mail_handler.setFormatter(production_formatter)
            app.logger.addHandler(mail_handler)
    
    # Set the log level for the app logger
    app.logger.setLevel(log_level)
    
    # Set log level for other loggers
    for logger_name in ['werkzeug', 'sqlalchemy', 'flask']:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.WARNING if not app.debug else logging.INFO)
        
        # Add handlers to other loggers
        for handler in app.logger.handlers:
            logger.addHandler(handler)
    
    # Log the configuration
    app.logger.info('Logging configured')


def _ensure_directories_exist(app: Flask) -> None:
    """
    Ensure that all required directories exist and are writable.
    
    This function creates the following directories if they don't exist:
    - instance/: For instance-specific files (config, database, etc.)
    - uploads/: For file uploads
    - logs/: For log files
    - tmp/: For temporary files
    
    Args:
        app: The Flask application instance
    """
    import os
    from pathlib import Path
    
    # Base directories
    base_dirs = [
        Path(app.instance_path),
        Path('uploads'),
        Path('logs'),
        Path('tmp'),
        Path('static/uploads'),
        Path('static/images'),
        Path('static/files'),
    ]
    
    # Add directories from configuration
    config_dirs = [
        app.config.get('UPLOAD_FOLDER'),
        app.config.get('CACHE_DIR'),
        app.config.get('SESSION_FILE_DIR'),
    ]
    
    # Create all directories
    for dir_path in [*base_dirs, *[Path(d) for d in config_dirs if d]]:
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            # Ensure the directory is writable
            test_file = dir_path / '.test'
            test_file.touch()
            test_file.unlink(missing_ok=True)
            app.logger.debug(f'Verified directory: {dir_path}')
        except OSError as e:
            app.logger.error(f'Failed to create/access directory {dir_path}: {e}')
            if app.debug:
                raise


def _register_context_processors(app: Flask) -> None:
    """
    Register context processors for the application.
    
    Context processors make variables available to all templates.
    
    Args:
        app: The Flask application instance
    """
    from datetime import datetime
    from flask import session, g
    from .models import User, Notification
    
    @app.context_processor
    def inject_now():
        """Inject the current datetime into all templates as 'now'."""
        return {'now': datetime.utcnow()}
    
    @app.context_processor
    def inject_user():
        """Inject the current user into all templates as 'current_user'."""
        if hasattr(g, 'user'):
            return {'current_user': g.user}
        return {}
    
    @app.context_processor
    def inject_config():
        """Inject common configuration into all templates."""
        return {
            'app_name': app.config.get('APP_NAME', 'Servicio Técnico'),
            'app_version': app.config.get('APP_VERSION', '1.0.0'),
            'debug': app.debug,
            'ga_tracking_id': app.config.get('GA_TRACKING_ID'),
        }
    
    @app.context_processor
    def inject_notifications():
        """Inject unread notifications count into all templates."""
        if hasattr(g, 'user') and g.user.is_authenticated:
            count = Notification.query.filter_by(
                user_id=g.user.id,
                is_read=False
            ).count()
            return {'unread_notifications': count}
        return {'unread_notifications': 0}
    
    @app.context_processor
    def inject_form_helpers():
        """Inject form helper functions into all templates."""
        from flask import request
        
        def is_active(endpoint, **kwargs):
            """Check if the current request matches the given endpoint."""
            if request.endpoint == endpoint:
                if not kwargs:
                    return 'active'
                
                # Check if all kwargs match the request's view args
                view_args = request.view_args or {}
                if all(view_args.get(k) == v for k, v in kwargs.items()):
                    return 'active'
            return ''
            
        return {'is_active': is_active}


def _register_template_filters(app: Flask) -> None:
    """
    Register custom template filters.
    
    These filters can be used in templates with the |filter_name syntax.
    
    Args:
        app: The Flask application instance
    """
    from datetime import datetime
    import math
    import pytz
    from markdown import markdown
    from markupsafe import Markup
    
    @app.template_filter('format_datetime')
    def format_datetime_filter(value, format='%Y-%m-%d %H:%M:%S', timezone=None):
        """Format a datetime object to a string."""
        if value is None:
            return ''
            
        if timezone:
            tz = pytz.timezone(timezone)
            if value.tzinfo is None:
                value = pytz.utc.localize(value)
            value = value.astimezone(tz)
            
        return value.strftime(format)
    
    @app.template_filter('time_ago')
    def time_ago_filter(value):
        """Format a datetime as a relative time string (e.g., '2 hours ago')."""
        if value is None:
            return ''
            
        now = datetime.utcnow()
        if value.tzinfo is not None:
            now = pytz.utc.localize(now)
            
        diff = now - value
        
        if diff.days > 365:
            return f"{diff.days // 365} years ago"
        if diff.days > 30:
            return f"{diff.days // 30} months ago"
        if diff.days > 0:
            return f"{diff.days} days ago"
        if diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        if diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        return "just now"
    
    @app.template_filter('format_currency')
    def format_currency_filter(value, currency='$'):
        """Format a number as currency."""
        if value is None:
            return ''
        return f"{currency}{value:,.2f}"
    
    @app.template_filter('markdown')
    def markdown_filter(text):
        """Convert markdown text to HTML."""
        if not text:
            return ''
        return Markup(markdown(text, output_format='html5'))
    
    @app.template_filter('truncate')
    def truncate_filter(text, length=100, end='...'):
        """Truncate text to the specified length."""
        if not text:
            return ''
        if len(text) <= length:
            return text
        return text[:length - len(end)] + end
    
    @app.template_filter('filesize')
    def filesize_filter(size):
        """Format a file size in bytes to a human-readable format."""
        if size is None:
            return '0 B'
            
        size = int(size)
        units = ('B', 'KB', 'MB', 'GB', 'TB')
        
        if size == 0:
            return '0 B'
            
        i = min(len(units) - 1, int(math.floor(math.log(size, 1024))))
        size = round(size / (1024 ** i), 2)
        
        return f"{size} {units[i]}"


def _configure_sqlalchemy_events(app: Flask) -> None:
    """
    Configure SQLAlchemy event listeners.
    
    This function sets up event listeners for SQLAlchemy to handle:
    - Automatic timestamps on models
    - Soft deletes
    - Audit logging
    - Query performance monitoring
    
    Args:
        app: The Flask application instance
    """
    from sqlalchemy import event
    from sqlalchemy.orm import Session
    from datetime import datetime
    from .models import db
    
    # Add timestamp mixin support
    @event.listens_for(Session, 'before_flush')
    def before_flush(session, flush_context, instances):
        """Set created_at and updated_at timestamps on models."""
        for instance in session.new:
            if hasattr(instance, 'created_at') and instance.created_at is None:
                instance.created_at = datetime.utcnow()
            if hasattr(instance, 'updated_at'):
                instance.updated_at = datetime.utcnow()
                
        for instance in session.dirty:
            if hasattr(instance, 'updated_at'):
                instance.updated_at = datetime.utcnow()
    
    # Add soft delete support
    @event.listens_for(Session, 'before_flush')
    def before_flush_soft_delete(session, flush_context, instances):
        """Handle soft deletes by setting deleted_at instead of actual deletion."""
        for instance in session.deleted:
            if hasattr(instance.__class__, 'deleted_at'):
                # Convert the delete to an update
                instance.deleted_at = datetime.utcnow()
                session.expunge(instance)
                session.add(instance)
    
    # Add query logging in development
    if app.config.get('SQLALCHEMY_ECHO'):
        import logging
        logging.basicConfig()
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    
    # Add performance monitoring
    if app.config.get('SQLALCHEMY_RECORD_QUERIES'):
        from sqlalchemy.engine import Engine
        import time
        
        @event.listens_for(Engine, 'before_cursor_execute')
        def before_cursor_execute(conn, cursor, statement, params, context, executemany):
            context._query_start_time = time.time()
            
        @event.listens_for(Engine, 'after_cursor_execute')
        def after_cursor_execute(conn, cursor, statement, params, context, executemany):
            total = time.time() - context._query_start_time
            app.logger.debug(f'SQL Query executed in {total:.4f}s: {statement}')
            
            # Log slow queries
            slow_query_threshold = app.config.get('SLOW_QUERY_THRESHOLD', 1.0)
            if total > slow_query_threshold:
                app.logger.warning(
                    f'Slow query ({total:.2f}s): {statement[:500]}',
                    extra={
                        'query': statement,
                        'params': params,
                        'duration': total,
                        'context': str(context)
                    }
                )


def _register_cli_commands(app: Flask) -> None:
    """
    Register custom CLI commands.
    
    This function registers all CLI commands defined in the cli module.
    
    Args:
        app: The Flask application instance
    """
    # Import CLI commands
    from .cli import init_db, create_admin, create_user, run_worker, run_scheduler, test, seed_db, clear_cache
    
    # Register commands with the application
    app.cli.add_command(init_db)
    app.cli.add_command(create_admin)
    app.cli.add_command(create_user)
    app.cli.add_command(run_worker)
    app.cli.add_command(run_scheduler)
    app.cli.add_command(test)
    app.cli.add_command(seed_db)
    app.cli.add_command(clear_cache)
    
    # Add any additional CLI commands here
    @app.cli.command('routes')
    def list_routes():
        """List all registered routes."""
        output = []
        for rule in app.url_map.iter_rules():
            methods = ','.join(rule.methods)
            line = f"{rule.endpoint}: {rule.rule} [{methods}]"
            output.append(line)
        
        for line in sorted(output):
            print(line)
    
    @app.cli.command('create-superuser')
    @click.argument('email')
    @click.argument('password')
    def create_superuser(email, password):
        """Create a superuser account."""
        from .models import User, Role, db
        from werkzeug.security import generate_password_hash
        
        # Create admin role if it doesn't exist
        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role:
            admin_role = Role(name='admin', description='Administrator')
            db.session.add(admin_role)
            db.session.commit()
        
        # Create user
        user = User(
            email=email,
            password=generate_password_hash(password),
            is_active=True,
            is_admin=True
        )
        
        # Add admin role
        user.roles.append(admin_role)
        
        try:
            db.session.add(user)
            db.session.commit()
            print(f'Superuser {email} created successfully')
        except Exception as e:
            db.session.rollback()
            print(f'Error creating superuser: {e}')
    
    app.logger.info('CLI commands registered')


def _register_teardown_handlers(app: Flask) -> None:
    """
    Register teardown handlers that run after each request.
    
    These handlers are responsible for cleaning up resources after each request.
    
    Args:
        app: The Flask application instance
    """
    from flask import g
    
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        """Remove the database session at the end of the request or when the application shuts down."""
        from .extensions import db
        
        # Remove the SQLAlchemy session
        db.session.remove()
        
        # Close any other database connections
        if hasattr(g, 'db_connection'):
            try:
                g.db_connection.close()
            except Exception as e:
                app.logger.error(f'Error closing database connection: {e}')
    
    @app.teardown_request
    def teardown_request(exception):
        """Teardown function called after each request."""
        # Clean up any request-specific resources
        pass
    
    @app.teardown_appcontext
    def shutdown_redis(exception=None):
        """Close Redis connections when the application context is torn down."""
        if hasattr(g, 'redis'):
            try:
                g.redis.close()
            except Exception as e:
                app.logger.error(f'Error closing Redis connection: {e}')
    
    # Register signal handlers for graceful shutdown
    import signal
    
    def handle_shutdown(signum, frame):
        """Handle shutdown signals gracefully."""
        app.logger.info('Shutting down gracefully...')
        
        # Close database connections
        if hasattr(app, 'db'):
            app.db.engine.dispose()
        
        # Close any other resources
        if hasattr(app, 'redis'):
            try:
                app.redis.close()
            except Exception as e:
                app.logger.error(f'Error closing Redis: {e}')
        
        app.logger.info('Shutdown complete')
        sys.exit(0)
    
    # Register signal handlers
    for sig in (signal.SIGTERM, signal.SIGINT):
        signal.signal(sig, handle_shutdown)
    
    app.logger.debug('Teardown handlers registered')


def _register_shell_context(app: Flask) -> None:
    """
    Register shell context processors.
    
    These objects will be available in the Flask shell.
    
    Args:
        app: The Flask application instance
    """
    from . import models, db
    from .models.user import User
    from .models.role import Role, Permission
    from .models.notification import Notification
    from .models.audit_log import AuditLog
    
    def make_shell_context():
        return {
            'db': db,
            'User': User,
            'Role': Role,
            'Permission': Permission,
            'Notification': Notification,
            'AuditLog': AuditLog,
            # Add other models here
        }
    
    app.shell_context_processor(make_shell_context)


def _register_error_handlers(app: Flask) -> None:
    """
    Register error handlers for the application.
    
    This function registers handlers for common HTTP errors and unhandled exceptions.
    It provides both HTML and JSON responses based on the request's Accept header.
    
    Args:
        app: The Flask application instance
    """
    from werkzeug.exceptions import default_exceptions, HTTPException
    
    def make_json_error(error: Exception) -> tuple:
        """Create a JSON response for an error."""
        if isinstance(error, HTTPException):
            status_code = error.code
            error_name = error.name.lower().replace(' ', '_')
            message = error.description
        else:
            status_code = 500
            error_name = 'internal_server_error'
            message = 'An internal server error occurred.'
        
        # Log server errors
        if status_code >= 500:
            app.logger.error(
                f'HTTP {status_code} Error: {message}',
                exc_info=app.debug and error or None
            )
        
        response = jsonify({
            'error': error_name,
            'message': message,
            'status': status_code,
            'path': request.path,
            'method': request.method,
            'timestamp': time.time()
        })
        response.status_code = status_code
        return response
    
    def make_html_error(error: Exception) -> tuple:
        """Create an HTML response for an error."""
        if isinstance(error, HTTPException):
            status_code = error.code
            error_name = error.name
            message = error.description
        else:
            status_code = 500
            error_name = 'Internal Server Error'
            message = 'An unexpected error occurred.'
        
        # Log server errors
        if status_code >= 500:
            app.logger.error(
                f'HTTP {status_code} Error: {message}',
                exc_info=app.debug and error or None
            )
        
        # Try to render a template for the error
        template_name = f'errors/{status_code}.html'
        try:
            return render_template(
                template_name,
                error=error,
                status_code=status_code,
                error_name=error_name,
                message=message
            ), status_code
        except Exception:
            # Fall back to a simple error page
            return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>{status_code} {error_name}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                    h1 {{ font-size: 50px; }}
                    .error {{ color: #e74c3c; }}
                </style>
            </head>
            <body>
                <h1><span class="error">{status_code}</span> {error_name}</h1>
                <p>{message}</p>
                <p><a href="{url_for('main.index')}">Return to the homepage</a></p>
            </body>
            </html>
            """, status_code
    
    def error_handler(error: Exception) -> tuple:
        """Handle an error and return an appropriate response."""
        # Handle API requests with JSON
        if request.path.startswith('/api/'):
            return make_json_error(error)
            
        # Handle AJAX requests with JSON
        if request.is_json or request.accept_mimetypes.accept_json:
            return make_json_error(error)
            
        # Default to HTML for browser requests
        return make_html_error(error)
    
    # Register handlers for all HTTP exceptions
    for code in default_exceptions:
        app.errorhandler(code)(error_handler)
    
    # Register a catch-all error handler
    @app.errorhandler(Exception)
    def handle_exception(error):
        return error_handler(error)
    
    # Log application startup
    app.logger.info('Servicio Técnico startup')


def _configure_app_context(app):
    """Configures the application context."""
    # Configure Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    login_manager.session_protection = 'strong'
    
    # Register context processors
    from app.utils.context_processors import inject_template_vars
    app.context_processor(inject_template_vars)
    
    # Configure user loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.models import Usuario
        return db.session.get(Usuario, int(user_id))
