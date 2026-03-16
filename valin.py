"""
Punto de entrada de la aplicación Valin v2.

Configura Flask, registra rutas, inicializa DB y usuario admin.
Ejecutar: python valin.py
"""

import os
import secrets
from flask import Flask, redirect, url_for, session
from db.connection import close_db, init_db
from db.queries_auth import ensure_admin_exists
from services.config_manager import get_config, save_config

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def create_app():
    app = Flask(__name__,
                template_folder=os.path.join(BASE_DIR, 'templates'),
                static_folder=os.path.join(BASE_DIR, 'static'))

    # Configuración
    config = get_config()

    # Generar secret_key aleatorio en primera ejecución
    sk = config.get('secret_key', '')
    if not sk:
        sk = secrets.token_hex(32)
        save_config({'secret_key': sk})
    app.secret_key = sk
    app.config['DATABASE'] = os.path.join(BASE_DIR, 'instance', 'valin.db')

    # Asegurar directorios
    os.makedirs(os.path.join(BASE_DIR, 'instance', 'backups'), exist_ok=True)

    # Registrar cierre de conexión al final de cada request
    app.teardown_appcontext(close_db)

    # Inicializar DB y admin al arrancar
    with app.app_context():
        init_db()
        admin_pass = config.get('admin_password', '10041004')
        ensure_admin_exists(password=admin_pass)

    # Registrar blueprints
    from routes.auth import bp as auth_bp
    from routes.dashboard import bp as dashboard_bp
    from routes.maestros import bp as maestros_bp
    from routes.viajes import bp as viajes_bp
    from routes.frigos import bp as frigos_bp
    from routes.aldi import bp as aldi_bp
    from routes.rrhh import bp as rrhh_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(maestros_bp)
    app.register_blueprint(viajes_bp)
    app.register_blueprint(frigos_bp)
    app.register_blueprint(aldi_bp)
    app.register_blueprint(rrhh_bp)

    # Ruta raíz → dashboard o login
    @app.route('/')
    def index():
        if 'user_id' in session:
            return redirect(url_for('dashboard.index'))
        return redirect(url_for('auth.login'))

    return app


if __name__ == '__main__':
    config = get_config()
    app = create_app()
    port = config.get('port', 5000)
    debug = config.get('debug', False)
    print(f"\n  Sistema Valin v2 iniciado en http://127.0.0.1:{port}\n")
    # use_reloader=False evita que Flask lance un segundo proceso en Windows,
    # lo cual confunde a usuarios no técnicos y puede causar conflictos de puerto.
    try:
        app.run(debug=debug, port=port, use_reloader=False)
    except OSError as e:
        if 'Address already in use' in str(e) or '10048' in str(e):
            print(f"\n  ERROR: El puerto {port} ya está en uso.")
            print(f"  Esto ocurre si la aplicación ya está abierta en otra ventana.")
            print(f"  Cierre la otra ventana e inténtelo de nuevo.\n")
            input("  Pulse Enter para cerrar...")
        else:
            raise
