"""
Conexión centralizada a SQLite.

- get_db()  → Devuelve la conexión del request actual (patrón g de Flask).
- close_db() → Se registra como teardown y cierra al terminar cada request.
- init_db()  → Lee schema.sql y crea las tablas si no existen.
"""

import os
import sqlite3
from flask import g, current_app


def get_db():
    """Devuelve la conexión SQLite del request. Crea una si no existe."""
    if 'db' not in g:
        g.db = sqlite3.connect(current_app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row          # Acceso por nombre: row['campo']
        g.db.execute("PRAGMA foreign_keys = ON")  # Activar integridad referencial
    return g.db


def close_db(e=None):
    """Cierra la conexión al final del request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    """Crea las tablas leyendo schema.sql si la DB no existe o está vacía."""
    db_path = current_app.config['DATABASE']
    schema_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'schema.sql'
    )

    # Asegurar que el directorio instance/ existe
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    db = get_db()

    # Verificar si ya tiene tablas
    tablas = db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    ).fetchall()

    if len(tablas) == 0:
        # DB vacía, ejecutar esquema completo
        with open(schema_path, 'r', encoding='utf-8') as f:
            db.executescript(f.read())
        print("[OK] Base de datos creada desde schema.sql")
    else:
        # DB ya existe. Ejecutar con IF NOT EXISTS para añadir tablas nuevas sin romper.
        with open(schema_path, 'r', encoding='utf-8') as f:
            db.executescript(f.read())
