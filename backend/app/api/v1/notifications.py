"""
Notification API endpoints.

This module handles user notifications including:
- Retrieving notifications (all or unread only)
- Getting unread count
- Marking individual or all notifications as read
- Deleting notifications
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.notification import NotificationOut, NotificationUpdate
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/", response_model=List[NotificationOut])
def get_notifications(
    unread_only: bool = Query(False, description="Filter to only unread notifications"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all notifications for the current user.

    Args:
        unread_only: If True, only return unread notifications
        current_user: Authenticated user
        db: Database session

    Returns:
        List of Notification objects ordered by creation date (newest first)
    """
    return NotificationService.get_user_notifications(db, current_user.id, unread_only)


@router.get("/unread-count")
def get_unread_count(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get the number of unread notifications for the current user.

    Args:
        current_user: Authenticated user
        db: Database session

    Returns:
        Dictionary with unread_count
    """
    count = NotificationService.get_unread_count(db, current_user.id)
    return {"unread_count": count}


@router.patch("/{notification_id}/read", response_model=NotificationOut)
def mark_notification_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Mark a specific notification as read.

    Args:
        notification_id: ID of the notification to mark as read
        current_user: Authenticated user (must own the notification)
        db: Database session

    Returns:
        The updated Notification object

    Raises:
        HTTPException 404: Notification not found
    """
    return NotificationService.mark_as_read(db, notification_id, current_user.id)


@router.patch("/read-all")
def mark_all_as_read(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Mark all notifications for the current user as read.

    Args:
        current_user: Authenticated user
        db: Database session

    Returns:
        Success message with count of marked notifications
    """
    return NotificationService.mark_all_as_read(db, current_user.id)


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a notification.

    Args:
        notification_id: ID of the notification to delete
        current_user: Authenticated user (must own the notification)
        db: Database session

    Returns:
        None (204 No Content)

    Raises:
        HTTPException 404: Notification not found
    """
    NotificationService.delete_notification(db, notification_id, current_user.id)
    return None