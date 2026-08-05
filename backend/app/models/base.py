"""
Base model class for all database models.

This abstract base class provides common fields and functionality
for all models including:
- Auto-incrementing primary key (id)
- Creation timestamp (created_at)
- Last update timestamp (updated_at)
"""
from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.sql import func
from app.core.database import Base


class BaseModel(Base):
    """
    Abstract base model for all database entities.

    All models inherit from this class to get common fields:
        - id: Auto-incrementing primary key
        - created_at: UTC timestamp set on creation
        - updated_at: UTC timestamp updated on each modification

    This class is abstract and does not create a table in the database.
    """
    __abstract__ = True

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="Unique identifier for the record"
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="Timestamp when the record was created (UTC)"
    )
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
        comment="Timestamp when the record was last updated (UTC)"
    )