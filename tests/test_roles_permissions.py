"""
Pruebas para el sistema de roles y permisos.

Este módulo contiene pruebas unitarias y de integración para verificar
el correcto funcionamiento del sistema de roles y permisos.
"""
import unittest
from flask import url_for, current_app
from flask_testing import TestCase
from werkzeug.security import generate_password_hash

from app import create_app, db
from app.models.models import Usuario, Rol, Permiso, RolPermiso

class TestRolePermissionSystem(TestCase):
    """Pruebas para el sistema de roles y permisos."""
    
    def create_app(self):
        """Crea la aplicación de prueba."""
        app = create_app()
        app.config.update(
            TESTING=True,
            WTF_CSRF_ENABLED=False,
            SQLALCHEMY_DATABASE_URI='sqlite:///:memory:',
            SECRET_KEY='test-secret-key'
        )
        return app
    
    def setUp(self):
        """Configuración previa a cada prueba."""
        db.create_all()
        self.create_test_data()
    
    def tearDown(self):
        """Limpieza después de cada prueba."""
        db.session.remove()
        db.drop_all()
    
    def create_test_data(self):
        """Crea datos de prueba."""
        # Crear roles
        roles = {
            'superadmin': Rol(nombre='superadmin', descripcion='Super Administrador', nivel=3),
            'admin': Rol(nombre='admin', descripcion='Administrador', nivel=2),
            'tecnico': Rol(nombre='tecnico', descripcion='Técnico', nivel=1)
        }
        
        for role in roles.values():
            db.session.add(role)
        
        # Crear permisos
        permissions = {
            'ver_usuarios': Permiso(nombre='ver_usuarios', descripcion='Ver usuarios'),
            'crear_usuarios': Permiso(nombre='crear_usuarios', descripcion='Crear usuarios'),
            'ver_asignaciones': Permiso(nombre='ver_asignaciones', descripcion='Ver asignaciones'),
            'crear_asignaciones': Permiso(nombre='crear_asignaciones', descripcion='Crear asignaciones'),
            'solicitar_piezas': Permiso(nombre='solicitar_piezas', descripcion='Solicitar piezas')
        }
        
        for perm in permissions.values():
            db.session.add(perm)
        
        db.session.commit()
        
        # Asignar permisos a roles
        role_perms = [
            # Superadmin tiene todos los permisos implícitamente
            RolPermiso(rol_id=roles['admin'].id, permiso_id=permissions['ver_usuarios'].id),
            RolPermiso(rol_id=roles['admin'].id, permiso_id=permissions['crear_usuarios'].id),
            RolPermiso(rol_id=roles['admin'].id, permiso_id=permissions['ver_asignaciones'].id),
            RolPermiso(rol_id=roles['admin'].id, permiso_id=permissions['crear_asignaciones'].id),
            RolPermiso(rol_id=roles['tecnico'].id, permiso_id=permissions['ver_asignaciones'].id),
            RolPermiso(rol_id=roles['tecnico'].id, permiso_id=permissions['solicitar_piezas'].id)
        ]
        
        for rp in role_perms:
            db.session.add(rp)
        
        # Crear usuarios de prueba
        users = [
            Usuario(
                username='superadmin',
                email='superadmin@test.com',
                password=generate_password_hash('test123'),
                rol='superadmin',
                activo=True
            ),
            Usuario(
                username='admin',
                email='admin@test.com',
                password=generate_password_hash('test123'),
                rol='admin',
                activo=True
            ),
            Usuario(
                username='tecnico',
                email='tecnico@test.com',
                password=generate_password_hash('test123'),
                rol='tecnico',
                activo=True
            )
        ]
        
        for user in users:
            db.session.add(user)
        
        db.session.commit()
    
    def login(self, email, password='test123'):
        """Inicia sesión como un usuario de prueba."""
        return self.client.post(
            url_for('auth.login'),
            data=dict(email=email, password=password, remember_me=False),
            follow_redirects=True
        )
    
    def test_role_hierarchy(self):
        """Prueba la jerarquía de roles."""
        from app.utils.validators import STANDARD_ROLES
        
        # Verificar que los roles tengan el nivel correcto
        self.assertEqual(STANDARD_ROLES['superadmin']['level'], 3)
        self.assertEqual(STANDARD_ROLES['admin']['level'], 2)
        self.assertEqual(STANDARD_ROLES['tecnico']['level'], 1)
        
        # Verificar que superadmin > admin > tecnico
        superadmin = Usuario.query.filter_by(email='superadmin@test.com').first()
        admin = Usuario.query.filter_by(email='admin@test.com').first()
        tecnico = Usuario.query.filter_by(email='tecnico@test.com').first()
        
        self.assertTrue(superadmin.is_admin())
        self.assertTrue(admin.is_admin())
        self.assertFalse(tecnico.is_admin())
        
        self.assertTrue(superadmin.is_tecnico())
        self.assertTrue(admin.is_tecnico())
        self.assertTrue(tecnico.is_tecnico())
    
    def test_permission_checking(self):
        """Prueba la verificación de permisos."""
        superadmin = Usuario.query.filter_by(email='superadmin@test.com').first()
        admin = Usuario.query.filter_by(email='admin@test.com').first()
        tecnico = Usuario.query.filter_by(email='tecnico@test.com').first()
        
        # Superadmin debería tener todos los permisos
        self.assertTrue(superadmin.tiene_permiso('ver_usuarios'))
        self.assertTrue(superadmin.tiene_permiso('crear_usuarios'))
        self.assertTrue(superadmin.tiene_permiso('ver_asignaciones'))
        
        # Admin debería tener permisos específicos
        self.assertTrue(admin.tiene_permiso('ver_usuarios'))
        self.assertTrue(admin.tiene_permiso('crear_usuarios'))
        self.assertTrue(admin.tiene_permiso('ver_asignaciones'))
        self.assertFalse(admin.tiene_permiso('permiso_inexistente'))
        
        # Técnico solo debería tener permisos asignados
        self.assertFalse(tecnico.tiene_permiso('ver_usuarios'))
        self.assertFalse(tecnico.tiene_permiso('crear_usuarios'))
        self.assertTrue(tecnico.tiene_permiso('ver_asignaciones'))
        self.assertTrue(tecnico.tiene_permiso('solicitar_piezas'))
    
    def test_role_required_decorator(self):
        """Prueba el decorador @role_required."""
        from app.decorators.role_required import role_required
        from flask import jsonify
        
        # Crear una ruta de prueba
        @self.app.route('/admin-only')
        @role_required('admin')
        def admin_only():
            return jsonify({'message': 'Acceso concedido'})
        
        # Probar acceso sin autenticación
        response = self.client.get('/admin-only')
        self.assertEqual(response.status_code, 302)  # Redirección a login
        
        # Probar acceso como técnico (sin permiso)
        self.login('tecnico@test.com')
        response = self.client.get('/admin-only')
        self.assertEqual(response.status_code, 403)  # Prohibido
        
        # Probar acceso como admin (con permiso)
        self.login('admin@test.com')
        response = self.client.get('/admin-only')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], 'Acceso concedido')
        
        # Superadmin debería tener acceso también
        self.login('superadmin@test.com')
        response = self.client.get('/admin-only')
        self.assertEqual(response.status_code, 200)
    
    def test_permission_required_decorator(self):
        """Prueba el decorador @permission_required."""
        from app.decorators.permission_required import permission_required
        from flask import jsonify
        
        # Crear una ruta de prueba
        @self.app.route('/manage-users')
        @permission_required('crear_usuarios')
        def manage_users():
            return jsonify({'message': 'Gestión de usuarios'})
        
        # Probar acceso sin autenticación
        response = self.client.get('/manage-users')
        self.assertEqual(response.status_code, 302)  # Redirección a login
        
        # Probar acceso como técnico (sin permiso)
        self.login('tecnico@test.com')
        response = self.client.get('/manage-users')
        self.assertEqual(response.status_code, 403)  # Prohibido
        
        # Probar acceso como admin (con permiso)
        self.login('admin@test.com')
        response = self.client.get('/manage-users')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], 'Gestión de usuarios')
        
        # Superadmin debería tener acceso también
        self.login('superadmin@test.com')
        response = self.client.get('/manage-users')
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
