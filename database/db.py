"""
Database connection and initialization module.

Provides SQLite database connectivity with proper connection management,
SQL injection protection through parameterized queries, and schema
initialization for all application tables.

Uses SQLAlchemy for ORM support and connection pooling.
"""

import logging
import os

from sqlalchemy import create_engine, event
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.pool import StaticPool

from database.models import Base

logger = logging.getLogger(__name__)

# Database file path - stored in the data directory
DB_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"
)
DB_PATH = os.path.join(DB_DIR, "expense_tracker.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"


def get_engine():
    """
    Create and return a SQLAlchemy engine instance.

    Uses StaticPool for SQLite to avoid threading issues in Streamlit.
    Enables WAL mode for better concurrent read performance.
    Enforces foreign key constraints.

    Returns:
        sqlalchemy.engine.Engine: Configured database engine
    """
    os.makedirs(DB_DIR, exist_ok=True)

    engine = create_engine(
        DATABASE_URL,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
        echo=False,
    )

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        """Enable WAL mode and foreign keys on connection."""
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


def get_db_session():
    """
    Create a scoped database session.

    Returns:
        sqlalchemy.orm.Session: Database session for transactional operations
    """
    engine = get_engine()
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)
    Session = scoped_session(session_factory)
    return Session()


def get_db_connection():
    """
    Get a database connection for raw SQL operations if needed.
    Maintained for backward compatibility.

    Returns:
        tuple: (engine, session) for database operations
    """
    engine = get_engine()
    session = get_db_session()
    return engine, session


def init_db():
    """
    Initialize the database schema.

    Creates all defined tables if they don't exist.
    Should be called once at application startup.
    """
    try:
        engine = get_engine()
        Base.metadata.create_all(engine)
        logger.info("Database initialized successfully at %s", DB_PATH)
    except Exception as e:
        logger.error("Failed to initialize database: %s", str(e))
        raise


def close_session(session):
    """
    Safely close a database session.

    Args:
        session: SQLAlchemy session to close
    """
    try:
        if session:
            session.close()
    except Exception as e:
        logger.warning("Error closing session: %s", str(e))
