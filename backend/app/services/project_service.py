"""
Project service for managing projects and memberships.

Handles project CRUD operations, member management (add, remove, update roles),
and membership reactivation (soft delete).
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional

from app.models.project import Project
from app.models.member import ProjectMember
from app.models.user import User
from app.models.notification import Notification
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:
    """Service for project and membership management."""

    @staticmethod
    def create_project(
        db: Session,
        project_data: ProjectCreate,
        owner_id: int
    ) -> Project:
        """
        Create a new project with the user as Owner.

        Args:
            db: Database session
            project_data: Project creation data
            owner_id: ID of the user creating the project

        Returns:
            The newly created Project object
        """
        last_project = db.query(Project).order_by(Project.id.desc()).first()
        next_id = (last_project.id + 1) if last_project else 1
        key = f"PROJ-{next_id}"

        new_project = Project(
            name=project_data.name,
            key=key,
            description=project_data.description,
            owner_id=owner_id
        )
        db.add(new_project)
        db.flush()

        member = ProjectMember(
            project_id=new_project.id,
            user_id=owner_id,
            role="Owner"
        )
        db.add(member)
        db.commit()
        db.refresh(new_project)

        return new_project

    @staticmethod
    def get_user_projects(db: Session, user_id: int) -> List[Project]:
        """
        Get all active projects where the user is a member.

        Args:
            db: Database session
            user_id: ID of the user

        Returns:
            List of Project objects
        """
        member_projects = db.query(ProjectMember).filter(
            ProjectMember.user_id == user_id,
            ProjectMember.is_deleted == False
        ).all()

        project_ids = [mp.project_id for mp in member_projects]

        if not project_ids:
            return []

        projects = db.query(Project).filter(
            Project.id.in_(project_ids),
            Project.is_deleted == False
        ).all()

        return projects

    @staticmethod
    def get_project_by_id(
        db: Session,
        project_id: int,
        user_id: int
    ) -> Project:
        """
        Get a specific project with membership verification.

        Args:
            db: Database session
            project_id: ID of the project
            user_id: ID of the user (for verification)

        Returns:
            Project object

        Raises:
            HTTPException 403: User is not a member
            HTTPException 404: Project not found
        """
        member = db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
            ProjectMember.is_deleted == False
        ).first()

        if not member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this project"
            )

        project = db.query(Project).filter(
            Project.id == project_id,
            Project.is_deleted == False
        ).first()

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )

        return project

    @staticmethod
    def update_project(
        db: Session,
        project_id: int,
        user_id: int,
        project_data: ProjectUpdate
    ) -> Project:
        """
        Update a project (Admin/Owner only).

        Args:
            db: Database session
            project_id: ID of the project
            user_id: ID of the current user
            project_data: Updated project data

        Returns:
            The updated Project object

        Raises:
            HTTPException 403: User lacks permission
            HTTPException 404: Project not found
        """
        project = ProjectService.get_project_by_id(db, project_id, user_id)

        member = db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
            ProjectMember.role.in_(["Owner", "Admin"]),
            ProjectMember.is_deleted == False
        ).first()

        if not member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Owner or Admin can update project"
            )

        if project_data.name is not None:
            project.name = project_data.name
        if project_data.description is not None:
            project.description = project_data.description

        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def delete_project(
        db: Session,
        project_id: int,
        user_id: int
    ) -> None:
        """
        Soft delete a project (Owner only).

        Args:
            db: Database session
            project_id: ID of the project
            user_id: ID of the current user

        Raises:
            HTTPException 403: User is not the owner
            HTTPException 404: Project not found
        """
        project = ProjectService.get_project_by_id(db, project_id, user_id)

        member = db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
            ProjectMember.role == "Owner"
        ).first()

        if not member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Owner can delete project"
            )

        db.query(Notification).filter(Notification.project_id == project_id).delete()

        project.is_deleted = True
        db.commit()

    @staticmethod
    def get_project_members(
        db: Session,
        project_id: int,
        user_id: int
    ) -> List[dict]:
        """
        Get all active members of a project.

        Args:
            db: Database session
            project_id: ID of the project
            user_id: ID of the current user (for verification)

        Returns:
            List of member dictionaries with user details
        """
        ProjectService.get_project_by_id(db, project_id, user_id)

        members = db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id,
            ProjectMember.is_deleted == False
        ).all()

        result = []
        for member in members:
            user = db.query(User).filter(
                User.id == member.user_id,
                User.is_deleted == False
            ).first()
            if user:
                result.append({
                    "user_id": user.id,
                    "user_name": user.name,
                    "user_email": user.email,
                    "role": member.role,
                    "joined_at": member.created_at
                })

        return result

    @staticmethod
    def add_project_member(
        db: Session,
        project_id: int,
        user_id: int,
        target_user_id: int,
        role: str
    ) -> dict:
        """
        Add a new member or reactivate a soft-deleted member.

        Args:
            db: Database session
            project_id: ID of the project
            user_id: ID of the current user (must be Admin/Owner)
            target_user_id: ID of the user to add
            role: Role to assign

        Returns:
            Success message with user_id and role

        Raises:
            HTTPException 403: User lacks permission
            HTTPException 400: User is already a member
            HTTPException 404: User not found
        """
        current_member = db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
            ProjectMember.role.in_(["Owner", "Admin"]),
            ProjectMember.is_deleted == False
        ).first()

        if not current_member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Owner or Admin can add members"
            )

        target_user = db.query(User).filter(
            User.id == target_user_id,
            User.is_deleted == False
        ).first()

        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        existing = db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == target_user_id,
            ProjectMember.is_deleted == False
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a member of this project"
            )

        deleted_member = db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == target_user_id,
            ProjectMember.is_deleted == True
        ).first()

        if deleted_member:
            deleted_member.is_deleted = False
            deleted_member.role = role
            db.commit()
            db.refresh(deleted_member)
            return {
                "message": "Member reactivated successfully",
                "user_id": target_user_id,
                "role": role
            }

        new_member = ProjectMember(
            project_id=project_id,
            user_id=target_user_id,
            role=role
        )
        db.add(new_member)
        db.commit()
        db.refresh(new_member)

        return {
            "message": "Member added successfully",
            "user_id": target_user_id,
            "role": role
        }

    @staticmethod
    def update_member_role(
        db: Session,
        project_id: int,
        user_id: int,
        target_user_id: int,
        new_role: str
    ) -> dict:
        """
        Update a member's role (Admin/Owner only).

        Args:
            db: Database session
            project_id: ID of the project
            user_id: ID of the current user
            target_user_id: ID of the member to update
            new_role: New role

        Returns:
            Success message with user_id and new_role

        Raises:
            HTTPException 403: User lacks permission
            HTTPException 400: Cannot change Owner role
            HTTPException 404: Member not found
        """
        current_member = db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
            ProjectMember.role.in_(["Owner", "Admin"]),
            ProjectMember.is_deleted == False
        ).first()

        if not current_member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Owner or Admin can update roles"
            )

        target_member = db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == target_user_id,
            ProjectMember.is_deleted == False
        ).first()

        if not target_member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member not found"
            )

        if target_member.role == "Owner":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot change Owner role"
            )

        if target_member.role == "Admin" and current_member.role != "Owner":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Owner can change Admin role"
            )

        target_member.role = new_role
        db.commit()
        db.refresh(target_member)

        return {
            "message": "Role updated successfully",
            "user_id": target_user_id,
            "new_role": new_role
        }

    @staticmethod
    def remove_project_member(
        db: Session,
        project_id: int,
        user_id: int,
        target_user_id: int
    ) -> dict:
        """
        Remove a member (soft delete).

        Args:
            db: Database session
            project_id: ID of the project
            user_id: ID of the current user
            target_user_id: ID of the member to remove

        Returns:
            Success message

        Raises:
            HTTPException 403: User lacks permission
            HTTPException 400: Cannot remove Owner
            HTTPException 404: Member not found
        """
        current_member = db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
            ProjectMember.role.in_(["Owner", "Admin"]),
            ProjectMember.is_deleted == False
        ).first()

        if not current_member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Owner or Admin can remove members"
            )

        target_member = db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == target_user_id,
            ProjectMember.is_deleted == False
        ).first()

        if not target_member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member not found"
            )

        if target_member.role == "Owner":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot remove Owner from project"
            )

        target_member.is_deleted = True
        db.commit()

        return {"message": "Member removed successfully"}