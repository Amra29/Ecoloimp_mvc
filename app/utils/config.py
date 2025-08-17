"""
Configuration utilities for the application.

This module provides utilities for loading and validating configuration
from environment variables.
"""
import os
import logging
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

class ConfigError(Exception):
    """Raised when there is an error in the configuration."""
    pass

def get_env_variable(name: str, default: Any = None, required: bool = False) -> str:
    """
    Get an environment variable.

    Args:
        name: Name of the environment variable
        default: Default value if the variable is not set
        required: If True, raises ConfigError if the variable is not set

    Returns:
        The value of the environment variable or the default value

    Raises:
        ConfigError: If the variable is required but not set
    """
    value = os.getenv(name, default)
    if required and value is None:
        raise ConfigError(f"Required environment variable {name} is not set")
    return value

def get_bool_env(name: str, default: bool = False) -> bool:
    """
    Get a boolean value from an environment variable.

    Args:
        name: Name of the environment variable
        default: Default value if the variable is not set

    Returns:
        The boolean value of the environment variable
    """
    value = os.getenv(name, '').lower()
    if value in ('true', 't', '1', 'yes', 'y'):
        return True
    elif value in ('false', 'f', '0', 'no', 'n', ''):
        return False
    return default

def get_int_env(name: str, default: int = 0) -> int:
    """
    Get an integer value from an environment variable.

    Args:
        name: Name of the environment variable
        default: Default value if the variable is not set or invalid

    Returns:
        The integer value of the environment variable or the default value
    """
    try:
        return int(os.getenv(name, str(default)))
    except (ValueError, TypeError):
        return default

def get_list_env(name: str, separator: str = ',', default: Optional[List[str]] = None) -> List[str]:
    """
    Get a list of strings from an environment variable.

    Args:
        name: Name of the environment variable
        separator: Separator used to split the string into a list
        default: Default value if the variable is not set

    Returns:
        A list of strings from the environment variable
    """
    if default is None:
        default = []
    value = os.getenv(name, '')
    if not value:
        return default
    return [item.strip() for item in value.split(separator) if item.strip()]

def get_path_env(name: str, default: Optional[str] = None, required: bool = False) -> Path:
    """
    Get a Path object from an environment variable.

    Args:
        name: Name of the environment variable
        default: Default path as a string if the variable is not set
        required: If True, raises ConfigError if the variable is not set

    Returns:
        A Path object for the specified path

    Raises:
        ConfigError: If the variable is required but not set
    """
    path_str = get_env_variable(name, default, required)
    if path_str is None:
        return None
    return Path(path_str).resolve()

def ensure_directory_exists(path: Path) -> Path:
    """
    Ensure that a directory exists, creating it if necessary.

    Args:
        path: Path to the directory

    Returns:
        The path to the directory

    Raises:
        ConfigError: If the directory cannot be created or is not writable
    """
    try:
        path.mkdir(parents=True, exist_ok=True)
        if not os.access(path, os.W_OK):
            raise ConfigError(f"Directory is not writable: {path}")
        return path
    except OSError as e:
        raise ConfigError(f"Failed to create directory {path}: {e}")

def configure_logging() -> None:
    """
    Configure the logging system based on environment variables.
    """
    log_level = get_env_variable('LOG_LEVEL', 'INFO').upper()
    log_format = get_env_variable(
        'LOG_FORMAT',
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    log_file = get_env_variable('LOG_FILE', 'logs/app.log')
    
    # Ensure log directory exists
    log_path = Path(log_file).parent
    ensure_directory_exists(log_path)
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(),
            logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=get_int_env('LOG_MAX_BYTES', 10 * 1024 * 1024),  # 10MB
                backupCount=get_int_env('LOG_BACKUP_COUNT', 10),
                encoding='utf-8'
            )
        ]
    )
    
    # Set log levels for specific loggers
    for logger_name, level in [
        ('sqlalchemy.engine', 'WARNING'),
        ('werkzeug', 'WARNING'),
        ('flask', 'WARNING'),
    ]:
        logging.getLogger(logger_name).setLevel(
            get_env_variable(f'LOG_LEVEL_{logger_name.upper()}', level)
        )

# Configure logging when this module is imported
configure_logging()
