from functools import wraps
from flask import session, redirect, url_for


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'rol' not in session or session['rol'] != 'admin':
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return wrapper


def student_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'rol' not in session or session['rol'] != 'estudiante':
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return wrapper
