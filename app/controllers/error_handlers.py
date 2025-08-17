"""
Manejadores de errores personalizados para la aplicación.

Este módulo registra manejadores de errores globales para la aplicación Flask,
proporcionando respuestas personalizadas para diferentes códigos de error HTTP.
"""
from flask import render_template, jsonify, request
from werkzeug.exceptions import HTTPException

def register_error_handlers(app):
    """
    Registra los manejadores de errores personalizados en la aplicación Flask.
    
    Args:
        app: Instancia de la aplicación Flask
    """
    # Manejador para errores 404 - Página no encontrada
    @app.errorhandler(404)
    def not_found_error(error):
        if request.is_xhr or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'error': 'Recurso no encontrado',
                'message': 'La página o recurso solicitado no existe.'
            }), 404
        return render_template('errors/404.html'), 404
    
    # Manejador para errores 403 - Acceso prohibido
    @app.errorhandler(403)
    def forbidden_error(error):
        if request.is_xhr or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'error': 'Acceso denegado',
                'message': 'No tienes permiso para acceder a este recurso.'
            }), 403
        return render_template('errors/403.html'), 403
    
    # Manejador para errores 401 - No autorizado
    @app.errorhandler(401)
    def unauthorized_error(error):
        if request.is_xhr or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'error': 'No autorizado',
                'message': 'Debes iniciar sesión para acceder a este recurso.'
            }), 401
        return render_template('errors/401.html'), 401
    
    # Manejador para errores 500 - Error interno del servidor
    @app.errorhandler(500)
    def internal_error(error):
        # Importar aquí para evitar importaciones circulares
        from flask import current_app
        
        # Registrar el error en el log
        current_app.logger.error(f'Error 500: {str(error)}', exc_info=True)
        
        if request.is_xhr or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'error': 'Error interno del servidor',
                'message': 'Ha ocurrido un error inesperado. Por favor, inténtalo de nuevo más tarde.'
            }), 500
        return render_template('errors/500.html'), 500
    
    # Manejador genérico para excepciones HTTP
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        response = {
            'error': error.name,
            'message': error.description,
            'code': error.code
        }
        
        if request.is_xhr or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(response), error.code
        
        # Para errores HTTP comunes, usar plantillas específicas si existen
        if error.code in [400, 401, 403, 404, 405, 500]:
            return render_template(f'errors/{error.code}.html', error=error), error.code
            
        # Para otros errores HTTP, usar una plantilla genérica
        return render_template('errors/generic.html', error=error), error.code
    
    # Manejador para excepciones de base de datos
    @app.errorhandler(Exception)
    def handle_generic_exception(error):
        # Importar aquí para evitar importaciones circulares
        from flask import current_app
        from sqlalchemy.exc import SQLAlchemyError
        
        # Registrar el error en el log
        current_app.logger.error(f'Excepción no manejada: {str(error)}', exc_info=True)
        
        # Manejar errores de SQLAlchemy
        if isinstance(error, SQLAlchemyError):
            db.session.rollback()
            error_message = 'Error en la base de datos. Por favor, inténtalo de nuevo.'
        else:
            error_message = 'Ha ocurrido un error inesperado. Por favor, inténtalo de nuevo más tarde.'
        
        if request.is_xhr or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'error': 'Error del servidor',
                'message': error_message
            }), 500
            
        return render_template('errors/500.html', error=error_message), 500
