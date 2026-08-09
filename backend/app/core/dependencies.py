"""
Dependency injection utilities for authentication and authorization.

Provides:
- JWT token validation and user retrieval
- Active user verification
- Project membership and role authorization checks
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from typing import Optional

from app.core.database import get_db
from app.core.config import settings
from app.models.user import User
from app.models.member import ProjectMember


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# Authentication Dependencies

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Decode JWT token and retrieve the current authenticated user.

    Args:
        token: JWT access token from the request
        db: Database session

    Returns:
        User object for the authenticated user

    Raises:
        HTTPException 401: Invalid or expired token
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Verify that the current user account is active.

    Args:
        current_user: User object from get_current_user

    Returns:
        Active User object

    Raises:
        HTTPException 400: User account is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


# Authorization Dependencies

def check_project_member(
    project_id: int,
    user_id: int,
    db: Session
) -> ProjectMember:
    """
    Verify that a user is an active member of a project.

    Args:
        project_id: ID of the project
        user_id: ID of the user
        db: Database session

    Returns:
        ProjectMember object

    Raises:
        HTTPException 403: User is not a member
    """
    member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user_id,
        ProjectMember.is_deleted == False
    ).first()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this project"
        )
    return member


def check_project_admin(
    project_id: int,
    user_id: int,
    db: Session
) -> ProjectMember:
    """
    Verify that a user has Admin or Owner role in a project.

    Args:
        project_id: ID of the project
        user_id: ID of the user
        db: Database session

    Returns:
        ProjectMember object

    Raises:
        HTTPException 403: User lacks admin permissions
    """
    member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user_id,
        ProjectMember.role.in_(["Owner", "Admin"]),
        ProjectMember.is_deleted == False
    ).first()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have admin permissions for this project"
        )
    return member


def check_project_owner(
    project_id: int,
    user_id: int,
    db: Session
) -> ProjectMember:
    """
    Verify that a user is the Owner of a project.

    Args:
        project_id: ID of the project
        user_id: ID of the user
        db: Database session

    Returns:
        ProjectMember object

    Raises:
        HTTPException 403: User is not the project owner
    """
    member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user_id,
        ProjectMember.role == "Owner",
        ProjectMember.is_deleted == False
    ).first()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the project owner can perform this action"
        )
    return member