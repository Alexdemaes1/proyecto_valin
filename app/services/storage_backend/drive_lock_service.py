import os
import json
import socket
from datetime import datetime
import time

class DriveLockService:
    """
    Manages a .lock file within the Google Drive synced folder to prevent
    concurrent modifications by multiple PCs of Transportes Valin.
    """
    LOCK_FILENAME = ".valin_db.lock"

    def __init__(self, drive_path: str):
        self.drive_path = drive_path
        self.lock_file_path = os.path.join(self.drive_path, self.LOCK_FILENAME)

    def is_locked_by_others(self) -> dict:
        """
        Check if the lock file exists and belongs to someone else.
        Returns a dictionary with locking metadata or None.
        """
        if not os.path.exists(self.lock_file_path):
            return None
        
        try:
            with open(self.lock_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data
        except Exception:
            return {"error": "lock_file_corrupted", "owner": "Desconocido"}

    def acquire_lock(self, user="Admin"):
        """Creates a lock file declaring this PC as the operational owner."""
        # Wait a little for possible Google Drive syncs
        time.sleep(1)
        
        if self.is_locked_by_others():
            raise Exception("No se puede adquirir el lock. Otro PC está operando.")
            
        data = {
            "locked_by_user": user,
            "locked_by_pc": socket.gethostname(),
            "locked_at": datetime.now().isoformat(),
            "status": "active_edit"
        }
        
        os.makedirs(self.drive_path, exist_ok=True)
        with open(self.lock_file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f)
            
        # Optional: wait to ensure Google drive syncs it up, but that's transparent to OS.
        return data

    def release_lock(self):
        """Removes the lock file so other PCs can operate."""
        if os.path.exists(self.lock_file_path):
            os.remove(self.lock_file_path)
