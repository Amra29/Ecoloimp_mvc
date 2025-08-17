"""
Rate limiting middleware for the application.

This module provides rate limiting functionality to protect against
brute force attacks and API abuse.
"""
import time
from functools import wraps
from flask import request, jsonify, g, current_app
from werkzeug.exceptions import TooManyRequests

class RateLimiter:
    """Rate limiter middleware."""
    
    def __init__(self, app=None):
        """Initialize the rate limiter."""
        self.app = app
        self.rate_limit_store = {}
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the rate limiter with the Flask app."""
        # Default rate limiting configuration
        app.config.setdefault('RATELIMIT_DEFAULT', '200 per day;50 per hour')
        app.config.setdefault('RATELIMIT_ENABLED', True)
        app.config.setdefault('RATELIMIT_STORAGE_URL', 'memory://')
        
        # Register the before request handler
        app.before_request(self._check_rate_limit)
        
        # Add rate limit headers to responses
        app.after_request(self._inject_headers)
    
    def _get_identifier(self):
        """Get a unique identifier for the current request."""
        # Try to get the user ID if authenticated
        if hasattr(g, 'user') and g.user and hasattr(g.user, 'id'):
            return f'user:{g.user.id}'
        
        # Fall back to IP address
        return f'ip:{request.remote_addr}'
    
    def _parse_rate_limit_config(self, rate_limit_config):
        """Parse a rate limit configuration string."""
        limits = []
        
        for part in rate_limit_config.split(';'):
            part = part.strip()
            if not part:
                continue
                
            try:
                count, _, period = part.partition(' ')
                count = int(count)
                period = period.lower()
                
                # Convert period to seconds
                if period.startswith('second'):
                    seconds = 1
                elif period.startswith('minute'):
                    seconds = 60
                elif period.startswith('hour'):
                    seconds = 3600
                elif period.startswith('day'):
                    seconds = 86400
                else:
                    current_app.logger.warning(f'Invalid rate limit period: {period}')
                    continue
                
                limits.append((count, seconds))
                
            except (ValueError, AttributeError):
                current_app.logger.warning(f'Invalid rate limit config: {part}')
                continue
        
        return limits
    
    def _check_rate_limit(self):
        """Check if the current request exceeds the rate limit."""
        # Skip rate limiting for certain paths
        if not current_app.config['RATELIMIT_ENABLED']:
            return
            
        # Skip for static files and health checks
        if request.path.startswith('/static/') or request.path == '/health' or request.path == '/favicon.ico':
            return
        
        # Get the rate limit configuration for this endpoint
        rate_limit_config = getattr(request.url_rule, 'rate_limit', None) if request.url_rule else None
        if not rate_limit_config:
            rate_limit_config = current_app.config['RATELIMIT_DEFAULT']
        
        # Parse the rate limit configuration
        limits = self._parse_rate_limit_config(rate_limit_config)
        if not limits:
            return
        
        # Get the identifier for this request
        identifier = self._get_identifier()
        
        # Check each rate limit
        for count, seconds in limits:
            window = int(time.time() // seconds)
            key = f"{identifier}:{window}:{seconds}"
            
            # Initialize or increment the counter
            if key not in self.rate_limit_store:
                self.rate_limit_store[key] = 0
            self.rate_limit_store[key] += 1
            
            # Check if the limit has been exceeded
            if self.rate_limit_store[key] > count:
                raise TooManyRequests(
                    description=f"Rate limit exceeded: {count} requests per {seconds} seconds"
                )
        
        # Clean up old entries (simple garbage collection)
        self._cleanup_old_entries()
    
    def _cleanup_old_entries(self):
        """Clean up old rate limit entries."""
        current_time = time.time()
        keys_to_delete = []
        
        for key in self.rate_limit_store:
            try:
                _, window, seconds = key.rsplit(':', 2)
                window = int(window)
                seconds = int(seconds)
                
                if (current_time // seconds) > window + 1:  # Keep one extra window
                    keys_to_delete.append(key)
                    
            except (ValueError, AttributeError):
                keys_to_delete.append(key)
        
        # Delete old entries
        for key in keys_to_delete:
            self.rate_limit_store.pop(key, None)
    
    def _inject_headers(self, response):
        """Inject rate limit headers into the response."""
        # Skip if rate limiting is disabled
        if not current_app.config['RATELIMIT_ENABLED']:
            return response
        
        # Get the rate limit configuration for this endpoint
        rate_limit_config = getattr(request.url_rule, 'rate_limit', None) if request.url_rule else None
        if not rate_limit_config:
            rate_limit_config = current_app.config['RATELIMIT_DEFAULT']
        
        # Parse the rate limit configuration
        limits = self._parse_rate_limit_config(rate_limit_config)
        if not limits:
            return response
        
        # Find the most restrictive limit
        min_requests = float('inf')
        window_seconds = 0
        
        for count, seconds in limits:
            if count < min_requests:
                min_requests = count
                window_seconds = seconds
        
        # Add rate limit headers
        response.headers['X-RateLimit-Limit'] = str(min_requests)
        response.headers['X-RateLimit-Window'] = f"{window_seconds} seconds"
        
        return response


def rate_limit(rate_limit_config):
    """Decorator to apply rate limiting to a route."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            return f(*args, **kwargs)
        
        # Store the rate limit configuration on the function
        decorated_function.rate_limit = rate_limit_config
        return decorated_function
    return decorator
