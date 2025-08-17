"""
Controlador para la gestión de técnicos
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import or_
from app.models.models import db, Tecnico, Usuario, Visita, Asignacion
from app.forms import TecnicoForm, BuscarTecnicoForm
from app.decorators import admin_required
from werkzeug.security import generate_password_hash

# Crear blueprint
tecnicos_bp = Blueprint('tecnicos', __name__, url_prefix='/tecnicos')


@tecnicos_bp.route('/')
@login_required
def listar():
    """Lista todos los técnicos con opciones de filtrado"""
    form = BuscarTecnicoForm()
    
    # Consultar técnicos con filtros
    query = Tecnico.query
    
    # Aplicar filtros si se envió el formulario
    if request.args.get('buscar'):
        if form.busqueda.data:
            termino = f"%{form.busqueda.data}%"
            query = query.filter(
                or_(
                    Tecnico.nombre.ilike(termino),
                    Tecnico.email.ilike(termino),
                    Tecnico.telefono.ilike(termino),
                    Tecnico.especialidad.ilike(termino)
                )
            )
        if form.estado.data != 'todos':
            activo = form.estado.data == 'activo'
            query = query.filter(Tecnico.activo == activo)
    
    # Ordenar por nombre
    query = query.order_by(Tecnico.nombre)
    
    # Paginación
    page = request.args.get('page', 1, type=int)
    por_pagina = 15
    tecnicos = query.paginate(page=page, per_page=por_pagina, error_out=False)
    
    return render_template('tecnicos/listar.html', 
                         tecnicos=tecnicos,
                         form=form,
                         titulo='Técnicos')


@tecnicos_bp.route('/nuevo', methods=['GET', 'POST'])
@admin_required
def nuevo():
    """Crea un nuevo técnico"""
    form = TecnicoForm()
    
    # Verificar si el correo ya está en uso
    if form.validate_on_submit():
        try:
            # Verificar si ya existe un usuario con este correo
            if Usuario.query.filter_by(email=form.email.data.lower().strip()).first():
                flash('Ya existe un usuario con este correo electrónico', 'error')
                return render_template('tecnicos/form.html', 
                                    form=form, 
                                    titulo='Nuevo Técnico')
            
            # Crear nuevo técnico (que también es un Usuario por herencia)
            tecnico = Tecnico(
                nombre=form.nombre.data.strip(),
                email=form.email.data.lower().strip(),
                telefono=form.telefono.data.strip() if form.telefono.data else None,
                activo=form.activo.data,
                especialidad=form.especialidad.data,
                habilidades=form.habilidades.data,
                notas=form.notas.data,
                fecha_ingreso=form.fecha_ingreso.data or datetime.utcnow()
            )
            
            # Establecer contraseña
            tecnico.set_password(form.password.data)
            
            # Guardar en la base de datos
            db.session.add(tecnico)
            db.session.commit()
            
            flash('Técnico creado exitosamente', 'success')
            return redirect(url_for('tecnicos.detalle', id=tecnico.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear el técnico: {str(e)}', 'error')
    
    return render_template('tecnicos/form.html', 
                         form=form, 
                         titulo='Nuevo Técnico')


@tecnicos_bp.route('/<int:id>')
@login_required
def detalle(id):
    """Muestra los detalles de un técnico"""
    tecnico = Tecnico.query.get_or_404(id)
    
    # Obtener estadísticas
    hoy = datetime.utcnow().date()
    mes_pasado = hoy - timedelta(days=30)
    
    # Obtener conteo de visitas
    total_visitas = Visita.query.filter_by(tecnico_id=id).count()
    visitas_mes = Visita.query.filter(
        Visita.tecnico_id == id,
        Visita.fecha_visita >= mes_pasado
    ).count()
    
    visitas_pendientes = Visita.query.filter(
        Visita.tecnico_id == id,
        Visita.estado.in_(['programada', 'en_proceso'])
    ).count()
    
    # Obtener asignaciones recientes
    asignaciones = Asignacion.query.filter_by(tecnico_id=id)\
                                 .order_by(Asignacion.fecha_asignacion.desc())\
                                 .limit(5).all()
    
    return render_template('tecnicos/detalle.html',
                         tecnico=tecnico,
                         total_visitas=total_visitas,
                         visitas_mes=visitas_mes,
                         visitas_pendientes=visitas_pendientes,
                         asignaciones=asignaciones,
                         hoy=hoy,
                         titulo=f'Detalles de {tecnico.nombre}')


@tecnicos_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@admin_required
def editar(id):
    """Edita un técnico existente"""
    tecnico = Tecnico.query.get_or_404(id)
    form = TecnicoForm(obj=tecnico)
    
    if form.validate_on_submit():
        try:
            # Verificar si el correo ya está en uso por otro usuario
            if form.email.data.lower() != tecnico.email and \
               Usuario.query.filter(Usuario.email == form.email.data.lower(), 
                                  Usuario.id != tecnico.id).first():
                flash('El correo electrónico ya está en uso por otro usuario', 'error')
            else:
                # Actualizar datos básicos
                tecnico.nombre = form.nombre.data.strip()
                tecnico.email = form.email.data.lower().strip()
                tecnico.telefono = form.telefono.data.strip() if form.telefono.data else None
                tecnico.activo = form.activo.data
                
                # Actualizar contraseña si se proporcionó una nueva
                if form.password.data:
                    tecnico.set_password(form.password.data)
                
                # Actualizar datos específicos del técnico
                tecnico.especialidad = form.especialidad.data.strip() if form.especialidad.data else None
                tecnico.habilidades = form.habilidades.data.strip() if form.habilidades.data else None
                tecnico.fecha_ingreso = form.fecha_ingreso.data or tecnico.fecha_ingreso
                tecnico.notas = form.notas.data.strip() if form.notas.data else None
                
                db.session.commit()
                flash('Técnico actualizado correctamente', 'success')
                return redirect(url_for('tecnicos.detalle', id=tecnico.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el técnico: {str(e)}', 'error')
    
    return render_template('tecnicos/form.html', 
                         form=form, 
                         tecnico=tecnico,
                         titulo='Editar Técnico')


@tecnicos_bp.route('/<int:id>/eliminar', methods=['POST'])
@admin_required
def eliminar(id):
    """Elimina un técnico existente"""
    tecnico = Tecnico.query.get_or_404(id)

    # Verificar si tiene asignaciones
    if tecnico.asignaciones:
        flash('No se puede eliminar el técnico porque tiene asignaciones asociadas', 'error')
        return redirect(url_for('tecnicos.listar'))

    try:
        # Eliminar el técnico (que también eliminará el usuario por CASCADE)
        db.session.delete(tecnico)
        db.session.commit()
        flash('Técnico eliminado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el técnico: {str(e)}', 'error')
    
    return redirect(url_for('tecnicos.listar'))
