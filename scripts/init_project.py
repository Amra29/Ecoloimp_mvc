#!/usr/bin/env python3
"""
Project initialization script.

This script sets up the project structure, creates necessary directories,
and initializes the database.
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv(project_root / '.env')

def create_directories():
    """Create necessary directories if they don't exist."""
    directories = [
        project_root / 'instance',
        project_root / 'instance' / 'uploads',
        project_root / 'logs',
        project_root / 'migrations',
        project_root / 'frontend' / 'static',
        project_root / 'frontend' / 'templates',
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {directory}")

def init_database():
    """Initialize the database."""
    from app import create_app
    from app.extensions import db
    
    app = create_app()
    
    with app.app_context():
        # Create database tables
        db.create_all()
        print("Database tables created.")
        
        # Run database migrations
        try:
            result = subprocess.run(
                ['flask', 'db', 'upgrade'],
                capture_output=True,
                text=True,
                cwd=project_root
            )
            if result.returncode == 0:
                print("Database migrations applied successfully.")
            else:
                print(f"Error applying migrations: {result.stderr}")
        except Exception as e:
            print(f"Error running migrations: {e}")

def install_dependencies():
    """Install Python dependencies."""
    print("Installing Python dependencies...")
    requirements_file = project_root / 'requirements.txt'
    
    try:
        subprocess.check_call(
            [sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)]
        )
        print("Dependencies installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        sys.exit(1)

def setup_environment():
    """Set up the development environment."""
    # Create .env file if it doesn't exist
    env_file = project_root / '.env'
    if not env_file.exists():
        shutil.copy(project_root / '.env.example', env_file)
        print("Created .env file from .env.example")
    else:
        print(".env file already exists, skipping creation.")

def main():
    """Main function to run the initialization process."""
    print("Starting project initialization...\n")
    
    # Create necessary directories
    print("\n=== Creating directories ===")
    create_directories()
    
    # Set up environment
    print("\n=== Setting up environment ===")
    setup_environment()
    
    # Install dependencies
    print("\n=== Installing dependencies ===")
    install_dependencies()
    
    # Initialize database
    print("\n=== Initializing database ===")
    init_database()
    
    print("\nProject initialization completed successfully!")
    print("\nNext steps:")
    print("1. Review the .env file and update configuration as needed")
    print("2. Run the development server with 'flask run'")
    print("3. Access the application at http://localhost:5000")

if __name__ == "__main__":
    main()
