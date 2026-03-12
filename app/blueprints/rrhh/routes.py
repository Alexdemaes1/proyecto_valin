from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required
from . import bp
from app.models.operaciones import PlanificacionDia, ViajePollo, ServicioFrigo, ServicioAldi
from app.models.rrhh import JornadaEmpleado
from app.models.maestros import Conductor
from app.services.rrhh_engine import RrhhEngine
from app.extensions import db
from datetime import datetime

@bp.route('/')
@login_required
def index():
    planificaciones = PlanificacionDia.query.order_by(PlanificacionDia.fecha_operativa.desc()).all()
    return render_template('rrhh/index.html', planificaciones=planificaciones, title='Control de Horarios y Nóminas')

@bp.route('/<int:plan_id>/generar_jornadas', methods=['POST'])
@login_required
def generar_jornadas(plan_id):
    """
    IMPORTANTE: Este es el motor de consolidación.
    Toma todos los viajes de un día y crea/actualiza JornadaEmpleado.
    """
    plan = PlanificacionDia.query.get_or_404(plan_id)
    
    # 1. Limpiar jornadas previas del día (o actualizar)
    JornadaEmpleado.query.filter_by(planificacion_id=plan_id).delete()
    
    # 2. Agrupar por conductor
    conductores_dia = set()
    viajes = ViajePollo.query.filter_by(planificacion_id=plan_id).all()
    frigos = ServicioFrigo.query.filter_by(planificacion_id=plan_id).all()
    aldis = ServicioAldi.query.filter_by(planificacion_id=plan_id).all()
    
    for v in viajes: conductores_dia.add(v.conductor_id)
    for f in frigos: conductores_dia.add(f.conductor_id)
    for a in aldis: conductores_dia.add(a.conductor_id)
    
    for c_id in conductores_dia:
        if not c_id: continue
        
        # Consolidar lógica:
        # Buscamos min(inicio) y max(fin) de todos sus servicios
        tiempos = []
        
        # Viajes Pollo
        v_conduct = [v for v in viajes if v.conductor_id == c_id]
        for v in v_conduct:
            if v.hora_salida_sueca_calc and v.hora_fin_jornada_aprox_calc:
                tiempos.append((v.hora_salida_sueca_calc, v.hora_fin_jornada_aprox_calc))
        
        # Frigos
        f_conduct = [f for f in frigos if f.conductor_id == c_id]
        for f in f_conduct:
            if f.hora_salida_sueca:
                # Asumimos jornada estándar 9h si no hay fin real
                tiempos.append((f.hora_salida_sueca, f.hora_salida_sueca)) 

        if not tiempos: continue
        
        # Simplificación: Cogemos el inicio más temprano y fin más tarde
        # Esto es lo que pide el Excel para "Doble Viaje"
        inicio_min = min([t[0] for t in tiempos])
        fin_max = max([t[1] for t in tiempos])
        
        # Calcular nocturnidad con el motor
        t_min, noct_min, noct_dec = RrhhEngine.calc_nocturnidad(inicio_min, fin_max, plan.fecha_operativa)
        
        nueva_jornada = JornadaEmpleado(
            planificacion_id=plan_id,
            conductor_id=c_id,
            hora_inicio_real=inicio_min,
            hora_fin_real=fin_max,
            horas_nocturnas_dec=noct_dec,
            # Lógica de tipo: Si hay > 1 viaje es tipo 2
            tipo_normalizado_interno='2' if len(tiempos) > 1 else '1',
            dieta=RrhhEngine.get_bonos_por_tipo('2' if len(tiempos) > 1 else '1')
        )
        db.session.add(nueva_jornada)
        
    db.session.commit()
    flash(f"Jornadas generadas para {len(conductores_dia)} conductores.", "success")
    return redirect(url_for('rrhh.view_horario', plan_id=plan_id))

@bp.route('/horario/<int:plan_id>')
@login_required
def view_horario(plan_id):
    plan = PlanificacionDia.query.get_or_404(plan_id)
    jornadas = JornadaEmpleado.query.filter_by(planificacion_id=plan_id).all()
    return render_template('rrhh/horario_dia.html', plan=plan, jornadas=jornadas, title=f"Horario {plan.fecha_operativa}")
