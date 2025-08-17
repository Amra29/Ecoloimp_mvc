"""
Script de inicialización para Ecoloimp.

Este script realiza la configuración inicial del sistema, incluyendo:
1. Creación de la base de datos
2. Aplicación de migraciones
3. Inicialización de permisos
4. Creación de usuarios por defecto
"""
import sys
import os
from pathlib import Path

# Asegurarse de que el directorio raíz del proyecto esté en el path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

def print_header():
    """Muestra el encabezado del script."""
    print("=" * 60)
    print("INICIALIZACIÓN DEL SISTEMA ECOLOIMP".center(60))
    print("=" * 60)
    print("Este script realizará la configuración inicial del sistema.")
    print("Asegúrese de tener configurado correctamente el archivo .env")
    print("=" * 60)

def run_script(script_name):
    """Ejecuta un script de inicialización."""
    script_path = os.path.join("app", "scripts", f"{script_name}.py")
    if not os.path.exists(script_path):
        print(f"Error: No se encontró el script {script_name}.py")
        return False
    
    print(f"\nEjecutando {script_name}...")
    try:
        # Usar exec para ejecutar el script en el mismo proceso
        with open(script_path, 'r', encoding='utf-8') as f:
            code = compile(f.read(), script_path, 'exec')
            exec(code, {'__name__': '__main__'})
        return True
    except Exception as e:
        print(f"Error al ejecutar {script_name}: {str(e)}")
        return False

def main():
    """Función principal del script de inicialización."""
    print_header()
    
    # Verificar si se debe continuar
    respuesta = input("\n¿Desea continuar con la inicialización? (s/n): ").strip().lower()
    if respuesta != 's':
        print("\nInicialización cancelada por el usuario.")
        return
    
    # 1. Inicializar la base de datos y aplicar migraciones
    if not run_script("init_db"):
        print("\nError al inicializar la base de datos. Saliendo...")
        return
    
    # 2. Inicializar permisos
    if not run_script("init_permissions"):
        print("\nError al inicializar los permisos. Saliendo...")
        return
    
    # 3. Inicializar usuarios por defecto
    if not run_script("init_users"):
        print("\nError al crear usuarios por defecto. Saliendo...")
        return
    
    print("\n" + "=" * 60)
    print("INICIALIZACIÓN COMPLETADA EXITOSAMENTE".center(60))
    print("=" * 60)
    print("\nCredenciales de acceso iniciales:")
    print("  Super Administrador:")
    print("    Email: superadmin@ecoloimp.com")
    print("    Contraseña: admin123")
    print("\n  Administrador:")
    print("    Email: admin@ecoloimp.com")
    print("    Contraseña: admin123")
    print("\n  Técnico:")
    print("    Email: tecnico@ecoloimp.com")
    print("    Contraseña: tecnico123")
    print("\nIMPORTANTE: Cambie las contraseñas predeterminadas en su primer inicio de sesión.")
    print("=" * 60)

if __name__ == '__main__':
    main()
