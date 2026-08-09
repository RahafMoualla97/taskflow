"""
Timesheet API endpoints.
Handles time tracking operations including logging work hours on tasks,
retrieving timesheets for tasks and users, weekly summary generation,
and admin access to all timesheets.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import date

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.models.member import ProjectMember
from app.schemas.timesheet import TimesheetCreate, TimesheetUpdate, TimesheetOut
from app.services.timesheet_service import TimesheetService

router = APIRouter(prefix="/timesheets", tags=["Timesheets"])


@router.post("/", response_model=TimesheetOut, status_code=status.HTTP_201_CREATED)
def create_timesheet(
    timesheet_data: TimesheetCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Log work hours on a task.
    
    Regular users can only log hours for themselves.
    Admins and Owners can log hours for other users.
    
    Args:
        timesheet_data: Timesheet data (task_id, date, hours, description)
        current_user: The authenticated user
        db: Database session
    
    Returns:
        The newly created Timesheet object
    
    Raises:
        HTTPException 404: Task not found
        HTTPException 403: User is not a project member or lacks permission
    """
    return TimesheetService.create_timesheet(db, timesheet_data, current_user.id)


@router.get("/task/{task_id}", response_model=List[TimesheetOut])
def get_task_timesheets(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all timesheet entries for a specific task.
    
    Regular users see only their own entries.
    Admins and Owners see all entries.
    
    Args:
        task_id: The ID of the task
        current_user: The authenticated user (must be a project member)
        db: Database session
    
    Returns:
        List of Timesheet entries for the task
    
    Raises:
        HTTPException 404: Task not found
        HTTPException 403: User is not a project member
    """
    return TimesheetService.get_task_timesheets(db, task_id, current_user.id)


@router.get("/my", response_model=List[TimesheetOut])
def get_my_timesheets(
    start_date: Optional[date] = Query(None, description="Filter entries from this date"),
    end_date: Optional[date] = Query(None, description="Filter entries to this date"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get timesheet entries for the current user.
    
    Regular users see only their own entries.
    Admins and Owners see all entries (with optional user filtering).
    
    Args:
        start_date: Optional start date filter
        end_date: Optional end date filter
        current_user: The authenticated user
        db: Database session
    
    Returns:
        List of Timesheet entries for the user
    """
    return TimesheetService.get_user_timesheets(db, current_user.id, start_date, end_date)


@router.get("/weekly-summary")
def get_weekly_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a weekly summary of hours for the current user.
    
    The week starts on Monday and ends on Sunday.
    
    Args:
        current_user: The authenticated user
        db: Database session
    
    Returns:
        Weekly summary including total hours and daily breakdown
    """
    return TimesheetService.get_weekly_summary(db, current_user.id)


@router.delete("/{timesheet_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_timesheet(
    timesheet_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a timesheet entry.
    
    Users can only delete their own entries.
    
    Args:
        timesheet_id: The ID of the timesheet entry
        current_user: The authenticated user (must own the entry)
        db: Database session
    
    Returns:
        None (204 No Content)
    
    Raises:
        HTTPException 404: Timesheet entry not found
    """
    TimesheetService.delete_timesheet(db, timesheet_id, current_user.id)
    return None


@router.get("/all", response_model=List[TimesheetOut])
def get_all_timesheets(
    start_date: Optional[date] = Query(None, description="Filter entries from this date"),
    end_date: Optional[date] = Query(None, description="Filter entries to this date"),
    user_id: Optional[int] = Query(None, description="Filter by specific user ID (admin only)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all timesheet entries across the system.
    
    Only Admins and Owners can access this endpoint.
    
    Args:
        start_date: Optional start date filter
        end_date: Optional end date filter
        user_id: Optional user ID filter (to view specific user's entries)
        current_user: The authenticated user (must be Admin or Owner)
        db: Database session
    
    Returns:
        List of all Timesheet entries
    
    Raises:
        HTTPException 403: User is not an Admin or Owner
    """
    is_admin = db.query(ProjectMember).filter(
        ProjectMember.user_id == current_user.id,
        ProjectMember.role.in_(["Owner", "Admin"])
    ).first()

    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Admins and Owners can view all timesheets"
        )

    target_user_id = user_id if user_id else None

    return TimesheetService.get_all_timesheets(db, target_user_id, start_date, end_date)