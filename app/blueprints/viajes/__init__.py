from flask import Blueprint

bp = Blueprint('viajes', __name__, url_prefix='/viajes')

from . import routes
