import os
import json

class LocalSettingsManager:
    """
    Manages PC-specific settings (like Google Drive paths).
    These settings are NOT synced to Drive/Git.
    """
    
    @classmethod
    def get_settings_path(cls):
        # We place it in the project root to ensure portability
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        return os.path.join(base_dir, 'local_settings.json')

    @classmethod
    def get_settings(cls):
        path = cls.get_settings_path()
        if not os.path.exists(path):
            return {
                "drive_folder_path": "",
                "master_db_filename": "valin_master.db",
                "legacy_excel_path": "", # Optional path to the .xlsm in Drive
                "pc_name": os.environ.get("COMPUTERNAME", "PC-Desconocido"),
                "is_configured": False
            }
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                data['is_configured'] = True if data.get('drive_folder_path') else False
                return data
        except:
            return cls.get_settings() # Return defaults on error

    @classmethod
    def save_settings(cls, data: dict):
        path = cls.get_settings_path()
        # Merge with existing
        current = cls.get_settings()
        current.update(data)
        current['is_configured'] = True if current.get('drive_folder_path') else False
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(current, f, indent=4)
        return current
