from flask import Blueprint

bp = Blueprint('aldi', __name__, url_prefix='/aldi')

from . import routes
