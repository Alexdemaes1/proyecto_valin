from flask import Blueprint

bp = Blueprint('maestros', __name__, url_prefix='/maestros')

from . import routes
