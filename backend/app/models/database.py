import os
import time
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from sqlalchemy.exc import OperationalError, DatabaseError
from typing import Generator
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./snapbrand.db")

# Create engine with proper SQLite configuration to prevent locking
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={
            "check_same_thread": False,
            "timeout": 60,  # Increased timeout for I/O operations
            "isolation_level": None,  # Autocommit mode
        },
        poolclass=StaticPool,
        pool_pre_ping=True,  # Verify connections before use
        pool_recycle=300,  # Recycle connections every 5 minutes
        echo=False,  # Set to True for SQL debugging
    )
    
    # Enable optimized SQLite configuration for better I/O handling
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        try:
            # Set journal mode to DELETE for better I/O error handling
            cursor.execute("PRAGMA journal_mode=DELETE")
            # Set busy timeout
            cursor.execute("PRAGMA busy_timeout=60000")
            # Enable foreign keys
            cursor.execute("PRAGMA foreign_keys=ON")
            # Optimize for better performance and I/O handling
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA cache_size=2000")
            cursor.execute("PRAGMA temp_store=MEMORY")
            cursor.execute("PRAGMA mmap_size=268435456")  # 256MB
            # Enable automatic index creation
            cursor.execute("PRAGMA automatic_index=ON")
            logger.info("SQLite pragmas configured successfully")
        except Exception as e:
            logger.error(f"Error setting SQLite pragmas: {e}")
        finally:
            cursor.close()
else:
    engine = create_engine(DATABASE_URL, echo=False)

# Create session factory with better configuration
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine,
    expire_on_commit=False  # Prevent issues with detached instances
)

Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """Get database session with retry logic for I/O errors."""
    db = None
    max_retries = 3
    retry_delay = 1  # seconds
    
    for attempt in range(max_retries):
        try:
            db = SessionLocal()
            yield db
            break
        except (OperationalError, DatabaseError) as e:
            if db:
                db.close()
            
            error_msg = str(e).lower()
            if "disk i/o error" in error_msg or "database is locked" in error_msg:
                if attempt < max_retries - 1:
                    logger.warning(f"Database I/O error (attempt {attempt + 1}/{max_retries}): {e}")
                    time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
                    continue
                else:
                    logger.error(f"Database I/O error after {max_retries} attempts: {e}")
                    raise
            else:
                logger.error(f"Database error: {e}")
                raise
        except Exception as e:
            if db:
                db.close()
            logger.error(f"Unexpected database error: {e}")
            raise
        finally:
            if db:
                try:
                    db.close()
                except Exception as e:
                    logger.error(f"Error closing database session: {e}")

def init_db():
    """Initialize the database."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

def drop_db():
    """Drop all database tables."""
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("Database dropped successfully")
    except Exception as e:
        logger.error(f"Error dropping database: {e}")
        raise 