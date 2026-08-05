"""
Timesheet Pydantic schemas.

This module defines the request/response schemas for:
- Logging work hours on tasks
- Updating timesheet entries
- Timesheet responses with user and task details
"""
from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional


class TimesheetCreate(BaseModel):
    """
    Schema for creating a timesheet entry.

    Attributes:
        task_id: ID of the task
        user_id: Optional user ID (defaults to current user)
        date: Date of work
        hours: Number of hours worked
        description: Optional description of work done
    """
    task_id: int
    user_id: Optional[int] = None
    date: date
    hours: float
    description: Optional[str] = None


class TimesheetUpdate(BaseModel):
    """
    Schema for updating a timesheet entry.

    Attributes:
        date: Updated date
        hours: Updated hours
        description: Updated description
    """
    date: Optional[date] = None
    hours: Optional[float] = None
    description: Optional[str] = None


class TimesheetOut(BaseModel):
    """
    Schema for timesheet response.

    Attributes:
        id: Timesheet entry ID
        task_id: ID of the task
        user_id: ID of the user
        user_name: Name of the user (enriched)
        task_title: Title of the task (enriched)
        date: Date of work
        hours: Number of hours worked
        description: Description of work done
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    id: int
    task_id: int
    user_id: int
    user_name: Optional[str] = None
    task_title: Optional[str] = None
    date: date
    hours: float
    description: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True