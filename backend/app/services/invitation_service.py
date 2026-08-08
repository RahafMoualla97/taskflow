"""
Invitation service for managing project invitations.

This service handles:
- Creating and sending project invitations via email
- Accepting invitations with token validation
- Checking invitation validity
- Reactivating soft-deleted members
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timedelta, timezone
import uuid
import logging
from typing import Optional

from app.core.config import settings
from app.models.invitation import Invitation
from app.models.project import Project
from app.models.member import ProjectMember
from app.models.user import User
from app.models.task import Task
from app.schemas.invitation import InvitationCreate
from app.services.email_service import EmailService

logger = logging.getLogger(__name__)


class InvitationService:
    """Service for invitation management operations."""

    @staticmethod
    def create_invitation(
        db: Session,
        inv_data: InvitationCreate,
        inviter_id: int
    ) -> Invitation:
        """
        Create a new invitation and send it via email.

        Args:
            db: Database session
            inv_data: Invitation data (email, project_id, role, task_id)
            inviter_id: ID of the user sending the invitation

        Returns:
            The newly created Invitation object

        Raises:
            HTTPException 404: Project not found
            HTTPException 403: User lacks permission (not Owner or Admin)
            HTTPException 400: Email already a member or pending invitation
        """
        project = db.query(Project).filter(
            Project.id == inv_data.project_id,
            Project.is_deleted == False
        ).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )

        inviter = db.query(ProjectMember).filter(
            ProjectMember.project_id == inv_data.project_id,
            ProjectMember.user_id == inviter_id,
            ProjectMember.role.in_(["Owner", "Admin"]),
            ProjectMember.is_deleted == False
        ).first()
        if not inviter:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Owner or Admin can send invitations"
            )

        existing_user = db.query(User).filter(
            User.email == inv_data.email,
            User.is_deleted == False
        ).first()
        if existing_user:
            existing_member = db.query(ProjectMember).filter(
                ProjectMember.project_id == inv_data.project_id,
                ProjectMember.user_id == existing_user.id,
                ProjectMember.is_deleted == False
            ).first()
            if existing_member:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User is already a member of this project"
                )

        pending_inv = db.query(Invitation).filter(
            Invitation.email == inv_data.email,
            Invitation.project_id == inv_data.project_id,
            Invitation.status == "Pending"
        ).first()
        if pending_inv:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An invitation is already pending for this email"
            )

        token = str(uuid.uuid4())
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)

        new_invitation = Invitation(
            email=inv_data.email,
            project_id=inv_data.project_id,
            task_id=inv_data.task_id,
            token=token,
            expires_at=expires_at,
            status="Pending",
            inviter_id=inviter_id
        )
        db.add(new_invitation)
        db.commit()
        db.refresh(new_invitation)

        user = db.query(User).filter(User.id == inviter_id).first()
        inviter_name = user.name if user else "Someone"

        EmailService.send_invitation_email(
            to_email=inv_data.email,
            token=new_invitation.token,
            project_name=project.name,
            inviter_name=inviter_name
        )

        return new_invitation

    @staticmethod
    def accept_invitation(
        db: Session,
        token: str,
        user_id: int
    ) -> dict:
        """
        Accept an invitation using the provided token.

        Args:
            db: Database session
            token: Unique invitation token
            user_id: ID of the user accepting the invitation

        Returns:
            Dictionary with success message and project_id

        Raises:
            HTTPException 404: Invalid or expired invitation
            HTTPException 400: Email mismatch or invitation expired
        """
        invitation = db.query(Invitation).filter(
            Invitation.token == token,
            Invitation.status == "Pending"
        ).first()

        if not invitation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid or expired invitation"
            )

        if invitation.expires_at < datetime.now(timezone.utc):
            invitation.status = "Expired"
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invitation has expired"
            )

        user = db.query(User).filter(
            User.id == user_id,
            User.is_deleted == False
        ).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if user.email.lower() != invitation.email.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email does not match invitation"
            )

        existing_member = db.query(ProjectMember).filter(
            ProjectMember.project_id == invitation.project_id,
            ProjectMember.user_id == user_id,
            ProjectMember.is_deleted == False
        ).first()

        if existing_member:
            invitation.status = "Accepted"
            db.commit()
            return {
                "message": "User is already a member",
                "project_id": invitation.project_id
            }

        deleted_member = db.query(ProjectMember).filter(
            ProjectMember.project_id == invitation.project_id,
            ProjectMember.user_id == user_id,
            ProjectMember.is_deleted == True
        ).first()

        if deleted_member:
            deleted_member.is_deleted = False
            deleted_member.role = "Member"
            db.add(deleted_member)
        else:
            new_member = ProjectMember(
                project_id=invitation.project_id,
                user_id=user_id,
                role="Member"
            )
            db.add(new_member)

        if invitation.task_id:
            task = db.query(Task).filter(
                Task.id == invitation.task_id,
                Task.is_deleted == False
            ).first()
            if task and task.assignee_id is None:
                task.assignee_id = user_id

        invitation.status = "Accepted"
        db.commit()

        return {
            "message": "Invitation accepted successfully",
            "project_id": invitation.project_id,
            "task_id": invitation.task_id
        }

    @staticmethod
    def get_invitation_by_token(
        db: Session,
        token: str
    ) -> Optional[dict]:
        """
        Get invitation details by token for validation.

        Args:
            db: Database session
            token: Unique invitation token

        Returns:
            Dictionary with invitation details, or None if not found
        """
        invitation = db.query(Invitation).filter(
            Invitation.token == token,
            Invitation.status == "Pending"
        ).first()

        if not invitation:
            return None

        inviter = db.query(User).filter(User.id == invitation.inviter_id).first()
        project = db.query(Project).filter(Project.id == invitation.project_id).first()

        return {
            "valid": True,
            "email": invitation.email,
            "project_id": invitation.project_id,
            "project_name": project.name if project else None,
            "task_id": invitation.task_id,
            "expires_at": invitation.expires_at,
            "inviter_name": inviter.name if inviter else "Someone"
        }