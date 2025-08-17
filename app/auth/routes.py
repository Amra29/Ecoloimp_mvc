"""
Authentication and authorization routes.

This module contains all the authentication and authorization related routes,
including login, logout, registration, password reset, and account management.
"""
from flask import (
    Blueprint, render_template, redirect, url_for, flash, request, 
    current_app, session, jsonify
)
from flask_login import (
    login_user, logout_user, login_required, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash

from ..models import db, Usuario
from ..utils.security import (
    hash_password, verify_password, generate_csrf_token,
    validate_csrf_token, generate_secure_token, is_safe_redirect,
    sanitize_input, validate_email, check_password_strength
)

# Create auth blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    # Redirect if already logged in
    if current_user.is_authenticated:
        next_page = request.args.get('next')
        if next_page and is_safe_redirect(next_page):
            return redirect(next_page)
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        # Get form data
        email = sanitize_input(request.form.get('email', ''))
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'
        
        # Validate input
        if not email or not password:
            flash('Email and password are required', 'error')
            return render_template('auth/login.html', email=email), 400
        
        # Find user by email
        user = Usuario.query.filter_by(email=email).first()
        
        # Check if user exists and password is correct
        if not user or not verify_password(user.password_hash, password):
            flash('Invalid email or password', 'error')
            return render_template('auth/login.html', email=email), 401
        
        # Check if account is active
        if not user.activo:
            flash('This account has been deactivated', 'error')
            return render_template('auth/login.html', email=email), 403
        
        # Log the user in
        login_user(user, remember=remember)
        
        # Log the login
        current_app.logger.info(f'User {user.id} logged in successfully')
        
        # Redirect to next page or home
        next_page = request.args.get('next')
        if next_page and is_safe_redirect(next_page):
            return redirect(next_page)
        return redirect(url_for('main.index'))
    
    # GET request - show login form
    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Handle user logout."""
    # Log the logout
    current_app.logger.info(f'User {current_user.id} logged out')
    
    # Log the user out
    logout_user()
    
    # Clear session
    session.clear()
    
    # Redirect to login page
    return redirect(url_for('auth.login'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    # Only allow registration if enabled in config
    if not current_app.config.get('ALLOW_REGISTRATION', False):
        flash('Registration is currently disabled', 'error')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        # Get form data
        email = sanitize_input(request.form.get('email', ''))
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validate input
        if not email or not password or not confirm_password:
            flash('All fields are required', 'error')
            return render_template('auth/register.html', email=email), 400
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('auth/register.html', email=email), 400
        
        if not validate_email(email):
            flash('Please enter a valid email address', 'error')
            return render_template('auth/register.html', email=email), 400
        
        # Check password strength
        is_strong, message = check_password_strength(password)
        if not is_strong:
            flash(f'Password is not strong enough: {message}', 'error')
            return render_template('auth/register.html', email=email), 400
        
        # Check if email is already registered
        if Usuario.query.filter_by(email=email).first():
            flash('Email is already registered', 'error')
            return render_template('auth/register.html', email=email), 409
        
        # Create new user
        try:
            user = Usuario(
                email=email,
                password_hash=hash_password(password),
                nombre=sanitize_input(request.form.get('first_name', '')),
                apellido=sanitize_input(request.form.get('last_name', '')),
                rol='usuario',  # Default role
                activo=True
            )
            
            # Add to database
            db.session.add(user)
            db.session.commit()
            
            # Log the registration
            current_app.logger.info(f'New user registered: {user.id} ({email})')
            
            # Log the user in
            login_user(user)
            
            # Redirect to home
            flash('Registration successful!', 'success')
            return redirect(url_for('main.index'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error during registration: {str(e)}')
            flash('An error occurred during registration. Please try again.', 'error')
            return render_template('auth/register.html', email=email), 500
    
    # GET request - show registration form
    return render_template('auth/register.html')


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Handle password reset request."""
    if request.method == 'POST':
        email = sanitize_input(request.form.get('email', ''))
        
        if not email or not validate_email(email):
            flash('Please enter a valid email address', 'error')
            return render_template('auth/forgot_password.html', email=email), 400
        
        # Find user by email
        user = Usuario.query.filter_by(email=email).first()
        
        if user:
            # Generate password reset token
            from ..utils.security import generate_password_reset_token
            token = generate_password_reset_token(user.id)
            
            # Send password reset email
            from ..utils.email import send_password_reset_email
            try:
                send_password_reset_email(user, token)
                flash('Password reset instructions have been sent to your email', 'info')
            except Exception as e:
                current_app.logger.error(f'Error sending password reset email: {str(e)}')
                flash('An error occurred while sending the password reset email', 'error')
        else:
            # Don't reveal that the email doesn't exist
            current_app.logger.warning(f'Password reset attempt for non-existent email: {email}')
            
        # Always return the same message to prevent email enumeration
        flash('If your email is registered, you will receive password reset instructions', 'info')
        return redirect(url_for('auth.login'))
    
    # GET request - show forgot password form
    return render_template('auth/forgot_password.html')


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Handle password reset with token."""
    # Verify token
    from ..utils.security import verify_password_reset_token
    user_id = verify_password_reset_token(token)
    
    if not user_id:
        flash('Invalid or expired password reset link', 'error')
        return redirect(url_for('auth.forgot_password'))
    
    # Get user
    user = Usuario.query.get(user_id)
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('auth.forgot_password'))
    
    if request.method == 'POST':
        # Get form data
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validate input
        if not password or not confirm_password:
            flash('All fields are required', 'error')
            return render_template('auth/reset_password.html', token=token), 400
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('auth/reset_password.html', token=token), 400
        
        # Check password strength
        is_strong, message = check_password_strength(password)
        if not is_strong:
            flash(f'Password is not strong enough: {message}', 'error')
            return render_template('auth/reset_password.html', token=token), 400
        
        # Update password
        try:
            user.password_hash = hash_password(password)
            db.session.commit()
            
            # Log the password reset
            current_app.logger.info(f'Password reset for user: {user.id}')
            
            # Log the user in
            login_user(user)
            
            # Redirect to home
            flash('Your password has been reset successfully', 'success')
            return redirect(url_for('main.index'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error resetting password: {str(e)}')
            flash('An error occurred while resetting your password', 'error')
            return render_template('auth/reset_password.html', token=token), 500
    
    # GET request - show reset password form
    return render_template('auth/reset_password.html', token=token)


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Handle password change for logged-in users."""
    if request.method == 'POST':
        # Get form data
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validate input
        if not current_password or not new_password or not confirm_password:
            flash('All fields are required', 'error')
            return render_template('auth/change_password.html'), 400
        
        # Verify current password
        if not verify_password(current_user.password_hash, current_password):
            flash('Current password is incorrect', 'error')
            return render_template('auth/change_password.html'), 401
        
        # Check if new password is different
        if current_password == new_password:
            flash('New password must be different from current password', 'error')
            return render_template('auth/change_password.html'), 400
        
        # Check if new passwords match
        if new_password != confirm_password:
            flash('New passwords do not match', 'error')
            return render_template('auth/change_password.html'), 400
        
        # Check password strength
        is_strong, message = check_password_strength(new_password)
        if not is_strong:
            flash(f'New password is not strong enough: {message}', 'error')
            return render_template('auth/change_password.html'), 400
        
        # Update password
        try:
            current_user.password_hash = hash_password(new_password)
            db.session.commit()
            
            # Log the password change
            current_app.logger.info(f'Password changed for user: {current_user.id}')
            
            # Log the user out
            logout_user()
            
            # Redirect to login
            flash('Your password has been changed. Please log in again.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error changing password: {str(e)}')
            flash('An error occurred while changing your password', 'error')
            return render_template('auth/change_password.html'), 500
    
    # GET request - show change password form
    return render_template('auth/change_password.html')


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Handle user profile updates."""
    if request.method == 'POST':
        # Get form data
        first_name = sanitize_input(request.form.get('first_name', ''))
        last_name = sanitize_input(request.form.get('last_name', ''))
        
        # Update user profile
        try:
            current_user.nombre = first_name
            current_user.apellido = last_name
            
            # Save changes
            db.session.commit()
            
            # Log the profile update
            current_app.logger.info(f'Profile updated for user: {current_user.id}')
            
            # Redirect to profile
            flash('Your profile has been updated', 'success')
            return redirect(url_for('auth.profile'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error updating profile: {str(e)}')
            flash('An error occurred while updating your profile', 'error')
    
    # GET request - show profile form
    return render_template('auth/profile.html')
