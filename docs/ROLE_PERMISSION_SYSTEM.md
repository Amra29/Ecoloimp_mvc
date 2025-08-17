# Sistema de Roles y Permisos

Este documento describe la implementación del sistema de roles y permisos en la aplicación Flask.

## Estructura de Roles

La aplicación utiliza los siguientes roles jerárquicos:

| Rol | Nivel | Descripción |
|-----|-------|-------------|
| `superadmin` | 3 | Acceso total al sistema (desarrollador) |
| `admin` | 2 | Administrador con gestión completa |
| `tecnico` | 1 | Técnico con acceso limitado |

## Permisos Disponibles

### Gestión de Usuarios
- `ver_usuarios`: Ver lista de usuarios
- `crear_usuarios`: Crear nuevos usuarios
- `editar_usuarios`: Editar usuarios existentes
- `eliminar_usuarios`: Eliminar usuarios

### Gestión de Asignaciones
- `ver_asignaciones`: Ver lista de asignaciones
- `crear_asignaciones`: Crear nuevas asignaciones
- `editar_asignaciones`: Editar asignaciones existentes
- `eliminar_asignaciones`: Eliminar asignaciones

### Gestión de Inventario
- `ver_inventario`: Ver inventario de piezas
- `gestionar_inventario`: Agregar/editar/eliminar piezas

### Pedidos de Piezas
- `solicitar_piezas`: Solicitar piezas del inventario
- `aprobar_pedidos`: Aprobar pedidos de piezas (admin)
- `rechazar_pedidos`: Rechazar pedidos de piezas (admin)

### Reportes
- `ver_reportes`: Ver reportes
- `generar_reportes`: Generar nuevos reportes
- `exportar_datos`: Exportar datos a diferentes formatos

## Uso de Decoradores

### @role_required

Verifica que el usuario tenga al menos el rol especificado:

```python
from app.decorators import role_required

@bp.route('/admin/dashboard')
@login_required
@role_required('admin')
def admin_dashboard():
    return render_template('admin/dashboard.html')
```

### @permission_required

Verifica que el usuario tenga los permisos especificados:

```python
from app.decorators import permission_required

@bp.route('/users')
@login_required
@permission_required('ver_usuarios')
def list_users():
    users = Usuario.query.all()
    return render_template('users/list.html', users=users)
```

### @object_permission_required

Verifica permisos sobre un objeto específico:

```python
from app.decorators import object_permission_required

def get_asignacion(asignacion_id):
    return Asignacion.query.get_or_404(asignacion_id)

@bp.route('/asignacion/<int:asignacion_id>/editar')
@login_required
@object_permission_required('editar', get_asignacion)
def editar_asignacion(asignacion_id, obj):
    # obj es la asignación cargada por get_asignacion
    form = AsignacionForm(obj=obj)
    # ...
```

## Migración de Datos

Para actualizar los roles y permisos en la base de datos:

```bash
python scripts/migrate_roles_permissions.py
```

## Pruebas

Ejecutar las pruebas con:

```bash
python -m pytest tests/test_roles_permissions.py -v
```

## Mejores Prácticas

1. **Siempre usar los decoradores** para proteger las rutas
2. **No confiar únicamente** en la interfaz de usuario para la seguridad
3. **Validar permisos** en los formularios y acciones
4. **Mantener actualizada** la documentación de permisos
5. **Probar** todos los flujos de autenticación y autorización

## Solución de Problemas

### Error: "Rol no válido"
Verificar que el rol exista en la tabla `roles` y esté correctamente escrito.

### Error: "Permiso denegado"
Asegurarse de que el usuario tenga el rol o permiso necesario asignado.

### Error: "Blueprint no encontrado"
Verificar que el blueprint esté registrado en `app/__init__.py` o `app_factory.py`.
