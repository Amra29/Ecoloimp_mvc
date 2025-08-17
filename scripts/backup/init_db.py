"""
Script para inicializar la base de datos y crear un usuario administrador.
"""
import os
from app import create_app, db
from app.models.models import Usuario, Administrador, Cliente, Servicio, Parte

def init_db():
    # Crear la aplicación
    app = create_app()
    
    with app.app_context():
        # Eliminar todas las tablas existentes
        print("Eliminando tablas existentes...")
        db.drop_all()
        
        # Crear todas las tablas
        print("Creando tablas...")
        db.create_all()
        
        # Crear usuario administrador
        print("Creando usuario administrador...")
        admin = Administrador(
            nombre='Administrador',
            email='admin@servicio.com',
            telefono='1234567890',
            activo=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Crear algunos datos de prueba
        print("Creando datos de prueba...")
        clientes = [
            Cliente(nombre='Juan Pérez', email='juan@email.com', telefono='3001234567',
                   direccion='Calle 123 #45-67', contacto_principal='Juan Pérez', activo=True),
            Cliente(nombre='Empresa ABC S.A.S.', email='contacto@abc.com', telefono='3012345678',
                   direccion='Carrera 45 #12-34', contacto_principal='Carlos López', activo=True)
        ]
        
        servicios = [
            Servicio(nombre='Mantenimiento Preventivo', descripcion='Mantenimiento preventivo de equipos',
                     precio_base=50000, categoria='Mantenimiento'),
            Servicio(nombre='Reparación de Hardware', descripcion='Reparación de componentes de hardware',
                     precio_base=80000, categoria='Reparación')
        ]
        
        for cliente in clientes:
            db.session.add(cliente)
        
        for servicio in servicios:
            db.session.add(servicio)
        
        # Guardar cambios
        db.session.commit()
        
        print("¡Base de datos inicializada correctamente!")
        print(f"Puede iniciar sesión con:")
        print(f"Email: admin@servicio.com")
        print(f"Contraseña: admin123")

if __name__ == '__main__':
    init_db()
