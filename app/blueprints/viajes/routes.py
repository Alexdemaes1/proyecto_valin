from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from . import bp
from app.models.operaciones import PlanificacionDia, ViajePollo
from app.models.maestros import Granja, Vehiculo, Conductor
from app.services.viajes_engine import ViajesEngine
from app.extensions import db
from datetime import datetime, date

@bp.route('/')
@login_required
def index():
    planificaciones = PlanificacionDia.query.order_by(PlanificacionDia.fecha_operativa.desc()).all()
    return render_template('viajes/index.html', planificaciones=planificaciones, title='Planificación Pollo Vivo')

@bp.route('/nueva', methods=['POST'])
@login_required
def crear_planificacion():
    fecha_str = request.form.get('fecha')
    if not fecha_str:
        flash("La fecha es obligatoria", "error")
        return redirect(url_for('viajes.index'))
    
    fecha_op = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    
    # Comprobar si ya existe
    existente = PlanificacionDia.query.filter_by(fecha_operativa=fecha_op).first()
    if existente:
        flash("Ya existe una planificación para esa fecha", "warning")
        return redirect(url_for('viajes.view_planificacion', id=existente.id))
        
    nueva = PlanificacionDia(
        fecha_operativa=fecha_op,
        dia_semana=fecha_op.strftime('%A').upper(),
        semana_excel=fecha_op.isocalendar()[1], # Fallback, se puede ajustar a legacy
        created_by=current_user.id
    )
    db.session.add(nueva)
    db.session.commit()
    return redirect(url_for('viajes.view_planificacion', id=nueva.id))

@bp.route('/<int:id>')
@login_required
def view_planificacion(id):
    plan = PlanificacionDia.query.get_or_4_4(id)
    granjas = Granja.query.filter_by(activo=True).order_by(Granja.codigo).all()
    vehiculos = Vehiculo.query.filter_by(activo=True).order_by(Vehiculo.codigo_interno).all()
    conductores = Conductor.query.filter_by(activo=True).order_by(Conductor.alias).all()
    
    return render_template('viajes/plan_maestra.html', 
                           plan=plan, 
                           granjas=granjas, 
                           vehiculos=vehiculos, 
                           conductores=conductores,
                           title=f"Plan {plan.fecha_operativa}")

@bp.route('/api/update_row', methods=['POST'])
@login_required
def update_row():
    """
    Ruta HTMX para actualización parcial de campos y recálculo inverso.
    """
    viaje_id = request.form.get('viaje_id')
    campo = request.form.get('campo') # 'granja_id', 'vehiculo_id', 'conductor_id', 'llegada'
    valor = request.form.get('valor')
    
    viaje = ViajePollo.query.get(viaje_id)
    if not viaje:
        return "Error: Viaje no encontrado", 404
        
    # Actualizar campo específico
    if campo == 'granja_id':
        viaje.granja_id = valor if valor else None
    elif campo == 'vehiculo_id':
        viaje.vehiculo_id = valor if valor else None
    elif campo == 'conductor_id':
        viaje.conductor_id = valor if valor else None
    elif campo == 'hora_llegada_matadero':
        viaje.hora_llegada_matadero = valor
    elif campo == 'moffett':
        viaje.moffett = valor
    elif campo == 'codigo_visual_extra':
        viaje.codigo_visual_extra = valor

    # Realizar recálculo si tenemos los datos necesarios
    if viaje.granja_id and viaje.hora_llegada_matadero and len(viaje.hora_llegada_matadero) == 5:
        granja = Granja.query.get(viaje.granja_id)
        if granja:
            res = ViajesEngine.calculate_reverse_times(
                viaje.hora_llegada_matadero,
                granja.tiempo_trayecto_min,
                granja.tiempo_carga_min,
                viaje.planificacion.fecha_operativa
            )
            viaje.hora_carga_granja_calc = res['carga_str']
            viaje.hora_salida_sueca_calc = res['salida_str']
            viaje.hora_fin_jornada_aprox_calc = res['fin_str']
            
    # Validar duplicidades (esto se puede sofisticar)
    # Por ahora marcamos alerta si el conductor se repite en esta planificacion
    duplicados = ViajePollo.query.filter_by(
        planificacion_id=viaje.planificacion_id, 
        conductor_id=viaje.conductor_id
    ).count()
    viaje.alerta_duplicidad_conductor = (duplicados > 1 and viaje.conductor_id is not None)

    db.session.commit()
    
    # Devolver la fila renderizada para que HTMX la reemplace
    return render_template('viajes/partials/viaje_row.html', viaje=viaje)

@bp.route('/<int:plan_id>/add_row', methods=['POST'])
@login_required
def add_row(plan_id):
    plan = PlanificacionDia.query.get_or_4_4(plan_id)
    last_orden = ViajePollo.query.filter_by(planificacion_id=plan_id).count()
    
    # Buscamos valores por defecto (ej la primera granja, vehiculo o dejar vacio)
    nuevo = ViajePollo(
        planificacion_id=plan_id,
        orden_visual=last_orden + 1,
        granja_id=request.form.get('def_granja_id') or None, # O permitir nulos en el modelo
        vehiculo_id=request.form.get('def_vehiculo_id') or None,
        conductor_id=request.form.get('def_conductor_id') or None,
        hora_llegada_matadero="00:00"
    )
    # Si mi modelo no permite nulos en granja_id, vehiculo_id etc (que creo que puse nullable=False)
    # necesitamos ids reales. Para el ejemplo, cojo los primeros activos.
    if not nuevo.granja_id:
        g = Granja.query.filter_by(activo=True).first()
        nuevo.granja_id = g.id if g else None
    if not nuevo.vehiculo_id:
        v = Vehiculo.query.filter_by(activo=True).first()
        nuevo.vehiculo_id = v.id if v else None
    if not nuevo.conductor_id:
        c = Conductor.query.filter_by(activo=True).first()
        nuevo.conductor_id = c.id if c else None
        
    db.session.add(nuevo)
    db.session.commit()
    
    return redirect(url_for('viajes.view_planificacion', id=plan_id))
