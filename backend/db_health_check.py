#!/usr/bin/env python3
"""
Database health check and cleanup script for SnapBrand.ai
Helps prevent and resolve database locking issues.
"""

import sys
import os
import sqlite3
import subprocess
from pathlib import Path

def check_database_locks():
    """Check for processes using the database."""
    db_path = Path("snapbrand.db").absolute()
    
    try:
        result = subprocess.run(
            ["lsof", str(db_path)], 
            capture_output=True, 
            text=True
        )
        
        if result.returncode == 0 and result.stdout.strip():
            print("🔒 Database is currently in use by:")
            print(result.stdout)
            return True
        else:
            print("✅ No processes are currently using the database")
            return False
            
    except FileNotFoundError:
        print("⚠ lsof command not found, skipping lock check")
        return False

def cleanup_database_files():
    """Clean up database lock files."""
    db_files = [
        "snapbrand.db-journal",
        "snapbrand.db-wal",
        "snapbrand.db-shm"
    ]
    
    cleaned = False
    for file in db_files:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"🧹 Removed {file}")
                cleaned = True
            except Exception as e:
                print(f"❌ Failed to remove {file}: {e}")
    
    if not cleaned:
        print("✅ No cleanup files found")

def test_database_connection():
    """Test database connection and basic operations."""
    try:
        # Test connection
        conn = sqlite3.connect("snapbrand.db", timeout=10)
        cursor = conn.cursor()
        
        # Test basic query
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"✅ Database connection successful")
        print(f"📊 Found {len(tables)} tables")
        
        # Test write operation
        cursor.execute("BEGIN IMMEDIATE;")
        cursor.execute("ROLLBACK;")
        print("✅ Write test successful")
        
        conn.close()
        return True
        
    except sqlite3.OperationalError as e:
        if "database is locked" in str(e):
            print("❌ Database is locked!")
            return False
        else:
            print(f"❌ Database error: {e}")
            return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def optimize_database():
    """Optimize database performance."""
    try:
        conn = sqlite3.connect("snapbrand.db")
        cursor = conn.cursor()
        
        print("🔧 Optimizing database...")
        
        # Enable WAL mode
        cursor.execute("PRAGMA journal_mode=WAL;")
        
        # Set optimizations
        cursor.execute("PRAGMA synchronous=NORMAL;")
        cursor.execute("PRAGMA cache_size=1000;")
        cursor.execute("PRAGMA temp_store=MEMORY;")
        cursor.execute("PRAGMA busy_timeout=30000;")
        
        # Vacuum to optimize
        cursor.execute("VACUUM;")
        
        conn.close()
        print("✅ Database optimized")
        
    except Exception as e:
        print(f"❌ Optimization failed: {e}")

def kill_python_processes():
    """Kill any hanging Python processes that might be locking the database."""
    try:
        result = subprocess.run(
            ["pgrep", "-f", "python.*main.py"], 
            capture_output=True, 
            text=True
        )
        
        if result.returncode == 0 and result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            print(f"🔪 Found {len(pids)} Python processes to kill")
            
            for pid in pids:
                try:
                    subprocess.run(["kill", pid], check=True)
                    print(f"✅ Killed process {pid}")
                except Exception as e:
                    print(f"❌ Failed to kill process {pid}: {e}")
        else:
            print("✅ No hanging Python processes found")
            
    except FileNotFoundError:
        print("⚠ pgrep command not found, skipping process check")

def main():
    """Main health check function."""
    print("🏥 SnapBrand.ai Database Health Check")
    print("=" * 50)
    
    # Check for locks
    has_locks = check_database_locks()
    
    if has_locks:
        print("\n🚨 Database appears to be locked. Attempting cleanup...")
        
        # Kill hanging processes
        kill_python_processes()
        
        # Clean up lock files
        cleanup_database_files()
        
        # Wait a moment
        import time
        time.sleep(2)
        
        # Check again
        has_locks = check_database_locks()
    
    # Test connection
    print("\n🔍 Testing database connection...")
    connection_ok = test_database_connection()
    
    if not connection_ok:
        print("\n💊 Attempting to fix database issues...")
        cleanup_database_files()
        kill_python_processes()
        
        # Try again
        connection_ok = test_database_connection()
    
    if connection_ok:
        print("\n⚡ Optimizing database...")
        optimize_database()
        
        print("\n✅ Database health check complete!")
        print("🎉 Database is ready for use!")
    else:
        print("\n❌ Database health check failed!")
        print("💡 Try restarting your backend server or check for other issues.")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main() 