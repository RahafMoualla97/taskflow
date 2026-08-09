"""
User model for authentication and profile management.

Handles user authentication (email/password and OAuth), profile information
(name, avatar), account status (active, deleted), and relationships to
projects, tasks, comments, and other entities.
"""
from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class User(BaseModel):
    """
    User account with authentication and profile data.

    Attributes:
        email: Unique email address (used for login)
        name: User's full name
        hashed_password: Bcrypt-hashed password (nullable for OAuth users)
        avatar_url: Optional profile picture URL
        is_active: Account status flag
        is_deleted: Soft delete flag
    """
    __tablename__ = "users"

    email = Column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
        comment="Unique email address (used for login)"
    )
    name = Column(
        String(255),
        nullable=False,
        comment="User's full name"
    )
    hashed_password = Column(
        String(255),
        nullable=True,
        comment="Bcrypt-hashed password (nullable for OAuth users)"
    )
    avatar_url = Column(
        String(500),
        nullable=True,
        comment="Optional profile picture URL"
    )
    is_active = Column(
        Boolean,
        default=True,
        comment="Account status flag"
    )
    is_deleted = Column(
        Boolean,
        default=False,
        index=True,
        comment="Soft delete flag"
    )

    projects_owned = relationship(
        "Project",
        foreign_keys="Project.owner_id",
        back_populates="owner"
    )
    project_members = relationship(
        "ProjectMember",
        back_populates="user"
    )

    tasks_assigned = relationship(
        "Task",
        foreign_keys="Task.assignee_id",
        back_populates="assignee"
    )
    tasks_reported = relationship(
        "Task",
        foreign_keys="Task.reporter_id",
        back_populates="reporter"
    )

    collaborated_tasks = relationship(
        "Task",
        secondary="task_collaborators",
        back_populates="collaborators"
    )
    watched_tasks = relationship(
        "Task",
        secondary="task_watchers",
        back_populates="watchers"
    )

    comments = relationship(
        "Comment",
        back_populates="author"
    )
    notifications = relationship(
        "Notification",
        back_populates="user"
    )
    activities = relationship(
        "Activity",
        back_populates="user"
    )
    timesheets = relationship(
        "Timesheet",
        back_populates="user",
        cascade="all, delete-orphan"
    )