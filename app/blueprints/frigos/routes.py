from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required
from . import bp
from app.models.operaciones import PlanificacionDia, ServicioFrigo
from app.models.maestros import RutaFrigo, Vehiculo, Conductor
from app.extensions import db
from datetime import datetime

@bp.route('/')
@login_required
def index():
    planificaciones = PlanificacionDia.query.order_by(PlanificacionDia.fecha_operativa.desc()).all()
    return render_template('frigos/index.html', planificaciones=planificaciones, title='Servicios Frigoríficos')

@bp.route('/<int:id>')
@login_required
def view_planificacion(id):
    plan = PlanificacionDia.query.get_or_404(id)
    rutas = RutaFrigo.query.filter_by(activo=True).order_by(RutaFrigo.codigo_ruta).all()
    vehiculos = Vehiculo.query.filter_by(activo=True).order_by(Vehiculo.codigo_interno).all()
    conductores = Conductor.query.filter_by(activo=True).order_by(Conductor.alias).all()
    
    return render_template('frigos/plan_frigo.html', 
                           plan=plan, 
                           rutas=rutas, 
                           vehiculos=vehiculos, 
                           conductores=conductores,
                           title=f"Frigos {plan.fecha_operativa}")

@bp.route('/api/update_row', methods=['POST'])
@login_required
def update_row():
    servicio_id = request.form.get('servicio_id')
    campo = request.form.get('campo')
    valor = request.form.get('valor')
    
    servicio = ServicioFrigo.query.get(servicio_id)
    if not servicio:
        return "Error", 404
        
    if campo == 'ruta_frigo_id':
        servicio.ruta_frigo_id = valor if valor else None
        # Recalcular texto si procede
        if servicio.ruta_frigo_id:
            ruta = RutaFrigo.query.get(servicio.ruta_frigo_id)
            if ruta:
                servicio.texto_trayecto_calc = f"{ruta.codigo_ruta} - {ruta.poblacion}".upper()
    elif campo == 'vehiculo_id':
        servicio.vehiculo_id = valor if valor else None
    elif campo == 'conductor_id':
        servicio.conductor_id = valor if valor else None
    elif campo == 'hora_salida_sueca':
        servicio.hora_salida_sueca = valor
    elif campo == 'observaciones':
        servicio.observaciones = valor

    db.session.commit()
    return render_template('frigos/partials/frigo_row.html', s=servicio)

@bp.route('/<int:plan_id>/add_row', methods=['POST'])
@login_required
def add_row(plan_id):
    plan = PlanificacionDia.query.get_or_404(plan_id)
    
    ruta = RutaFrigo.query.filter_by(activo=True).first()
    veh = Vehiculo.query.filter_by(activo=True).first()
    cond = Conductor.query.filter_by(activo=True).first()
    
    nuevo = ServicioFrigo(
        planificacion_id=plan_id,
        ruta_frigo_id=ruta.id if ruta else None,
        vehiculo_id=veh.id if veh else None,
        conductor_id=cond.id if cond else None,
        hora_salida_sueca="06:00"
    )
    
    db.session.add(nuevo)
    db.session.commit()
    return redirect(url_for('frigos.view_planificacion', id=plan_id))
