"""
Notification model for user alerts and system messages.

This model handles:
- Real-time user notifications (TaskAssigned, StatusChanged, etc.)
- Read/unread status tracking
- Action URLs for navigation
"""
from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Notification(BaseModel):
    """
    User notification with type, content, and read status.

    Attributes:
        user_id: ID of the user receiving the notification
        type: Type of notification (TaskAssigned, StatusChanged, etc.)
        title: Short notification title
        content: Detailed notification message
        task_id: Optional related task ID
        project_id: Optional related project ID
        action_url: Optional URL for navigation when clicked
        read: Read/unread status flag
        extra_data: Optional JSON with additional context
    """
    __tablename__ = "notifications"

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
        comment="ID of the user receiving the notification"
    )
    type = Column(
        String(50),
        nullable=False,
        comment="Notification type: TaskAssigned, StatusChanged, etc."
    )
    title = Column(
        String(255),
        nullable=False,
        comment="Short notification title"
    )
    content = Column(
        String(1000),
        nullable=False,
        comment="Detailed notification message"
    )
    task_id = Column(
        Integer,
        ForeignKey("tasks.id"),
        nullable=True,
        comment="Optional related task ID"
    )
    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        nullable=True,
        comment="Optional related project ID"
    )
    action_url = Column(
        String(500),
        nullable=True,
        comment="URL to navigate when notification is clicked"
    )
    read = Column(
        Boolean,
        default=False,
        index=True,
        comment="Read/unread status flag"
    )
    extra_data = Column(
        JSON,
        nullable=True,
        comment="Additional context data as JSON"
    )

    user = relationship("User", back_populates="notifications")
    task = relationship("Task", back_populates="notifications")
    project = relationship("Project", back_populates="notifications")