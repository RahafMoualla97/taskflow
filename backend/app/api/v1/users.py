"""
User management API endpoints.
Handles user retrieval operations including listing all active users,
getting a user by ID, and getting a user by email.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.user import UserOut

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=List[UserOut])
def get_users(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all active users.
    
    Only returns users that are not deleted and are active.
    This endpoint is used for member management.
    
    Args:
        current_user: The authenticated user
        db: Database session
    
    Returns:
        List of active User objects
    """
    users = db.query(User).filter(
        User.is_deleted == False,
        User.is_active == True
    ).all()
    return users


@router.get("/{user_id}", response_model=UserOut)
def get_user_by_id(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific user by their ID.
    
    Args:
        user_id: The ID of the user to retrieve
        current_user: The authenticated user
        db: Database session
    
    Returns:
        User object
    
    Raises:
        HTTPException 404: User not found
    """
    user = db.query(User).filter(
        User.id == user_id,
        User.is_deleted == False
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


@router.get("/email/{email}", response_model=UserOut)
def get_user_by_email(
    email: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific user by their email address.
    
    Args:
        email: The email address of the user to retrieve
        current_user: The authenticated user
        db: Database session
    
    Returns:
        User object
    
    Raises:
        HTTPException 404: User not found
    """
    user = db.query(User).filter(
        User.email == email,
        User.is_deleted == False
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user