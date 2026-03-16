"""
Utilidades comunes para las rutas: decorador login_required y helper de usuario actual.
"""

from functools import wraps
from flask import session, redirect, url_for, flash, g
from db.connection import get_db


def login_required(f):
    """Decorador que exige sesión activa. Reemplaza Flask-Login."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor, inicie sesión para continuar.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


def get_current_user():
    """Devuelve los datos del usuario logueado, o None."""
    if 'user_id' not in session:
        return None
    if not hasattr(g, '_current_user') or g._current_user is None:
        db = get_db()
        g._current_user = db.execute(
            "SELECT * FROM users WHERE id = ?", (session['user_id'],)
        ).fetchone()
    return g._current_user
