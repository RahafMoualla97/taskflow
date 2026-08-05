"""
Comment API endpoints.

This module handles comment operations on tasks including:
- Adding comments with mentions
- Retrieving all comments for a task
- Soft deleting comments
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentUpdate, CommentOut
from app.services.task_service import TaskService

router = APIRouter(prefix="/comments", tags=["Comments"])


@router.post("/task/{task_id}", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
def add_comment(
    task_id: int,
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Add a comment to a task.

    Supports:
    - Mentioning other users (via @mentions)

    Args:
        task_id: ID of the task to comment on
        comment_data: Comment content and mentions
        current_user: Authenticated user
        db: Database session

    Returns:
        The newly created comment object

    Raises:
        HTTPException 404: Task not found
        HTTPException 403: User is not a project member
    """
    return TaskService.add_comment(
        db,
        task_id,
        current_user.id,
        comment_data.content,
        comment_data.mentions
    )


@router.get("/task/{task_id}", response_model=List[CommentOut])
def get_task_comments(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve all comments for a task.

    Includes author information.

    Args:
        task_id: ID of the task
        current_user: Authenticated user (for membership verification)
        db: Database session

    Returns:
        List of comment objects with author_name

    Raises:
        HTTPException 404: Task not found
        HTTPException 403: User is not a project member
    """
    return TaskService.get_task_comments(db, task_id, current_user.id)


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    comment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Soft delete a comment.

    Only the comment author, Admin, or Owner can delete a comment.

    Args:
        comment_id: ID of the comment to delete
        current_user: Authenticated user
        db: Database session

    Returns:
        None (204 No Content)

    Raises:
        HTTPException 404: Comment not found
        HTTPException 403: User lacks permission
    """
    TaskService.delete_comment(db, comment_id, current_user.id)
    return None