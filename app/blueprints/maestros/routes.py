from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required
from . import bp
from .forms import VehiculoForm, ConductorForm, GranjaForm, RutaFrigoForm
from app.models.maestros import Vehiculo, Conductor, Granja, RutaFrigo
from app.extensions import db

@bp.route('/')
@login_required
def index():
    return render_template('maestros/index.html', title='Gestión de Datos Maestros')

# --- VEHICULOS ---
@bp.route('/vehiculos')
@login_required
def list_vehiculos():
    items = Vehiculo.query.all()
    return render_template('maestros/vehiculos.html', items=items, title='Vehículos')

@bp.route('/vehiculos/nuevo', methods=['GET', 'POST'])
@login_required
def create_vehiculo():
    form = VehiculoForm()
    if form.validate_on_submit():
        item = Vehiculo(
            codigo_interno=form.codigo_interno.data,
            matricula_tractora=form.matricula_tractora.data,
            matricula_semirremolque=form.matricula_semirremolque.data,
            activo=form.activo.data,
            observaciones=form.observaciones.data
        )
        db.session.add(item)
        db.session.commit()
        flash('Vehículo creado correctamente', 'success')
        return redirect(url_for('maestros.list_vehiculos'))
    return render_template('maestros/form_generic.html', form=form, title='Nuevo Vehículo')

# --- CONDUCTORES ---
@bp.route('/conductores')
@login_required
def list_conductores():
    items = Conductor.query.all()
    return render_template('maestros/conductores.html', items=items, title='Conductores')

@bp.route('/conductores/nuevo', methods=['GET', 'POST'])
@login_required
def create_conductor():
    form = ConductorForm()
    if form.validate_on_submit():
        item = Conductor(
            alias=form.alias.data,
            codigo_alfabetico=form.codigo_alfabetico.data,
            nombre_legal=form.nombre_legal.data,
            dni=form.dni.data,
            telefono=form.telefono.data,
            empresa=form.empresa.data,
            activo=form.activo.data,
            notas=form.notas.data
        )
        db.session.add(item)
        db.session.commit()
        flash('Conductor creado correctamente', 'success')
        return redirect(url_for('maestros.list_conductores'))
    return render_template('maestros/form_generic.html', form=form, title='Nuevo Conductor')

# --- GRANJAS ---
@bp.route('/granjas')
@login_required
def list_granjas():
    items = Granja.query.all()
    return render_template('maestros/granjas.html', items=items, title='Granjas')

@bp.route('/granjas/nuevo', methods=['GET', 'POST'])
@login_required
def create_granja():
    form = GranjaForm()
    if form.validate_on_submit():
        item = Granja(
            codigo=form.codigo.data,
            nombre_cliente=form.nombre_cliente.data,
            localidad=form.localidad.data,
            plantas=form.plantas.data,
            tiempo_trayecto_min=form.tiempo_trayecto_min.data,
            tiempo_carga_min=form.tiempo_carga_min.data,
            telefono_1=form.telefono_1.data,
            telefono_2=form.telefono_2.data,
            ubicacion_url=form.ubicacion_url.data,
            anotaciones=form.anotaciones.data,
            activo=form.activo.data
        )
        db.session.add(item)
        db.session.commit()
        flash('Granja creada correctamente', 'success')
        return redirect(url_for('maestros.list_granjas'))
    return render_template('maestros/form_generic.html', form=form, title='Nueva Granja')
