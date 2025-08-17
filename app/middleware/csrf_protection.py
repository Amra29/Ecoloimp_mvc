"""
CSRF protection middleware for the application.

This module provides CSRF protection for forms and API endpoints.
"""
import hmac
import hashlib
import secrets
from functools import wraps
from flask import request, session, current_app, g, abort, jsonify

class CSRFProtection:
    """CSRF protection middleware."""
    
    def __init__(self, app=None):
        """Initialize the CSRF protection."""
        self.app = app
        self._exempt_views = set()
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the CSRF protection with the Flask app."""
        # Default configuration
        app.config.setdefault('WTF_CSRF_ENABLED', True)
        app.config.setdefault('WTF_CSRF_SECRET_KEY', None)
        app.config.setdefault('WTF_CSRF_TIME_LIMIT', 3600)  # 1 hour
        app.config.setdefault('WTF_CSRF_HEADERS', ['X-CSRFToken', 'X-CSRF-Token'])
        app.config.setdefault('WTF_CSRF_SSL_STRICT', True)
        app.config.setdefault('WTF_CSRF_CHECK_DEFAULT', True)
        
        # Generate a secret key if not provided
        if not app.config['WTF_CSRF_SECRET_KEY']:
            app.config['WTF_CSRF_SECRET_KEY'] = secrets.token_hex(32)
        
        # Register the before request handler
        app.before_request(self._csrf_protect)
        
        # Add CSRF token to the template context
        app.context_processor(self._csrf_context_processor)
    
    def exempt(self, view):
        """Mark a view as exempt from CSRF protection."""
        if isinstance(view, str):
            view_location = view
        else:
            view_location = f"{view.__module__}.{view.__name__}"
        
        self._exempt_views.add(view_location)
        return view
    
    def _csrf_protect(self):
        """Protect a view with CSRF."""
        # Skip if CSRF protection is disabled
        if not current_app.config['WTF_CSRF_ENABLED']:
            return
        
        # Skip for safe methods
        if request.method in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
            return
        
        # Skip for API endpoints that use token authentication
        if hasattr(g, 'user') and g.user and hasattr(g.user, 'is_authenticated') and g.user.is_authenticated:
            auth_header = request.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                return
        
        # Skip exempt views
        if request.endpoint and f"{request.endpoint}" in self._exempt_views:
            return
        
        # Get the token from the form or headers
        token = self._get_csrf_token()
        
        # Verify the token
        if not token or not self._verify_csrf_token(token):
            current_app.logger.warning('CSRF token is missing or invalid')
            if request.is_json:
                return jsonify({'error': 'Invalid CSRF token'}), 403
            abort(403, 'CSRF token is missing or invalid')
    
    def _get_csrf_token(self):
        """Get the CSRF token from the request."""
        # Check form data
        token = request.form.get('csrf_token')
        if token:
            return token
        
        # Check headers
        for header in current_app.config['WTF_CSRF_HEADERS']:
            token = request.headers.get(header)
            if token:
                return token
        
        # Check JSON data
        if request.is_json:
            data = request.get_json(silent=True) or {}
            token = data.get('csrf_token')
            if token:
                return token
        
        return None
    
    def _verify_csrf_token(self, token):
        """Verify a CSRF token."""
        if not token or 'csrf_token' not in session:
            return False
        
        # Get the stored token and timestamp
        stored_token = session.get('csrf_token')
        token_timestamp = session.get('_csrf_token_timestamp', 0)
        
        # Check if the token has expired
        if current_app.config['WTF_CSRF_TIME_LIMIT']:
            from time import time
            if (time() - token_timestamp) > current_app.config['WTF_CSRF_TIME_LIMIT']:
                return False
        
        # Compare the tokens securely
        return hmac.compare_digest(token, stored_token)
    
    def generate_csrf_token(self):
        """Generate a new CSRF token."""
        if '_csrf_token' not in session:
            # Generate a new token
            token = secrets.token_hex(32)
            session['_csrf_token'] = token
            
            # Store the timestamp
            from time import time
            session['_csrf_token_timestamp'] = int(time())
            
            # Sign the token with the secret key
            secret_key = current_app.config['WTF_CSRF_SECRET_KEY']
            signature = hmac.new(
                secret_key.encode('utf-8'),
                token.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            # Store the signed token
            session['_csrf_token'] = f"{token}:{signature}"
        
        return session['_csrf_token'].split(':', 1)[0]
    
    def _csrf_context_processor(self):
        """Add CSRF token to the template context."""
        return {
            'csrf_token': self.generate_csrf_token(),
        }


def csrf_protect(f=None, exempt=False):
    """Decorator to enable CSRF protection for a view."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(*args, **kwargs):
            # Skip CSRF protection for exempt views
            if exempt:
                return view_func(*args, **kwargs)
            
            # Get the CSRF protection instance
            csrf = current_app.extensions.get('csrf')
            if csrf is None:
                csrf = CSRFProtection()
                csrf.init_app(current_app)
            
            # Check CSRF token
            csrf._csrf_protect()
            
            # Call the view function
            return view_func(*args, **kwargs)
        
        # Mark the view as exempt if needed
        if exempt:
            csrf = current_app.extensions.get('csrf')
            if csrf is not None:
                csrf.exempt(wrapped_view)
        
        return wrapped_view
    
    # Handle the case when the decorator is used with or without arguments
    if f is None:
        return decorator
    return decorator(f)
