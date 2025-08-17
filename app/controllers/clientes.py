"""
Controlador para la gestión de clientes
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from sqlalchemy import or_
from app.models.models import db, Cliente, Sucursal, Equipo, Visita
from app.forms import ClienteForm, BuscarClienteForm
from app.decorators import admin_required

# Crear blueprint
clientes_bp = Blueprint('clientes', __name__, url_prefix='/clientes')


@clientes_bp.route('/')
@login_required
def listar():
    """Lista todos los clientes con opciones de filtrado"""
    form = BuscarClienteForm()
    
    # Inicializar consulta
    query = Cliente.query
    
    # Aplicar filtros si se envió el formulario
    if request.args.get('buscar'):
        if form.termino_busqueda.data:
            termino = f"%{form.termino_busqueda.data}%"
            query = query.filter(
                or_(
                    Cliente.nombre.ilike(termino),
                    Cliente.rfc.ilike(termino),
                    Cliente.email.ilike(termino),
                    Cliente.telefono.ilike(termino)
                )
            )
        if form.activo.data is not None:
            query = query.filter_by(activo=form.activo.data)
    
    # Ordenar por nombre
    query = query.order_by(Cliente.nombre)
    
    # Paginación
    page = request.args.get('page', 1, type=int)
    por_pagina = 15
    clientes = query.paginate(page=page, per_page=por_pagina, error_out=False)
    
    return render_template('clientes/listar.html', 
                         clientes=clientes,
                         form=form,
                         titulo='Clientes')


@clientes_bp.route('/nuevo', methods=['GET', 'POST'])
@admin_required
def nuevo():
    """Crea un nuevo cliente"""
    form = ClienteForm()
    
    if form.validate_on_submit():
        try:
            cliente = Cliente(
                nombre=form.nombre.data.strip(),
                rfc=form.rfc.data.upper().strip() if form.rfc.data else None,
                email=form.email.data.lower().strip() if form.email.data else None,
                telefono=form.telefono.data.strip() if form.telefono.data else None,
                direccion=form.direccion.data.strip() if form.direccion.data else None,
                contacto_principal=form.contacto_principal.data.strip() if form.contacto_principal.data else None,
                telefono_contacto=form.telefono_contacto.data.strip() if form.telefono_contacto.data else None,
                email_contacto=form.email_contacto.data.lower().strip() if form.email_contacto.data else None,
                tipo_cliente=form.tipo_cliente.data,
                dias_credito=form.dias_credito.data if form.dias_credito.data else 0,
                limite_credito=form.limite_credito.data if form.limite_credito.data else 0,
                activo=form.activo.data,
                notas=form.notas.data.strip() if form.notas.data else None,
                creado_por=current_user.id
            )
            
            db.session.add(cliente)
            db.session.commit()
            
            flash(f'Cliente {cliente.nombre} registrado correctamente.', 'success')
            return redirect(url_for('clientes.detalle', id=cliente.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar el cliente: {str(e)}', 'error')
    
    return render_template('clientes/form.html', 
                         form=form, 
                         titulo='Nuevo Cliente')


@clientes_bp.route('/<int:id>')
@login_required
def detalle(id):
    """Muestra los detalles de un cliente"""
    cliente = Cliente.query.get_or_404(id)
    
    # Obtener estadísticas
    estadisticas = {
        'sucursales': Sucursal.query.filter_by(cliente_id=id, activo=True).count(),
        'equipos': Equipo.query.filter_by(cliente_id=id, activo=True).count(),
        'visitas': Visita.query.join(Sucursal).filter(Sucursal.cliente_id == id).count(),
        'ultima_visita': Visita.query.join(Sucursal)
            .filter(Sucursal.cliente_id == id)
            .order_by(Visita.fecha_visita.desc())
            .first()
    }
    
    # Obtener sucursales activas
    sucursales = Sucursal.query.filter_by(
        cliente_id=id, 
        activo=True
    ).order_by('nombre').all()
    
    # Obtener equipos recientes
    equipos = Equipo.query.filter_by(
        cliente_id=id,
        activo=True
    ).order_by(Equipo.fecha_registro.desc()).limit(5).all()
    
    # Obtener visitas recientes
    visitas = Visita.query.join(Sucursal).filter(
        Sucursal.cliente_id == id
    ).order_by(Visita.fecha_visita.desc()).limit(5).all()
    
    return render_template('clientes/detalle.html',
                         cliente=cliente,
                         estadisticas=estadisticas,
                         sucursales=sucursales,
                         equipos=equipos,
                         visitas=visitas)


@clientes_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@admin_required
def editar(id):
    """Edita un cliente existente"""
    cliente = Cliente.query.get_or_404(id)
    form = ClienteForm(obj=cliente)
    
    if form.validate_on_submit():
        try:
            cliente.nombre = form.nombre.data.strip()
            cliente.rfc = form.rfc.data.upper().strip() if form.rfc.data else None
            cliente.email = form.email.data.lower().strip() if form.email.data else None
            cliente.telefono = form.telefono.data.strip() if form.telefono.data else None
            cliente.direccion = form.direccion.data.strip() if form.direccion.data else None
            cliente.contacto_principal = form.contacto_principal.data.strip() if form.contacto_principal.data else None
            cliente.telefono_contacto = form.telefono_contacto.data.strip() if form.telefono_contacto.data else None
            cliente.email_contacto = form.email_contacto.data.lower().strip() if form.email_contacto.data else None
            cliente.tipo_cliente = form.tipo_cliente.data
            cliente.dias_credito = form.dias_credito.data if form.dias_credito.data else 0
            cliente.limite_credito = form.limite_credito.data if form.limite_credito.data else 0
            cliente.activo = form.activo.data
            cliente.notas = form.notas.data.strip() if form.notas.data else None
            
            db.session.commit()
            
            flash('Cliente actualizado correctamente.', 'success')
            return redirect(url_for('clientes.detalle', id=cliente.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el cliente: {str(e)}', 'error')
    
    return render_template('clientes/form.html', 
                         form=form, 
                         cliente=cliente,
                         titulo='Editar Cliente')


@clientes_bp.route('/<int:id>/eliminar', methods=['POST'])
@admin_required
def eliminar(id):
    """Elimina un cliente (borrado lógico)"""
    cliente = Cliente.query.get_or_404(id)
    
    # Verificar si el cliente tiene sucursales o equipos activos
    if Sucursal.query.filter_by(cliente_id=id, activo=True).count() > 0:
        flash('No se puede desactivar el cliente porque tiene sucursales activas.', 'error')
        return redirect(url_for('clientes.detalle', id=id))
    
    if Equipo.query.filter_by(cliente_id=id, activo=True).count() > 0:
        flash('No se puede desactivar el cliente porque tiene equipos activos.', 'error')
        return redirect(url_for('clientes.detalle', id=id))
    
    try:
        # Realizar borrado lógico
        cliente.activo = False
        cliente.fecha_baja = db.func.now()
        db.session.commit()
        
        flash('Cliente desactivado correctamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al desactivar el cliente: {str(e)}', 'error')
    
    return redirect(url_for('clientes.listar'))


@clientes_bp.route('/buscar-ajax')
@login_required
def buscar_ajax():
    """Búsqueda de clientes para AJAX (usado en formularios)"""
    query = request.args.get('q', '').strip()
    
    if len(query) < 2:
        return jsonify([])
    
    # Buscar por nombre o RFC
    resultados = Cliente.query.filter(
        (Cliente.nombre.ilike(f'%{query}%')) |
        (Cliente.rfc.ilike(f'%{query}%'))
    ).filter_by(activo=True).limit(10).all()
    
    # Formatear resultados para Select2
    data = [{
        'id': c.id,
        'text': f"{c.nombre} ({c.rfc})" if c.rfc else c.nombre
    } for c in resultados]
    
    return jsonify(data)
