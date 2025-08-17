import os
import sys
from datetime import datetime, timedelta
from faker import Faker
import random

# Asegurarse de que el directorio raíz esté en el path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar después de configurar el path
from app import create_app, db
from app.models.models import (
    Usuario, Cliente, Sucursal, Tecnico, Impresora, ConteoImpresion
)

def create_test_data():
    app = create_app()
    with app.app_context():
        # Eliminar datos existentes
        print("Eliminando datos existentes...")
        db.drop_all()
        db.create_all()
        
        fake = Faker('es_ES')
        
        # Crear roles de usuario
        print("Creando usuarios de prueba...")
        
        # Usuario administrador
        admin = Usuario(
            nombre="Administrador Sistema",
            email="admin@ecoloim.com",
            rol="administrador"
        )
        admin.set_password("admin123")
        db.session.add(admin)
        
        # Crear técnicos y usuarios técnicos
        tecnicos = []
        for i in range(1, 4):
            usuario = Usuario(
                nombre=f"Técnico {i} {fake.last_name()}",
                email=f"tecnico{i}@ecoloim.com",
                telefono=fake.phone_number(),
                rol="tecnico"
            )
            usuario.set_password(f"tecnico{i}123")
            db.session.add(usuario)
            
            tecnico = Tecnico(
                usuario=usuario,
                nombre=usuario.nombre,
                email=usuario.email,
                telefono=usuario.telefono,
                especialidad=random.choice(["Impresoras", "Redes", "Sistemas"]),
                nivel_experiencia=random.choice(["junior", "senior"])
            )
            db.session.add(tecnico)
            tecnicos.append(tecnico)
        
        # Crear cliente de prueba
        print("Creando clientes de prueba...")
        cliente = Cliente(
            nombre="Ecoloim S.A.",
            email="info@ecoloim.com",
            telefono=fake.phone_number(),
            direccion=fake.address(),
            tipo_cliente="empresa"
        )
        db.session.add(cliente)
        db.session.commit()
        
        # Crear sucursales
        print("Creando sucursales...")
        sucursales = []
        ciudades = ["Buenos Aires", "Córdoba", "Rosario", "Mendoza", "Tucumán"]
        for i, ciudad in enumerate(ciudades, 1):
            sucursal = Sucursal(
                nombre=f"Sucursal {ciudad}",
                direccion=fake.street_address(),
                ciudad=ciudad,
                telefono=fake.phone_number(),
                email=f"sucursal{i}@ecoloim.com",
                cliente_id=cliente.id
            )
            db.session.add(sucursal)
            sucursales.append(sucursal)
        db.session.commit()
        
        # Crear impresoras
        print("Creando impresoras...")
        marcas = ["HP", "Epson", "Brother", "Canon", "Xerox"]
        modelos = ["LaserJet Pro", "OfficeJet", "WorkForce", "ImageRunner", "Phaser"]
        tipos = ["Láser", "Inyección de tinta", "Tóner", "Multifunción"]
        
        impresoras = []
        for i in range(1, 16):
            sucursal = random.choice(sucursales)
            impresora = Impresora(
                numero_serie=f"SN-{fake.unique.bothify('??##??##')}",
                modelo=random.choice(modelos) + " " + str(random.randint(1000, 9999)),
                marca=random.choice(marcas),
                tipo_impresora=random.choice(tipos),
                fecha_instalacion=fake.date_time_this_year(),
                estado=random.choices(
                    ["activa", "inactiva", "en_mantenimiento"],
                    weights=[0.8, 0.1, 0.1]
                )[0],
                cliente_id=cliente.id,
                sucursal_id=sucursal.id,
                ubicacion=random.choice(["Oficina Principal", "Sala de Reuniones", "Recepción", "Área de Producción"]),
                contador_actual_impresiones=random.randint(1000, 50000),
                contador_actual_escaneos=random.randint(100, 20000)
            )
            db.session.add(impresora)
            impresoras.append(impresora)
        db.session.commit()
        
        # Crear conteos de impresión
        print("Creando conteos de impresión...")
        for impresora in impresoras:
            fecha_actual = datetime.utcnow()
            contador_impresiones = 0
            contador_escaneos = 0
            
            # Crear 12 conteos (uno por mes del último año)
            for meses_atras in range(12, 0, -1):
                fecha_conteo = fecha_actual - timedelta(days=30 * meses_atras)
                nuevo_contador_impresiones = contador_impresiones + random.randint(1000, 10000)
                nuevo_contador_escaneos = contador_escaneos + random.randint(100, 2000)
                
                conteo = ConteoImpresion(
                    fecha_conteo=fecha_conteo,
                    impresora_id=impresora.id,
                    tecnico_id=random.choice(tecnicos).id,
                    contador_impresiones=nuevo_contador_impresiones,
                    contador_escaneos=nuevo_contador_escaneos,
                    impresiones_desde_ultimo=nuevo_contador_impresiones - contador_impresiones if contador_impresiones > 0 else 0,
                    escaneos_desde_ultimo=nuevo_contador_escaneos - contador_escaneos if contador_escaneos > 0 else 0,
                    observaciones=random.choice([
                        "Conteo regular", 
                        "Sin incidencias", 
                        "Limpieza básica realizada",
                        "Cambio de tóner",
                        "Ajustes de configuración"
                    ]),
                    requiere_mantenimiento=random.choices([True, False], weights=[0.2, 0.8])[0],
                    problemas_detectados=random.choices([
                        "Ninguno",
                        "Atasco de papel",
                        "Bajo nivel de tinta",
                        "Rendimiento lento",
                        "Ruidos extraños"
                    ], weights=[0.7, 0.1, 0.1, 0.05, 0.05])[0],
                    aprobado_por_cliente=random.choices([True, False], weights=[0.8, 0.2])[0],
                    nombre_aprobador=fake.name() if random.random() > 0.5 else None,
                    firma_aprobador=None  # Podríamos generar una firma dummy si es necesario
                )
                
                db.session.add(conteo)
                contador_impresiones = nuevo_contador_impresiones
                contador_escaneos = nuevo_contador_escaneos
                
                # Actualizar contadores de la impresora si es el conteo más reciente
                if meses_atras == 1:
                    impresora.contador_actual_impresiones = contador_impresiones
                    impresora.contador_actual_escaneos = contador_escaneos
                    impresora.fecha_ultimo_conteo = fecha_conteo
        
        db.session.commit()
        print("¡Datos de prueba creados exitosamente!")

if __name__ == "__main__":
    create_test_data()
