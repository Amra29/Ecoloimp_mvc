"""
Script to restructure the project into separate frontend and backend directories.
"""
import os
import shutil
from pathlib import Path

def create_directory(path):
    """Create directory if it doesn't exist."""
    path.mkdir(parents=True, exist_ok=True)

def move_files(source, destination, file_patterns):
    """Move files matching patterns from source to destination."""
    source_path = Path(source)
    dest_path = Path(destination)
    
    for pattern in file_patterns:
        for file_path in source_path.glob(pattern):
            if file_path.is_file():
                dest_file = dest_path / file_path.relative_to(source_path)
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(file_path), str(dest_file))
                print(f"Moved: {file_path} -> {dest_file}")

def main():
    # Define paths
    project_root = Path(__file__).parent.parent
    backend_dir = project_root / 'backend'
    frontend_dir = project_root / 'frontend'
    
    print("Starting project restructuring...")
    
    # Create backend directory structure
    backend_app_dir = backend_dir / 'app'
    backend_migrations_dir = backend_dir / 'migrations'
    
    create_directory(backend_dir)
    create_directory(backend_app_dir)
    create_directory(backend_migrations_dir)
    
    # Create frontend directory structure
    frontend_pages_dir = frontend_dir / 'pages'
    frontend_public_dir = frontend_dir / 'public'
    
    create_directory(frontend_dir)
    create_directory(frontend_pages_dir)
    create_directory(frontend_public_dir)
    
    # Move backend files
    backend_patterns = [
        'app/*',
        'migrations/*',
        '*.py',
        'requirements*.txt',
        '.flaskenv',
        '.env*',
        '.gitignore',
        'config.py',
        'wsgi.py'
    ]
    
    # Move frontend files
    frontend_patterns = [
        'pages/*',
        'public/*',
        'components.json',
        'next.config.mjs',
        'package.json',
        'pnpm-lock.yaml',
        'postcss.config.mjs',
        'tailwind.config.ts',
        'tsconfig.json'
    ]
    
    print("\nMoving backend files...")
    move_files(project_root, backend_dir, backend_patterns)
    
    print("\nMoving frontend files...")
    move_files(project_root, frontend_dir, frontend_patterns)
    
    # Create a new .gitignore in the root
    with open(project_root / '.gitignore', 'w') as f:
        f.write("""# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/
env/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Database
*.sqlite
*.db

# Logs
logs/
*.log

# Environment variables
.env

# Frontend
node_modules/
.next/
out/

# System Files
.DS_Store
Thumbs.db
""")
    
    print("\nProject restructuring complete!")
    print("\nNext steps:")
    print("1. Review the new directory structure")
    print("2. Update any hardcoded paths in configuration files")
    print("3. Test the application to ensure everything works as expected")

if __name__ == '__main__':
    main()
