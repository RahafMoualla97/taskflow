"""
ProjectMember model for managing project membership and roles.

This model handles:
- User membership in projects
- Role-based access control (Owner, Admin, Member, Viewer)
- Soft deletion of memberships
"""
from sqlalchemy import Column, Integer, ForeignKey, String, UniqueConstraint, Boolean
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class ProjectMember(BaseModel):
    """
    Project membership with role-based permissions.

    Attributes:
        project_id: ID of the project
        user_id: ID of the user
        role: User's role in the project (Owner, Admin, Member, Viewer)
        is_deleted: Soft delete flag for reactivation support
    """
    __tablename__ = "project_members"

    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        nullable=False,
        index=True,
        comment="ID of the project"
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
        comment="ID of the user"
    )
    role = Column(
        String(20),
        nullable=False,
        default="Member",
        comment="User role: Owner, Admin, Member, or Viewer"
    )
    is_deleted = Column(
        Boolean,
        default=False,
        index=True,
        comment="Soft delete flag (allows reactivation)"
    )

    __table_args__ = (
        UniqueConstraint('project_id', 'user_id', name='unique_project_member'),
    )

    project = relationship("Project", back_populates="members")
    user = relationship("User", back_populates="project_members")