"""
Project management API endpoints.

This module handles project CRUD operations including:
- Creating new projects
- Retrieving user projects
- Searching projects by name/description/key
- Updating project details
- Soft deleting projects
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.models.project import Project
from app.models.member import ProjectMember
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectOut
from app.services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("/", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new project.

    The creator automatically becomes the project Owner.

    Args:
        project_data: Project creation data (name, description)
        current_user: Authenticated user
        db: Database session

    Returns:
        The newly created Project object
    """
    return ProjectService.create_project(db, project_data, current_user.id)


@router.get("/", response_model=List[ProjectOut])
def get_projects(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all projects the current user is a member of.

    Returns only active projects (is_deleted=False).

    Args:
        current_user: Authenticated user
        db: Database session

    Returns:
        List of Project objects
    """
    return ProjectService.get_user_projects(db, current_user.id)


@router.get("/search", response_model=List[ProjectOut])
def search_projects(
    q: str = Query(..., min_length=1, description="Search term for name, description, or key"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Search for projects by name, description, or key.

    Only searches within projects the user is a member of.

    Args:
        q: Search term (minimum 1 character)
        current_user: Authenticated user
        db: Database session

    Returns:
        List of Project objects matching the search
    """
    member_projects = db.query(ProjectMember).filter(
        ProjectMember.user_id == current_user.id,
        ProjectMember.is_deleted == False
    ).all()
    project_ids = [mp.project_id for mp in member_projects]

    if not project_ids:
        return []

    projects = db.query(Project).filter(
        Project.id.in_(project_ids),
        Project.is_deleted == False,
        or_(
            Project.name.ilike(f"%{q}%"),
            Project.description.ilike(f"%{q}%"),
            Project.key.ilike(f"%{q}%")
        )
    ).all()

    return projects


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific project by ID.

    Args:
        project_id: ID of the project
        current_user: Authenticated user (must be a project member)
        db: Database session

    Returns:
        Project object

    Raises:
        HTTPException 403: User is not a project member
        HTTPException 404: Project not found
    """
    return ProjectService.get_project_by_id(db, project_id, current_user.id)


@router.put("/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing project.

    Only Admins and Owners can update projects.

    Args:
        project_id: ID of the project
        project_data: Updated project data
        current_user: Authenticated user (must be Admin or Owner)
        db: Database session

    Returns:
        The updated Project object

    Raises:
        HTTPException 403: User lacks permission
        HTTPException 404: Project not found
    """
    return ProjectService.update_project(db, project_id, current_user.id, project_data)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Soft delete a project.

    Only the Owner can delete a project.
    Associated notifications are also deleted.

    Args:
        project_id: ID of the project
        current_user: Authenticated user (must be Owner)
        db: Database session

    Returns:
        None (204 No Content)

    Raises:
        HTTPException 403: User is not the project owner
        HTTPException 404: Project not found
    """
    ProjectService.delete_project(db, project_id, current_user.id)
    return None