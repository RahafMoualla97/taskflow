"""
Notification Pydantic schemas.

Defines request/response schemas for:
- Notification responses with read status
- Updating notification read status
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class NotificationOut(BaseModel):
    """
    Schema for notification response.

    Attributes:
        id: Notification ID
        user_id: ID of the user receiving the notification
        type: Notification type (TaskAssigned, StatusChanged, etc.)
        title: Short notification title
        content: Detailed notification message
        task_id: Optional related task ID
        project_id: Optional related project ID
        action_url: Optional URL for navigation
        read: Read/unread status
        created_at: Creation timestamp
    """
    id: int
    user_id: int
    type: str
    title: str
    content: str
    task_id: Optional[int] = None
    project_id: Optional[int] = None
    action_url: Optional[str] = None
    read: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationUpdate(BaseModel):
    """
    Schema for marking a notification as read.

    Attributes:
        read: New read status (default: True)
    """
    read: bool = Field(True, description="Mark notification as read")