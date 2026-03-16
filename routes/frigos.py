"""
Rutas de Frigos — MVP: listado básico dentro del plan.
"""

from flask import Blueprint, render_template, redirect, url_for, flash
from routes import login_required
from db import queries_operaciones as qo

bp = Blueprint('frigos', __name__, url_prefix='/frigos')


@bp.route('/')
@login_required
def index():
    planificaciones = qo.listar_planificaciones()
    return render_template('viajes/index.html',
                           planificaciones=planificaciones,
                           title='Control de Frigoríficos',
                           modulo='frigos')
