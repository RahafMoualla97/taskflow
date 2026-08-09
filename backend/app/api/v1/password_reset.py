"""
Password Reset API endpoints.

Handles password reset requests, token verification, and password updates.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.password_reset import (
    PasswordResetRequest,
    PasswordResetVerify,
    PasswordResetResponse,
)
from app.services.password_reset_service import PasswordResetService

router = APIRouter(prefix="/password-reset", tags=["Password Reset"])


@router.post("/request", response_model=PasswordResetResponse)
def request_password_reset(
    data: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """
    Request a password reset email.

    Args:
        data: Email address
        db: Database session

    Returns:
        Success message
    """
    return PasswordResetService.request_reset(db, data.email)


@router.post("/verify")
def verify_reset_token(
    token: str,
    db: Session = Depends(get_db)
):
    """
    Verify a reset token.

    Args:
        token: Reset token
        db: Database session

    Returns:
        Validity status
    """
    return PasswordResetService.verify_token(db, token)


@router.post("/reset", response_model=PasswordResetResponse)
def reset_password(
    data: PasswordResetVerify,
    db: Session = Depends(get_db)
):
    """
    Reset password using a valid token.

    Args:
        data: Token and new password
        db: Database session

    Returns:
        Success message
    """
    return PasswordResetService.reset_password(db, data.token, data.new_password)


@router.get("/user")
def get_user_by_token(
    token: str,
    db: Session = Depends(get_db)
):
    """
    Get user info from a valid token.

    Args:
        token: Reset token
        db: Database session

    Returns:
        User info
    """
    return PasswordResetService.get_user_by_token(db, token)