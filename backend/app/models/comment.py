"""
Comment model for task discussions and user interactions.

This model supports:
- User mentions with @mentions
- Soft deletion of comments
"""
from sqlalchemy import Column, Integer, ForeignKey, Text, Boolean, JSON
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Comment(BaseModel):
    """
    Comment on a task.

    Attributes:
        content: The comment text content
        task_id: ID of the task this comment belongs to
        author_id: ID of the user who wrote the comment
        mentions: JSON array of user IDs mentioned in the comment
        is_deleted: Soft delete flag
    """
    __tablename__ = "comments"

    content = Column(
        Text,
        nullable=False,
        comment="The comment text content"
    )
    task_id = Column(
        Integer,
        ForeignKey("tasks.id"),
        nullable=False,
        index=True,
        comment="ID of the task this comment belongs to"
    )
    author_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
        comment="ID of the user who wrote the comment"
    )
    mentions = Column(
        JSON,
        nullable=True,
        comment="JSON array of user IDs mentioned in the comment"
    )
    is_deleted = Column(
        Boolean,
        default=False,
        index=True,
        comment="Soft delete flag"
    )

    task = relationship("Task", back_populates="comments")
    author = relationship("User", back_populates="comments")