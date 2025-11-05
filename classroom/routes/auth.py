from flask import Blueprint, request, redirect, render_template, session, url_for, current_app
from extensions import bcrypt  # ✅ Ya no hay ciclo
from models.db import db
from utils.auth import admin_required

auth_bp = Blueprint('auth', __name__)


# Este bcrypt debe ser inicializado en tu app principal:
# from flask_bcrypt import Bcrypt
# bcrypt = Bcrypt(app)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = db.usuarios.find_one({'email': email})

        if user and bcrypt.check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])
            session['nombre'] = user['nombre']
            session['rol'] = user['rol']

            if user['rol'] == 'admin':
                return redirect('/admin/panel')
            elif user['rol'] == 'estudiante':
                return redirect('/student/panel')
            else:
                return render_template('login.html', error="Rol desconocido.")

        return render_template('login.html', error="Correo o contraseña incorrectos")

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))


@auth_bp.route('/crear_usuario', methods=['GET', 'POST'])
@admin_required
def crear_usuario():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        password = request.form['password']
        rol = request.form['rol']  # 'admin' o 'estudiante'

        if not nombre or not email or not password or rol not in ['admin', 'estudiante']:
            return render_template('crear_usuario.html', error="Todos los campos son obligatorios")

        if db.usuarios.find_one({'email': email}):
            return render_template('crear_usuario.html', error="Ya existe un usuario con ese email")

        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')

        db.usuarios.insert_one({
            'nombre': nombre,
            'email': email,
            'password': hashed_pw,
            'rol': rol,
            'cursos_asignados': [] if rol == 'estudiante' else None
        })

        return render_template('crear_usuario.html', mensaje="Usuario creado exitosamente")

    return render_template('crear_usuario.html')
