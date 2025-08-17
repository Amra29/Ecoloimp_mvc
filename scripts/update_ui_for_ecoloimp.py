#!/usr/bin/env python3
"""
Script para actualizar las plantillas de la interfaz de usuario para Ecoloimp.
Asegura que los menús y opciones sean consistentes con los roles y permisos.
"""
import os
import re
from pathlib import Path

# Directorios de plantillas
TEMPLATES_DIR = Path("app/templates")
BASE_TEMPLATE = TEMPLATES_DIR / "base.html"
DASHBOARD_TEMPLATE = TEMPLATES_DIR / "dashboard"

# Definición de elementos de menú por rol
MENU_ITEMS = {
    'superadmin': [
        {
            'title': 'Administración',
            'icon': 'fas fa-cogs',
            'items': [
                {'title': 'Usuarios', 'url': 'admin.gestionar_usuarios', 'permission': 'gestionar_usuarios'},
                {'title': 'Roles y Permisos', 'url': 'admin.gestionar_roles', 'permission': 'gestionar_roles'},
                {'title': 'Configuración', 'url': 'admin.configuracion', 'permission': 'configurar_sistema'},
                {'title': 'Copias de Seguridad', 'url': 'admin.backups', 'permission': 'gestionar_backups'}
            ]
        },
        {
            'title': 'Clientes',
            'icon': 'fas fa-users',
            'items': [
                {'title': 'Lista de Clientes', 'url': 'clientes.listar', 'permission': 'ver_clientes'},
                {'title': 'Agregar Cliente', 'url': 'clientes.crear', 'permission': 'crear_clientes'}
            ]
        },
        {
            'title': 'Equipos',
            'icon': 'fas fa-print',
            'items': [
                {'title': 'Todos los Equipos', 'url': 'equipos.listar', 'permission': 'ver_equipos'},
                {'title': 'Agregar Equipo', 'url': 'equipos.crear', 'permission': 'crear_equipos'}
            ]
        },
        {
            'title': 'Visitas',
            'icon': 'fas fa-calendar-alt',
            'items': [
                {'title': 'Calendario', 'url': 'visitas.calendario', 'permission': 'ver_visitas'},
                {'title': 'Programar Visita', 'url': 'visitas.crear', 'permission': 'programar_visitas'},
                {'title': 'Mis Visitas', 'url': 'visitas.mis_visitas', 'permission': 'ver_visitas_propias'}
            ]
        },
        {
            'title': 'Conteos',
            'icon': 'fas fa-chart-line',
            'items': [
                {'title': 'Historial', 'url': 'conteos.historial', 'permission': 'ver_conteos'},
                {'title': 'Nuevo Conteo', 'url': 'conteos.registrar', 'permission': 'crear_conteos'},
                {'title': 'Mis Conteos', 'url': 'conteos.mis_conteos', 'permission': 'ver_conteos_propios'}
            ]
        },
        {
            'title': 'Reportes',
            'icon': 'fas fa-file-alt',
            'items': [
                {'title': 'Estadísticas', 'url': 'reportes.estadisticas', 'permission': 'ver_estadisticas'},
                {'title': 'Generar Informe', 'url': 'reportes.generar', 'permission': 'generar_reportes'},
                {'title': 'Exportar Datos', 'url': 'reportes.exportar', 'permission': 'exportar_datos'}
            ]
        },
        {
            'title': 'Inventario',
            'icon': 'fas fa-boxes',
            'items': [
                {'title': 'Ver Inventario', 'url': 'inventario.listar', 'permission': 'ver_inventario'},
                {'title': 'Solicitar Materiales', 'url': 'inventario.solicitar', 'permission': 'solicitar_materiales'},
                {'title': 'Aprobar Solicitudes', 'url': 'inventario.aprobar', 'permission': 'aprobar_solicitudes'}
            ]
        }
    ],
    'admin': [
        # Menú similar a superadmin pero sin opciones de administración del sistema
        {
            'title': 'Clientes',
            'icon': 'fas fa-users',
            'items': [
                {'title': 'Lista de Clientes', 'url': 'clientes.listar', 'permission': 'ver_clientes'},
                {'title': 'Agregar Cliente', 'url': 'clientes.crear', 'permission': 'crear_clientes'}
            ]
        },
        {
            'title': 'Equipos',
            'icon': 'fas fa-print',
            'items': [
                {'title': 'Todos los Equipos', 'url': 'equipos.listar', 'permission': 'ver_equipos'},
                {'title': 'Agregar Equipo', 'url': 'equipos.crear', 'permission': 'crear_equipos'}
            ]
        },
        {
            'title': 'Visitas',
            'icon': 'fas fa-calendar-alt',
            'items': [
                {'title': 'Calendario', 'url': 'visitas.calendario', 'permission': 'ver_visitas'},
                {'title': 'Programar Visita', 'url': 'visitas.crear', 'permission': 'programar_visitas'},
                {'title': 'Mis Visitas', 'url': 'visitas.mis_visitas', 'permission': 'ver_visitas_propias'}
            ]
        },
        {
            'title': 'Conteos',
            'icon': 'fas fa-chart-line',
            'items': [
                {'title': 'Historial', 'url': 'conteos.historial', 'permission': 'ver_conteos'},
                {'title': 'Nuevo Conteo', 'url': 'conteos.registrar', 'permission': 'crear_conteos'}
            ]
        },
        {
            'title': 'Reportes',
            'icon': 'fas fa-file-alt',
            'items': [
                {'title': 'Estadísticas', 'url': 'reportes.estadisticas', 'permission': 'ver_estadisticas'},
                {'title': 'Generar Informe', 'url': 'reportes.generar', 'permission': 'generar_reportes'}
            ]
        },
        {
            'title': 'Inventario',
            'icon': 'fas fa-boxes',
            'items': [
                {'title': 'Ver Inventario', 'url': 'inventario.listar', 'permission': 'ver_inventario'},
                {'title': 'Solicitar Materiales', 'url': 'inventario.solicitar', 'permission': 'solicitar_materiales'}
            ]
        }
    ],
    'tecnico': [
        {
            'title': 'Mis Equipos',
            'icon': 'fas fa-print',
            'items': [
                {'title': 'Equipos Asignados', 'url': 'equipos.mis_equipos', 'permission': 'ver_equipos_asignados'}
            ]
        },
        {
            'title': 'Mis Visitas',
            'icon': 'fas fa-calendar-alt',
            'items': [
                {'title': 'Calendario', 'url': 'visitas.calendario', 'permission': 'ver_visitas_propias'},
                {'title': 'Mis Visitas', 'url': 'visitas.mis_visitas', 'permission': 'ver_visitas_propias'}
            ]
        },
        {
            'title': 'Conteos',
            'icon': 'fas fa-chart-line',
            'items': [
                {'title': 'Mis Conteos', 'url': 'conteos.mis_conteos', 'permission': 'ver_conteos_propios'},
                {'title': 'Registrar Conteo', 'url': 'conteos.registrar', 'permission': 'crear_conteos'}
            ]
        },
        {
            'title': 'Inventario',
            'icon': 'fas fa-boxes',
            'items': [
                {'title': 'Solicitar Materiales', 'url': 'inventario.solicitar', 'permission': 'solicitar_materiales'}
            ]
        }
    ]
}

