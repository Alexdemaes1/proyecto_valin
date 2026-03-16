"""
Sincronización de la DB local con Google Drive.

Estrategia: copia de archivo, NUNCA acceso directo a la DB desde Drive.
- PULL: Copia valin_master.db de Drive → instance/valin.db (con backup previo)
- PUSH: Copia instance/valin.db → Drive/valin_master.db (con lock + backup)

El lock se basa en un archivo JSON en la carpeta de Drive. Expira tras 30 min
para evitar locks huérfanos si un PC se apaga sin liberar.
"""

import os
import json
import shutil
import socket
from datetime import datetime
from services.config_manager import get_config, get_db_path, get_drive_db_path
from services.backup_manager import crear_backup

LOCK_FILENAME = ".valin_lock.json"
LOCK_TIMEOUT_MINUTES = 30  # 30 min para permitir uso real sin prisas


def _get_lock_path():
    config = get_config()
    drive_path = config.get('drive_folder_path', '')
    if drive_path:
        return os.path.join(drive_path, LOCK_FILENAME)
    return None


def check_drive_status():
    """
    Comprueba el estado de la conexión con Google Drive.
    Devuelve un dict con toda la info necesaria para la UI.
    """
    config = get_config()
    drive_path = config.get('drive_folder_path', '')

    status = {
        'drive_configurado': bool(drive_path),
        'drive_accesible': False,
        'db_existe_en_drive': False,
        'bloqueado': False,
        'bloqueado_por': None,
        'mensaje': ''
    }

    if not drive_path:
        status['mensaje'] = (
            'Google Drive no está configurado. '
            'Puede trabajar en modo local sin problemas.'
        )
        return status

    if not os.path.isdir(drive_path):
        status['mensaje'] = (
            f'La carpeta de Drive no es accesible: {drive_path}\n'
            f'Compruebe que Google Drive está sincronizado en este PC.'
        )
        return status

    status['drive_accesible'] = True

    # ¿Existe la DB maestra?
    drive_db = get_drive_db_path()
    if drive_db and os.path.exists(drive_db):
        status['db_existe_en_drive'] = True

    # ¿Hay lock?
    lock_info = _read_lock()
    if lock_info and not lock_info.get('expired'):
        # ¿Es nuestro propio lock?
        pc_actual = socket.gethostname()
        if lock_info.get('locked_by_pc') == pc_actual:
            status['mensaje'] = 'Google Drive conectado. Este PC tiene el control de edición.'
        else:
            status['bloqueado'] = True
            status['bloqueado_por'] = lock_info.get('locked_by_pc', 'Desconocido')
            minutos = lock_info.get('elapsed_minutes', 0)
            status['mensaje'] = (
                f"La base de datos está siendo editada por "
                f"{lock_info.get('locked_by_pc', 'otro PC')} "
                f"(hace {int(minutos)} minutos). "
                f"Puede descargar datos pero no subir cambios."
            )
    else:
        if status['db_existe_en_drive']:
            status['mensaje'] = 'Google Drive conectado. Base maestra disponible.'
        else:
            status['mensaje'] = (
                'Google Drive conectado pero no hay base maestra. '
                'Pulse "Subir a Drive" para crear la primera copia.'
            )

    return status


