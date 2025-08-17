import os
import secrets
import uuid
from datetime import timedelta
from typing import Dict, Any


class Config:
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    
    # Session Security
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    SESSION_REFRESH_EACH_REQUEST = True
    
    # CSRF Protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hour
    WTF_CSRF_SSL_STRICT = True
    
    # Rate Limiting
    RATELIMIT_DEFAULT = '200 per day;50 per hour;10 per minute'
    RATELIMIT_STRATEGY = 'fixed-window-elastic-expiry'
    
    # Password hashing
    BCRYPT_LOG_ROUNDS = 12
    BCRYPT_HANDLE_LONG_PASSWORDS = True
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or secrets.token_hex(32)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_CSRF_IN_COOKIES = True
    JWT_TOKEN_LOCATION = ['headers', 'cookies']
    
    # Database configuration
    basedir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(basedir, 'instance', 'servicio_tecnico.db')
    
    # Use PostgreSQL in production if DATABASE_URL is set, otherwise use SQLite
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'sqlite:///{db_path}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Database engine options
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_timeout': 30,
        'pool_size': 20,
        'max_overflow': 10,
    }
    
    # SQLite specific settings (only used if using SQLite)
    if SQLALCHEMY_DATABASE_URI.startswith('sqlite'):
        SQLALCHEMY_ENGINE_OPTIONS.update({
            'connect_args': {
                'timeout': 30,
                'check_same_thread': False
            }
        })

    # Pagination
    POSTS_PER_PAGE = 10
    
    # File uploads
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}
    
    # Logging configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_FILE = os.path.join(basedir, 'logs', 'app.log')
    
    # Email configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@example.com')
    
    # Security headers
    SECURITY_HEADERS = {
        # Content Security Policy
        'Content-Security-Policy': "; ".join([
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net",
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
            "img-src 'self' data: https: http:",
            "font-src 'self' https://fonts.gstatic.com data:",
            "connect-src 'self' https://api.example.com",
            "frame-ancestors 'self'",
            "form-action 'self'",
            "base-uri 'self'"
        ]),
        # Prevent MIME type sniffing
        'X-Content-Type-Options': 'nosniff',
        # Prevent clickjacking
        'X-Frame-Options': 'SAMEORIGIN',
        # Enable XSS protection
        'X-XSS-Protection': '1; mode=block',
        # Referrer Policy
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        # HSTS - Strict Transport Security
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
        # Permissions Policy
        'Permissions-Policy': 'camera=(), microphone=(), geolocation=(), payment=()',
        # Cross-Origin Embedder Policy
        'Cross-Origin-Embedder-Policy': 'require-corp',
        # Cross-Origin Opener Policy
        'Cross-Origin-Opener-Policy': 'same-origin',
        # Cross-Origin Resource Policy
        'Cross-Origin-Resource-Policy': 'same-site'
    }
    
    @classmethod
    def init_app(cls, app):
        """Initialize Flask application with this configuration."""
        # Ensure upload directory exists
        os.makedirs(cls.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(os.path.dirname(cls.LOG_FILE), exist_ok=True)


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_ECHO = True
    LOG_LEVEL = 'DEBUG'


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    LOG_LEVEL = 'CRITICAL'  # Suppress logging during tests


class ProductionConfig(Config):
    """Production configuration with enhanced security settings."""
    DEBUG = False
    
    # Session Security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=4)  # Shorter session in production
    
    # Security
    WTF_CSRF_SSL_STRICT = True
    WTF_CSRF_TIME_LIMIT = 1800  # 30 minutes
    
    # Rate Limiting - Stricter in production
    RATELIMIT_DEFAULT = '1000 per day;100 per hour;20 per minute'
    
    # JWT Settings
    JWT_COOKIE_SECURE = True
    JWT_COOKIE_SAMESITE = 'Lax'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)  # Shorter token lifetime
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)    # Shorter refresh token lifetime
    
    # Database
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 3600,
        'pool_timeout': 30,
        'pool_size': 20,
        'max_overflow': 10,
        'pool_use_lifo': True,  # Use LIFO queue for better connection reuse
    }
    
    @classmethod
    def init_app(cls, app):
        """Initialize production-specific configurations."""
        super().init_app(app)
        
        # Log to stderr in production
        import logging
        from logging import StreamHandler
        
        # Configure production logging
        stream_handler = StreamHandler()
        stream_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'
        )
        stream_handler.setFormatter(formatter)
        
        # Remove all handlers and add our production handler
        for handler in app.logger.handlers[:]:
            app.logger.removeHandler(handler)
        app.logger.addHandler(stream_handler)
        app.logger.setLevel(logging.INFO)
        
        # Log application startup
        app.logger.info('Production application startup')
        
        # Add security headers middleware
        cls._add_security_headers(app)
    
    @classmethod
    def _add_security_headers(cls, app):
        """Add security headers to all responses."""
        from flask import g, request, session
        from functools import wraps
        from datetime import datetime
        
        @app.after_request
        def set_security_headers(response):
            # Add security headers
            for header, value in cls.SECURITY_HEADERS.items():
                if header.lower() not in response.headers:
                    response.headers[header] = value
            
            # Add HSTS header with preload directive in production
            if 'strict-transport-security' not in response.headers:
                response.headers['Strict-Transport-Security'] = 'max-age=63072000; includeSubDomains; preload'
            
            # Add server timing header (can be useful for performance monitoring)
            if 'Server-Timing' not in response.headers:
                response.headers['Server-Timing'] = 'total;dur=0.001'
            
            # Add X-Request-ID header if not present
            if 'X-Request-ID' not in response.headers:
                request_id = request.headers.get('X-Request-ID') or str(uuid.uuid4())
                response.headers['X-Request-ID'] = request_id
            
            # Add security headers for API responses
            if request.path.startswith('/api/'):
                response.headers['X-Content-Type-Options'] = 'nosniff'
                response.headers['X-Frame-Options'] = 'DENY'
                response.headers['X-XSS-Protection'] = '1; mode=block'
                response.headers['Referrer-Policy'] = 'no-referrer'
                response.headers['Feature-Policy'] = "geolocation 'none'; microphone 'none'; camera 'none'"
            
            return response


# Configuration dictionary
config: Dict[str, Any] = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
