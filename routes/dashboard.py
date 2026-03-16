"""
Dashboard: panel principal con configuración, sincronización e importación.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from routes import login_required
from services import config_manager
from services import sync_drive
from services import import_excel
from services import backup_manager
from db.queries_maestros import contar_maestros

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@bp.route('/')
@login_required
def index():
    config = config_manager.get_config()
    drive_status = sync_drive.check_drive_status()
    conteos = contar_maestros()
    backups = backup_manager.listar_backups()[:10]  # Últimos 10

    return render_template('dashboard/index.html',
                           config=config,
                           drive_status=drive_status,
                           conteos=conteos,
                           backups=backups,
                           title='Panel de Control')


@bp.route('/guardar-config', methods=['POST'])
@login_required
def guardar_config():
    data = {
        'drive_folder_path': request.form.get('drive_folder_path', '').strip(),
        'legacy_excel_path': request.form.get('legacy_excel_path', '').strip(),
        'pc_name': request.form.get('pc_name', '').strip(),
        'master_db_filename': request.form.get('master_db_filename', 'valin_master.db').strip(),
    }

    # Validar antes de guardar
    avisos = config_manager.validar_config(data)
    for aviso in avisos:
        flash(aviso, 'warning')

    config_manager.save_config(data)

    if not avisos:
        flash('Configuración guardada correctamente.', 'success')
    else:
        flash('Configuración guardada, pero revise los avisos anteriores.', 'info')

    return redirect(url_for('dashboard.index'))


@bp.route('/importar-excel', methods=['POST'])
@login_required
def importar_excel():
    config = config_manager.get_config()
    ruta = config.get('legacy_excel_path', '')

    resultado = import_excel.importar_maestros(ruta)

    if resultado['exito']:
        total_nuevos = (resultado['vehiculos_nuevos'] +
                        resultado['conductores_nuevos'] +
                        resultado['granjas_nuevas'])
        if total_nuevos > 0:
            flash(
                f"Importación completada: "
                f"{resultado['vehiculos_nuevos']} vehículos nuevos, "
                f"{resultado['conductores_nuevos']} conductores nuevos, "
                f"{resultado['granjas_nuevas']} granjas nuevas.",
                'success'
            )
        else:
            flash(
                "No se importaron datos nuevos. "
                "Todos los registros del Excel ya existían en la base de datos.",
                'info'
            )
    else:
        for error in resultado['errores']:
            flash(error, 'danger')
        # Reportar importación parcial si hubo datos
        total_nuevos = (resultado['vehiculos_nuevos'] +
                        resultado['conductores_nuevos'] +
                        resultado['granjas_nuevas'])
        if total_nuevos > 0:
            flash(
                f"Importación parcial: "
                f"{resultado['vehiculos_nuevos']} vehículos, "
                f"{resultado['conductores_nuevos']} conductores, "
                f"{resultado['granjas_nuevas']} granjas.",
                'warning'
            )

    # Mostrar avisos (saltados, backup creado, etc.)
    for aviso in resultado.get('avisos', []):
        flash(aviso, 'info')

    return redirect(url_for('dashboard.index'))


@bp.route('/sync-pull', methods=['POST'])
@login_required
def sync_pull():
    ok, msg = sync_drive.pull_from_drive()
    flash(msg, 'success' if ok else 'danger')
    return redirect(url_for('dashboard.index'))


@bp.route('/sync-push', methods=['POST'])
@login_required
def sync_push():
    from flask import session
    user = session.get('username', 'Admin')
    ok, msg = sync_drive.push_to_drive(user=user)
    flash(msg, 'success' if ok else 'danger')
    return redirect(url_for('dashboard.index'))


@bp.route('/backup', methods=['POST'])
@login_required
def crear_backup():
    ruta = backup_manager.crear_backup(motivo='manual')
    if ruta:
        flash('Copia de seguridad creada correctamente.', 'success')
    else:
        flash(
            'No se pudo crear la copia de seguridad. '
            'Compruebe que la base de datos existe en la carpeta instance/.',
            'warning'
        )
    return redirect(url_for('dashboard.index'))


@bp.route('/restaurar-backup', methods=['POST'])
@login_required
def restaurar_backup():
    nombre = request.form.get('backup_nombre', '')
    if not nombre:
        flash('No se indicó el backup a restaurar.', 'warning')
        return redirect(url_for('dashboard.index'))

    ok, msg = backup_manager.restaurar_backup(nombre)
    flash(msg, 'success' if ok else 'danger')
    return redirect(url_for('dashboard.index'))
