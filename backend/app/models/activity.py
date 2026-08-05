"""
Activity model for tracking user actions and system events.

This model stores audit logs of all user activities including:
- Task creation, updates, and status changes
- Comment additions and mentions
- Project and member management actions
"""
from sqlalchemy import Column, String, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Activity(BaseModel):
    """
    Activity log entry tracking user actions across the system.

    Attributes:
        user_id: ID of the user who performed the action
        project_id: ID of the project context
        task_id: Optional task ID if action relates to a task
        action: Human-readable description of the action
        details: Optional JSON with additional context/data
    """
    __tablename__ = "activities"

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
        comment="ID of the user who performed the action"
    )
    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        nullable=False,
        index=True,
        comment="ID of the project context"
    )
    task_id = Column(
        Integer,
        ForeignKey("tasks.id"),
        nullable=True,
        comment="ID of the task if action relates to a task"
    )
    action = Column(
        String(500),
        nullable=False,
        comment="Human-readable action description"
    )
    details = Column(
        JSON,
        nullable=True,
        comment="Additional context/data as JSON"
    )

    user = relationship("User", back_populates="activities")
    project = relationship("Project", back_populates="activities")
    task = relationship("Task", back_populates="activities")