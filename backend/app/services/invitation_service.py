"""
Invitation service for managing project invitations.
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
        """
        logger.info("=" * 60)
        logger.info(f"📨 [INVITE] Starting invitation creation for {inv_data.email}")
        logger.info(f"📨 [INVITE] Project ID: {inv_data.project_id}")
        logger.info(f"📨 [INVITE] Role: {inv_data.role}")
        logger.info(f"📨 [INVITE] Inviter ID: {inviter_id}")

        try:
            # Verify project exists
            logger.info("📨 [INVITE] Step 1: Verifying project...")
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

            # Verify inviter has permission
            logger.info("📨 [INVITE] Step 2: Verifying inviter permissions...")
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
            logger.info("📨 [INVITE] Step 3: Checking if user is already a member...")
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
            logger.info("📨 [INVITE] Step 4: Checking for pending invitations...")
            pending_inv = db.query(Invitation).filter(
                Invitation.email == inv_data.email,
                Invitation.project_id == inv_data.project_id,
                Invitation.status == "Pending"
            ).first()
            if pending_inv:
                logger.warning(f"⚠️ Pending invitation already exists for {inv_data.email}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="An invitation is already pending for this email"
                )
            logger.info("✅ No pending invitations found")

            # Generate unique token and expiration
            logger.info("📨 [INVITE] Step 5: Generating token...")
            token = str(uuid.uuid4())
            expires_at = datetime.now(timezone.utc) + timedelta(days=7)
            logger.info(f"✅ Token generated: {token}")
            logger.info(f"✅ Expires at: {expires_at}")

            # Create invitation
            logger.info("📨 [INVITE] Step 6: Creating invitation record...")
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

            # Get inviter name
            user = db.query(User).filter(User.id == inviter_id).first()
            inviter_name = user.name if user else "Someone"

            # Send invitation email
            logger.info("📨 [INVITE] Step 7: Sending invitation email...")
            email_result = EmailService.send_invitation_email(
                to_email=inv_data.email,
                token=new_invitation.token,
                project_name=project.name,
                inviter_name=inviter_name
            )

            if email_result:
                logger.info("📨 [INVITE] ✅ Email sent successfully!")
            else:
                logger.warning("📨 [INVITE] ⚠️ Email may not have been delivered")

            logger.info("=" * 60)
            logger.info(f"📨 [INVITE] ✅ Invitation process completed for {inv_data.email}")
            logger.info("=" * 60)

            return new_invitation

        except HTTPException:
            raise
        except Exception as e:
            logger.error("=" * 60)
            logger.error(f"❌ [INVITE] Unexpected error: {e}")
            logger.error(f"❌ [INVITE] Error type: {type(e).__name__}")
            logger.error("=" * 60)
            raise