"""
Comment Pydantic schemas.

This module defines the request/response schemas for:
- Creating comments with mentions
- Updating comments
- Comment responses with author information
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class CommentCreate(BaseModel):
    """
    Schema for creating a new comment.

    Attributes:
        content: Comment text content
        mentions: List of user IDs mentioned in the comment
    """
    content: str = Field(..., min_length=1, description="Comment text content")
    mentions: Optional[List[int]] = Field(default=[], description="List of mentioned user IDs")


class CommentUpdate(BaseModel):
    """
    Schema for updating an existing comment.

    Attributes:
        content: Updated comment text content
    """
    content: str = Field(..., min_length=1, description="Updated comment text content")


class CommentOut(BaseModel):
    """
    Schema for comment response.

    Attributes:
        id: Comment ID
        content: Comment text content
        task_id: ID of the task this comment belongs to
        author_id: ID of the comment author
        author_name: Name of the comment author
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    id: int
    content: str
    task_id: int
    author_id: int
    author_name: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True