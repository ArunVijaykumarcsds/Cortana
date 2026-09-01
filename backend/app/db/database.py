"""
CORTANA — Database Connection and Session Management.
Supports PostgreSQL (Production) and SQLite (Development/Testing).
"""

import os
from contextlib import contextmanager
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# Configurable database URL. Defaults to SQLite for local development/testing.
# For production PostgreSQL: postgresql+psycopg2://user:password@host:port/dbname
DATABASE_URL = os.getenv("CORTANA_DATABASE_URL", "sqlite:///./cortana_dev.db")

# SQLite connection args for threading support
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=os.getenv("CORTANA_DB_ECHO", "0") == "1",
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI-compatible and standalone database session generator.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def create_all_tables(target_engine=None):
    """
    Creates all database tables defined in metadata.
    """
    eng = target_engine or engine
    Base.metadata.create_all(bind=eng)


def drop_all_tables(target_engine=None):
    """
    Drops all database tables defined in metadata.
    """
    eng = target_engine or engine
    Base.metadata.drop_all(bind=eng)
