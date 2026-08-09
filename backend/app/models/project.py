"""
Project model for managing work spaces and task collections.

Handles project creation and metadata, unique project key generation,
soft deletion support, and relationships to members, tasks, and activities.
"""
from sqlalchemy import Column, String, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Project(BaseModel):
    """
    Project container for tasks and team collaboration.

    Attributes:
        name: Display name of the project
        key: Unique identifier (e.g., PROJ-001) for quick reference
        description: Optional project description
        owner_id: ID of the user who owns the project
        is_deleted: Soft delete flag
    """
    __tablename__ = "projects"

    name = Column(
        String(255),
        nullable=False,
        comment="Display name of the project"
    )
    key = Column(
        String(10),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique project key for quick reference (e.g., PROJ-001)"
    )
    description = Column(
        String(1000),
        nullable=True,
        comment="Optional project description"
    )
    owner_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
        comment="ID of the user who owns the project"
    )
    is_deleted = Column(
        Boolean,
        default=False,
        index=True,
        comment="Soft delete flag"
    )

    owner = relationship(
        "User",
        foreign_keys=[owner_id],
        back_populates="projects_owned"
    )
    members = relationship(
        "ProjectMember",
        back_populates="project",
        cascade="all, delete-orphan"
    )
    tasks = relationship("Task", back_populates="project")
    invitations = relationship("Invitation", back_populates="project")
    notifications = relationship("Notification", back_populates="project")
    activities = relationship("Activity", back_populates="project")