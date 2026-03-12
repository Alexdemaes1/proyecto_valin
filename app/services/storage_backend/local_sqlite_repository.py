import os
import shutil
from datetime import datetime

class LocalSqliteRepository:
    """
    Manages the local instance of the SQLite database.
    This serves as the only operational database connected to SQLAlchemy.
    """
    def __init__(self, db_path: str):
        self.db_path = db_path
        
    def backup_local_before_pull(self, backup_dir: str):
        """Creates a safety copy of the local file before overwriting from Drive."""
        if os.path.exists(self.db_path):
            os.makedirs(backup_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%md_%H%M%S")
            backup_file = os.path.join(backup_dir, f"local_pre_pull_{timestamp}.db")
            shutil.copy2(self.db_path, backup_file)
            return backup_file
        return None

    def backup_local_before_push(self, backup_dir: str):
        """Creates a safety copy of the local file before pushing it."""
        if os.path.exists(self.db_path):
            os.makedirs(backup_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%md_%H%M%S")
            backup_file = os.path.join(backup_dir, f"local_pre_push_{timestamp}.db")
            shutil.copy2(self.db_path, backup_file)
            return backup_file
        return None
