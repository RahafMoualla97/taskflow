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
        logger.info("=" * 60)
        logger.info(f"📨 [INVITE] Creating invitation for {inv_data.email}")
        logger.info(f"📨 [INVITE] Project ID: {inv_data.project_id}")
        logger.info(f"📨 [INVITE] Role: {inv_data.role}")

        # Verify project exists
        project = db.query(Project).filter(
            Project.id == inv_data.project_id,
            Project.is_deleted == False
        ).first()
        if not project:
            logger.error(f"❌ Project {inv_data.project_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        logger.info(f"✅ Project found: {project.name}")

        # Verify inviter has permission (Owner or Admin)
        inviter = db.query(ProjectMember).filter(
            ProjectMember.project_id == inv_data.project_id,
            ProjectMember.user_id == inviter_id,
            ProjectMember.role.in_(["Owner", "Admin"]),
            ProjectMember.is_deleted == False
        ).first()
        if not inviter:
            logger.error(f"❌ User {inviter_id} is not Owner or Admin")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Owner or Admin can send invitations"
            )
        logger.info(f"✅ Inviter has permission: {inviter.role}")

        # Check if email is already an active member
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
                logger.warning(f"⚠️ User {inv_data.email} is already a member")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User is already a member of this project"
                )
        logger.info("✅ User is not a member")

        # Check for existing pending invitation
        pending_inv = db.query(Invitation).filter(
            Invitation.email == inv_data.email,
            Invitation.project_id == inv_data.project_id,
            Invitation.status == "Pending"
        ).first()
        if pending_inv:
            logger.warning(f"⚠️ Pending invitation exists for {inv_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An invitation is already pending for this email"
            )
        logger.info("✅ No pending invitations")

        # Generate unique token and expiration
        token = str(uuid.uuid4())
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        logger.info(f"✅ Token generated: {token}")

        # Create invitation
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
        logger.info(f"✅ Invitation created with ID: {new_invitation.id}")

        # Send invitation email
        user = db.query(User).filter(User.id == inviter_id).first()
        inviter_name = user.name if user else "Someone"

        logger.info(f"📧 [INVITE] Sending email to {inv_data.email}...")
        email_result = EmailService.send_invitation_email(
            to_email=inv_data.email,
            token=new_invitation.token,
            project_name=project.name,
            inviter_name=inviter_name
        )

        if email_result:
            logger.info(f"✅ Invitation email sent to {inv_data.email}")
        else:
            logger.error(f"❌ Failed to send invitation email to {inv_data.email}")

        logger.info("=" * 60)
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
        logger.info("=" * 60)
        logger.info(f"📨 [ACCEPT] Accepting invitation with token: {token}")
        logger.info(f"📨 [ACCEPT] User ID: {user_id}")

        # Find the invitation
        invitation = db.query(Invitation).filter(
            Invitation.token == token,
            Invitation.status == "Pending"
        ).first()

        if not invitation:
            logger.error("❌ Invitation not found or not pending")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid or expired invitation"
            )

        logger.info(f"✅ Invitation found: ID={invitation.id}, email={invitation.email}")

        # Check expiration
        if invitation.expires_at < datetime.now(timezone.utc):
            invitation.status = "Expired"
            db.commit()
            logger.error("❌ Invitation has expired")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invitation has expired"
            )

        # Get user
        user = db.query(User).filter(
            User.id == user_id,
            User.is_deleted == False
        ).first()

        if not user:
            logger.error(f"❌ User not found: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        logger.info(f"✅ User found: {user.id}, email: {user.email}")

        # Verify email matches
        if user.email.lower() != invitation.email.lower():
            logger.error(f"❌ Email mismatch: {user.email} vs {invitation.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email does not match invitation"
            )

        # Check for existing active membership
        existing_member = db.query(ProjectMember).filter(
            ProjectMember.project_id == invitation.project_id,
            ProjectMember.user_id == user_id,
            ProjectMember.is_deleted == False
        ).first()

        if existing_member:
            logger.info(f"ℹ️ User is already a member: {user_id}")
            invitation.status = "Accepted"
            db.commit()
            return {
                "message": "User is already a member",
                "project_id": invitation.project_id
            }

        # Check for soft-deleted membership and reactivate
        deleted_member = db.query(ProjectMember).filter(
            ProjectMember.project_id == invitation.project_id,
            ProjectMember.user_id == user_id,
            ProjectMember.is_deleted == True
        ).first()

        if deleted_member:
            deleted_member.is_deleted = False
            deleted_member.role = "Member"
            db.add(deleted_member)
            logger.info(f"✅ Reactivated member: user_id={user_id}")
        else:
            new_member = ProjectMember(
                project_id=invitation.project_id,
                user_id=user_id,
                role="Member"
            )
            db.add(new_member)
            logger.info(f"✅ Added new member: user_id={user_id}")

        # If invitation is for a specific task, assign it
        if invitation.task_id:
            task = db.query(Task).filter(
                Task.id == invitation.task_id,
                Task.is_deleted == False
            ).first()
            if task and task.assignee_id is None:
                task.assignee_id = user_id
                logger.info(f"✅ Assigned task {task.id} to user {user_id}")

        # Mark invitation as accepted
        invitation.status = "Accepted"
        db.commit()
        logger.info(f"✅ Invitation accepted successfully")

        logger.info("=" * 60)
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