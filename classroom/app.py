from flask import Flask, session, redirect, url_for, send_file
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.student import student_bp
from config import SECRET_KEY
from models.db import fs
from bson.objectid import ObjectId
import io
from extensions import bcrypt

app = Flask(__name__)
app.secret_key = SECRET_KEY

# ✅ bcrypt vinculado correctamente a la única instancia de app
bcrypt.init_app(app)

# Registra los blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(student_bp)


@app.route('/')
def index():
    return redirect(url_for('auth.login'))


@app.route('/dashboard')
def dashboard():
    if 'rol' not in session:
        return redirect(url_for('auth.login'))
    if session['rol'] == 'admin':
        return redirect(url_for('admin.panel'))
    elif session['rol'] == 'estudiante':
        return redirect(url_for('student.panel'))
    return "Rol desconocido"


@app.route('/descargar/<archivo_id>')
def descargar(archivo_id):
    try:
        file = fs.get(ObjectId(archivo_id))
        return send_file(io.BytesIO(file.read()), download_name=file.filename, mimetype=file.content_type)
    except Exception as e:
        return f"Error al descargar el archivo: {str(e)}"


if __name__ == '__main__':
    app.run(debug=True)
