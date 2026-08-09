"""
Invitation model for project and task invitations.

Manages email-based invitations to projects or tasks with unique
token generation for secure acceptance, expiration tracking,
and status management.
"""
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
import uuid

from app.models.base import BaseModel


class Invitation(BaseModel):
    """
    Invitation to join a project or task.

    Attributes:
        email: Email address of the invited user
        project_id: ID of the project being invited to
        task_id: Optional task ID for task-specific invitations
        token: Unique UUID token for secure acceptance
        status: Current status (Pending, Accepted, Expired)
        expires_at: Expiration timestamp (7 days from creation)
        inviter_id: ID of the user who sent the invitation
    """
    __tablename__ = "invitations"

    email = Column(
        String(255),
        nullable=False,
        index=True,
        comment="Email address of the invited user"
    )
    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        nullable=False,
        index=True,
        comment="ID of the project being invited to"
    )
    task_id = Column(
        Integer,
        ForeignKey("tasks.id"),
        nullable=True,
        comment="Optional task ID for task-specific invitations"
    )
    token = Column(
        String(100),
        unique=True,
        nullable=False,
        default=lambda: str(uuid.uuid4()),
        comment="Unique UUID token for secure acceptance"
    )
    status = Column(
        String(20),
        nullable=False,
        default="Pending",
        comment="Current status: Pending, Accepted, or Expired"
    )
    expires_at = Column(
        DateTime(timezone=True),
        nullable=False,
        comment="Expiration timestamp (7 days from creation)"
    )
    inviter_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
        comment="ID of the user who sent the invitation"
    )

    project = relationship("Project", back_populates="invitations")
    task = relationship("Task", back_populates="invitations")
    inviter = relationship("User", foreign_keys=[inviter_id])