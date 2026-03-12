import os
from flask import Flask
from .extensions import db, migrate, login_manager, csrf
from .config import config_by_name

def create_app(config_name='dev'):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_by_name[config_name])

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Register blueprints (to be imported later when resolving circular refs)
    register_blueprints(app)

    return app

def register_blueprints(app):
    from .blueprints.auth import bp as auth_bp
    from .blueprints.dashboard import bp as dash_bp
    from .blueprints.maestros import bp as maest_bp
    from .blueprints.viajes import bp as viajes_bp
    from .blueprints.frigos import bp as frigos_bp
    from .blueprints.aldi import bp as aldi_bp
    from .blueprints.rrhh import bp as rrhh_bp
    from .blueprints.exports import bp as exports_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dash_bp)
    app.register_blueprint(maest_bp)
    app.register_blueprint(viajes_bp)
    app.register_blueprint(frigos_bp)
    app.register_blueprint(aldi_bp)
    app.register_blueprint(rrhh_bp)
    app.register_blueprint(exports_bp)
    # the rest will be populated as we build modules...
