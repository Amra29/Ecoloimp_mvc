"""
Script para inicializar los usuarios por defecto del sistema Ecoloimp.

Este script crea los usuarios iniciales del sistema con los roles correspondientes.
"""
import sys
import os
from datetime import datetime

# Asegurarse de que el directorio raíz del proyecto esté en el path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

def init_users():
    """Inicializa los usuarios por defecto del sistema."""
    from app import create_app, db
    from app.models.models import SuperAdmin, Admin, Tecnico
    
    # Crear la aplicación Flask
    app = create_app()
    
    with app.app_context():
        print("Inicializando usuarios por defecto...")
        
        # Contador para estadísticas
        usuarios_creados = 0
        
        # Verificar si ya existe el superadmin
        if not SuperAdmin.query.first():
            # Crear superadmin por defecto
            superadmin = SuperAdmin(
                nombre="Super Administrador",
                email="superadmin@ecoloimp.com",
                telefono="+1234567890",
                activo=True
            )
            superadmin.set_password("admin123")  # Contraseña temporal, debe ser cambiada
            db.session.add(superadmin)
            usuarios_creados += 1
            print("  - Creado superadmin por defecto")
        
        # Verificar si ya existe un admin
        if not Admin.query.first():
            # Crear admin por defecto
            admin = Admin(
                nombre="Administrador Ecoloimp",
                email="admin@ecoloimp.com",
                telefono="+1234567891",
                activo=True,
                departamento="Administración"
            )
            admin.set_password("admin123")  # Contraseña temporal, debe ser cambiada
            db.session.add(admin)
            usuarios_creados += 1
            print("  - Creado administrador por defecto")
        
        # Verificar si ya existe un técnico
        if not Tecnico.query.first():
            # Crear técnico por defecto
            tecnico = Tecnico(
                nombre="Técnico Ejemplo",
                email="tecnico@ecoloimp.com",
                telefono="+1234567892",
                activo=True,
                especialidad="Mantenimiento de impresoras",
                habilidades="Reparación de impresoras láser y de inyección de tinta",
                fecha_ingreso=datetime.utcnow()
            )
            tecnico.set_password("tecnico123")  # Contraseña temporal, debe ser cambiada
            db.session.add(tecnico)
            usuarios_creados += 1
            print("  - Creado técnico de ejemplo")
        
        # Confirmar cambios en la base de datos
        try:
            db.session.commit()
            if usuarios_creados > 0:
                print(f"\n¡Se crearon {usuarios_creados} usuarios por defecto!")
                print("IMPORTANTE: Cambia las contraseñas predeterminadas lo antes posible.")
            else:
                print("\nLos usuarios por defecto ya existen en la base de datos.")
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"\nError al crear usuarios por defecto: {str(e)}")
            return False

if __name__ == '__main__':
    init_users()
