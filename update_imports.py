import os
import re

def update_imports_in_file(file_path):
    """Update imports in a single file to use db from extensions."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if the file imports db from app
    if 'from app import db' in content:
        # Replace the import statement
        new_content = content.replace(
            'from app import db',
            'from app.extensions import db'
        )
        
        # Write the updated content back to the file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    
    # Also check for 'from .. import db' pattern
    if re.search(r'from\s+\.+\s+import\s+db', content):
        # Replace the import statement
        new_content = re.sub(
            r'from\s+(\.+)\s+import\s+db',
            'from app.extensions import db',
            content
        )
        
        # Write the updated content back to the file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    
    return False

def update_imports_in_directory(directory):
    """Update imports in all Python files in the given directory."""
    updated_files = []
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if update_imports_in_file(file_path):
                    updated_files.append(file_path)
    
    return updated_files

if __name__ == '__main__':
    # Update imports in all Python files in the controllers directory
    controllers_dir = os.path.join('app', 'controllers')
    updated = update_imports_in_directory(controllers_dir)
    
    if updated:
        print("Updated imports in the following files:")
        for file in updated:
            print(f"- {file}")
    else:
        print("No files were updated.")
    
    # Also update the main app directory
    app_dir = 'app'
    updated = update_imports_in_directory(app_dir)
    
    if updated:
        print("\nUpdated imports in the following files in the app directory:")
        for file in updated:
            print(f"- {file}")
    else:
        print("\nNo files in the app directory were updated.")
