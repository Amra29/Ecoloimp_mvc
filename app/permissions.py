"""
Definición de los permisos del sistema.

Cada permiso debe tener:
- Un nombre único (usado como clave)
- Una descripción clara
- Una categoría para agruparlos en la interfaz
"""

# Categorías para organizar los permisos
CATEGORIAS = {
    'sistema': 'Sistema',
    'administracion': 'Administración',
    'usuarios': 'Usuarios',
    'clientes': 'Clientes',
    'equipos': 'Equipos',
    'conteos': 'Conteos de Impresiones',
    'visitas': 'Visitas Técnicas',
    'inventario': 'Inventario',
    'reportes': 'Reportes',
    'facturacion': 'Facturación',
    'soporte': 'Soporte Técnico',
}

# Permisos del sistema para Ecoloimp
PERMISOS = {
    # =====================
    # Permisos de Sistema
    # =====================
    'admin_todo': {
        'descripcion': 'Acceso total al sistema (superusuario)',
        'categoria': 'sistema',
        'roles_por_defecto': ['superadmin']
    },
    'configurar_sistema': {
        'descripcion': 'Configuración general del sistema',
        'categoria': 'sistema',
        'roles_por_defecto': ['superadmin', 'admin']
    },
    'ver_logs': {
        'descripcion': 'Ver registros del sistema',
        'categoria': 'sistema',
        'roles_por_defecto': ['superadmin', 'admin']
    },
    
    # =====================
    # Administración
    # =====================
    'gestionar_backups': {
        'descripcion': 'Realizar y restaurar copias de seguridad',
        'categoria': 'administracion',
        'roles_por_defecto': ['superadmin', 'admin']
    },
    'gestionar_parametros': {
        'descripcion': 'Gestionar parámetros del sistema',
        'categoria': 'administracion',
        'roles_por_defecto': ['superadmin', 'admin']
    },
    
    # =====================
    # Usuarios
    # =====================
    'gestionar_usuarios': {
        'descripcion': 'Crear, editar y eliminar usuarios',
        'categoria': 'usuarios',
        'roles_por_defecto': ['superadmin', 'admin']
    },
    'ver_usuarios': {
        'descripcion': 'Ver lista de usuarios',
        'categoria': 'usuarios',
        'roles_por_defecto': ['superadmin', 'admin']
    },
    'asignar_roles': {
        'descripcion': 'Asignar roles a usuarios',
        'categoria': 'usuarios',
        'roles_por_defecto': ['superadmin', 'admin']
    },
    
    # =====================
    # Clientes
    # =====================
    'gestionar_clientes': {
        'descripcion': 'Crear, editar y eliminar clientes',
        'categoria': 'clientes',
        'roles_por_defecto': ['superadmin', 'admin']
    },
    'ver_clientes': {
        'descripcion': 'Ver lista de clientes',
        'categoria': 'clientes',
        'roles_por_defecto': ['superadmin', 'admin', 'tecnico']
    },
    'exportar_clientes': {
        'descripcion': 'Exportar datos de clientes',
        'categoria': 'clientes',
        'roles_por_defecto': ['superadmin', 'admin']
    },
    
    # =====================
    # Equipos
    # =====================
    'gestionar_equipos': {
        'descripcion': 'Gestionar todos los equipos',
        'categoria': 'equipos',
        'roles_por_defecto': ['superadmin', 'admin']
    },
    'ver_equipos': {
        'descripcion': 'Ver lista de equipos',
        'categoria': 'equipos',
        'roles_por_defecto': ['superadmin', 'admin', 'tecnico']
    },
    'ver_equipos_asignados': {
        'descripcion': 'Ver solo equipos asignados',
        'categoria': 'equipos',
        'roles_por_defecto': ['tecnico']
    },
    'registrar_mantenimiento': {
        'descripcion': 'Registrar mantenimiento de equipos',
        'categoria': 'equipos',
        'roles_por_defecto': ['superadmin', 'admin', 'tecnico']
    },
    
    # =====================
    # Conteos de Impresiones
    # =====================
    'gestionar_conteos': {
        'descripcion': 'Gestionar todos los conteos de impresiones',
        'categoria': 'conteos',
        'roles_por_defecto': ['superadmin', 'admin']
    },
    'ver_conteos': {
        'descripcion': 'Ver todos los conteos de impresiones',
        'categoria': 'conteos',
        'roles_por_defecto': ['superadmin', 'admin']
    },
    'ver_conteos_propios': {
        'descripcion': 'Ver solo conteos propios',
        'categoria': 'conteos',
        'roles_por_defecto': ['tecnico']
    },
    'crear_conteos': {
        'descripcion': 'Registrar nuevos conteos de impresiones',
        'categoria': 'conteos',
        'roles_por_defecto': ['admin', 'tecnico']
    },
    'editar_conteos': {
        'descripcion': 'Editar cualquier conteo de impresiones',
        'categoria': 'conteos',
        'roles_por_defecto': ['superadmin', 'admin']
    },
    'editar_conteos_propios': {
        'descripcion': 'Editar solo conteos propios',
        'categoria': 'conteos',
        'roles_por_defecto': ['tecnico']
    },
    'eliminar_conteos': {
        'descripcion': 'Eliminar conteos de impresiones',
        'categoria': 'conteos',
        'roles_por_defecto': ['superadmin']
    },
    'exportar_conteos': {
        'descripcion': 'Exportar datos de conteos',
        'categoria': 'conteos',
        'roles_por_defecto': ['superadmin', 'admin']
    },
    
    # Visitas Técnicas
    'gestionar_visitas': {
        'descripcion': 'Gestionar todas las visitas técnicas',
        'categoria': 'visitas',
        'roles_por_defecto': ['administrador', 'recepcion']
    },
    'ver_visitas': {
        'descripcion': 'Ver todas las visitas técnicas',
        'categoria': 'visitas',
        'roles_por_defecto': ['administrador', 'tecnico', 'recepcion', 'gerencia']
    },
    'crear_visitas': {
        'descripcion': 'Programar nuevas visitas técnicas',
        'categoria': 'visitas',
        'roles_por_defecto': ['administrador', 'recepcion']
    },
    'editar_visitas': {
        'descripcion': 'Editar cualquier visita técnica',
        'categoria': 'visitas',
        'roles_por_defecto': ['administrador', 'recepcion']
    },
    'registrar_visitas': {
        'descripcion': 'Registrar informes de visitas realizadas',
        'categoria': 'visitas',
        'roles_por_defecto': ['administrador', 'tecnico']
    },
    'eliminar_visitas': {
        'descripcion': 'Eliminar visitas técnicas',
        'categoria': 'visitas',
        'roles_por_defecto': ['administrador']
    },
    
    # Inventario
    'gestionar_inventario': {
        'descripcion': 'Gestionar el inventario completo',
        'categoria': 'inventario',
        'roles_por_defecto': ['administrador', 'recepcion']
    },
    'ver_inventario': {
        'descripcion': 'Ver el inventario',
        'categoria': 'inventario',
        'roles_por_defecto': ['administrador', 'tecnico', 'recepcion', 'gerencia']
    },
    
    # Reportes
    'ver_reportes': {
        'descripcion': 'Acceder a los reportes del sistema',
        'categoria': 'reportes',
        'roles_por_defecto': ['administrador', 'gerencia', 'recepcion']
    },
    'generar_reportes': {
        'descripcion': 'Generar reportes personalizados',
        'categoria': 'reportes',
        'roles_por_defecto': ['administrador', 'gerencia']
    },
    'exportar_datos': {
        'descripcion': 'Exportar datos a diferentes formatos',
        'categoria': 'reportes',
        'roles_por_defecto': ['administrador', 'gerencia']
    },
    
    # Facturación
    'gestionar_facturas': {
        'descripcion': 'Gestionar facturas y pagos',
        'categoria': 'facturacion',
        'roles_por_defecto': ['administrador', 'recepcion']
    },
    'ver_facturas': {
        'descripcion': 'Ver facturas y estados de pago',
        'categoria': 'facturacion',
        'roles_por_defecto': ['administrador', 'gerencia', 'recepcion']
    },
    'crear_facturas': {
        'descripcion': 'Crear nuevas facturas',
        'categoria': 'facturacion',
        'roles_por_defecto': ['administrador', 'recepcion']
    },
    'anular_facturas': {
        'descripcion': 'Anular facturas',
        'categoria': 'facturacion',
        'roles_por_defecto': ['administrador']
    },
    'generar_notas_credito': {
        'descripcion': 'Generar notas de crédito',
        'categoria': 'facturacion',
        'roles_por_defecto': ['administrador']
    }
}

# Mapeo de roles del sistema
ROLES = {
    'administrador': {
        'nombre': 'Administrador',
        'descripcion': 'Acceso completo al sistema'
    },
    'tecnico': {
        'nombre': 'Técnico',
        'descripcion': 'Personal técnico que realiza visitas y mantenimientos'
    },
    'recepcion': {
        'nombre': 'Recepción',
        'descripcion': 'Personal de recepción y atención al cliente'
    },
    'gerencia': {
        'nombre': 'Gerencia',
        'descripcion': 'Personal gerencial con acceso a reportes y estadísticas'
    },
    'cliente': {
        'nombre': 'Cliente',
        'descripcion': 'Usuarios clientes con acceso limitado'
    }
}
