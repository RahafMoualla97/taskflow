"""
Authentication and user Pydantic schemas.

This module defines the request/response schemas for:
- User registration and login
- User profile responses
- JWT token responses
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
import re


class UserCreate(BaseModel):
    """
    Schema for user registration request.

    Attributes:
        email: Valid email address
        name: Full name (2-100 characters, letters, numbers, spaces, hyphens, and dots)
        password: Password (minimum 6 characters)
    """
    email: EmailStr = Field(..., description="User's email address")
    name: str = Field(..., min_length=2, max_length=100, description="Full name")
    password: str = Field(..., min_length=6, description="Password (minimum 6 characters)")

    @validator('password')
    def validate_password(cls, v: str) -> str:
        """
        Validate password strength.

        Args:
            v: Password string

        Returns:
            Validated password

        Raises:
            ValueError: If password is too weak
        """
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v

    @validator('name')
    def validate_name(cls, v: str) -> str:
        """
        Validate name format.

        Args:
            v: Name string

        Returns:
            Validated name

        Raises:
            ValueError: If name contains invalid characters
        """
        if not re.match(r'^[a-zA-Z0-9\s\-\.]+$', v):
            raise ValueError('Name can only contain letters, numbers, spaces, hyphens, and dots')
        return v


class UserOut(BaseModel):
    """
    Schema for user response (excludes sensitive data like password).

    Attributes:
        id: User ID
        email: User's email address
        name: User's full name
        avatar_url: Optional profile picture URL
        created_at: Account creation timestamp
    """
    id: int
    email: EmailStr
    name: str
    avatar_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """
    Schema for JWT token response.

    Attributes:
        access_token: JWT access token string
        token_type: Token type (default: "bearer")
    """
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type")


class TokenData(BaseModel):
    """
    Schema for decoded JWT token payload.

    Attributes:
        user_id: ID of the authenticated user
        sub: Subject (usually email)
    """
    user_id: Optional[int] = None
    sub: Optional[str] = None