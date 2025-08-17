"""
Security headers middleware for the application.

This module provides middleware for adding security-related HTTP headers
to all responses, protecting against common web vulnerabilities.
"""
from flask import request, current_app
from functools import wraps
import re

class SecurityHeaders:
    """Middleware for adding security headers to responses."""
    
    def __init__(self, app=None):
        """Initialize the security headers middleware."""
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the security headers with the Flask app."""
        # Set default security headers if not configured
        app.config.setdefault('SECURITY_HEADERS', {
            'Content-Security-Policy': "default-src 'self';",
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'SAMEORIGIN',
            'X-XSS-Protection': '1; mode=block',
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Permissions-Policy': 'camera=(), microphone=(), geolocation=()',
        })
        
        # Add HSTS header for HTTPS
        if app.config.get('PREFERRED_URL_SCHEME', 'http') == 'https':
            app.config['SECURITY_HEADERS']['Strict-Transport-Security'] = \
                'max-age=31536000; includeSubDomains; preload'
        
        # Register the after request handler
        app.after_request(self._add_security_headers)
    
    def _add_security_headers(self, response):
        """Add security headers to the response."""
        # Add configured security headers
        for header, value in current_app.config.get('SECURITY_HEADERS', {}).items():
            if header not in response.headers:
                response.headers[header] = value
        
        # Add security headers for API responses
        if request.path.startswith('/api/'):
            self._add_api_security_headers(response)
        
        # Add security headers for HTML responses
        if 'text/html' in response.content_type:
            self._add_html_security_headers(response)
        
        return response
    
    def _add_api_security_headers(self, response):
        """Add security headers specific to API responses."""
        headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'Content-Security-Policy': "default-src 'none'; frame-ancestors 'none'",
            'Cache-Control': 'no-store, no-cache, must-revalidate, max-age=0',
            'Pragma': 'no-cache',
            'Expires': '0',
        }
        
        for header, value in headers.items():
            if header not in response.headers:
                response.headers[header] = value
    
    def _add_html_security_headers(self, response):
        """Add security headers specific to HTML responses."""
        # Add Content Security Policy nonce if not already set
        csp = response.headers.get('Content-Security-Policy', '')
        if "'nonce-" not in csp and 'script-src' in csp:
            nonce = self._generate_nonce()
            csp = re.sub(
                r"script-src ([^;]+)",
                f"script-src \\1 'nonce-{nonce}' 'strict-dynamic'",
                csp
            )
            response.headers['Content-Security-Policy'] = csp
            
            # Add nonce to the template context
            if hasattr(response, 'template_context'):
                response.template_context['csp_nonce'] = nonce
    
    @staticmethod
    def _generate_nonce():
        """Generate a random nonce for CSP."""       
        return secrets.token_urlsafe(16)


def secure_headers(f):
    """Decorator to add security headers to a specific route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = f(*args, **kwargs)
        return SecurityHeaders(current_app)._add_security_headers(response)
    return decorated_function
