"""
Script to refactor the models.py file to remove duplicate code and simplify the permissions system.
"""
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

def read_file(file_path: Path) -> str:
    """Read the content of a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return ""

def write_file(file_path: Path, content: str) -> None:
    """Write content to a file."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Successfully wrote to {file_path}")
    except Exception as e:
        print(f"Error writing to file {file_path}: {e}")

def extract_class_definition(content: str, class_name: str) -> Dict[str, Any]:
    """Extract a class definition from the content."""
    pattern = rf'(class\s+{class_name}\s*\([^:]*\):.*?)(?=^\s*class\s+\w+\s*\(|\Z)'
    match = re.search(pattern, content, re.DOTALL | re.MULTILINE)
    
    if not match:
        return {'content': '', 'start': -1, 'end': -1}
    
    return {
        'content': match.group(1).strip(),
        'start': match.start(),
        'end': match.end()
    }

def find_duplicate_methods(class_content: str) -> List[str]:
    """Find duplicate method definitions in a class."""
    method_pattern = r'def\s+(\w+)\s*\('
    methods = re.findall(method_pattern, class_content)
    
    # Find duplicates
    seen = set()
    duplicates = set()
    
    for method in methods:
        if method in seen:
            duplicates.add(method)
        else:
            seen.add(method)
    
    return list(duplicates)

def simplify_permissions_system(content: str) -> str:
    """Simplify the permissions system by removing duplicate permission checks."""
    # Find and remove duplicate permission checks
    permission_patterns = [
        r'@permission_required\s*\([^)]*\)',
        r'self\.tiene_permiso\s*\([^)]*\)',
        r'current_user\.tiene_permiso\s*\([^)]*\)'
    ]
    
    for pattern in permission_patterns:
        # Find all permission checks
        checks = re.findall(pattern, content, re.MULTILINE)
        unique_checks = list(dict.fromkeys(checks))  # Remove duplicates while preserving order
        
        # Replace duplicates with a single check
        for check in checks[1:]:  # Skip the first one
            content = content.replace(check, f"# Removed duplicate: {check}")
    
    return content

def fix_duplicate_repr(content: str) -> str:
    """Fix duplicate __repr__ methods in the Usuario class."""
    usuario_class = extract_class_definition(content, 'Usuario')
    if not usuario_class['content']:
        return content
    
    # Find all __repr__ methods in the Usuario class
    repr_pattern = r'def\s+__repr__\s*\([^)]*\)\s*:.*?return.*?(?=\n\s+\w|\Z)'
    repr_matches = list(re.finditer(repr_pattern, usuario_class['content'], re.DOTALL))
    
    if len(repr_matches) <= 1:
        return content  # No duplicates found
    
    # Keep only the first __repr__ method
    first_repr = repr_matches[0]
    for match in repr_matches[1:]:
        content = content.replace(match.group(0), f"# Removed duplicate: {match.group(0)}")
    
    return content

def fix_duplicate_return_dict(content: str) -> str:
    """Fix the duplicate 'return dict(permisos_por_categoria)' line."""
    lines = content.split('\n')
    found = False
    
    for i, line in enumerate(lines):
        if 'return dict(permisos_por_categoria)' in line:
            if found:
                lines[i] = f"# {line}  # Removed duplicate"
            found = True
    
    return '\n'.join(lines)

def refactor_models_file(file_path: Path) -> None:
    """Refactor the models.py file to remove duplicate code and simplify the permissions system."""
    print(f"Refactoring {file_path}...")
    
    # Create a backup
    backup_path = file_path.with_suffix('.py.backup')
    content = read_file(file_path)
    write_file(backup_path, content)
    print(f"Created backup at {backup_path}")
    
    # Apply refactoring steps
    content = fix_duplicate_repr(content)
    content = fix_duplicate_return_dict(content)
    content = simplify_permissions_system(content)
    
    # Write the refactored content
    write_file(file_path, content)
    print(f"Successfully refactored {file_path}")

def main():
    project_root = Path(__file__).parent.parent
    models_path = project_root / 'app' / 'models' / 'models.py'
    
    if not models_path.exists():
        print(f"Error: {models_path} does not exist")
        return
    
    refactor_models_file(models_path)
    print("\nRefactoring complete!")
    print("Please review the changes and run tests to ensure everything works as expected.")

if __name__ == '__main__':
    main()
