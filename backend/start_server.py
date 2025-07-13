#!/usr/bin/env python3
"""
Server startup script with automatic database recovery
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from db_recovery import DatabaseRecovery

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_and_recover_database():
    """Check database health and recover if needed."""
    logger.info("Checking database health...")
    
    recovery = DatabaseRecovery()
    
    # Quick integrity check
    if not recovery.check_database_integrity():
        logger.warning("Database integrity check failed, running recovery...")
        if recovery.recover_database():
            logger.info("Database recovery completed successfully")
        else:
            logger.error("Database recovery failed")
            return False
    else:
        logger.info("Database is healthy")
    
    return True

def start_server():
    """Start the FastAPI server."""
    logger.info("Starting SnapBrand AI server...")
    
    # Check if we're in development mode
    dev_mode = os.getenv("DEV_MODE", "true").lower() == "true"
    
    if dev_mode:
        # Development mode with auto-reload
        cmd = [
            "uvicorn", 
            "app.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ]
    else:
        # Production mode
        cmd = [
            "uvicorn", 
            "app.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--workers", "4"
        ]
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except subprocess.CalledProcessError as e:
        logger.error(f"Server failed to start: {e}")
        return False
    
    return True

def main():
    """Main function."""
    logger.info("SnapBrand AI Server Startup")
    logger.info("=" * 50)
    
    # Step 1: Check and recover database if needed
    if not check_and_recover_database():
        logger.error("Database recovery failed, cannot start server")
        sys.exit(1)
    
    # Step 2: Start the server
    if not start_server():
        logger.error("Server failed to start")
        sys.exit(1)

if __name__ == "__main__":
    main() 