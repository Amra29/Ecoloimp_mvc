"""
Email utilities for the application.

This module provides functions for sending various types of emails,
including account notifications, password resets, and system alerts.
"""
from flask import render_template, current_app, url_for
from flask_mail import Message
from threading import Thread
from datetime import datetime
import logging

def send_async_email(app, msg):
    """Send an email asynchronously."""
    with app.app_context():
        try:
            mail.send(msg)
            logging.info(f'Email sent to {msg.recipients}')
        except Exception as e:
            logging.error(f'Error sending email: {str(e)}')

def send_email(subject, sender, recipients, text_body, html_body, attachments=None, sync=False):
    """Send an email.
    
    Args:
        subject: Email subject
        sender: Email sender
        recipients: List of email recipients
        text_body: Plain text body
        html_body: HTML body
        attachments: List of (filename, content_type, data) tuples
        sync: If True, send synchronously (for testing)
    """
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    
    if attachments:
        for attachment in attachments:
            if len(attachment) == 3:
                filename, content_type, data = attachment
                msg.attach(filename, content_type, data)
            elif len(attachment) == 2:
                filename, data = attachment
                msg.attach(filename, 'application/octet-stream', data)
    
    if sync or current_app.config.get('TESTING'):
        mail.send(msg)
    else:
        Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()

def send_password_reset_email(user, token):
    """Send a password reset email to the user."""
    reset_url = url_for('auth.reset_password', token=token, _external=True)
    
    send_email(
        subject='Reset Your Password',
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[user.email],
        text_body=render_template('email/reset_password.txt', user=user, reset_url=reset_url),
        html_body=render_template('email/reset_password.html', user=user, reset_url=reset_url)
    )

def send_email_verification(user, token):
    """Send an email verification email to the user."""
    verify_url = url_for('auth.verify_email', token=token, _external=True)
    
    send_email(
        subject='Verify Your Email Address',
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[user.email],
        text_body=render_template('email/verify_email.txt', user=user, verify_url=verify_url),
        html_body=render_template('email/verify_email.html', user=user, verify_url=verify_url)
    )

def send_welcome_email(user):
    """Send a welcome email to a new user."""
    send_email(
        subject='Welcome to Our Service',
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[user.email],
        text_body=render_template('email/welcome.txt', user=user),
        html_body=render_template('email/welcome.html', user=user)
    )

def send_account_activity_notification(user, activity_type, ip_address, user_agent):
    """Send a notification about account activity."""
    current_time = datetime.utcnow()
    
    send_email(
        subject=f'New {activity_type} on Your Account',
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[user.email],
        text_body=render_template(
            'email/account_activity.txt',
            user=user,
            activity_type=activity_type,
            time=current_time,
            ip_address=ip_address,
            user_agent=user_agent
        ),
        html_body=render_template(
            'email/account_activity.html',
            user=user,
            activity_type=activity_type,
            time=current_time,
            ip_address=ip_address,
            user_agent=user_agent
        )
    )

def send_contact_form_email(name, email, subject, message):
    """Send a contact form submission email to the site admin."""
    send_email(
        subject=f'Contact Form: {subject}',
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[current_app.config['ADMIN_EMAIL']],
        text_body=render_template(
            'email/contact_form.txt',
            name=name,
            email=email,
            subject=subject,
            message=message
        ),
        html_body=render_template(
            'email/contact_form.html',
            name=name,
            email=email,
            subject=subject,
            message=message
        )
    )

def send_system_alert(subject, message, level='info'):
    """Send a system alert to the admin."""
    if not current_app.config.get('ADMIN_EMAIL'):
        return
    
    subject = f'[{current_app.config["APP_NAME"]}] {subject}'
    
    send_email(
        subject=subject,
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[current_app.config['ADMIN_EMAIL']],
        text_body=render_template(
            'email/system_alert.txt',
            subject=subject,
            message=message,
            level=level,
            timestamp=datetime.utcnow()
        ),
        html_body=render_template(
            'email/system_alert.html',
            subject=subject,
            message=message,
            level=level,
            timestamp=datetime.utcnow()
        )
    )

def send_notification_email(user, subject, message):
    """Send a generic notification email to a user."""
    send_email(
        subject=subject,
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[user.email],
        text_body=render_template(
            'email/notification.txt',
            user=user,
            subject=subject,
            message=message
        ),
        html_body=render_template(
            'email/notification.html',
            user=user,
            subject=subject,
            message=message
        )
    )
