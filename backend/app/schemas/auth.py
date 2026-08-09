"""
Authentication Pydantic schemas.

Defines request/response schemas for:
- JWT token responses
- Token data
"""
from pydantic import BaseModel, Field
from typing import Optional


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