def _read_lock():
    """Lee el archivo de lock si existe. Devuelve None o dict con info del lock."""
    lock_path = _get_lock_path()
    if not lock_path or not os.path.exists(lock_path):
        return None

    try:
        with open(lock_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Comprobar si el lock ha expirado
        locked_at = datetime.fromisoformat(data.get('locked_at', ''))
        elapsed = (datetime.now() - locked_at).total_seconds() / 60
        data['elapsed_minutes'] = elapsed

        if elapsed > LOCK_TIMEOUT_MINUTES:
            data['expired'] = True
            # Eliminar lock expirado
            try:
                os.remove(lock_path)
            except OSError:
                pass

        return data
    except Exception:
        return {'error': 'lock_corrupto', 'locked_by_pc': 'Desconocido'}


def _acquire_lock(user='Admin'):
    """Crea un archivo de lock en Drive."""
    lock_path = _get_lock_path()
    if not lock_path:
        return False, "Drive no configurado."

    existing = _read_lock()
    if existing and not existing.get('expired'):
        # Permitir re-adquirir si somos el mismo PC
        if existing.get('locked_by_pc') == socket.gethostname():
            pass  # OK, actualizar lock
        else:
            return False, (
                f"Otro PC está editando la base de datos "
                f"({existing.get('locked_by_pc', 'desconocido')}). "
                f"Espere a que termine o intente de nuevo en "
                f"{LOCK_TIMEOUT_MINUTES} minutos."
            )

    data = {
        "locked_by_user": user,
        "locked_by_pc": socket.gethostname(),
        "locked_at": datetime.now().isoformat(),
    }

    try:
        with open(lock_path, 'w', encoding='utf-8') as f:
            json.dump(data, f)
        return True, "Lock adquirido."
    except IOError as e:
        return False, f"No se pudo crear el lock en Drive: {e}"


def _release_lock():
    """Elimina el archivo de lock."""
    lock_path = _get_lock_path()
    if lock_path and os.path.exists(lock_path):
        try:
            os.remove(lock_path)
        except OSError:
            pass


def pull_from_drive():
    """
    Descarga la DB maestra de Drive a local.
    1. Verifica que Drive está accesible y la DB existe
    2. Crea backup de la DB local actual
    3. Copia Drive → local

    Returns:
        tuple: (éxito: bool, mensaje: str)
    """
    config = get_config()
    drive_path = config.get('drive_folder_path', '')

    if not drive_path:
        return False, (
            "Google Drive no está configurado. "
            "Configure la carpeta de Drive en la sección de Configuración."
        )

    if not os.path.isdir(drive_path):
        return False, (
            f"La carpeta de Drive no es accesible: {drive_path}\n"
            f"Compruebe que Google Drive está sincronizado en este PC."
        )

    drive_db = get_drive_db_path()
    if not drive_db or not os.path.exists(drive_db):
        return False, (
            "No existe base de datos maestra en Drive. "
            "Si es la primera vez, suba primero una copia con 'Subir a Drive'."
        )

    db_path = get_db_path()

    # Backup antes de sobreescribir
    if os.path.exists(db_path):
        backup = crear_backup(motivo='pre_pull')
        if not backup:
            return False, "No se pudo crear la copia de seguridad previa. Operación cancelada."

    try:
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        shutil.copy2(drive_db, db_path)
        return True, (
            "Base de datos descargada desde Drive correctamente. "
            "Se creó una copia de seguridad de la base anterior."
        )
    except IOError as e:
        return False, f"Error al copiar desde Drive: {e}"


def push_to_drive(user='Admin'):
    """
    Sube la DB local a Drive como maestra.
    1. Verifica Drive accesible + DB local existe
    2. Adquiere lock
    3. Backup local y remoto
    4. Copia local → Drive
    5. Libera lock

    Returns:
        tuple: (éxito: bool, mensaje: str)
    """
    config = get_config()
    drive_path = config.get('drive_folder_path', '')

    if not drive_path:
        return False, (
            "Google Drive no está configurado. "
            "Configure la carpeta de Drive en la sección de Configuración."
        )

    if not os.path.isdir(drive_path):
        return False, (
            f"La carpeta de Drive no es accesible: {drive_path}\n"
            f"Compruebe que Google Drive está sincronizado en este PC."
        )

    db_path = get_db_path()
    if not os.path.exists(db_path):
        return False, "No existe base de datos local para subir."

    # Backup de la DB local antes de la operación
    crear_backup(motivo='pre_push')

    # Adquirir lock
    ok, msg = _acquire_lock(user)
    if not ok:
        return False, msg

    try:
        drive_db = get_drive_db_path()

        # Backup del archivo remoto antes de sobreescribir
        if drive_db and os.path.exists(drive_db):
            snapshot_dir = os.path.join(drive_path, "snapshots_historicos")
            os.makedirs(snapshot_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            try:
                shutil.copy2(drive_db, os.path.join(snapshot_dir, f"valin_{timestamp}.db"))
            except IOError:
                pass  # Si no se puede hacer snapshot, continuar igualmente

        # Copiar local → Drive
        db_name = config.get('master_db_filename', 'valin_master.db')
        dest = os.path.join(drive_path, db_name)
        shutil.copy2(db_path, dest)

        return True, (
            "Base de datos subida a Drive correctamente. "
            "Los demás PCs pueden descargar la versión actualizada."
        )
    except IOError as e:
        return False, f"Error al copiar a Drive: {e}"
    finally:
        _release_lock()
