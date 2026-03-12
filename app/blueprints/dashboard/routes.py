from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from . import bp
from .forms import LocalConfigForm
from app.utils.local_settings import LocalSettingsManager
from app.services.storage_backend.drive_sync_service import GoogleDriveSyncService
from scripts.import_masters import import_excel_data
from flask import current_app
import os

@bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    settings = LocalSettingsManager.get_settings()
    
    # Manejar el formulario de configuración local
    config_form = LocalConfigForm()
    
    if config_form.validate_on_submit():
        path = config_form.drive_path.data
        if not os.path.exists(path):
            flash(f"La ruta '{path}' no existe en este PC. Por favor revise su configuración de Google Drive.", "warning")
        else:
            new_data = {
                "drive_folder_path": config_form.drive_path.data,
                "pc_name": config_form.pc_name.data,
                "master_db_filename": config_form.master_db_filename.data,
                "legacy_excel_path": config_form.legacy_excel_path.data
            }
            LocalSettingsManager.save_settings(new_data)
            flash(f"Configuración guardada correctamente. Este PC ya está vinculado.", "success")
            return redirect(url_for('dashboard.index'))
    
    if request.method == 'GET' and settings.get('is_configured'):
        config_form.drive_path.data = settings.get('drive_folder_path', '')
        config_form.pc_name.data = settings.get('pc_name', '')
        config_form.master_db_filename.data = settings.get('master_db_filename', 'valin_master.db')
        config_form.legacy_excel_path.data = settings.get('legacy_excel_path', '')
        
    return render_template(
        'dashboard/index.html', 
        settings=settings, 
        config_form=config_form,
        title="Panel de Control Principal"
    )

@bp.route('/import-legacy', methods=['POST'])
@login_required
def import_legacy():
    settings = LocalSettingsManager.get_settings()
    excel_path = settings.get('legacy_excel_path')
    
    if not excel_path or not os.path.exists(excel_path):
        flash("No se puede importar: La ruta al Excel legacy no es válida o no está configurada.", "danger")
    else:
        try:
            import_excel_data(excel_path)
            flash("Importación de maestros (Camiones, Chóferes, Granjas) completada con éxito.", "success")
        except Exception as e:
            flash(f"Error durante la importación: {str(e)}", "danger")
            
    return redirect(url_for('dashboard.index'))

@bp.route('/sync-pull', methods=['POST'])
@login_required
def sync_pull():
    settings = LocalSettingsManager.get_settings()
    if not settings.get('is_configured'):
        flash("Configure primero la ruta de Drive.", "warning")
        return redirect(url_for('dashboard.index'))
    
    db_path = current_app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    if db_path.startswith('/'): # Handle absolute paths for windows differently if needed
        # on windows sqlite:///C:\... becomes /C:\... sometimes depending on how it's handled. 
        # But here parent_dir based sqlite should be relative or absolute with drive.
        pass

    sync_service = GoogleDriveSyncService(
        drive_folder_path=settings.get('drive_folder_path'),
        local_instance_db_path=db_path
    )
    
    try:
        sync_service.pull_master_database()
        flash("Base de Datos sincronizada desde Google Drive.", "success")
    except Exception as e:
        flash(f"Error al sincronizar: {str(e)}", "danger")
        
    return redirect(url_for('dashboard.index'))

@bp.route('/sync-push', methods=['POST'])
@login_required
def sync_push():
    settings = LocalSettingsManager.get_settings()
    if not settings.get('is_configured'):
        flash("Configure primero la ruta de Drive.", "warning")
        return redirect(url_for('dashboard.index'))
    
    db_path = current_app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    sync_service = GoogleDriveSyncService(
        drive_folder_path=settings.get('drive_folder_path'),
        local_instance_db_path=db_path
    )
    
    try:
        sync_service.push_master_database(user=current_user.username)
        flash("Cambios subidos a Google Drive correctamente.", "success")
    except Exception as e:
        flash(f"Error al subir: {str(e)}", "danger")
        
    return redirect(url_for('dashboard.index'))
