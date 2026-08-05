"""
ProjectMember Pydantic schemas.

This module defines the request/response schemas for:
- Adding members to projects
- Updating member roles
- Member responses with user details
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class MemberAdd(BaseModel):
    """
    Schema for adding a member to a project.

    Attributes:
        user_id: ID of the user to add
        role: Role to assign (Owner, Admin, Member, Viewer)
    """
    user_id: int = Field(..., description="ID of the user to add")
    role: str = Field("Member", description="Role: Owner, Admin, Member, or Viewer")


class MemberUpdate(BaseModel):
    """
    Schema for updating a member's role.

    Attributes:
        role: New role for the member
    """
    role: str = Field(..., description="New role: Owner, Admin, Member, or Viewer")


class MemberOut(BaseModel):
    """
    Schema for member response with user details.

    Attributes:
        user_id: ID of the user
        user_name: Name of the user
        user_email: Email of the user
        role: User's role in the project
        joined_at: Date when the user joined the project
    """
    user_id: int
    user_name: str
    user_email: str
    role: str
    joined_at: datetime

    class Config:
        from_attributes = True