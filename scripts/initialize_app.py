"""
Consolidated initialization script for the application.
This script replaces multiple duplicate initialization scripts.
"""
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app import create_app, db
from app.models.user import User, Role, Permission
from app.models.other_models import *  # Import other models as needed

def initialize_database():
    """Initialize the database with required tables and initial data."""
    app = create_app()
    with app.app_context():
        # Create all database tables
        db.create_all()
        
        # Initialize roles and permissions if they don't exist
        Role.insert_roles()
        
        # Create admin user if it doesn't exist
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@example.com',
                password='changeme123',  # Should be changed after first login
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print("Created admin user with username 'admin' and password 'changeme123'")

if __name__ == '__main__':
    print("Initializing application...")
    initialize_database()
    print("Initialization complete.")
    print("IMPORTANT: Don't forget to change the default admin password after first login!")
