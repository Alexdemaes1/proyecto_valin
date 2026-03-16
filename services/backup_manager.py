"""
Gestión de copias de seguridad de la base de datos.

Crea backups automáticos antes de operaciones críticas (importar, sincronizar).
Permite listar y restaurar backups desde la UI.

Usa sqlite3.backup() para copias seguras que respetan transacciones en curso.
"""

import os
import sqlite3
import shutil
from datetime import datetime
from services.config_manager import get_db_path, BASE_DIR

BACKUP_DIR = os.path.join(BASE_DIR, 'instance', 'backups')
MAX_BACKUPS = 30


def crear_backup(motivo='manual'):
    """
    Crea una copia segura de la base de datos actual con timestamp.

    Usa sqlite3.backup() en vez de shutil.copy2 para garantizar que la copia
    es consistente aunque haya escrituras en curso o WAL pendiente.

    Args:
        motivo (str): Etiqueta del motivo (manual, pre_import, pre_pull, pre_push, pre_restaurar)

    Returns:
        str: Ruta al archivo de backup creado, o None si no hay DB.
    """
    db_path = get_db_path()
    if not os.path.exists(db_path):
        return None

    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"valin_{motivo}_{timestamp}.db"
    backup_path = os.path.join(BACKUP_DIR, backup_name)

    try:
        # Abrir conexión a la DB origen
        source = sqlite3.connect(db_path)
        # Crear conexión a la DB destino (backup)
        dest = sqlite3.connect(backup_path)
        # Copiar de forma segura (respeta WAL, locks, transacciones)
        source.backup(dest)
        dest.close()
        source.close()
    except Exception:
        # Fallback: si sqlite3.backup falla, usar copia de archivo
        try:
            shutil.copy2(db_path, backup_path)
        except Exception:
            return None

    # Limpiar backups antiguos automáticamente
    limpiar_backups_antiguos()

    return backup_path


def listar_backups():
    """
    Lista los backups disponibles, del más reciente al más antiguo.

    Returns:
        list[dict]: Lista de dicts con 'nombre', 'fecha', 'tamaño_mb', 'motivo'
    """
    if not os.path.isdir(BACKUP_DIR):
        return []

    # Mapeo de motivos técnicos a textos legibles
    motivos_legibles = {
        'manual': 'Manual',
        'pre_import': 'Antes de importar Excel',
        'pre_pull': 'Antes de descargar de Drive',
        'pre_push': 'Antes de subir a Drive',
        'pre_restaurar': 'Antes de restaurar backup',
    }

    backups = []
    for f in sorted(os.listdir(BACKUP_DIR), reverse=True):
        if f.endswith('.db'):
            filepath = os.path.join(BACKUP_DIR, f)
            stat = os.stat(filepath)

            # Extraer motivo del nombre: valin_MOTIVO_timestamp.db
            motivo_raw = '_'.join(f.replace('valin_', '').rsplit('_', 2)[:-2])
            motivo = motivos_legibles.get(motivo_raw, motivo_raw or 'Automático')

            backups.append({
                'nombre': f,
                'fecha': datetime.fromtimestamp(stat.st_mtime).strftime('%d/%m/%Y %H:%M'),
                'tamaño_mb': round(stat.st_size / (1024 * 1024), 2),
                'motivo': motivo,
            })
    return backups


def restaurar_backup(nombre_backup):
    """
    Restaura un backup reemplazando la DB actual.
    Crea un backup de seguridad de la DB actual antes de restaurar.

    Args:
        nombre_backup (str): Nombre del archivo de backup

    Returns:
        tuple: (éxito: bool, mensaje: str)
    """
    backup_path = os.path.join(BACKUP_DIR, nombre_backup)
    if not os.path.exists(backup_path):
        return False, f"No se encontró el backup '{nombre_backup}'."

    # Verificar que el backup es una SQLite válida
    try:
        test_conn = sqlite3.connect(backup_path)
        test_conn.execute("SELECT name FROM sqlite_master LIMIT 1")
        test_conn.close()
    except Exception:
        return False, f"El archivo '{nombre_backup}' no es una base de datos válida."

    db_path = get_db_path()

    # Backup de seguridad antes de restaurar
    if os.path.exists(db_path):
        crear_backup(motivo='pre_restaurar')

    try:
        shutil.copy2(backup_path, db_path)
        return True, f"Backup '{nombre_backup}' restaurado correctamente."
    except Exception as e:
        return False, f"Error al restaurar: {e}"


def limpiar_backups_antiguos(max_backups=MAX_BACKUPS):
    """Elimina los backups más antiguos si hay más de max_backups."""
    if not os.path.isdir(BACKUP_DIR):
        return

    archivos = sorted(
        [f for f in os.listdir(BACKUP_DIR) if f.endswith('.db')],
        reverse=True
    )

    if len(archivos) > max_backups:
        for f in archivos[max_backups:]:
            try:
                os.remove(os.path.join(BACKUP_DIR, f))
            except OSError:
                pass