def update_navigation():
    """Actualiza la barra de navegación con los menús según el rol del usuario."""
    nav_template = """{% if current_user.is_authenticated %}
    <!-- Menú principal -->
    <div class="sidebar">
        <div class="sidebar-header">
            <h3>Ecoloimp</h3>
        </div>
        
        <nav class="sidebar-nav">
            <ul class="nav">
                <li class="nav-item">
                    <a class="nav-link" href="{{ url_for('main.dashboard') }}">
                        <i class="fas fa-tachometer-alt"></i> Dashboard
                    </a>
                </li>
                
                {menu_items}
                
                <li class="nav-item">
                    <a class="nav-link" href="{{ url_for('auth.logout') }}">
                        <i class="fas fa-sign-out-alt"></i> Cerrar Sesión
                    </a>
                </li>
            </ul>
        </nav>
    </div>
    {% endif %}
    """
    
    menu_html = ""
    
    # Generar HTML para cada rol
    for rol, sections in MENU_ITEMS.items():
        role_menu = ""
        
        for section in sections:
            section_html = f"""
            <li class="nav-item nav-dropdown">
                <a class="nav-link nav-dropdown-toggle" href="#">
                    <i class="{section_icon}"></i> {section_title}
                </a>
                <ul class="nav-dropdown-items">
            """.format(
                section_icon=section['icon'],
                section_title=section['title']
            )
            
            for item in section['items']:
                section_html += f"""
                <li class="nav-item">
                    <a class="nav-link" href="{{{{ url_for('{item_url}') }}}}">
                        <i class="fas fa-chevron-right"></i> {item_title}
                    </a>
                </li>
                """.format(
                    item_url=item['url'],
                    item_title=item['title']
                )
            
            section_html += """
                </ul>
            </li>
            """
            
            role_menu += section_html
        
        # Guardar el menú para este rol
        menu_with_role = f"{{% if current_user.rol == '{rol}' %}}"
        menu_with_role += role_menu
        menu_with_role += "{% endif %}"
        
        menu_html += menu_with_role
    
    # Reemplazar en la plantilla base
    base_content = BASE_TEMPLATE.read_text(encoding='utf-8')
    
    # Buscar y reemplazar el menú de navegación
    nav_pattern = r'<!-- MENU_NAVIGATION_START -->.*?<!-- MENU_NAVIGATION_END -->'
    new_nav = f'<!-- MENU_NAVIGATION_START -->\n{nav_template.format(menu_items=menu_html)}\n    <!-- MENU_NAVIGATION_END -->'
    
    updated_content = re.sub(nav_pattern, new_nav, base_content, flags=re.DOTALL)
    
    # Guardar los cambios
    BASE_TEMPLATE.write_text(updated_content, encoding='utf-8')
    print(f"Se ha actualizado el menú de navegación en {BASE_TEMPLATE}")

