"""
Project Pydantic schemas.

Defines request/response schemas for:
- Creating and updating projects
- Project responses with statistics
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ProjectCreate(BaseModel):
    """
    Schema for creating a new project.

    Attributes:
        name: Project name
        description: Optional project description
    """
    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(None, max_length=1000, description="Project description")


class ProjectUpdate(BaseModel):
    """
    Schema for updating an existing project.

    Attributes:
        name: Updated project name
        description: Updated project description
    """
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Updated project name")
    description: Optional[str] = Field(None, max_length=1000, description="Updated project description")


class ProjectOut(BaseModel):
    """
    Schema for project response.

    Attributes:
        id: Project ID
        name: Project name
        key: Unique project key
        description: Project description
        owner_id: ID of the project owner
        created_at: Creation timestamp
    """
    id: int
    name: str
    key: str
    description: Optional[str] = None
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ProjectDetail(ProjectOut):
    """
    Extended project schema with statistics.

    Attributes:
        members_count: Number of project members
        tasks_count: Number of tasks in the project
    """
    members_count: int = 0
    tasks_count: int = 0