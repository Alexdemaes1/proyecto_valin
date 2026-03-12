from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required
from . import bp
from app.models.operaciones import PlanificacionDia, ServicioAldi
from app.models.maestros import Tienda, Vehiculo, Conductor
from app.services.aldi_engine import AldiEngine
from app.extensions import db

@bp.route('/')
@login_required
def index():
    planificaciones = PlanificacionDia.query.order_by(PlanificacionDia.fecha_operativa.desc()).all()
    return render_template('aldi/index.html', planificaciones=planificaciones, title='Planificación ALDI')

@bp.route('/<int:id>')
@login_required
def view_planificacion(id):
    plan = PlanificacionDia.query.get_or_404(id)
    tiendas = Tienda.query.filter_by(activo=True).order_by(Tienda.nombre).all()
    vehiculos = Vehiculo.query.filter_by(activo=True).order_by(Vehiculo.codigo_interno).all()
    conductores = Conductor.query.filter_by(activo=True).order_by(Conductor.alias).all()
    
    return render_template('aldi/plan_aldi.html', 
                           plan=plan, 
                           tiendas=tiendas, 
                           vehiculos=vehiculos, 
                           conductores=conductores,
                           title=f"ALDI {plan.fecha_operativa}")

@bp.route('/api/update_row', methods=['POST'])
@login_required
def update_row():
    servicio_id = request.form.get('servicio_id')
    campo = request.form.get('campo')
    valor = request.form.get('valor')
    
    servicio = ServicioAldi.query.get(servicio_id)
    if not servicio:
        return "Error", 404
        
    if campo == 'vehiculo_id':
        servicio.vehiculo_id = valor if valor else None
    elif campo == 'conductor_id':
        servicio.conductor_id = valor if valor else None
    elif campo in ['tienda_1_id', 'tienda_2_id', 'tienda_3_id', 'tienda_4_id']:
        setattr(servicio, campo, valor if valor else None)
        # Recalcular texto unificado ALDI
        tiendas_ids = [servicio.tienda_1_id, servicio.tienda_2_id, servicio.tienda_3_id, servicio.tienda_4_id]
        nombres = []
        for tid in tiendas_ids:
            if tid:
                t = Tienda.query.get(tid)
                if t: nombres.append(t.nombre)
        servicio.texto_trayecto_calc = AldiEngine.generar_texto_trayecto_aldi(nombres)
    elif campo == 'hora_inicio_real':
        servicio.hora_inicio_real = valor
    elif campo == 'observaciones':
        servicio.observaciones = valor

    db.session.commit()
    return render_template('aldi/partials/aldi_row.html', s=servicio, tiendas=Tienda.query.filter_by(activo=True).all(), vehiculos=Vehiculo.query.all(), conductores=Conductor.query.all())

@bp.route('/<int:plan_id>/add_row', methods=['POST'])
@login_required
def add_row(plan_id):
    plan = PlanificacionDia.query.get_or_404(plan_id)
    
    veh = Vehiculo.query.filter_by(activo=True).first()
    cond = Conductor.query.filter_by(activo=True).first()
    
    nuevo = ServicioAldi(
        planificacion_id=plan_id,
        vehiculo_id=veh.id if veh else None,
        conductor_id=cond.id if cond else None,
        base_origen='SAGUNTO',
        texto_trayecto_calc='SAGUNTO'
    )
    
    db.session.add(nuevo)
    db.session.commit()
    return redirect(url_for('aldi.view_planificacion', id=plan_id))
