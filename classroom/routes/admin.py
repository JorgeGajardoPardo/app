from werkzeug.security import generate_password_hash
from flask import Blueprint, render_template, request, redirect, session, url_for
from bson.objectid import ObjectId
from models.db import db, fs
from utils.auth import admin_required

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/admin/panel')
@admin_required
def panel():
    cursos = db.cursos.find()
    return render_template('dashboard_admin.html', cursos=cursos)


@admin_bp.route('/admin/crear_curso', methods=['GET', 'POST'])
@admin_required
def crear_curso():
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        if not nombre or not descripcion:
            return render_template('crear_curso.html', error="Todos los campos son obligatorios")
        db.cursos.insert_one({'nombre': nombre, 'descripcion': descripcion})
        return render_template('crear_curso.html', mensaje="Curso creado exitosamente")
    return render_template('crear_curso.html')


@admin_bp.route('/admin/subir_clase/<curso_id>', methods=['GET', 'POST'])
@admin_required
def subir_clase(curso_id):
    curso = db.cursos.find_one({'_id': ObjectId(curso_id)})
    if not curso:
        return redirect('/admin/panel')
    if request.method == 'POST':
        titulo = request.form['titulo']
        archivo = request.files['archivo']
        if not titulo or not archivo:
            return render_template('subir_clase.html', curso=curso, error="Título y archivo son obligatorios")
        file_id = fs.put(archivo, filename=archivo.filename,
                         content_type=archivo.content_type)
        db.clases.insert_one({
            'id_curso': ObjectId(curso_id),
            'titulo': titulo,
            'archivo_id': file_id,
            'tipo': 'video'
        })
        return redirect('/admin/panel')
    return render_template('subir_clase.html', curso=curso)


@admin_bp.route('/admin/asignar_estudiante/<curso_id>', methods=['GET', 'POST'])
@admin_required
def asignar_estudiante(curso_id):
    curso = db.cursos.find_one({'_id': ObjectId(curso_id)})
    if not curso:
        return redirect('/admin/panel')

    estudiantes = db.usuarios.find({'rol': 'estudiante'})
    asignados = list(db.usuarios.find(
        {'cursos_asignados': ObjectId(curso_id)}))

    if request.method == 'POST':
        estudiante_id = ObjectId(request.form['estudiante_id'])
        db.usuarios.update_one(
            {'_id': estudiante_id},
            {'$addToSet': {'cursos_asignados': ObjectId(curso_id)}}
        )
        asignados = list(db.usuarios.find(
            {'cursos_asignados': ObjectId(curso_id)}))
        return render_template('asignar_estudiante.html', curso=curso, estudiantes=estudiantes, asignados=asignados, mensaje="Estudiante asignado exitosamente")

    return render_template('asignar_estudiante.html', curso=curso, estudiantes=estudiantes, asignados=asignados)


@admin_bp.route('/admin/ver_informes/<curso_id>')
@admin_required
def ver_informes(curso_id):
    curso = db.cursos.find_one({'_id': ObjectId(curso_id)})
    if not curso:
        return redirect('/admin/panel')

    informes = db.informes.find({'id_curso': ObjectId(curso_id)})
    lista = []
    for informe in informes:
        estudiante = db.usuarios.find_one({'_id': informe['id_usuario']})
        lista.append({
            'nombre_estudiante': estudiante['nombre'],
            'archivo_id': informe['archivo_id'],
            'informe_id': str(informe['_id'])
        })

    return render_template('ver_informes.html', curso=curso, informes=lista)


@admin_bp.route('/admin/descargar_informe/<archivo_id>')
@admin_required
def descargar_informe(archivo_id):
    archivo = fs.get(ObjectId(archivo_id))
    return archivo.read(), 200, {
        'Content-Type': archivo.content_type,
        'Content-Disposition': f'attachment; filename={archivo.filename}'
    }


@admin_bp.route('/admin/ver_informe/<archivo_id>')
@admin_required
def ver_informe(archivo_id):
    archivo = fs.get(ObjectId(archivo_id))
    return archivo.read(), 200, {
        'Content-Type': archivo.content_type,
        'Content-Disposition': f'inline; filename={archivo.filename}'
    }


@admin_bp.route('/admin/eliminar_curso/<curso_id>', methods=['POST'])
@admin_required
def eliminar_curso(curso_id):
    db.cursos.delete_one({'_id': ObjectId(curso_id)})
    db.clases.delete_many({'id_curso': ObjectId(curso_id)})
    db.informes.delete_many({'id_curso': ObjectId(curso_id)})
    db.usuarios.update_many(
        {'cursos_asignados': {'$type': 'array'}},
        {'$pull': {'cursos_asignados': ObjectId(curso_id)}}
    )
    return redirect('/admin/panel')


@admin_bp.route('/admin/quitar_estudiante/<curso_id>/<estudiante_id>', methods=['POST'])
@admin_required
def quitar_estudiante(curso_id, estudiante_id):
    db.usuarios.update_one(
        {'_id': ObjectId(estudiante_id), 'cursos_asignados': {
            '$type': 'array'}},
        {'$pull': {'cursos_asignados': ObjectId(curso_id)}}
    )
    return redirect(f'/admin/asignar_estudiante/{curso_id}')


@admin_bp.route('/admin/fix_tipo/<clase_id>')
@admin_required
def fix_tipo(clase_id):
    result = db.clases.update_one(
        {'_id': ObjectId(clase_id)},
        {'$set': {'tipo': 'video'}}
    )
    if result.modified_count == 1:
        return f"Clase {clase_id} actualizada con tipo: video"
    else:
        return f"No se actualizó la clase {clase_id}. ¿Ya tenía tipo o el ID es incorrecto?"
