"""
Notification service for managing user notifications.

Provides CRUD operations for notifications including marking as read,
getting unread counts, and creating new notifications.
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional

from app.models.notification import Notification


class NotificationService:
    """Service for managing user notifications."""

    @staticmethod
    def get_user_notifications(
        db: Session,
        user_id: int,
        unread_only: bool = False
    ) -> List[Notification]:
        """
        Retrieve all notifications for a user.

        Args:
            db: Database session
            user_id: ID of the user
            unread_only: If True, only return unread notifications

        Returns:
            List of Notification objects ordered by creation date (newest first)
        """
        query = db.query(Notification).filter(Notification.user_id == user_id)
        if unread_only:
            query = query.filter(Notification.read == False)
        return query.order_by(Notification.created_at.desc()).all()

    @staticmethod
    def get_unread_count(db: Session, user_id: int) -> int:
        """
        Get the number of unread notifications for a user.

        Args:
            db: Database session
            user_id: ID of the user

        Returns:
            Count of unread notifications
        """
        return db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.read == False
        ).count()

    @staticmethod
    def mark_as_read(
        db: Session,
        notification_id: int,
        user_id: int
    ) -> Notification:
        """
        Mark a specific notification as read.

        Args:
            db: Database session
            notification_id: ID of the notification to mark as read
            user_id: ID of the user (for ownership verification)

        Returns:
            The updated Notification object

        Raises:
            HTTPException 404: If notification not found
        """
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()

        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )

        notification.read = True
        db.commit()
        db.refresh(notification)
        return notification

    @staticmethod
    def mark_all_as_read(db: Session, user_id: int) -> dict:
        """
        Mark all notifications for a user as read.

        Args:
            db: Database session
            user_id: ID of the user

        Returns:
            Dictionary with success message and count
        """
        notifications = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.read == False
        ).all()

        for notification in notifications:
            notification.read = True

        db.commit()
        return {"message": f"Marked {len(notifications)} notifications as read"}

    @staticmethod
    def delete_notification(
        db: Session,
        notification_id: int,
        user_id: int
    ) -> None:
        """
        Delete a notification.

        Args:
            db: Database session
            notification_id: ID of the notification to delete
            user_id: ID of the user (for ownership verification)

        Raises:
            HTTPException 404: If notification not found
        """
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()

        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )

        db.delete(notification)
        db.commit()

    @staticmethod
    def create_notification(
        db: Session,
        user_id: int,
        notif_type: str,
        title: str,
        content: str,
        task_id: Optional[int] = None,
        project_id: Optional[int] = None,
        action_url: Optional[str] = None
    ) -> Notification:
        """
        Create a new notification.

        Args:
            db: Database session
            user_id: ID of the user to notify
            notif_type: Type of notification (TaskAssigned, StatusChanged, etc.)
            title: Notification title
            content: Notification content
            task_id: Optional task ID
            project_id: Optional project ID
            action_url: Optional URL for the notification action

        Returns:
            The newly created Notification object
        """
        notification = Notification(
            user_id=user_id,
            type=notif_type,
            title=title,
            content=content,
            task_id=task_id,
            project_id=project_id,
            action_url=action_url,
            read=False
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)

        return notification