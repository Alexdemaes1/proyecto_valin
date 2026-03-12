from flask import Blueprint

bp = Blueprint('frigos', __name__, url_prefix='/frigos')

from . import routes
