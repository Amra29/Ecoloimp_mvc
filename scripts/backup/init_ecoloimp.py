def print_header():
    print("=" * 60)
    print("INICIALIZACIÓN DEL SISTEMA ECOLOIMP".center(60))
    print("=" * 60)

def run_script(script_name):
    # Ejecuta el script correspondiente y retorna True si todo OK
    # Aquí deberías implementar la lógica real de ejecución de cada script
    try:
        # Ejemplo: os.system(f"python {script_name}.py")
        print(f"Ejecutando {script_name} ...")
        return True
    except Exception as e:
        print(f"Error en {script_name}: {e}")
        return False

def main():
    print_header()
    respuesta = input("\n¿Desea continuar con la inicialización? (s/n): ").strip().lower()
    if respuesta != 's':
        print("\nInicialización cancelada por el usuario.")
        return

    # Inicializar base de datos y migraciones
    if not run_script("init_db"):
        print("\nError al inicializar la base de datos. Saliendo...")
        return

    # Inicializar permisos
    if not run_script("init_permissions"):
        print("\nError al inicializar los permisos. Saliendo...")
        return

    # Inicializar usuarios por defecto
    if not run_script("init_users"):
        print("\nError al crear usuarios por defecto. Saliendo...")
        return

    print("=" * 60)
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

if __name__ == "__main__":
    main()