"""
WSGI config for servicio-tecnico-mvc project.

This module contains the WSGI application used by Django's development server
and any production WSGI deployments. It should expose a module-level variable
named ``application``. Django's ``runserver`` and ``runfcgi`` commands discover
this application via the ``WSGI_APPLICATION`` setting.
"""
import os
import sys
from pathlib import Path

# Add the project directory to the Python path
project_root = str(Path(__file__).resolve().parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Set the default Django settings module
os.environ.setdefault('FLASK_APP', 'app')
os.environ.setdefault('FLASK_ENV', 'production')

# Create and configure the Flask application
from app import create_app

application = create_app()

# This is used when running the application with a production WSGI server like Gunicorn
if __name__ == "__main__":
    # For development purposes, you can run this file directly
    # to start the development server
    from werkzeug.serving import run_simple
    
    # Run the application using Werkzeug's development server
    run_simple(
        '0.0.0.0',
        5000,
        application,
        use_reloader=True,
        use_debugger=True,
        use_evalex=True
    )
