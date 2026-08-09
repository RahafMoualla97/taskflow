"""
Database connection and session management.

Provides:
- SQLAlchemy engine configuration
- Session factory for database operations
- Base class for all ORM models
- Dependency injection for database sessions
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings


# SQLAlchemy Engine Configuration
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=False,
)


# Session Factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# Base ORM Model Class
Base = declarative_base()


def get_db():
    """
    Dependency provider for database sessions.

    Yields a database session and ensures it is properly closed
    after the request is complete.

    Usage:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()

    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()