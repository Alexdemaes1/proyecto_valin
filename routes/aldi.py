"""
Rutas de Aldi — MVP: listado básico dentro del plan.
"""

from flask import Blueprint, render_template
from routes import login_required
from db import queries_operaciones as qo

bp = Blueprint('aldi', __name__, url_prefix='/aldi')


@bp.route('/')
@login_required
def index():
    planificaciones = qo.listar_planificaciones()
    return render_template('viajes/index.html',
                           planificaciones=planificaciones,
                           title='Control de Aldi',
                           modulo='aldi')