def update_dashboard():
    """Actualiza el dashboard según el rol del usuario."""
    for role in ['superadmin', 'admin', 'tecnico']:
        dashboard_file = DASHBOARD_TEMPLATE / f"{role}.html"
        if not dashboard_file.exists():
            continue
            
        content = dashboard_file.read_text(encoding='utf-8')
        
        # Agregar widgets según el rol
        if role == 'superadmin':
            widgets = """
            <div class="row">
                <!-- Widget de resumen general -->
                <div class="col-md-3">
                    <div class="card bg-primary text-white mb-4">
                        <div class="card-body">
                            <h5 class="card-title">Usuarios</h5>
                            <h2 class="mb-0">{{ total_usuarios }}</h2>
                            <p class="card-text">Usuarios registrados</p>
                        </div>
                        <div class="card-footer d-flex align-items-center justify-content-between">
                            <a class="small text-white stretched-link" href="{{ url_for('admin.gestionar_usuarios') }}">Ver detalles</a>
                            <div class="small text-white"><i class="fas fa-angle-right"></i></div>
                        </div>
                    </div>
                </div>
                <!-- Más widgets para superadmin... -->
            </div>
            """
        elif role == 'admin':
            widgets = """
            <div class="row">
                <!-- Widget de resumen para administradores -->
                <div class="col-md-3">
                    <div class="card bg-success text-white mb-4">
                        <div class="card-body">
                            <h5 class="card-title">Visitas del Mes</h5>
                            <h2 class="mb-0">{{ visitas_mes|length }}</h2>
                            <p class="card-text">Visitas programadas</p>
                        </div>
                        <div class="card-footer d-flex align-items-center justify-content-between">
                            <a class="small text-white stretched-link" href="{{ url_for('visitas.calendario') }}">Ver calendario</a>
                            <div class="small text-white"><i class="fas fa-angle-right"></i></div>
                        </div>
                    </div>
                </div>
                <!-- Más widgets para admin... -->
            </div>
            """
        else:  # técnico
            widgets = """
            <div class="row">
                <!-- Widget para técnicos -->
                <div class="col-md-6">
                    <div class="card mb-4">
                        <div class="card-header">
                            <i class="fas fa-tasks me-1"></i>
                            Mis Próximas Visitas
                        </div>
                        <div class="card-body">
                            {% if proximas_visitas %}
                            <div class="list-group">
                                {% for visita in proximas_visitas %}
                                <a href="{{ url_for('visitas.detalle', id=visita.id) }}" class="list-group-item list-group-item-action">
                                    <div class="d-flex w-100 justify-content-between">
                                        <h6 class="mb-1">{{ visita.cliente.nombre if visita.cliente else 'Cliente no especificado' }}</h6>
                                        <small>{{ visita.fecha_programada|format_datetime('%d/%m/%Y %H:%M') }}</small>
                                    </div>
                                    <p class="mb-1">{{ visita.descripcion|truncate(100) if visita.descripcion else 'Sin descripción' }}</p>
                                    <small>{{ visita.estado|title }}</small>
                                </a>
                                {% endfor %}
                            </div>
                            {% else %}
                            <p class="text-muted">No tienes visitas programadas.</p>
                            {% endif %}
                        </div>
                    </div>
                </div>
                <!-- Más widgets para técnicos... -->
            </div>
            """
        
        # Insertar widgets en el dashboard
        content = re.sub(
            r'<!-- DASHBOARD_WIDGETS_START -->.*?<!-- DASHBOARD_WIDGETS_END -->',
            f'<!-- DASHBOARD_WIDGETS_START -->\n            {widgets}\n            <!-- DASHBOARD_WIDGETS_END -->',
            content,
            flags=re.DOTALL
        )
        
        dashboard_file.write_text(content, encoding='utf-8')
        print(f"Se ha actualizado el dashboard para el rol {role}")

def main():
    """Función principal."""
    print("Actualizando la interfaz de usuario para Ecoloimp...")
    
    # Actualizar navegación
    update_navigation()
    
    # Actualizar dashboards
    update_dashboard()
    
    print("\n¡Actualización de la interfaz de usuario completada con éxito!")

if __name__ == "__main__":
    main()
