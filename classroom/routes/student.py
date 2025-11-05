from flask import Blueprint, render_template, request, redirect, session, url_for
from bson.objectid import ObjectId
from models.db import db, fs
from utils.auth import student_required

student_bp = Blueprint('student', __name__)


@student_bp.route('/student/panel')
@student_required
def panel():
    user_id = ObjectId(session['user_id'])
    user = db.usuarios.find_one({'_id': user_id})
    cursos = db.cursos.find({'_id': {'$in': user.get('cursos_asignados', [])}})
    return render_template('dashboard_student.html', cursos=cursos)


@student_bp.route('/student/ver_clases/<curso_id>')
@student_required
def ver_clases(curso_id):
    user_id = ObjectId(session['user_id'])
    user = db.usuarios.find_one({'_id': user_id})

    if ObjectId(curso_id) not in user.get('cursos_asignados', []):
        return redirect('/student/panel')

    clases = db.clases.find({'id_curso': ObjectId(curso_id)})
    curso = db.cursos.find_one({'_id': ObjectId(curso_id)})
    return render_template('view_classes.html', clases=clases, curso=curso)


@student_bp.route('/student/subir_informe/<curso_id>', methods=['GET', 'POST'])
@student_required
def subir_informe(curso_id):
    user_id = ObjectId(session['user_id'])
    user = db.usuarios.find_one({'_id': user_id})

    if ObjectId(curso_id) not in user.get('cursos_asignados', []):
        return redirect('/student/panel')  # o mostrar error

    if request.method == 'POST':
        archivo = request.files['archivo']
        file_id = fs.put(archivo, filename=archivo.filename,
                         content_type=archivo.content_type)
        db.informes.insert_one({
            'id_usuario': user_id,
            'id_curso': ObjectId(curso_id),
            'archivo_id': file_id
        })
        return redirect('/student/panel')

    return render_template('upload_report.html', curso_id=curso_id)


@student_bp.route('/student/curso/<curso_id>')
@student_required
def ver_contenido(curso_id):
    user_id = ObjectId(session['user_id'])
    user = db.usuarios.find_one({'_id': user_id})

    if ObjectId(curso_id) not in user.get('cursos_asignados', []):
        return redirect('/student/panel')  # o mostrar error

    curso = db.cursos.find_one({'_id': ObjectId(curso_id)})
    clases = db.clases.find({'id_curso': ObjectId(curso_id)})
    return render_template('ver_contenido.html', curso=curso, clases=clases)


@student_bp.route('/student/clase/<clase_id>')
@student_required
def ver_clase_individual(clase_id):
    clase = db.clases.find_one({'_id': ObjectId(clase_id)})
    curso = db.cursos.find_one({'_id': clase['id_curso']})
    return render_template('ver_clase.html', clase=clase, curso=curso)


@student_bp.route('/student/video/<file_id>')
@student_required
def ver_video(file_id):
    archivo = fs.get(ObjectId(file_id))
    return archivo.read(), 200, {
        'Content-Type': archivo.content_type,
        'Content-Disposition': 'inline; filename="video.mp4"'
    }
