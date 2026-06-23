"""
database.py - Database Connection & Session Management

Configures SQLAlchemy engine, session factory, and provides
the Base class for ORM models. Also provides a dependency
for injecting database sessions into route handlers.
"""

import psycopg2
from urllib.parse import urlparse

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import get_settings

# Load settings
settings = get_settings()

# ---------------------------------------------------------------------------
# SQLAlchemy Engine
# - pool_pre_ping: checks connections before use (handles stale connections)
# ---------------------------------------------------------------------------
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.DEBUG,  # Log SQL statements when DEBUG is True
)

# ---------------------------------------------------------------------------
# Session Factory
# - autocommit=False: we manually commit transactions
# - autoflush=False: we manually flush changes to the database
# ---------------------------------------------------------------------------
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# ---------------------------------------------------------------------------
# Declarative Base
# All ORM models inherit from this Base class.
# ---------------------------------------------------------------------------
Base = declarative_base()


def ensure_database_exists(database_url: str) -> None:
    """
    Ensure the target PostgreSQL database exists before SQLAlchemy starts.

    This avoids startup failures when the database has not been created yet.
    """
    parsed = urlparse(database_url)
    database_name = parsed.path.lstrip("/") or "postgres"

    if parsed.scheme not in {"postgresql", "postgres"}:
        raise ValueError("Unsupported database URL scheme: " + parsed.scheme)

    connection = psycopg2.connect(
        host=parsed.hostname or "localhost",
        port=parsed.port or 5432,
        user=parsed.username or "postgres",
        password=parsed.password,
        dbname="postgres",
    )
    connection.autocommit = True

    try:
        cursor = connection.cursor()
        try:
            cursor.execute(
                "SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s",
                (database_name,),
            )
            exists = cursor.fetchone()

            if not exists:
                cursor.execute(f'CREATE DATABASE "{database_name}"')
                print(f"Created missing PostgreSQL database: {database_name}")
            else:
                print(f"PostgreSQL database already exists: {database_name}")
        finally:
            cursor.close()
    finally:
        connection.close()


def get_db():
    """
    Dependency generator that provides a database session.

    Yields a SQLAlchemy session and ensures it is closed after
    the request is complete, even if an exception occurs.

    Usage in route handlers:
        @router.get("/example")
        def example(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
