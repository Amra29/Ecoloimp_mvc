"""
Security utilities for the application.

This module provides security-related utility functions for the application,
including password hashing, token generation, and input validation.
"""
import re
import hmac
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple

from flask import current_app, request, session
from werkzeug.security import generate_password_hash, check_password_hash


def hash_password(password: str) -> str:
    """
    Hash a password using the application's preferred hashing method.
    
    Args:
        password: The plaintext password to hash
        
    Returns:
        The hashed password
    """
    return generate_password_hash(
        password,
        method='pbkdf2:sha256',
        salt_length=16
    )


def verify_password(stored_hash: str, password: str) -> bool:
    """
    Verify a password against a stored hash.
    
    Args:
        stored_hash: The stored password hash
        password: The plaintext password to verify
        
    Returns:
        bool: True if the password matches, False otherwise
    """
    return check_password_hash(stored_hash, password)


def generate_csrf_token() -> str:
    """
    Generate a CSRF token and store it in the session.
    
    Returns:
        The generated CSRF token
    """
    if '_csrf_token' not in session:
        session['_csrf_token'] = secrets.token_urlsafe(32)
    return session['_csrf_token']


def validate_csrf_token(token: str) -> bool:
    """
    Validate a CSRF token.
    
    Args:
        token: The token to validate
        
    Returns:
        bool: True if the token is valid, False otherwise
    """
    if not token or token != session.get('_csrf_token'):
        return False
    return True


def generate_secure_token(length: int = 64) -> str:
    """
    Generate a secure random token.
    
    Args:
        length: Length of the token in bytes (will be base64 encoded)
        
    Returns:
        A URL-safe base64-encoded random string
    """
    return secrets.token_urlsafe(length)


def is_safe_redirect(target: str) -> bool:
    """
    Check if a redirect target is safe.
    
    Args:
        target: The target URL to check
        
    Returns:
        bool: True if the target is safe, False otherwise
    """
    from urllib.parse import urlparse, urljoin
    
    # Check if the URL is relative
    if not target:
        return False
        
    # Parse the target URL
    target_url = urlparse(target)
    
    # Allow relative URLs
    if not target_url.netloc:
        return True
        
    # Check if the target is on the same domain
    host_url = urlparse(request.host_url)
    return (target_url.scheme == host_url.scheme and 
            target_url.netloc == host_url.netloc)


def sanitize_input(input_str: str, max_length: int = 255) -> str:
    """
    Sanitize user input to prevent XSS and other injection attacks.
    
    Args:
        input_str: The input string to sanitize
        max_length: Maximum allowed length of the input
        
    Returns:
        The sanitized string
    """
    if not input_str:
        return ''
        
    # Truncate if too long
    if len(input_str) > max_length:
        input_str = input_str[:max_length]
    
    # Remove null bytes and control characters
    input_str = ''.join(c for c in input_str if ord(c) >= 32 or c in '\t\n\r')
    
    # Replace potentially dangerous characters with HTML entities
    input_str = input_str.replace('&', '&amp;')
    input_str = input_str.replace('<', '&lt;')
    input_str = input_str.replace('>', '&gt;')
    input_str = input_str.replace('"', '&quot;')
    input_str = input_str.replace('\'', '&#x27;')
    
    return input_str


def validate_email(email: str) -> bool:
    """
    Validate an email address.
    
    Args:
        email: The email address to validate
        
    Returns:
        bool: True if the email is valid, False otherwise
    """
    if not email or len(email) > 254:
        return False
        
    # Simple email regex for basic validation
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def generate_password_reset_token(user_id: int, expires_in: int = 3600) -> str:
    """
    Generate a secure password reset token.
    
    Args:
        user_id: The user ID to generate the token for
        expires_in: Token expiration time in seconds (default: 1 hour)
        
    Returns:
        A JWT token for password reset
    """
    from flask_jwt_extended import create_access_token
    
    # Include user ID and expiration in the token
    token_data = {
        'user_id': user_id,
        'purpose': 'password_reset',
        'exp': datetime.utcnow() + timedelta(seconds=expires_in)
    }
    
    return create_access_token(identity=token_data)


def verify_password_reset_token(token: str) -> Optional[int]:
    """
    Verify a password reset token and return the user ID if valid.
    
    Args:
        token: The token to verify
        
    Returns:
        The user ID if the token is valid, None otherwise
    """
    from flask_jwt_extended import decode_token, JWTError
    
    try:
        # Decode the token
        data = decode_token(token)
        
        # Check if the token is for password reset
        if data.get('purpose') != 'password_reset':
            return None
            
        # Return the user ID
        return data.get('user_id')
        
    except (JWTError, KeyError, AttributeError):
        return None


def secure_filename(filename: str) -> str:
    """
    Sanitize a filename to be safe for storage.
    
    Args:
        filename: The original filename
        
    Returns:
        A sanitized version of the filename
    """
    import os
    from werkzeug.utils import secure_filename as werkzeug_secure_filename
    
    # Use werkzeug's secure_filename as a base
    filename = werkzeug_secure_filename(filename)
    
    # Add a random string to prevent guessing file names
    name, ext = os.path.splitext(filename)
    random_str = secrets.token_hex(8)
    
    return f"{name}_{random_str}{ext}"


def check_password_strength(password: str) -> Tuple[bool, str]:
    """
    Check if a password meets the minimum strength requirements.
    
    Args:
        password: The password to check
        
    Returns:
        A tuple of (is_strong, message)
    """
    if len(password) < 12:
        return False, "Password must be at least 12 characters long"
        
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
        
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
        
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
        
    if not re.search(r'[^A-Za-z0-9]', password):
        return False, "Password must contain at least one special character"
        
    # Check for common passwords
    common_passwords = {'password', '123456', 'qwerty', 'letmein', 'welcome', 'admin'}
    if password.lower() in common_passwords:
        return False, "Password is too common"
        
    return True, "Password is strong"
