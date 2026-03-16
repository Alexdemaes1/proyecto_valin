"""
Gestión centralizada de configuración.

Lee y escribe config.json en la raíz del proyecto.
El usuario edita la configuración desde la UI, nunca desde la consola.
"""

import os
import json
import socket

# Ruta al archivo de configuración
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, 'config.json')
CONFIG_EXAMPLE_PATH = os.path.join(BASE_DIR, 'config.json.example')

# Valores por defecto si no existe config.json
DEFAULTS = {
    "secret_key": "",
    "drive_folder_path": "",
    "master_db_filename": "valin_master.db",
    "legacy_excel_path": "",
    "pc_name": "",
    "admin_password": "10041004",
    "debug": False,
    "port": 5000
}


def get_config():
    """Lee la configuración actual. Si no existe, crea una desde el ejemplo o los defaults."""
    if not os.path.exists(CONFIG_PATH):
        # Intentar copiar desde el ejemplo
        if os.path.exists(CONFIG_EXAMPLE_PATH):
            import shutil
            shutil.copy2(CONFIG_EXAMPLE_PATH, CONFIG_PATH)
        else:
            save_config(DEFAULTS)

    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError):
        data = DEFAULTS.copy()
        save_config(data)

    # Asegurar que todos los campos por defecto existen
    for key, default_val in DEFAULTS.items():
        if key not in data:
            data[key] = default_val

    # Detectar nombre del PC si no está configurado
    if not data.get('pc_name'):
        data['pc_name'] = socket.gethostname()

    # Campos derivados para la UI
    drive_path = data.get('drive_folder_path', '')
    data['drive_configurado'] = bool(drive_path)
    data['drive_accesible'] = bool(drive_path) and os.path.isdir(drive_path)
    data['excel_configurado'] = bool(data.get('legacy_excel_path', ''))
    data['excel_existe'] = bool(data.get('legacy_excel_path')) and os.path.exists(data['legacy_excel_path'])
    data['db_existe'] = os.path.exists(get_db_path())

    return data


def save_config(data):
    """Guarda la configuración en config.json."""
    # Fusionar con la configuración existente
    current = {}
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                current = json.load(f)
        except (json.JSONDecodeError, IOError):
            pass

    current.update(data)

    # No guardar campos derivados
    for key in ['drive_configurado', 'drive_accesible', 'excel_configurado',
                'excel_existe', 'db_existe', 'is_configured']:
        current.pop(key, None)

    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(current, f, indent=4, ensure_ascii=False)

    return current


def validar_config(data):
    """
    Valida los datos de configuración antes de guardar.

    Returns:
        list[str]: Lista de avisos/errores (vacía si todo es correcto)
    """
    avisos = []

    drive_path = data.get('drive_folder_path', '').strip()
    if drive_path:
        if not os.path.isdir(drive_path):
            avisos.append(
                f"La carpeta de Google Drive no existe o no es accesible: {drive_path}. "
                f"Compruebe que Google Drive está sincronizado y la ruta es correcta."
            )

    excel_path = data.get('legacy_excel_path', '').strip()
    if excel_path:
        if not os.path.exists(excel_path):
            avisos.append(
                f"El archivo Excel no se encuentra: {excel_path}. "
                f"Compruebe que la ruta es correcta."
            )
        else:
            ext = os.path.splitext(excel_path)[1].lower()
            if ext not in ('.xlsx', '.xlsm'):
                avisos.append(
                    f"El archivo debe ser .xlsx o .xlsm, pero tiene extensión '{ext}'."
                )

    db_name = data.get('master_db_filename', '').strip()
    if db_name and not db_name.endswith('.db'):
        avisos.append(
            f"El nombre del archivo maestro debería terminar en .db (actual: '{db_name}')."
        )

    return avisos


def get_db_path():
    """Devuelve la ruta absoluta a la base de datos SQLite local."""
    return os.path.join(BASE_DIR, 'instance', 'valin.db')


def get_drive_db_path():
    """Devuelve la ruta al archivo maestro en Google Drive, o None."""
    config = get_config()
    drive_path = config.get('drive_folder_path', '')
    db_name = config.get('master_db_filename', 'valin_master.db')
    if drive_path and os.path.isdir(drive_path):
        return os.path.join(drive_path, db_name)
    return None
