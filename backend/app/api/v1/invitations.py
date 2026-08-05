"""
Invitation API endpoints.

This module handles project invitations including:
- Creating and sending invitations via email
- Accepting invitations
- Checking invitation validity
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.invitation import InvitationCreate, InvitationAccept, InvitationOut
from app.services.invitation_service import InvitationService

router = APIRouter(prefix="/invitations", tags=["Invitations"])


@router.post("/", response_model=InvitationOut, status_code=status.HTTP_201_CREATED)
def create_invitation(
    inv_data: InvitationCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create and send a project invitation.

    Only project Admins and Owners can send invitations.
    The invitation will be sent via email with a unique token.

    Args:
        inv_data: Invitation data (email, project_id, role)
        current_user: Authenticated user (must be Admin or Owner)
        db: Database session

    Returns:
        The created Invitation object

    Raises:
        HTTPException 403: User lacks permission
        HTTPException 400: Email is already a member or invitation pending
        HTTPException 404: Project not found
    """
    return InvitationService.create_invitation(db, inv_data, current_user.id)


@router.post("/accept")
def accept_invitation(
    token: str = Query(..., description="Invitation token from email"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Accept an invitation using the provided token.

    The user must be authenticated and their email must match
    the email the invitation was sent to.

    Args:
        token: Unique invitation token
        current_user: Authenticated user
        db: Database session

    Returns:
        Success message with project_id

    Raises:
        HTTPException 404: Invalid or expired invitation
        HTTPException 400: Email mismatch or invitation expired
        HTTPException 403: User lacks permission
    """
    return InvitationService.accept_invitation(db, token, current_user.id)


@router.get("/check")
def check_invitation(
    token: str = Query(..., description="Invitation token to validate"),
    db: Session = Depends(get_db)
):
    """
    Validate an invitation token without requiring authentication.

    This endpoint is used to check if an invitation is valid
    before the user logs in or creates an account.

    Args:
        token: Unique invitation token
        db: Database session

    Returns:
        Invitation details if valid (email, project_id, project_name, etc.)

    Raises:
        HTTPException 404: Invalid or expired invitation
    """
    invitation_data = InvitationService.get_invitation_by_token(db, token)

    if not invitation_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid or expired invitation"
        )

    return {
        "valid": True,
        "email": invitation_data.get("email"),
        "project_id": invitation_data.get("project_id"),
        "project_name": invitation_data.get("project_name"),
        "task_id": invitation_data.get("task_id"),
        "expires_at": invitation_data.get("expires_at"),
        "inviter_name": invitation_data.get("inviter_name", "Someone")
    }