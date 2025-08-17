#!/usr/bin/env python3
"""
Script para limpiar archivos no utilizados del proyecto.
"""
import os
import shutil
from pathlib import Path

# Directorio base del proyecto
BASE_DIR = Path(__file__).parent.absolute()

# Archivos y carpetas a eliminar
FILES_TO_REMOVE = [
    # Archivos de configuración de IDEs
    '.idea',
    '.vscode',
    '*.sublime-workspace',
    '*.sublime-project',
    
    # Archivos de entorno
    'venv',
    '.venv',
    'env',
    'ENV',
    'env.bak',
    'venv.bak',
    
    # Archivos de caché
    '__pycache__',
    '.pytest_cache',
    '.mypy_cache',
    '.coverage',
    'htmlcov',
    
    # Archivos de base de datos
    '*.sqlite',
    '*.sqlite3',
    '*.db',
    'instance',
    
    # Archivos temporales
    '*.swp',
    '*.swo',
    '*~',
    
    # Archivos de configuración local
    '.env',
    'local_settings.py',
    'db.sqlite3',
    'db.sqlite3-journal',
    
    # Archivos del sistema operativo
    '.DS_Store',
    'Thumbs.db',
    
    # Archivos de Jupyter Notebook
    '.ipynb_checkpoints',
]

# Controladores a conservar
CONTROLLERS_TO_KEEP = {
    'auth.py',
    'main.py',
    '__init__.py',
    'conteo_impresiones',  # Nuestro módulo de conteo
}

# Plantillas a conservar
TEMPLATES_TO_KEEP = {
    'base.html',
    'index.html',
    'auth',
    'conteo_impresiones',  # Nuestras plantillas de conteo
}

def remove_path(path):
    """Elimina un archivo o directorio."""
    try:
        if os.path.isfile(path) or os.path.islink(path):
            os.unlink(path)
            print(f"Eliminado archivo: {path}")
        elif os.path.isdir(path):
            shutil.rmtree(path)
            print(f"Eliminado directorio: {path}")
    except Exception as e:
        print(f'Error al eliminar {path}: {e}')

def clean_project():
    """Limpia el proyecto de archivos y directorios no deseados."""
    print("Iniciando limpieza del proyecto...")
    
    # Limpiar controladores no utilizados
    controllers_dir = BASE_DIR / 'app' / 'controllers'
    if controllers_dir.exists():
        for item in controllers_dir.iterdir():
            if item.name not in CONTROLLERS_TO_KEEP and item.name != '__pycache__':
                remove_path(item)
    
    # Limpiar plantillas no utilizadas
    templates_dir = BASE_DIR / 'app' / 'templates'
    if templates_dir.exists():
        for item in templates_dir.iterdir():
            if item.name not in TEMPLATES_TO_KEEP and not item.name.startswith('.'):
                remove_path(item)
    
    # Limpiar archivos según los patrones
    for pattern in FILES_TO_REMOVE:
        for path in BASE_DIR.rglob(pattern):
            if path.is_file() or path.is_dir():
                remove_path(path)
    
    print("\n¡Limpieza completada!")

if __name__ == '__main__':
    clean_project()
