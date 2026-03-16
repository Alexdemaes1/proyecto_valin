"""
Queries de autenticación y gestión de usuarios.
"""

from werkzeug.security import generate_password_hash, check_password_hash
from db.connection import get_db


def get_user_by_id(user_id):
    """Obtiene un usuario por su ID."""
    db = get_db()
    return db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def get_user_by_username(username):
    """Obtiene un usuario por su nombre de usuario."""
    db = get_db()
    return db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()


def verify_password(username, password):
    """Verifica las credenciales. Devuelve el usuario si son correctas, None si no."""
    user = get_user_by_username(username)
    if user and check_password_hash(user['password_hash'], password):
        return user
    return None


def get_user_role(user_id):
    """Obtiene el rol de un usuario."""
    db = get_db()
    return db.execute(
        "SELECT r.* FROM roles r JOIN users u ON u.role_id = r.id WHERE u.id = ?",
        (user_id,)
    ).fetchone()


def is_admin(user_id):
    """Comprueba si el usuario es administrador."""
    role = get_user_role(user_id)
    return role and role['name'] == 'Admin'


def ensure_admin_exists(password='10041004'):
    """Crea el rol Admin y el usuario admin si no existen. Se ejecuta al arrancar."""
    db = get_db()

    # Asegurar rol Admin
    admin_role = db.execute("SELECT id FROM roles WHERE name = 'Admin'").fetchone()
    if not admin_role:
        db.execute(
            "INSERT INTO roles (name, description) VALUES (?, ?)",
            ('Admin', 'Permisos ilimitados sobre el sistema.')
        )
        db.commit()
        admin_role = db.execute("SELECT id FROM roles WHERE name = 'Admin'").fetchone()

    # Asegurar usuario admin (solo se crea la primera vez, nunca se sobreescribe)
    admin_user = db.execute("SELECT id FROM users WHERE username = 'admin'").fetchone()
    if not admin_user:
        db.execute(
            "INSERT INTO users (username, email, password_hash, role_id) VALUES (?, ?, ?, ?)",
            ('admin', 'trafico@transportesvalin.com',
             generate_password_hash(password), admin_role['id'])
        )
        db.commit()
        print("[OK] Usuario 'admin' creado.")
