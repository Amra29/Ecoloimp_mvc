"""
Script de migración para estandarizar roles y permisos.

Este script realiza los siguientes cambios:
1. Crea roles estándar si no existen
2. Actualiza los roles de los usuarios existentes
3. Crea permisos faltantes
4. Asigna permisos a roles
"""
import sys
from pathlib import Path

# Asegurar que el directorio raíz esté en el path
root_path = str(Path(__file__).parent.parent)
if root_path not in sys.path:
    sys.path.insert(0, root_path)

from app import create_app
from app.models.models import db, Usuario, Rol, Permiso, RolPermiso

# Configuración de roles estándar
STANDARD_ROLES = {
    'superadmin': {
        'level': 3,
        'description': 'Acceso total al sistema (desarrollador)'
    },
    'admin': {
        'level': 2,
        'description': 'Administrador con gestión completa'
    },
    'tecnico': {
        'level': 1,
        'description': 'Técnico con acceso limitado'
    }
}

# Permisos básicos por rol
ROLE_PERMISSIONS = {
    'superadmin': [
        '*',  # Todos los permisos
    ],
    'admin': [
        'ver_usuarios', 'crear_usuarios', 'editar_usuarios', 'eliminar_usuarios',
        'ver_roles', 'asignar_roles', 'ver_permisos', 'asignar_permisos',
        'ver_reportes', 'generar_reportes', 'exportar_datos',
        'ver_equipos', 'crear_equipos', 'editar_equipos', 'eliminar_equipos',
        'ver_clientes', 'crear_clientes', 'editar_clientes', 'eliminar_clientes',
        'ver_asignaciones', 'crear_asignaciones', 'editar_asignaciones', 'eliminar_asignaciones',
        'ver_visitas', 'crear_visitas', 'editar_visitas', 'eliminar_visitas',
        'ver_pedidos', 'aprobar_pedidos', 'rechazar_pedidos',
        'ver_inventario', 'gestionar_inventario'
    ],
    'tecnico': [
        'ver_mis_asignaciones', 'actualizar_estado_asignacion',
        'solicitar_piezas', 'ver_mis_pedidos',
        'registrar_visitas', 'ver_mis_visitas',
        'generar_reportes_tecnicos'
    ]
}

def create_standard_roles():
    """Crea los roles estándar si no existen."""
    for role_name, role_data in STANDARD_ROLES.items():
        role = Rol.query.filter_by(nombre=role_name).first()
        if not role:
            role = Rol(
                nombre=role_name,
                descripcion=role_data['description'],
                nivel=role_data['level']
            )
            db.session.add(role)
            print(f"[+] Rol creado: {role_name}")
        else:
            role.nivel = role_data['level']
            role.descripcion = role_data['description']
            print(f"[i] Rol actualizado: {role_name}")
    
    db.session.commit()

def create_standard_permissions():
    """Crea los permisos estándar si no existen."""
    # Recolectar todos los permisos únicos
    all_permissions = set()
    for permissions in ROLE_PERMISSIONS.values():
        all_permissions.update(permissions)
    
    # Eliminar el comodín de superadmin
    all_permissions.discard('*')
    
    # Crear permisos faltantes
    for perm_name in sorted(all_permissions):
        perm = Permiso.query.filter_by(nombre=perm_name).first()
        if not perm:
            perm = Permiso(
                nombre=perm_name,
                descripcion=f'Permiso para {perm_name}'
            )
            db.session.add(perm)
            print(f"[+] Permiso creado: {perm_name}")
    
    db.session.commit()

def assign_permissions_to_roles():
    """Asigna los permisos a los roles correspondientes."""
    for role_name, permissions in ROLE_PERMISSIONS.items():
        role = Rol.query.filter_by(nombre=role_name).first()
        if not role:
            print(f"[!] Error: Rol no encontrado: {role_name}")
            continue
            
        # Limpiar permisos existentes
        RolPermiso.query.filter_by(rol_id=role.id).delete()
        
        # Si es superadmin con permiso '*', no es necesario agregar permisos individuales
        if '*' in permissions:
            print(f"[i] Rol {role_name} tiene todos los permisos")
            continue
            
        # Asignar permisos individuales
        for perm_name in permissions:
            perm = Permiso.query.filter_by(nombre=perm_name).first()
            if not perm:
                print(f"[!] Permiso no encontrado: {perm_name}")
                continue
                
            role_perm = RolPermiso(rol_id=role.id, permiso_id=perm.id)
            db.session.add(role_perm)
            print(f"[+] Permiso asignado: {role_name} -> {perm_name}")
    
    db.session.commit()

def update_user_roles():
    """Actualiza los roles de los usuarios existentes."""
    # Mapeo de roles antiguos a nuevos
    role_mapping = {
        'administrador': 'admin',
        'técnico': 'tecnico',
        'superusuario': 'superadmin',
        'usuario': 'tecnico'  # Por defecto, usuarios sin rol claro serán técnicos
    }
    
    for user in Usuario.query.all():
        if not user.rol or user.rol not in STANDARD_ROLES:
            new_role = role_mapping.get(user.rol.lower(), 'tecnico')
            print(f"[i] Actualizando rol de {user.email} de '{user.rol}' a '{new_role}'")
            user.rol = new_role
    
    db.session.commit()

def main():
    print("=== Iniciando migración de roles y permisos ===")
    
    # Crear aplicación para acceder al contexto
    app = create_app()
    with app.app_context():
        try:
            # 1. Crear roles estándar
            print("\n1. Creando/actualizando roles estándar...")
            create_standard_roles()
            
            # 2. Crear permisos estándar
            print("\n2. Creando permisos estándar...")
            create_standard_permissions()
            
            # 3. Asignar permisos a roles
            print("\n3. Asignando permisos a roles...")
            assign_permissions_to_roles()
            
            # 4. Actualizar roles de usuarios existentes
            print("\n4. Actualizando roles de usuarios...")
            update_user_roles()
            
            print("\n=== Migración completada exitosamente ===")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n[!] Error durante la migración: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == '__main__':
    main()
