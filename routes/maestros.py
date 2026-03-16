"""
Rutas de datos maestros: vehículos, conductores, granjas.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from routes import login_required
from db import queries_maestros as qm

bp = Blueprint('maestros', __name__, url_prefix='/maestros')


@bp.route('/')
@login_required
def index():
    return render_template('maestros/index.html', title='Datos Maestros')


# ─── VEHÍCULOS ──────────────────────────────────────────────────
@bp.route('/vehiculos')
@login_required
def list_vehiculos():
    items = qm.listar_vehiculos(solo_activos=False)
    return render_template('maestros/listado.html',
                           items=items,
                           tipo='vehiculo',
                           columnas=['codigo_interno', 'matricula_tractora', 'matricula_semirremolque', 'activo'],
                           cabeceras=['Código', 'Matrícula Tractora', 'Matrícula Semirremolque', 'Activo'],
                           title='Vehículos')


@bp.route('/vehiculos/nuevo', methods=['GET', 'POST'])
@login_required
def create_vehiculo():
    if request.method == 'POST':
        codigo = request.form.get('codigo_interno', '').strip()
        if not codigo:
            flash('El código interno es obligatorio.', 'warning')
        else:
            try:
                qm.crear_vehiculo(
                    codigo_interno=codigo,
                    matricula_tractora=request.form.get('matricula_tractora', ''),
                    matricula_semirremolque=request.form.get('matricula_semirremolque', ''),
                    observaciones=request.form.get('observaciones', '')
                )
                flash('Vehículo creado correctamente.', 'success')
                return redirect(url_for('maestros.list_vehiculos'))
            except Exception as e:
                flash(f'Error al crear vehículo: {e}', 'danger')

    campos = [
        {'name': 'codigo_interno', 'label': 'Código interno', 'required': True},
        {'name': 'matricula_tractora', 'label': 'Matrícula tractora'},
        {'name': 'matricula_semirremolque', 'label': 'Matrícula semirremolque'},
        {'name': 'observaciones', 'label': 'Observaciones', 'type': 'textarea'},
    ]
    return render_template('maestros/form.html', campos=campos, tipo='Vehículo', title='Nuevo Vehículo')


# ─── CONDUCTORES ────────────────────────────────────────────────
@bp.route('/conductores')
@login_required
def list_conductores():
    items = qm.listar_conductores(solo_activos=False)
    return render_template('maestros/listado.html',
                           items=items,
                           tipo='conductor',
                           columnas=['alias', 'codigo_alfabetico', 'nombre_legal', 'telefono', 'activo'],
                           cabeceras=['Alias', 'Código', 'Nombre Legal', 'Teléfono', 'Activo'],
                           title='Conductores')


@bp.route('/conductores/nuevo', methods=['GET', 'POST'])
@login_required
def create_conductor():
    if request.method == 'POST':
        alias = request.form.get('alias', '').strip()
        if not alias:
            flash('El alias es obligatorio.', 'warning')
        else:
            try:
                qm.crear_conductor(
                    alias=alias,
                    codigo_alfabetico=request.form.get('codigo_alfabetico', ''),
                    nombre_legal=request.form.get('nombre_legal', ''),
                    dni=request.form.get('dni', ''),
                    telefono=request.form.get('telefono', ''),
                    empresa=request.form.get('empresa', ''),
                    notas=request.form.get('notas', '')
                )
                flash('Conductor creado correctamente.', 'success')
                return redirect(url_for('maestros.list_conductores'))
            except Exception as e:
                flash(f'Error al crear conductor: {e}', 'danger')

    campos = [
        {'name': 'alias', 'label': 'Alias (nombre operativo)', 'required': True},
        {'name': 'codigo_alfabetico', 'label': 'Código alfabético'},
        {'name': 'nombre_legal', 'label': 'Nombre legal completo'},
        {'name': 'dni', 'label': 'DNI'},
        {'name': 'telefono', 'label': 'Teléfono'},
        {'name': 'empresa', 'label': 'Empresa'},
        {'name': 'notas', 'label': 'Notas', 'type': 'textarea'},
    ]
    return render_template('maestros/form.html', campos=campos, tipo='Conductor', title='Nuevo Conductor')


# ─── GRANJAS ────────────────────────────────────────────────────
@bp.route('/granjas')
@login_required
def list_granjas():
    items = qm.listar_granjas(solo_activos=False)
    return render_template('maestros/listado.html',
                           items=items,
                           tipo='granja',
                           columnas=['codigo', 'nombre_cliente', 'localidad', 'tiempo_trayecto_min', 'activo'],
                           cabeceras=['Código', 'Cliente', 'Localidad', 'Trayecto (min)', 'Activo'],
                           title='Granjas')


@bp.route('/granjas/nuevo', methods=['GET', 'POST'])
@login_required
def create_granja():
    if request.method == 'POST':
        codigo = request.form.get('codigo', '').strip()
        if not codigo:
            flash('El código de granja es obligatorio.', 'warning')
        else:
            try:
                qm.crear_granja(
                    codigo=codigo,
                    nombre_cliente=request.form.get('nombre_cliente', 'DESCONOCIDO'),
                    localidad=request.form.get('localidad', ''),
                    plantas=int(request.form.get('plantas', 1) or 1),
                    tiempo_trayecto_min=int(request.form.get('tiempo_trayecto_min', 120) or 120),
                    tiempo_carga_min=int(request.form.get('tiempo_carga_min', 60) or 60),
                    telefono_1=request.form.get('telefono_1', ''),
                    telefono_2=request.form.get('telefono_2', ''),
                    ubicacion_url=request.form.get('ubicacion_url', ''),
                    anotaciones=request.form.get('anotaciones', '')
                )
                flash('Granja creada correctamente.', 'success')
                return redirect(url_for('maestros.list_granjas'))
            except Exception as e:
                flash(f'Error al crear granja: {e}', 'danger')

    campos = [
        {'name': 'codigo', 'label': 'Código de granja', 'required': True},
        {'name': 'nombre_cliente', 'label': 'Nombre del cliente'},
        {'name': 'localidad', 'label': 'Localidad'},
        {'name': 'plantas', 'label': 'Nº de plantas', 'type': 'number', 'value': '1'},
        {'name': 'tiempo_trayecto_min', 'label': 'Tiempo de trayecto (minutos)', 'type': 'number', 'value': '120'},
        {'name': 'tiempo_carga_min', 'label': 'Tiempo de carga (minutos)', 'type': 'number', 'value': '60'},
        {'name': 'telefono_1', 'label': 'Teléfono 1'},
        {'name': 'telefono_2', 'label': 'Teléfono 2'},
        {'name': 'ubicacion_url', 'label': 'URL de ubicación (Google Maps)'},
        {'name': 'anotaciones', 'label': 'Anotaciones', 'type': 'textarea'},
    ]
    return render_template('maestros/form.html', campos=campos, tipo='Granja', title='Nueva Granja')
