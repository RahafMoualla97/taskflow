"""
Invitation Pydantic schemas.

Defines request/response schemas for:
- Creating project/task invitations
- Accepting invitations
- Invitation status and details
"""
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class InvitationCreate(BaseModel):
    """
    Schema for creating a new invitation.

    Attributes:
        email: Email address of the invited user
        project_id: ID of the project to invite to
        task_id: Optional task ID for task-specific invitations
        role: Role to assign to the user (Member, Admin, Viewer)
    """
    email: EmailStr = Field(..., description="Email address of the invited user")
    project_id: int = Field(..., description="ID of the project to invite to")
    task_id: Optional[int] = Field(None, description="Optional task ID for task-specific invitation")
    role: str = Field("Member", description="Role to assign: Member, Admin, or Viewer")


class InvitationAccept(BaseModel):
    """
    Schema for accepting an invitation.

    Attributes:
        token: Unique invitation token
    """
    token: str = Field(..., description="Unique invitation token from email")


class InvitationOut(BaseModel):
    """
    Schema for invitation response.

    Attributes:
        id: Invitation ID
        email: Email address of the invited user
        project_id: ID of the project
        task_id: Optional task ID
        token: Unique invitation token
        status: Current status (Pending, Accepted, Expired)
        expires_at: Expiration timestamp
        created_at: Creation timestamp
    """
    id: int
    email: EmailStr
    project_id: int
    task_id: Optional[int] = None
    token: str
    status: str
    expires_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True