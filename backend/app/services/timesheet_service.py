"""
Timesheet service for tracking work hours on tasks.

This service handles:
- Logging work hours on tasks
- Retrieving timesheets for tasks and users
- Weekly summary generation
- Admin access to all timesheets
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional
from datetime import date, datetime, timedelta

from app.models.timesheet import Timesheet
from app.models.task import Task
from app.models.member import ProjectMember
from app.models.user import User
from app.schemas.timesheet import TimesheetCreate, TimesheetUpdate


class TimesheetService:
    """Service for timesheet management operations."""

    @staticmethod
    def create_timesheet(
        db: Session,
        timesheet_data: TimesheetCreate,
        current_user_id: int
    ) -> Timesheet:
        """
        Create a new timesheet entry.

        Args:
            db: Database session
            timesheet_data: Timesheet creation data
            current_user_id: ID of the current user

        Returns:
            The newly created Timesheet object

        Raises:
            HTTPException 404: Task not found
            HTTPException 403: User is not a project member
            HTTPException 403: User lacks permission to log for others
        """
        task = db.query(Task).filter(
            Task.id == timesheet_data.task_id,
            Task.is_deleted == False
        ).first()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        member = db.query(ProjectMember).filter(
            ProjectMember.project_id == task.project_id,
            ProjectMember.user_id == current_user_id,
            ProjectMember.is_deleted == False
        ).first()
        if not member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this project"
            )

        target_user_id = timesheet_data.user_id if timesheet_data.user_id else current_user_id

        if target_user_id != current_user_id:
            is_admin = db.query(ProjectMember).filter(
                ProjectMember.project_id == task.project_id,
                ProjectMember.user_id == current_user_id,
                ProjectMember.role.in_(["Owner", "Admin"]),
                ProjectMember.is_deleted == False
            ).first()
            if not is_admin:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only Admins and Owners can log time for other users"
                )

        new_timesheet = Timesheet(
            task_id=timesheet_data.task_id,
            user_id=target_user_id,
            date=timesheet_data.date,
            hours=timesheet_data.hours,
            description=timesheet_data.description
        )
        db.add(new_timesheet)

        task.logged_hours = (task.logged_hours or 0) + timesheet_data.hours

        db.commit()
        db.refresh(new_timesheet)

        return new_timesheet

    @staticmethod
    def get_task_timesheets(
        db: Session,
        task_id: int,
        user_id: int
    ) -> List[dict]:
        """
        Get timesheet entries for a specific task.

        Args:
            db: Database session
            task_id: ID of the task
            user_id: ID of the current user

        Returns:
            List of timesheet dictionaries

        Raises:
            HTTPException 404: Task not found
            HTTPException 403: User is not a project member
        """
        task = db.query(Task).filter(
            Task.id == task_id,
            Task.is_deleted == False
        ).first()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        member = db.query(ProjectMember).filter(
            ProjectMember.project_id == task.project_id,
            ProjectMember.user_id == user_id,
            ProjectMember.is_deleted == False
        ).first()

        if not member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this project"
            )

        is_admin_or_owner = member.role in ["Owner", "Admin"]

        query = db.query(Timesheet).filter(Timesheet.task_id == task_id)

        if not is_admin_or_owner:
            query = query.filter(Timesheet.user_id == user_id)

        timesheets = query.order_by(Timesheet.date.desc()).all()

        result = []
        for ts in timesheets:
            user = db.query(User).filter(
                User.id == ts.user_id,
                User.is_deleted == False
            ).first()
            result.append({
                "id": ts.id,
                "task_id": ts.task_id,
                "user_id": ts.user_id,
                "user_name": user.name if user else "Unknown",
                "date": ts.date,
                "hours": ts.hours,
                "description": ts.description,
                "created_at": ts.created_at,
                "updated_at": ts.updated_at
            })

        return result

    @staticmethod
    def get_user_timesheets(
        db: Session,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[dict]:
        """
        Get timesheet entries for a user.

        Args:
            db: Database session
            user_id: ID of the user
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            List of timesheet dictionaries
        """
        is_admin = db.query(ProjectMember).filter(
            ProjectMember.user_id == user_id,
            ProjectMember.role.in_(["Owner", "Admin"])
        ).first()

        query = db.query(Timesheet)

        if not is_admin:
            query = query.filter(Timesheet.user_id == user_id)

        if start_date:
            query = query.filter(Timesheet.date >= start_date)
        if end_date:
            query = query.filter(Timesheet.date <= end_date)

        timesheets = query.order_by(Timesheet.date.desc()).all()

        result = []
        for ts in timesheets:
            user = db.query(User).filter(
                User.id == ts.user_id,
                User.is_deleted == False
            ).first()
            task = db.query(Task).filter(
                Task.id == ts.task_id,
                Task.is_deleted == False
            ).first()
            result.append({
                "id": ts.id,
                "task_id": ts.task_id,
                "task_title": task.title if task else "Unknown",
                "user_id": ts.user_id,
                "user_name": user.name if user else "Unknown",
                "date": ts.date,
                "hours": ts.hours,
                "description": ts.description,
                "created_at": ts.created_at,
                "updated_at": ts.updated_at
            })

        return result

    @staticmethod
    def delete_timesheet(
        db: Session,
        timesheet_id: int,
        user_id: int
    ) -> None:
        """
        Delete a timesheet entry.

        Args:
            db: Database session
            timesheet_id: ID of the timesheet entry
            user_id: ID of the current user

        Raises:
            HTTPException 404: Timesheet entry not found
        """
        timesheet = db.query(Timesheet).filter(
            Timesheet.id == timesheet_id,
            Timesheet.user_id == user_id
        ).first()

        if not timesheet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Timesheet entry not found"
            )

        task = db.query(Task).filter(Task.id == timesheet.task_id).first()
        if task:
            task.logged_hours = max(0, (task.logged_hours or 0) - timesheet.hours)

        db.delete(timesheet)
        db.commit()

    @staticmethod
    def get_weekly_summary(db: Session, user_id: int) -> dict:
        """
        Get a weekly summary of hours for a user.

        Args:
            db: Database session
            user_id: ID of the user

        Returns:
            Weekly summary with total hours and daily breakdown
        """
        today = date.today()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        timesheets = db.query(Timesheet).filter(
            Timesheet.user_id == user_id,
            Timesheet.date >= start_of_week,
            Timesheet.date <= end_of_week
        ).all()

        total_hours = sum(ts.hours for ts in timesheets)

        daily_summary = {}
        for ts in timesheets:
            day = ts.date.isoformat()
            daily_summary[day] = daily_summary.get(day, 0) + ts.hours

        return {
            "week_start": start_of_week.isoformat(),
            "week_end": end_of_week.isoformat(),
            "total_hours": round(total_hours, 1),
            "daily": [{"date": d, "hours": h} for d, h in daily_summary.items()]
        }

    @staticmethod
    def get_all_timesheets(
        db: Session,
        user_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[dict]:
        """
        Get all timesheet entries (Admin/Owner only).

        Args:
            db: Database session
            user_id: Optional user ID filter
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            List of timesheet dictionaries
        """
        query = db.query(Timesheet)

        if user_id:
            query = query.filter(Timesheet.user_id == user_id)

        if start_date:
            query = query.filter(Timesheet.date >= start_date)
        if end_date:
            query = query.filter(Timesheet.date <= end_date)

        timesheets = query.order_by(Timesheet.date.desc()).all()

        result = []
        for ts in timesheets:
            user = db.query(User).filter(
                User.id == ts.user_id,
                User.is_deleted == False
            ).first()
            task = db.query(Task).filter(
                Task.id == ts.task_id,
                Task.is_deleted == False
            ).first()
            result.append({
                "id": ts.id,
                "task_id": ts.task_id,
                "task_title": task.title if task else "Unknown",
                "user_id": ts.user_id,
                "user_name": user.name if user else "Unknown",
                "date": ts.date,
                "hours": ts.hours,
                "description": ts.description,
                "created_at": ts.created_at
            })

        return result