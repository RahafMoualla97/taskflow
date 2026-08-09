"""
Activity service for tracking user actions and system events.

Provides logging of activities for tasks, projects, and comments,
retrieving activity logs with enriched user and task data,
and recent activity feeds for dashboard.
"""
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List

from app.models.activity import Activity
from app.models.member import ProjectMember
from app.models.project import Project
from app.models.task import Task
from app.models.user import User


class ActivityService:
    """Service for managing activity logs across the system."""

    @staticmethod
    def log_activity(
        db: Session,
        user_id: int,
        project_id: int,
        action: str,
        task_id: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> Activity:
        """
        Create a new activity log entry.

        Args:
            db: Database session
            user_id: ID of the user performing the action
            project_id: ID of the project context
            action: Human-readable action description
            task_id: Optional task ID for task-related actions
            details: Optional JSON data with additional context

        Returns:
            The newly created Activity object
        """
        activity = Activity(
            user_id=user_id,
            project_id=project_id,
            task_id=task_id,
            action=action,
            details=details
        )
        db.add(activity)
        db.commit()
        db.refresh(activity)
        return activity

    @staticmethod
    def get_project_activities(
        db: Session,
        project_id: int,
        limit: int = 50
    ) -> List[Activity]:
        """
        Retrieve activity logs for a specific project.

        Args:
            db: Database session
            project_id: ID of the project
            limit: Maximum number of activities to return

        Returns:
            List of Activity objects ordered by creation date (newest first)
        """
        return db.query(Activity).filter(
            Activity.project_id == project_id
        ).order_by(
            Activity.created_at.desc()
        ).limit(limit).all()

    @staticmethod
    def get_task_activities(
        db: Session,
        task_id: int,
        limit: int = 20
    ) -> List[Activity]:
        """
        Retrieve activity logs for a specific task.

        Args:
            db: Database session
            task_id: ID of the task
            limit: Maximum number of activities to return

        Returns:
            List of Activity objects ordered by creation date (newest first)
        """
        return db.query(Activity).filter(
            Activity.task_id == task_id
        ).order_by(
            Activity.created_at.desc()
        ).limit(limit).all()

    @staticmethod
    def get_recent_activities(
        db: Session,
        user_id: int,
        limit: int = 10
    ) -> List[dict]:
        """
        Retrieve recent activities from projects the user is a member of.

        Args:
            db: Database session
            user_id: ID of the user
            limit: Maximum number of activities to return

        Returns:
            List of enriched activity dictionaries with user, project, and task details
        """
        member_projects = db.query(ProjectMember).filter(
            ProjectMember.user_id == user_id,
            ProjectMember.is_deleted == False
        ).all()
        project_ids = [mp.project_id for mp in member_projects]

        if not project_ids:
            return []

        activities = db.query(Activity).filter(
            Activity.project_id.in_(project_ids)
        ).order_by(
            Activity.created_at.desc()
        ).limit(limit).all()

        result = []
        for activity in activities:
            user = db.query(User).filter(User.id == activity.user_id).first()
            project = db.query(Project).filter(Project.id == activity.project_id).first()
            task = None
            if activity.task_id:
                task = db.query(Task).filter(Task.id == activity.task_id).first()

            result.append({
                "id": activity.id,
                "user_id": activity.user_id,
                "user_name": user.name if user else "Unknown",
                "project_id": activity.project_id,
                "project_name": project.name if project else None,
                "task_id": activity.task_id,
                "task_title": task.title if task else None,
                "action": activity.action,
                "created_at": activity.created_at
            })

        return result