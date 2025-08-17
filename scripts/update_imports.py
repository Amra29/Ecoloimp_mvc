"""
Script to update imports after project restructuring.
"""
import re
from pathlib import Path

def update_imports_in_file(file_path):
    """Update imports in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Update imports from app.* to backend.app.*
        updated_content = re.sub(
            r'^from\s+app\.',
            'from backend.app.',
            content,
            flags=re.MULTILINE
        )
        
        # Update relative imports if needed
        updated_content = re.sub(
            r'^from\s+\.\.app\.',
            'from backend.app.',
            updated_content,
            flags=re.MULTILINE
        )
        
        # Update imports in the same line
        updated_content = re.sub(
            r'import\s+app\.',
            'import backend.app.',
            updated_content
        )
        
        # Only write if changes were made
        if updated_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            print(f"Updated imports in {file_path}")
            
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")

def main():
    project_root = Path(__file__).parent.parent
    backend_dir = project_root / 'backend'
    
    if not backend_dir.exists():
        print("Backend directory not found. Please run restructure_project.py first.")
        return
    
    print("Updating imports in Python files...")
    
    # Process all Python files in the backend directory
    for py_file in backend_dir.rglob('*.py'):
        update_imports_in_file(py_file)
    
    print("\nImport updates complete!")
    print("\nPlease manually review the following files for any remaining import issues:")
    print("- Flask application factory (app/__init__.py)")
    print("- WSGI entry point (wsgi.py if it exists)")
    print("- Any test files")

if __name__ == '__main__':
    main()
