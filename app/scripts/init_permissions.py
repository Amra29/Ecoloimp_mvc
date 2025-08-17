""
Script para inicializar los permisos del sistema.

Este script crea los permisos definidos en permissions.py y los asigna a los roles correspondientes.
"""
import sys
import os

# Asegurarse de que el directorio raíz del proyecto esté en el path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

def init_permissions():
    """Inicializa los permisos del sistema."""
    from app import create_app, db
    from app.models.models import Permiso, RolPermiso
    from app.permissions import PERMISOS, ROLES
    
    # Crear la aplicación Flask
    app = create_app()
    
    with app.app_context():
        print("Inicializando permisos del sistema...")
        
        # Contadores para estadísticas
        permisos_creados = 0
        permisos_actualizados = 0
        asignaciones_creadas = 0
        
        # Crear o actualizar permisos
        for permiso_id, datos_permiso in PERMISOS.items():
            permiso = Permiso.query.filter_by(nombre=permiso_id).first()
            
            if permiso:
                # Actualizar permiso existente si es necesario
                actualizado = False
                if permiso.descripcion != datos_permiso['descripcion']:
                    permiso.descripcion = datos_permiso['descripcion']
                    actualizado = True
                if permiso.categoria != datos_permiso['categoria']:
                    permiso.categoria = datos_permiso['categoria']
                    actualizado = True
                
                if actualizado:
                    permisos_actualizados += 1
                    print(f"  - Actualizado permiso: {permiso_id}")
            else:
                # Crear nuevo permiso
                permiso = Permiso(
                    nombre=permiso_id,
                    descripcion=datos_permiso['descripcion'],
                    categoria=datos_permiso['categoria']
                )
                db.session.add(permiso)
                permisos_creados += 1
                print(f"  - Creado permiso: {permiso_id}")
            
            # Asegurarse de que los roles tengan los permisos por defecto
            for rol_id in datos_permiso.get('roles_por_defecto', []):
                # Verificar si ya existe la asignación
                if not RolPermiso.query.filter_by(
                    rol=rol_id,
                    permiso_id=permiso_id
                ).first():
                    # Crear la relación
                    rol_permiso = RolPermiso(rol=rol_id, permiso_id=permiso_id)
                    db.session.add(rol_permiso)
                    asignaciones_creadas += 1
        
        # Confirmar cambios en la base de datos
        try:
            db.session.commit()
            print("\nResumen de la inicialización:")
            print(f"  - Permisos creados: {permisos_creados}")
            print(f"  - Permisos actualizados: {permisos_actualizados}")
            print(f"  - Asignaciones de roles creadas: {asignaciones_creadas}")
            print("\n¡Inicialización de permisos completada exitosamente!")
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"\nError al inicializar permisos: {str(e)}")
            return False

if __name__ == '__main__':
    init_permissions()
