import os
import shutil
from datetime import datetime
from .local_sqlite_repository import LocalSqliteRepository
from .drive_lock_service import DriveLockService

class GoogleDriveSyncService:
    """
    Simulates Google Drive file-system synchronization.
    Given that Google Drive Desktop creates a local folder that syncs transparently, 
    this service pulls the remote valin.db into local 'instance' and pushes it back 
    upon saving, while respecting locks.
    """
    
    def __init__(self, drive_folder_path: str, local_instance_db_path: str):
        self.drive_folder_path = drive_folder_path
        self.remote_db_path = os.path.join(drive_folder_path, "valin_master.db")
        self.local_repo = LocalSqliteRepository(local_instance_db_path)
        self.lock_service = DriveLockService(drive_folder_path)
        
    def pull_master_database(self):
        """Copies the master DB from Drive to the local operational instance."""
        if not os.path.exists(self.drive_folder_path):
            os.makedirs(self.drive_folder_path, exist_ok=True)
            
        locked = self.lock_service.is_locked_by_others()
        if locked:
            print(f"La BD está bloqueada. Iniciando en modo sólo lectura. ({locked})")
            # Logic could fall into read-only
            
        if os.path.exists(self.remote_db_path):
            # Safe copy before replace
            self.local_repo.backup_local_before_pull(
                backup_dir=os.path.join(os.path.dirname(self.local_repo.db_path), "backups")
            )
            shutil.copy2(self.remote_db_path, self.local_repo.db_path)
            print("Base de datos sincronizada dedse Drive con éxito.")
        else:
            print("No existe base maestra en Drive. Se creará una sobre la marcha localmente.")

    def push_master_database(self, user="Admin"):
        """Pushes the local DB back to Google Drive cleanly, creating a historic snapshot."""
        # 1. Acquire Lock to prevent others overlapping this
        self.lock_service.acquire_lock(user=user)
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # Save historic snapshot in drive
            snapshot_dir = os.path.join(self.drive_folder_path, "snapshots_historicos")
            os.makedirs(snapshot_dir, exist_ok=True)
            
            if os.path.exists(self.remote_db_path): # Keep the old
                old_snap = os.path.join(snapshot_dir, f"valin_{timestamp}_old.db")
                shutil.copy2(self.remote_db_path, old_snap)
                
            # Overwrite master with local changes
            shutil.copy2(self.local_repo.db_path, self.remote_db_path)
            print(f"Base de datos subida a Drive como versión maestra.")
            
        finally:
            self.lock_service.release_lock()
