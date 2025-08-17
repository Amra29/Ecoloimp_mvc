"""
Security middleware for the application.

This module provides security-related middleware for the Flask application,
including security headers, rate limiting, and other security measures.
"""
import time
from functools import wraps
from flask import request, g, current_app, jsonify
from werkzeug.exceptions import TooManyRequests


def setup_security_headers(app):
    """Set up security headers for all responses."""
    @app.after_request
    def set_security_headers(response):
        # Skip if already processed by production config
        if hasattr(app, 'security_headers_processed'):
            return response
            
        # Add security headers from config
        for header, value in app.config.get('SECURITY_HEADERS', {}).items():
            if header.lower() not in response.headers:
                response.headers[header] = value
                
        # Add HSTS header for HTTPS
        if request.is_secure:
            response.headers.setdefault(
                'Strict-Transport-Security',
                'max-age=31536000; includeSubDomains; preload'
            )
            
        # Add X-Request-ID if not present
        if 'X-Request-ID' not in response.headers:
            request_id = request.headers.get('X-Request-ID') or str(uuid.uuid4())
            response.headers['X-Request-ID'] = request_id
            
        return response


def rate_limit(limit, per_second=1, key_func=None, scope_func=None):
    ""
    Rate limiting decorator for Flask routes.
    
    Args:
        limit: Maximum number of requests allowed
        per_second: Time window in seconds
        key_func: Function to get the key for rate limiting (defaults to remote IP)
        scope_func: Function to get the scope for rate limiting (e.g., per user or per IP)
    """
    def decorator(f):
        # Use rate limit store from app context
        @wraps(f)
        def wrapped(*args, **kwargs):
            # Initialize rate limit store if not exists
            if not hasattr(g, '_rate_limit_store'):
                g._rate_limit_store = {}
                g._rate_limit_timestamps = {}
            
            # Get the key for rate limiting
            key = key_func() if key_func else request.remote_addr
            scope = scope_func() if scope_func else 'global'
            
            # Get current timestamp
            current_time = time.time()
            
            # Initialize rate limit data for this key and scope
            store_key = f"{scope}:{key}"
            if store_key not in g._rate_limit_store:
                g._rate_limit_store[store_key] = 0
                g._rate_limit_timestamps[store_key] = current_time
            
            # Check rate limit
            if g._rate_limit_store[store_key] >= limit:
                # Check if time window has passed
                if current_time - g._rate_limit_timestamps[store_key] >= per_second:
                    # Reset counter
                    g._rate_limit_store[store_key] = 0
                    g._rate_limit_timestamps[store_key] = current_time
                else:
                    # Rate limit exceeded
                    retry_after = int(per_second - (current_time - g._rate_limit_timestamps[store_key]))
                    response = jsonify({
                        'error': 'rate_limit_exceeded',
                        'message': 'Too many requests. Please try again later.',
                        'retry_after': retry_after
                    })
                    response.status_code = 429
                    response.headers['Retry-After'] = str(retry_after)
                    return response
            
            # Increment counter
            g._rate_limit_store[store_key] += 1
            
            # Call the actual route handler
            return f(*args, **kwargs)
        return wrapped
    return decorator


def csrf_protect(f):
    """
    CSRF protection decorator for non-API routes.
    
    This should be used for any form submission routes that don't use Flask-WTF forms.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            csrf_token = request.headers.get('X-CSRFToken') or request.form.get('csrf_token')
            if not csrf_token or csrf_token != session.get('_csrf_token'):
                if request.is_json:
                    return jsonify({'error': 'Invalid CSRF token'}), 403
                return 'Invalid CSRF token', 403
        return f(*args, **kwargs)
    return decorated_function


def secure_headers(response):
    """
    Add security headers to the response.
    
    This is a more flexible alternative to the after_request approach.
    """
    headers = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'SAMEORIGIN',
        'X-XSS-Protection': '1; mode=block',
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Permissions-Policy': 'camera=(), microphone=(), geolocation=()',
    }
    
    # Only add HSTS for HTTPS
    if request.is_secure:
        headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
    
    # Add headers to response
    for key, value in headers.items():
        response.headers.setdefault(key, value)
    
    return response


def init_app(app):
    """Initialize security middleware with the Flask application."""
    # Set up security headers
    app.after_request(setup_security_headers(app))
    
    # Add security headers to all responses
    app.after_request(secure_headers)
    
    # Add rate limiting to all API endpoints by default
    if app.config.get('ENABLE_RATE_LIMITING', True):
        @app.before_request
        def check_rate_limit():
            # Skip rate limiting for certain paths
            if request.path.startswith('/static/') or request.path == '/health' or request.path == '/favicon.ico':
                return
                
            # Apply rate limiting to API endpoints
            if request.path.startswith('/api/'):
                limit = app.config.get('RATE_LIMIT', '200 per day;50 per hour;10 per minute')
                try:
                    # Parse the rate limit string (e.g., '100 per day')
                    limit_parts = limit.split()
                    if len(limit_parts) >= 3 and limit_parts[1] == 'per':
                        max_requests = int(limit_parts[0])
                        time_window = limit_parts[2]
                        
                        # Convert time window to seconds
                        seconds_per_unit = {
                            'second': 1,
                            'minute': 60,
                            'hour': 3600,
                            'day': 86400,
                        }.get(time_window, 1)
                        
                        # Apply rate limiting
                        @rate_limit(max_requests, seconds_per_unit)
                        def rate_limited_route():
                            pass
                            
                        return rate_limited_route()
                except Exception as e:
                    app.logger.error(f'Error applying rate limit: {e}')
    
    # Add security middleware to the app
    app.extensions['security'] = {
        'rate_limit': rate_limit,
        'csrf_protect': csrf_protect,
    }
