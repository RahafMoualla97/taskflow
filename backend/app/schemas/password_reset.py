"""
Password Reset Pydantic schemas.

Defines request/response schemas for password reset operations.
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime


class PasswordResetRequest(BaseModel):
    """
    Schema for requesting a password reset.
    
    Attributes:
        email: User's email address
    """
    email: EmailStr = Field(..., description="User's email address")


class PasswordResetVerify(BaseModel):
    """
    Schema for verifying a reset token.
    
    Attributes:
        token: Reset token from email
        new_password: New password (min 6 characters)
        confirm_password: Confirm new password
    """
    token: str = Field(..., description="Reset token from email")
    new_password: str = Field(..., min_length=6, description="New password (minimum 6 characters)")
    confirm_password: str = Field(..., min_length=6, description="Confirm new password")

    @validator('confirm_password')
    def passwords_match(cls, v: str, values: dict) -> str:
        """Validate that passwords match."""
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v


class PasswordResetResponse(BaseModel):
    """
    Schema for password reset response.
    
    Attributes:
        message: Success or info message
    """
    message: str
    user_id: Optional[int] = None