"""
Member management API endpoints.
Handles project member operations including listing project members,
adding new members (or reactivating deleted ones), updating member roles,
and removing members (soft delete).
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.member import MemberAdd, MemberUpdate, MemberOut
from app.services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["Members"])


@router.get("/{project_id}/members", response_model=List[MemberOut])
def get_project_members(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all active members of a project.
    
    Only returns members with is_deleted=False.
    Includes user details (name, email, role, joined date).
    
    Args:
        project_id: The ID of the project
        current_user: The authenticated user (must be a project member)
        db: Database session
    
    Returns:
        List of member objects with user details
    
    Raises:
        HTTPException 403: User is not a project member
        HTTPException 404: Project not found
    """
    return ProjectService.get_project_members(db, project_id, current_user.id)


@router.post("/{project_id}/members", status_code=status.HTTP_201_CREATED)
def add_project_member(
    project_id: int,
    member_data: MemberAdd,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Add a new member to a project or reactivate a soft-deleted member.
    
    Only Admins and Owners can add members.
    If the user was previously removed (soft delete), they will be reactivated.
    
    Args:
        project_id: The ID of the project
        member_data: User ID and role for the new member
        current_user: The authenticated user (must be Admin or Owner)
        db: Database session
    
    Returns:
        Success message with user_id and role
    
    Raises:
        HTTPException 403: User lacks permission
        HTTPException 400: User is already a member
        HTTPException 404: User or project not found
    """
    return ProjectService.add_project_member(
        db, project_id, current_user.id, member_data.user_id, member_data.role
    )


@router.put("/{project_id}/members/{user_id}")
def update_member_role(
    project_id: int,
    user_id: int,
    role_data: MemberUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update a member's role in a project.
    
    Only Admins and Owners can update roles.
    Owner role cannot be changed.
    Only Owner can change Admin role.
    
    Args:
        project_id: The ID of the project
        user_id: The ID of the member to update
        role_data: New role data
        current_user: The authenticated user (must be Admin or Owner)
        db: Database session
    
    Returns:
        Success message with user_id and new_role
    
    Raises:
        HTTPException 403: User lacks permission
        HTTPException 400: Cannot change Owner role
        HTTPException 404: Member not found
    """
    return ProjectService.update_member_role(
        db, project_id, current_user.id, user_id, role_data.role
    )


@router.delete("/{project_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_project_member(
    project_id: int,
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Remove a member from a project (soft delete).
    
    Only Admins and Owners can remove members.
    Owner cannot be removed.
    The member can be reactivated later via the add endpoint.
    
    Args:
        project_id: The ID of the project
        user_id: The ID of the member to remove
        current_user: The authenticated user (must be Admin or Owner)
        db: Database session
    
    Returns:
        None (204 No Content)
    
    Raises:
        HTTPException 403: User lacks permission
        HTTPException 400: Cannot remove Owner
        HTTPException 404: Member not found
    """
    ProjectService.remove_project_member(db, project_id, current_user.id, user_id)
    return None