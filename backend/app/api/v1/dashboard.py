"""
Dashboard API endpoints.
Provides aggregated statistics and data for the user's dashboard,
including task counts, project summaries, and activity timelines.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.models.task import Task
from app.models.project import Project
from app.models.member import ProjectMember
from app.models.activity import Activity
from app.services.dashboard_service import DashboardService
from app.services.task_service import TaskService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats")
def get_dashboard_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get basic dashboard statistics for the current user.
    
    Returns counts for: projects, total tasks, completed tasks,
    overdue tasks, and tasks assigned to the user.
    
    Args:
        current_user: The authenticated user
        db: Database session
    
    Returns:
        Dictionary with dashboard statistics
    """
    return DashboardService.get_dashboard_stats(db, current_user.id)


@router.get("/tasks/recent")
def get_recent_tasks(
    limit: int = Query(5, ge=1, le=20, description="Number of recent tasks to return"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get the most recent tasks from projects the user is a member of.
    
    Args:
        limit: Maximum number of tasks to return (1-20)
        current_user: The authenticated user
        db: Database session
    
    Returns:
        List of recent Task objects
    """
    return TaskService.get_recent_tasks(db, current_user.id, limit)


@router.get("/tasks/overdue")
def get_overdue_tasks(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all overdue tasks from projects the user is a member of.
    
    Tasks are considered overdue if due_date is in the past
    and status is not "Done".
    
    Args:
        current_user: The authenticated user
        db: Database session
    
    Returns:
        List of overdue Task objects
    """
    return TaskService.get_overdue_tasks(db, current_user.id)


@router.get("/tasks/my")
def get_my_tasks(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all tasks assigned to the current user (excluding completed tasks).
    
    Args:
        current_user: The authenticated user
        db: Database session
    
    Returns:
        List of assigned Task objects
    """
    return TaskService.get_my_tasks(db, current_user.id)


@router.get("/advanced-stats")
def get_advanced_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive dashboard statistics for the current user.
    
    Includes:
    - Tasks breakdown by status (ToDo, InProgress, Done)
    - Tasks breakdown by priority (Low, Medium, High)
    - Tasks breakdown by project
    - Weekly activity timeline
    - Total task count
    - Completion rate percentage
    - Overdue task count
    
    Args:
        current_user: The authenticated user
        db: Database session
    
    Returns:
        Dictionary with advanced dashboard statistics
    """
    member_projects = db.query(ProjectMember).filter(
        ProjectMember.user_id == current_user.id,
        ProjectMember.is_deleted == False
    ).all()
    project_ids = [mp.project_id for mp in member_projects]

    if not project_ids:
        return {
            "tasks_by_status": {"ToDo": 0, "InProgress": 0, "Done": 0},
            "tasks_by_priority": {"Low": 0, "Medium": 0, "High": 0},
            "tasks_by_project": [],
            "weekly_activity": [],
            "total_tasks": 0,
            "completion_rate": 0,
            "overdue_count": 0
        }

    status_counts = db.query(
        Task.status,
        func.count(Task.id).label('count')
    ).filter(
        Task.project_id.in_(project_ids),
        Task.is_deleted == False
    ).group_by(Task.status).all()

    tasks_by_status = {"ToDo": 0, "InProgress": 0, "Done": 0}
    for s in status_counts:
        if s.status in tasks_by_status:
            tasks_by_status[s.status] = s.count

    priority_counts = db.query(
        Task.priority,
        func.count(Task.id).label('count')
    ).filter(
        Task.project_id.in_(project_ids),
        Task.is_deleted == False
    ).group_by(Task.priority).all()

    tasks_by_priority = {"Low": 0, "Medium": 0, "High": 0}
    for p in priority_counts:
        if p.priority in tasks_by_priority:
            tasks_by_priority[p.priority] = p.count

    project_counts = db.query(
        Project.id,
        Project.name,
        func.count(Task.id).label('count')
    ).join(
        Task, Task.project_id == Project.id
    ).filter(
        Project.id.in_(project_ids),
        Project.is_deleted == False,
        Task.is_deleted == False
    ).group_by(Project.id, Project.name).all()

    tasks_by_project = [
        {"name": p.name, "count": p.count}
        for p in project_counts
    ]

    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    daily_activity = db.query(
        func.date(Activity.created_at).label('date'),
        func.count(Activity.id).label('count')
    ).filter(
        Activity.project_id.in_(project_ids),
        Activity.created_at >= week_ago
    ).group_by(
        func.date(Activity.created_at)
    ).order_by(
        func.date(Activity.created_at)
    ).all()

    weekly_activity = [
        {"date": d.date.strftime("%Y-%m-%d"), "count": d.count}
        for d in daily_activity
    ]

    total_tasks = db.query(Task).filter(
        Task.project_id.in_(project_ids),
        Task.is_deleted == False
    ).count()

    completed = db.query(Task).filter(
        Task.project_id.in_(project_ids),
        Task.status == "Done",
        Task.is_deleted == False
    ).count()

    completion_rate = round((completed / total_tasks * 100) if total_tasks > 0 else 0, 1)

    now = datetime.now(timezone.utc)
    overdue_count = db.query(Task).filter(
        Task.project_id.in_(project_ids),
        Task.due_date.isnot(None),
        Task.due_date < now,
        Task.status != "Done",
        Task.is_deleted == False
    ).count()

    return {
        "tasks_by_status": tasks_by_status,
        "tasks_by_priority": tasks_by_priority,
        "tasks_by_project": tasks_by_project,
        "weekly_activity": weekly_activity,
        "total_tasks": total_tasks,
        "completion_rate": completion_rate,
        "overdue_count": overdue_count
    }