"""
Rutas de planificación de viajes (Pollo Vivo).
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from datetime import datetime
from routes import login_required
from db import queries_operaciones as qo
from db import queries_maestros as qm
from engines.viajes_engine import ViajesEngine

bp = Blueprint('viajes', __name__, url_prefix='/viajes')


@bp.route('/')
@login_required
def index():
    planificaciones = qo.listar_planificaciones()
    return render_template('viajes/index.html',
                           planificaciones=planificaciones,
                           title='Planificación Pollo Vivo')


@bp.route('/nueva', methods=['POST'])
@login_required
def crear_planificacion():
    fecha_str = request.form.get('fecha', '').strip()
    if not fecha_str:
        flash('La fecha es obligatoria.', 'warning')
        return redirect(url_for('viajes.index'))

    # Comprobar si ya existe
    existente = qo.obtener_planificacion_por_fecha(fecha_str)
    if existente:
        flash('Ya existe una planificación para esa fecha.', 'warning')
        return redirect(url_for('viajes.plan', id=existente['id']))

    try:
        fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        dias_es = {0: 'LUNES', 1: 'MARTES', 2: 'MIÉRCOLES', 3: 'JUEVES',
                   4: 'VIERNES', 5: 'SÁBADO', 6: 'DOMINGO'}
        dia_semana = dias_es.get(fecha_obj.weekday(), '')

        plan_id = qo.crear_planificacion(
            fecha_operativa=fecha_str,
            dia_semana=dia_semana,
            semana_excel=fecha_obj.isocalendar()[1],
            created_by=session.get('user_id')
        )
        flash('Planificación creada.', 'success')
        return redirect(url_for('viajes.plan', id=plan_id))
    except Exception as e:
        flash(f'Error al crear planificación: {e}', 'danger')
        return redirect(url_for('viajes.index'))


@bp.route('/<int:id>')
@login_required
def plan(id):
    plan = qo.obtener_planificacion(id)
    if not plan:
        flash('Planificación no encontrada.', 'danger')
        return redirect(url_for('viajes.index'))

    viajes = qo.listar_viajes_plan(id)
    granjas = qm.listar_granjas()
    vehiculos = qm.listar_vehiculos()
    conductores = qm.listar_conductores()

    return render_template('viajes/plan.html',
                           plan=plan,
                           viajes=viajes,
                           granjas=granjas,
                           vehiculos=vehiculos,
                           conductores=conductores,
                           title=f"Plan {plan['fecha_operativa']}")


@bp.route('/<int:plan_id>/add', methods=['POST'])
@login_required
def add_viaje(plan_id):
    plan = qo.obtener_planificacion(plan_id)
    if not plan:
        flash('Planificación no encontrada.', 'danger')
        return redirect(url_for('viajes.index'))

    qo.crear_viaje(
        plan_id=plan_id,
        granja_id=request.form.get('granja_id') or None,
        vehiculo_id=request.form.get('vehiculo_id') or None,
        conductor_id=request.form.get('conductor_id') or None,
        hora_llegada=request.form.get('hora_llegada', '00:00')
    )
    flash('Viaje añadido.', 'success')
    return redirect(url_for('viajes.plan', id=plan_id))


@bp.route('/viaje/<int:viaje_id>/actualizar', methods=['POST'])
@login_required
def actualizar_viaje(viaje_id):
    """Actualiza un campo de un viaje y recalcula horarios si es necesario."""
    from db.connection import get_db
    db = get_db()

    viaje = db.execute("SELECT * FROM viajes_pollos WHERE id = ?", (viaje_id,)).fetchone()
    if not viaje:
        flash('Viaje no encontrado.', 'danger')
        return redirect(url_for('viajes.index'))

    # Actualizar todos los campos del formulario
    campos = {}
    for key in ['granja_id', 'vehiculo_id', 'conductor_id', 'hora_llegada_matadero',
                'moffett', 'codigo_visual_extra', 'notas']:
        val = request.form.get(key)
        if val is not None:
            campos[key] = val if val else None

    if campos:
        qo.actualizar_viaje(viaje_id, **campos)

    # Recalcular horarios si tenemos granja y hora de llegada
    viaje = db.execute("SELECT * FROM viajes_pollos WHERE id = ?", (viaje_id,)).fetchone()
    granja_id = viaje['granja_id']
    hora_llegada = viaje['hora_llegada_matadero']

    if granja_id and hora_llegada and len(hora_llegada) == 5:
        granja = qm.obtener_granja(granja_id)
        if granja:
            plan = qo.obtener_planificacion(viaje['planificacion_id'])
            fecha_op = datetime.strptime(plan['fecha_operativa'], '%Y-%m-%d').date()
            res = ViajesEngine.calculate_reverse_times(
                hora_llegada,
                granja['tiempo_trayecto_min'],
                granja['tiempo_carga_min'],
                fecha_op
            )
            qo.actualizar_viaje(viaje_id,
                                hora_carga_granja_calc=res['carga_str'],
                                hora_salida_sueca_calc=res['salida_str'],
                                hora_fin_jornada_aprox_calc=res['fin_str'])

    # Comprobar duplicidad de conductor
    conductor_id = viaje['conductor_id']
    if conductor_id:
        count = qo.contar_viajes_conductor_en_plan(viaje['planificacion_id'], conductor_id)
        qo.actualizar_viaje(viaje_id, alerta_duplicidad_conductor=1 if count > 1 else 0)

    return redirect(url_for('viajes.plan', id=viaje['planificacion_id']))


@bp.route('/viaje/<int:viaje_id>/eliminar', methods=['POST'])
@login_required
def eliminar_viaje(viaje_id):
    from db.connection import get_db
    db = get_db()
    viaje = db.execute("SELECT planificacion_id FROM viajes_pollos WHERE id = ?", (viaje_id,)).fetchone()
    if viaje:
        qo.eliminar_viaje(viaje_id)
        flash('Viaje eliminado.', 'info')
        return redirect(url_for('viajes.plan', id=viaje['planificacion_id']))
    flash('Viaje no encontrado.', 'danger')
    return redirect(url_for('viajes.index'))
