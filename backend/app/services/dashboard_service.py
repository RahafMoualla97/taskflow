"""
Dashboard service for aggregated statistics and analytics.

Provides task statistics (by status, priority, overdue), project statistics
(counts, members, tasks), dashboard overview statistics, and recent activity feeds.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from app.models.task import Task
from app.models.project import Project
from app.models.member import ProjectMember
from app.models.user import User
from app.models.activity import Activity


class DashboardService:
    """Service for dashboard analytics and statistics."""

    @staticmethod
    def get_task_stats(db: Session, user_id: int) -> Dict[str, Any]:
        """
        Get task statistics for a user.

        Args:
            db: Database session
            user_id: ID of the user

        Returns:
            Dictionary with task statistics (total, by_status, overdue, by_priority)
        """
        member_projects = db.query(ProjectMember).filter(
            ProjectMember.user_id == user_id,
            ProjectMember.is_deleted == False
        ).all()
        project_ids = [mp.project_id for mp in member_projects]

        if not project_ids:
            return {
                "total_tasks": 0,
                "by_status": {"ToDo": 0, "InProgress": 0, "Done": 0},
                "overdue": 0,
                "by_priority": {"Low": 0, "Medium": 0, "High": 0}
            }

        total_tasks = db.query(Task).filter(
            Task.project_id.in_(project_ids),
            Task.is_deleted == False
        ).count()

        status_counts = db.query(
            Task.status,
            func.count(Task.id).label('count')
        ).filter(
            Task.project_id.in_(project_ids),
            Task.is_deleted == False
        ).group_by(Task.status).all()

        by_status = {"ToDo": 0, "InProgress": 0, "Done": 0}
        for s in status_counts:
            if s.status in by_status:
                by_status[s.status] = s.count

        now = datetime.now(timezone.utc)
        overdue = db.query(Task).filter(
            Task.project_id.in_(project_ids),
            Task.due_date.isnot(None),
            Task.due_date < now,
            Task.status != "Done",
            Task.is_deleted == False
        ).count()

        priority_counts = db.query(
            Task.priority,
            func.count(Task.id).label('count')
        ).filter(
            Task.project_id.in_(project_ids),
            Task.is_deleted == False
        ).group_by(Task.priority).all()

        by_priority = {"Low": 0, "Medium": 0, "High": 0}
        for p in priority_counts:
            if p.priority in by_priority:
                by_priority[p.priority] = p.count

        return {
            "total_tasks": total_tasks,
            "by_status": by_status,
            "overdue": overdue,
            "by_priority": by_priority
        }

    @staticmethod
    def get_project_stats(db: Session, user_id: int) -> Dict[str, Any]:
        """
        Get project statistics for a user.

        Args:
            db: Database session
            user_id: ID of the user

        Returns:
            Dictionary with project statistics (total, members, tasks)
        """
        member_projects = db.query(ProjectMember).filter(
            ProjectMember.user_id == user_id,
            ProjectMember.is_deleted == False
        ).all()
        project_ids = [p.project_id for p in member_projects]

        total_projects = len(project_ids)

        if not project_ids:
            return {
                "total_projects": 0,
                "total_members": 0,
                "total_tasks": 0
            }

        total_members = db.query(ProjectMember).filter(
            ProjectMember.project_id.in_(project_ids),
            ProjectMember.is_deleted == False
        ).count()

        total_tasks = db.query(Task).filter(
            Task.project_id.in_(project_ids),
            Task.is_deleted == False
        ).count()

        return {
            "total_projects": total_projects,
            "total_members": total_members,
            "total_tasks": total_tasks
        }

    @staticmethod
    def get_project_detail_stats(
        db: Session,
        project_id: int,
        user_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get detailed statistics for a specific project.

        Args:
            db: Database session
            project_id: ID of the project
            user_id: ID of the user (for membership verification)

        Returns:
            Dictionary with project statistics, or None if user is not a member
        """
        member = db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
            ProjectMember.is_deleted == False
        ).first()

        if not member:
            return None

        total_tasks = db.query(Task).filter(
            Task.project_id == project_id,
            Task.is_deleted == False
        ).count()

        status_counts = db.query(
            Task.status,
            func.count(Task.id).label('count')
        ).filter(
            Task.project_id == project_id,
            Task.is_deleted == False
        ).group_by(Task.status).all()

        by_status = {"ToDo": 0, "InProgress": 0, "Done": 0}
        for s in status_counts:
            if s.status in by_status:
                by_status[s.status] = s.count

        now = datetime.now(timezone.utc)
        overdue = db.query(Task).filter(
            Task.project_id == project_id,
            Task.due_date.isnot(None),
            Task.due_date < now,
            Task.status != "Done",
            Task.is_deleted == False
        ).count()

        priority_counts = db.query(
            Task.priority,
            func.count(Task.id).label('count')
        ).filter(
            Task.project_id == project_id,
            Task.is_deleted == False
        ).group_by(Task.priority).all()

        by_priority = {"Low": 0, "Medium": 0, "High": 0}
        for p in priority_counts:
            if p.priority in by_priority:
                by_priority[p.priority] = p.count

        return {
            "total_tasks": total_tasks,
            "by_status": by_status,
            "overdue": overdue,
            "by_priority": by_priority
        }

    @staticmethod
    def get_dashboard_stats(db: Session, user_id: int) -> Dict[str, Any]:
        """
        Get simplified dashboard statistics for a user.

        Args:
            db: Database session
            user_id: ID of the user

        Returns:
            Dictionary with dashboard statistics
        """
        member_projects = db.query(ProjectMember).filter(
            ProjectMember.user_id == user_id,
            ProjectMember.is_deleted == False
        ).all()
        project_ids = [mp.project_id for mp in member_projects]

        total_projects = len(project_ids)

        if not project_ids:
            return {
                "total_projects": 0,
                "total_tasks": 0,
                "completed_tasks": 0,
                "overdue_tasks": 0,
                "my_tasks": 0
            }

        total_tasks = db.query(Task).filter(
            Task.project_id.in_(project_ids),
            Task.is_deleted == False
        ).count()

        completed_tasks = db.query(Task).filter(
            Task.project_id.in_(project_ids),
            Task.status == "Done",
            Task.is_deleted == False
        ).count()

        now = datetime.now(timezone.utc)
        overdue_tasks = db.query(Task).filter(
            Task.project_id.in_(project_ids),
            Task.due_date.isnot(None),
            Task.due_date < now,
            Task.status != "Done",
            Task.is_deleted == False
        ).count()

        my_tasks = db.query(Task).filter(
            Task.assignee_id == user_id,
            Task.is_deleted == False,
            Task.status != "Done"
        ).count()

        return {
            "total_projects": total_projects,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "overdue_tasks": overdue_tasks,
            "my_tasks": my_tasks
        }

    @staticmethod
    def get_recent_activities(
        db: Session,
        user_id: int,
        limit: int = 10
    ) -> List[dict]:
        """
        Get recent activities from projects the user is a member of.

        Args:
            db: Database session
            user_id: ID of the user
            limit: Maximum number of activities to return

        Returns:
            List of enriched activity dictionaries
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
                "user_name": user.name if user else None,
                "project_id": activity.project_id,
                "project_name": project.name if project else None,
                "task_id": activity.task_id,
                "task_title": task.title if task else None,
                "action": activity.action,
                "created_at": activity.created_at
            })

        return result