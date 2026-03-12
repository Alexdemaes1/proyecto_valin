from flask import Blueprint

bp = Blueprint('rrhh', __name__, url_prefix='/rrhh')

from . import routes
