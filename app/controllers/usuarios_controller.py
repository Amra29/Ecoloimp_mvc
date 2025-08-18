from flask import Blueprint, request, render_template, redirect, url_for, flash
from app.models.models import db, Usuario
from flask_login import login_required

usuarios_bp = Blueprint('usuarios', __name__, url_prefix='/usuarios')

@usuarios_bp.route('/')
@login_required
def listar():
    usuarios = Usuario.query.all()
    return render_template('usuarios/listar.html', usuarios=usuarios)

@usuarios_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        password_hash = request.form['password'] # Debes hashear la contraseña antes de guardar
        rol = request.form.get('rol', 'tecnico')
        usuario = Usuario(nombre=nombre, email=email, password_hash=password_hash, rol=rol)
        db.session.add(usuario)
        db.session.commit()
        flash('Usuario creado correctamente.')
        return redirect(url_for('usuarios.listar'))
    return render_template('usuarios/nuevo.html')

@usuarios_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    usuario = Usuario.query.get_or_404(id)
    if request.method == 'POST':
        usuario.nombre = request.form['nombre']
        usuario.email = request.form['email']
        usuario.rol = request.form.get('rol', usuario.rol)
        db.session.commit()
        flash('Usuario actualizado correctamente.')
        return redirect(url_for('usuarios.listar'))
    return render_template('usuarios/editar.html', usuario=usuario)

@usuarios_bp.route('/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar(id):
    usuario = Usuario.query.get_or_404(id)
    db.session.delete(usuario)
    db.session.commit()
    flash('Usuario eliminado correctamente.')
    return redirect(url_for('usuarios.listar'))