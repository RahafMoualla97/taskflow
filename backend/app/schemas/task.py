"""
Task Pydantic schemas.

Defines request/response schemas for:
- Creating, updating, and managing tasks
- Task status updates
- Task responses with enriched data
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TaskCreate(BaseModel):
    """
    Schema for creating a new task.

    Attributes:
        title: Task title
        description: Optional task description
        project_id: ID of the parent project
        assignee_id: Optional user ID assigned to the task
        due_date: Optional due date
        priority: Task priority (Low, Medium, High)
    """
    title: str = Field(..., min_length=1, max_length=255, description="Task title")
    description: Optional[str] = Field(None, max_length=2000, description="Task description")
    project_id: int = Field(..., description="ID of the parent project")
    assignee_id: Optional[int] = Field(None, description="User ID assigned to the task")
    due_date: Optional[datetime] = Field(None, description="Due date")
    priority: str = Field("Medium", description="Task priority: Low, Medium, or High")


class TaskUpdate(BaseModel):
    """
    Schema for updating an existing task.

    Attributes:
        title: Updated task title
        description: Updated task description
        assignee_id: Updated assignee
        due_date: Updated due date
        priority: Updated priority
        estimated_hours: Updated estimated hours
    """
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    assignee_id: Optional[int] = None
    due_date: Optional[datetime] = None
    priority: Optional[str] = None
    estimated_hours: Optional[int] = Field(None, ge=0)


class TaskStatusUpdate(BaseModel):
    """
    Schema for updating task status.

    Attributes:
        status: New status (ToDo, InProgress, Done)
    """
    status: str = Field(..., description="New status: ToDo, InProgress, or Done")


class TaskOut(BaseModel):
    """
    Schema for task response with enriched data.

    Attributes:
        id: Task ID
        title: Task title
        description: Task description
        status: Current status
        priority: Task priority
        project_id: ID of the parent project
        assignee_id: ID of the assignee
        reporter_id: ID of the reporter
        due_date: Due date
        estimated_hours: Estimated hours
        logged_hours: Logged hours
        created_at: Creation timestamp
        updated_at: Last update timestamp
        assignee_name: Name of the assignee (enriched)
        reporter_name: Name of the reporter (enriched)
        project_name: Name of the project (enriched)
    """
    id: int
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    project_id: int
    assignee_id: Optional[int] = None
    reporter_id: int
    due_date: Optional[datetime] = None
    estimated_hours: Optional[int] = None
    logged_hours: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None

    assignee_name: Optional[str] = None
    reporter_name: Optional[str] = None
    project_name: Optional[str] = None

    class Config:
        from_attributes = True