import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = str(Path(__file__).parent.absolute())
sys.path.insert(0, project_root)

from app import create_app, db
from app.models.models import *

def reset_database():
    # Create the Flask application
    app = create_app()
    
    with app.app_context():
        print("Dropping all tables...")
        db.drop_all()
        print("Creating all tables...")
        db.create_all()
        print("Database reset complete!")

if __name__ == "__main__":
    reset_database()
