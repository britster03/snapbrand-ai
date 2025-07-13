#!/usr/bin/env python3
"""
Database Recovery Script
Handles SQLite I/O errors, corruption, and database recovery
"""

import os
import sqlite3
import shutil
import time
import subprocess
import logging
from datetime import datetime
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseRecovery:
    def __init__(self, db_path="snapbrand.db"):
        self.db_path = db_path
        self.backup_dir = "db_backups"
        self.ensure_backup_dir()
    
    def ensure_backup_dir(self):
        """Ensure backup directory exists."""
        Path(self.backup_dir).mkdir(exist_ok=True)
    
    def kill_database_processes(self):
        """Kill any processes that might be using the database."""
        try:
            # Find processes using the database
            result = subprocess.run(
                ["lsof", self.db_path],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0 and result.stdout:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                pids = []
                
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 2:
                        pid = parts[1]
                        pids.append(pid)
                
                if pids:
                    logger.info(f"Found {len(pids)} processes using database: {pids}")
                    for pid in pids:
                        try:
                            subprocess.run(["kill", "-9", pid], check=True)
                            logger.info(f"Killed process {pid}")
                        except subprocess.CalledProcessError:
                            logger.warning(f"Could not kill process {pid}")
                    
                    time.sleep(2)  # Wait for processes to die
                else:
                    logger.info("No processes found using database")
            else:
                logger.info("No processes found using database")
                
        except FileNotFoundError:
            logger.warning("lsof command not found, skipping process cleanup")
        except Exception as e:
            logger.error(f"Error killing database processes: {e}")
    
    def backup_database(self):
        """Create a backup of the current database."""
        if not os.path.exists(self.db_path):
            logger.warning(f"Database file {self.db_path} does not exist")
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(self.backup_dir, f"snapbrand_backup_{timestamp}.db")
        
        try:
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"Database backed up to {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"Error backing up database: {e}")
            return None
    
    def check_database_integrity(self):
        """Check database integrity."""
        try:
            with sqlite3.connect(self.db_path, timeout=30) as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA integrity_check")
                result = cursor.fetchone()
                
                if result and result[0] == "ok":
                    logger.info("Database integrity check passed")
                    return True
                else:
                    logger.error(f"Database integrity check failed: {result}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error checking database integrity: {e}")
            return False
    
    def clean_database_files(self):
        """Clean up WAL and SHM files."""
        wal_file = f"{self.db_path}-wal"
        shm_file = f"{self.db_path}-shm"
        
        for file_path in [wal_file, shm_file]:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    logger.info(f"Removed {file_path}")
                except Exception as e:
                    logger.error(f"Error removing {file_path}: {e}")
    
    def optimize_database(self):
        """Optimize and vacuum the database."""
        try:
            with sqlite3.connect(self.db_path, timeout=60) as conn:
                cursor = conn.cursor()
                
                # Set journal mode to DELETE for better I/O error handling
                cursor.execute("PRAGMA journal_mode=DELETE")
                logger.info("Set journal mode to DELETE")
                
                # Set busy timeout
                cursor.execute("PRAGMA busy_timeout=60000")
                
                # Vacuum the database
                cursor.execute("VACUUM")
                logger.info("Database vacuumed")
                
                # Optimize
                cursor.execute("PRAGMA optimize")
                logger.info("Database optimized")
                
                return True
                
        except Exception as e:
            logger.error(f"Error optimizing database: {e}")
            return False
    
    def repair_database(self):
        """Attempt to repair a corrupted database."""
        logger.info("Attempting database repair...")
        
        # Create a backup first
        backup_path = self.backup_database()
        if not backup_path:
            logger.error("Could not create backup, aborting repair")
            return False
        
        temp_db = f"{self.db_path}.repair"
        
        try:
            # Create a new database and copy data
            with sqlite3.connect(self.db_path, timeout=60) as source:
                with sqlite3.connect(temp_db, timeout=60) as target:
                    source.backup(target)
            
            # Replace the original database
            shutil.move(temp_db, self.db_path)
            logger.info("Database repaired successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error repairing database: {e}")
            
            # Clean up temp file
            if os.path.exists(temp_db):
                os.remove(temp_db)
            
            return False
    
    def recover_database(self):
        """Main recovery function."""
        logger.info("Starting database recovery process...")
        
        # Step 1: Kill any processes using the database
        self.kill_database_processes()
        
        # Step 2: Clean up WAL and SHM files
        self.clean_database_files()
        
        # Step 3: Check integrity
        if not os.path.exists(self.db_path):
            logger.error(f"Database file {self.db_path} does not exist")
            return False
        
        integrity_ok = self.check_database_integrity()
        
        # Step 4: Optimize database
        if integrity_ok:
            optimize_ok = self.optimize_database()
            if optimize_ok:
                logger.info("Database recovery completed successfully")
                return True
        
        # Step 5: Attempt repair if integrity check failed
        logger.warning("Database integrity check failed, attempting repair...")
        repair_ok = self.repair_database()
        
        if repair_ok:
            # Check integrity again after repair
            integrity_ok = self.check_database_integrity()
            if integrity_ok:
                self.optimize_database()
                logger.info("Database recovery completed successfully after repair")
                return True
        
        logger.error("Database recovery failed")
        return False

def main():
    """Main function to run database recovery."""
    recovery = DatabaseRecovery()
    
    if recovery.recover_database():
        print("✅ Database recovery completed successfully!")
        print("You can now restart your application.")
    else:
        print("❌ Database recovery failed.")
        print("You may need to restore from a backup or recreate the database.")
        
        # List available backups
        backup_dir = Path(recovery.backup_dir)
        if backup_dir.exists():
            backups = list(backup_dir.glob("*.db"))
            if backups:
                print(f"\nAvailable backups in {recovery.backup_dir}:")
                for backup in sorted(backups, reverse=True):
                    print(f"  - {backup.name}")

if __name__ == "__main__":
    main() 