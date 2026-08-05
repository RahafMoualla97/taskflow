"""
Activity API endpoints for retrieving project and task activity logs.

This module provides endpoints to fetch recent activities for projects,
tasks, and the current user's dashboard.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.services.activity_service import ActivityService
from app.services.project_service import ProjectService
from app.services.task_service import TaskService

router = APIRouter(prefix="/activities", tags=["Activities"])


@router.get("/project/{project_id}")
def get_project_activities(
    project_id: int,
    limit: int = Query(50, ge=1, le=100, description="Number of activities to return"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve activity logs for a specific project.

    Requires the user to be a member of the project.

    Args:
        project_id: ID of the project
        limit: Maximum number of activities to return (1-100)
        current_user: Authenticated user
        db: Database session

    Returns:
        List of activity records for the project
    """
    ProjectService.get_project_by_id(db, project_id, current_user.id)
    return ActivityService.get_project_activities(db, project_id, limit)


@router.get("/task/{task_id}")
def get_task_activities(
    task_id: int,
    limit: int = Query(20, ge=1, le=50, description="Number of activities to return"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve activity logs for a specific task.

    Requires the user to be a member of the task's project.

    Args:
        task_id: ID of the task
        limit: Maximum number of activities to return (1-50)
        current_user: Authenticated user
        db: Database session

    Returns:
        List of activity records for the task
    """
    TaskService.get_task_by_id(db, task_id, current_user.id)
    return ActivityService.get_task_activities(db, task_id, limit)


@router.get("/recent")
def get_recent_activities(
    limit: int = Query(10, ge=1, le=50, description="Number of activities to return"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve recent activities for the current user.

    Returns activities from all projects the user is a member of,
    ordered by most recent first.

    Args:
        limit: Maximum number of activities to return (1-50)
        current_user: Authenticated user
        db: Database session

    Returns:
        List of recent activity records for the user
    """
    return ActivityService.get_recent_activities(db, current_user.id, limit)