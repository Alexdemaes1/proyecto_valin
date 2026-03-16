"""
Rutas de RRHH: generación de jornadas y visualización de horarios.
"""

from flask import Blueprint, render_template, redirect, url_for, flash
from datetime import datetime
from routes import login_required
from db import queries_operaciones as qo
from db import queries_rrhh as qr
from engines.rrhh_engine import RrhhEngine

bp = Blueprint('rrhh', __name__, url_prefix='/rrhh')


@bp.route('/')
@login_required
def index():
    planificaciones = qo.listar_planificaciones()
    return render_template('rrhh/index.html',
                           planificaciones=planificaciones,
                           title='Control de Horarios y Nóminas')


@bp.route('/<int:plan_id>/generar', methods=['POST'])
@login_required
def generar_jornadas(plan_id):
    """Motor de consolidación: genera jornadas a partir de los servicios del día."""
    plan = qo.obtener_planificacion(plan_id)
    if not plan:
        flash('Planificación no encontrada.', 'danger')
        return redirect(url_for('rrhh.index'))

    # Limpiar jornadas previas
    qr.borrar_jornadas_plan(plan_id)

    # Obtener conductores únicos del día
    conductores = qr.obtener_conductores_en_plan(plan_id)
    fecha_op = datetime.strptime(plan['fecha_operativa'], '%Y-%m-%d').date()
    generados = 0

    for c_id in conductores:
        tiempos = qr.obtener_horarios_conductor_en_plan(plan_id, c_id)
        if not tiempos:
            continue

        # Consolidar: min(inicio) y max(fin)
        inicio_min = min(t[0] for t in tiempos)
        fin_max = max(t[1] for t in tiempos)

        # Calcular nocturnidad
        try:
            t_min, noct_min, noct_dec = RrhhEngine.calc_nocturnidad(
                inicio_min, fin_max, fecha_op
            )
        except Exception:
            t_min, noct_min, noct_dec = 0, 0, 0.0

        tipo = '2' if len(tiempos) > 1 else '1'

        qr.crear_jornada(
            plan_id=plan_id,
            fecha=plan['fecha_operativa'],
            conductor_id=c_id,
            tipo_jornada=tipo,
            hora_inicio=inicio_min,
            hora_fin=fin_max,
            horas_trabajadas_min=t_min,
            horas_nocturnas_min=noct_min,
            horas_nocturnas_decimal=noct_dec,
            dieta_bool=1 if RrhhEngine.get_bonos_por_tipo(tipo) else 0,
            viajes_count=len(tiempos),
            semana_excel=plan['semana_excel']
        )
        generados += 1

    flash(f'Jornadas generadas para {generados} conductores.', 'success')
    return redirect(url_for('rrhh.horario', plan_id=plan_id))


@bp.route('/horario/<int:plan_id>')
@login_required
def horario(plan_id):
    plan = qo.obtener_planificacion(plan_id)
    if not plan:
        flash('Planificación no encontrada.', 'danger')
        return redirect(url_for('rrhh.index'))

    jornadas = qr.listar_jornadas_plan(plan_id)
    return render_template('rrhh/horario.html',
                           plan=plan,
                           jornadas=jornadas,
                           title=f"Horario {plan['fecha_operativa']}")
