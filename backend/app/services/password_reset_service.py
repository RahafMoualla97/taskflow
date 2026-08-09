"""
Password Reset service for managing password recovery.
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timedelta, timezone
import uuid

from app.core.config import settings
from app.core.security import get_password_hash
from app.models.password_reset import PasswordReset
from app.models.user import User
from app.services.email_service import EmailService


class PasswordResetService:
    """Service for password reset operations."""

    @staticmethod
    def request_reset(db: Session, email: str) -> dict:
        """
        Send a password reset email to the user.

        Args:
            db: Database session
            email: User's email address

        Returns:
            Success message (always returns success for security)
        """
        user = db.query(User).filter(
            User.email == email,
            User.is_deleted == False
        ).first()
        
        # Always return success to prevent email enumeration attacks
        if not user:
            return {"message": "If an account exists, a reset link has been sent"}
        
        # Delete old unused reset tokens for this user
        db.query(PasswordReset).filter(
            PasswordReset.user_id == user.id,
            PasswordReset.used == False
        ).delete()
        
        # Create new reset token
        token = str(uuid.uuid4())
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        
        reset = PasswordReset(
            user_id=user.id,
            token=token,
            expires_at=expires_at,
            used=False
        )
        db.add(reset)
        db.commit()
        
        # Send reset email
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
        EmailService.send_password_reset_email(
            to_email=user.email,
            user_name=user.name,
            reset_url=reset_url
        )
        
        return {"message": "If an account exists, a reset link has been sent"}

    @staticmethod
    def verify_token(db: Session, token: str) -> dict:
        """
        Verify a reset token's validity.

        Args:
            db: Database session
            token: Reset token

        Returns:
            Dictionary with validity status

        Raises:
            HTTPException 400: Invalid or expired token
        """
        reset = db.query(PasswordReset).filter(
            PasswordReset.token == token,
            PasswordReset.used == False
        ).first()
        
        if not reset:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired token"
            )
        
        if reset.expires_at < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token has expired"
            )
        
        return {"valid": True, "user_id": reset.user_id}

    @staticmethod
    def reset_password(db: Session, token: str, new_password: str) -> dict:
        """
        Reset password using a valid token.

        Args:
            db: Database session
            token: Reset token
            new_password: New password

        Returns:
            Success message

        Raises:
            HTTPException 400: Invalid or expired token
            HTTPException 404: User not found
        """
        reset = db.query(PasswordReset).filter(
            PasswordReset.token == token,
            PasswordReset.used == False
        ).first()
        
        if not reset:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired token"
            )
        
        if reset.expires_at < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token has expired"
            )
        
        user = db.query(User).filter(User.id == reset.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update password
        user.hashed_password = get_password_hash(new_password)
        
        # Mark token as used
        reset.used = True
        db.commit()
        
        return {"message": "Password reset successfully"}

    @staticmethod
    def get_user_by_token(db: Session, token: str) -> dict:
        """
        Get user info from a valid token (for frontend).

        Args:
            db: Database session
            token: Reset token

        Returns:
            User info dictionary

        Raises:
            HTTPException 400: Invalid or expired token
        """
        reset = db.query(PasswordReset).filter(
            PasswordReset.token == token,
            PasswordReset.used == False
        ).first()
        
        if not reset:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired token"
            )
        
        if reset.expires_at < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token has expired"
            )
        
        user = db.query(User).filter(User.id == reset.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {
            "email": user.email,
            "name": user.name,
            "valid": True
        }