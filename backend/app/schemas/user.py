"""
User Pydantic schemas.

This module defines the request/response schemas for:
- User registration and login
- User profile responses
- User profile updates
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    """
    Schema for user registration.

    Attributes:
        email: User's email address
        name: User's full name
        password: Password (min 6 characters)
    """
    email: EmailStr = Field(..., description="User's email address")
    name: str = Field(..., min_length=2, max_length=100, description="User's full name")
    password: str = Field(..., min_length=6, description="Password (minimum 6 characters)")


class UserOut(BaseModel):
    """
    Schema for user response.

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


class UserUpdate(BaseModel):
    """
    Schema for updating user profile.

    Attributes:
        name: Updated name
        avatar_url: Updated avatar URL
    """
    name: Optional[str] = Field(None, min_length=2, max_length=100, description="Updated name")
    avatar_url: Optional[str] = Field(None, description="Updated avatar URL")