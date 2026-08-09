"""
Task service layer - Core business logic for task management.

Handles task CRUD operations, task status transitions, comment management
with mentions, collaborator and watcher management, and dashboard task queries.
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional
from datetime import datetime, timezone

from app.models.task import Task
from app.models.project import Project
from app.models.member import ProjectMember
from app.models.user import User
from app.models.comment import Comment
from app.models.notification import Notification
from app.schemas.task import TaskCreate, TaskUpdate
from app.services.activity_service import ActivityService
from app.services.notification_service import NotificationService


class TaskService:
    """Service for task-related business logic."""

    @staticmethod
    def create_task(db: Session, task_data: TaskCreate, reporter_id: int) -> Task:
        """
        Create a new task.

        Args:
            db: Database session
            task_data: Task creation data
            reporter_id: ID of the user creating the task

        Returns:
            The newly created Task object

        Raises:
            HTTPException 404: Project not found
            HTTPException 403: User is not a project member
            HTTPException 400: Assignee is not a project member
        """
        project = db.query(Project).filter(
            Project.id == task_data.project_id,
            Project.is_deleted == False
        ).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )

        member = db.query(ProjectMember).filter(
            ProjectMember.project_id == task_data.project_id,
            ProjectMember.user_id == reporter_id,
            ProjectMember.is_deleted == False
        ).first()
        if not member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this project"
            )

        if task_data.assignee_id:
            assignee_member = db.query(ProjectMember).filter(
                ProjectMember.project_id == task_data.project_id,
                ProjectMember.user_id == task_data.assignee_id,
                ProjectMember.is_deleted == False
            ).first()
            if not assignee_member:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Assignee is not a member of this project"
                )

        new_task = Task(
            title=task_data.title,
            description=task_data.description,
            project_id=task_data.project_id,
            assignee_id=task_data.assignee_id,
            reporter_id=reporter_id,
            due_date=task_data.due_date,
            priority=task_data.priority,
            status="ToDo"
        )
        db.add(new_task)
        db.flush()

        ActivityService.log_activity(
            db=db,
            user_id=reporter_id,
            project_id=task_data.project_id,
            task_id=new_task.id,
            action=f"Created task '{new_task.title}'",
            details={
                "title": new_task.title,
                "description": new_task.description,
                "priority": new_task.priority,
                "due_date": str(new_task.due_date) if new_task.due_date else None,
                "assignee_id": new_task.assignee_id
            }
        )

        if task_data.assignee_id:
            NotificationService.create_notification(
                db=db,
                user_id=task_data.assignee_id,
                notif_type="TaskAssigned",
                title=f"New task assigned: {new_task.title}",
                content=f"Task '{new_task.title}' has been assigned to you in project {project.name}",
                task_id=new_task.id,
                project_id=task_data.project_id,
                action_url=f"/tasks/{new_task.id}"
            )

        db.commit()
        db.refresh(new_task)
        return new_task

    @staticmethod
    def get_project_tasks(
        db: Session,
        project_id: int,
        user_id: int,
        status: Optional[str] = None
    ) -> List[Task]:
        """
        Get all tasks for a specific project.

        Args:
            db: Database session
            project_id: ID of the project
            user_id: ID of the current user
            status: Optional status filter

        Returns:
            List of Task objects

        Raises:
            HTTPException 403: User is not a project member
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

        query = db.query(Task).filter(
            Task.project_id == project_id,
            Task.is_deleted == False
        )
        if status:
            query = query.filter(Task.status == status)

        return query.all()

    @staticmethod
    def get_task_by_id(db: Session, task_id: int, user_id: int) -> dict:
        """
        Get a specific task with enriched data.

        Args:
            db: Database session
            task_id: ID of the task
            user_id: ID of the current user

        Returns:
            Task dictionary with enriched data

        Raises:
            HTTPException 404: Task not found
            HTTPException 403: User is not a project member
        """
        task = db.query(Task).filter(
            Task.id == task_id,
            Task.is_deleted == False
        ).first()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        member = db.query(ProjectMember).filter(
            ProjectMember.project_id == task.project_id,
            ProjectMember.user_id == user_id,
            ProjectMember.is_deleted == False
        ).first()
        if not member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this project"
            )

        assignee_name = None
        if task.assignee_id:
            assignee = db.query(User).filter(
                User.id == task.assignee_id,
                User.is_deleted == False
            ).first()
            assignee_name = assignee.name if assignee else None

        reporter = db.query(User).filter(
            User.id == task.reporter_id,
            User.is_deleted == False
        ).first()
        reporter_name = reporter.name if reporter else None

        project = db.query(Project).filter(
            Project.id == task.project_id,
            Project.is_deleted == False
        ).first()
        project_name = project.name if project else None

        collaborators = [
            {"id": u.id, "name": u.name, "email": u.email}
            for u in task.collaborators
        ]
        watchers = [
            {"id": u.id, "name": u.name, "email": u.email}
            for u in task.watchers
        ]

        return {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "priority": task.priority,
            "project_id": task.project_id,
            "assignee_id": task.assignee_id,
            "reporter_id": task.reporter_id,
            "due_date": task.due_date,
            "estimated_hours": task.estimated_hours,
            "logged_hours": task.logged_hours,
            "created_at": task.created_at,
            "updated_at": task.updated_at,
            "assignee_name": assignee_name,
            "reporter_name": reporter_name,
            "project_name": project_name,
            "collaborators": collaborators,
            "watchers": watchers,
        }

    @staticmethod
    def update_task(db: Session, task_id: int, user_id: int, task_data: TaskUpdate) -> Task:
        """
        Update an existing task.

        Args:
            db: Database session
            task_id: ID of the task
            user_id: ID of the current user
            task_data: Updated task data

        Returns:
            The updated Task object

        Raises:
            HTTPException 404: Task not found
            HTTPException 403: User lacks permission
            HTTPException 400: Assignee is not a project member
        """
        task = db.query(Task).filter(
            Task.id == task_id,
            Task.is_deleted == False
        ).first()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        member = db.query(ProjectMember).filter(
            ProjectMember.project_id == task.project_id,
            ProjectMember.user_id == user_id,
            ProjectMember.is_deleted == False
        ).first()
        if not member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this project"
            )

        old_assignee = task.assignee_id
        old_data = {
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "due_date": str(task.due_date) if task.due_date else None,
            "assignee_id": task.assignee_id
        }

        admin_member = db.query(ProjectMember).filter(
            ProjectMember.project_id == task.project_id,
            ProjectMember.user_id == user_id,
            ProjectMember.role.in_(["Owner", "Admin"]),
            ProjectMember.is_deleted == False
        ).first()

        if not admin_member and task.assignee_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only assignee, Admin, or Owner can update this task"
            )

        if task_data.title is not None:
            task.title = task_data.title
        if task_data.description is not None:
            task.description = task_data.description
        if task_data.assignee_id is not None:
            assignee_member = db.query(ProjectMember).filter(
                ProjectMember.project_id == task.project_id,
                ProjectMember.user_id == task_data.assignee_id,
                ProjectMember.is_deleted == False
            ).first()
            if not assignee_member:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Assignee is not a member of this project"
                )
            task.assignee_id = task_data.assignee_id

            if old_assignee != task_data.assignee_id:
                assignee_user = db.query(User).filter(
                    User.id == task_data.assignee_id,
                    User.is_deleted == False
                ).first()
                if assignee_user:
                    NotificationService.create_notification(
                        db=db,
                        user_id=task_data.assignee_id,
                        notif_type="TaskAssigned",
                        title=f"Task assigned to you: {task.title}",
                        content=f"You have been assigned to task '{task.title}'",
                        task_id=task.id,
                        project_id=task.project_id,
                        action_url=f"/tasks/{task.id}"
                    )
        if task_data.due_date is not None:
            task.due_date = task_data.due_date
        if task_data.priority is not None:
            task.priority = task_data.priority
        if task_data.estimated_hours is not None:
            task.estimated_hours = task_data.estimated_hours

        new_data = {
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "due_date": str(task.due_date) if task.due_date else None,
            "assignee_id": task.assignee_id
        }

        ActivityService.log_activity(
            db=db,
            user_id=user_id,
            project_id=task.project_id,
            task_id=task.id,
            action=f"Updated task '{task.title}'",
            details={
                "old": old_data,
                "new": new_data
            }
        )

        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def update_task_status(
        db: Session,
        task_id: int,
        user_id: int,
        new_status: str
    ) -> Task:
        """
        Update the status of a task.

        Args:
            db: Database session
            task_id: ID of the task
            user_id: ID of the current user
            new_status: New status (ToDo, InProgress, Done)

        Returns:
            The updated Task object

        Raises:
            HTTPException 404: Task not found
            HTTPException 400: Invalid status or transition
            HTTPException 403: User lacks permission
        """
        task = db.query(Task).filter(
            Task.id == task_id,
            Task.is_deleted == False
        ).first()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        member = db.query(ProjectMember).filter(
            ProjectMember.project_id == task.project_id,
            ProjectMember.user_id == user_id,
            ProjectMember.is_deleted == False
        ).first()
        if not member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this project"
            )

        valid_statuses = ["ToDo", "InProgress", "Done"]
        if new_status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of {valid_statuses}"
            )

        if task.status == "ToDo" and new_status == "Done":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot move from ToDo to Done directly. Must go through InProgress"
            )

        admin_member = db.query(ProjectMember).filter(
            ProjectMember.project_id == task.project_id,
            ProjectMember.user_id == user_id,
            ProjectMember.role.in_(["Owner", "Admin"]),
            ProjectMember.is_deleted == False
        ).first()

        if not admin_member and task.assignee_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only assignee, Admin, or Owner can change task status"
            )

        old_status = task.status
        task.status = new_status

        ActivityService.log_activity(
            db=db,
            user_id=user_id,
            project_id=task.project_id,
            task_id=task.id,
            action=f"Changed status from '{old_status}' to '{new_status}'",
            details={
                "old_status": old_status,
                "new_status": new_status
            }
        )

        if task.assignee_id and task.assignee_id != user_id:
            NotificationService.create_notification(
                db=db,
                user_id=task.assignee_id,
                notif_type="StatusChanged",
                title=f"Task status changed: {task.title}",
                content=f"Task '{task.title}' status changed from {old_status} to {new_status}",
                task_id=task.id,
                project_id=task.project_id,
                action_url=f"/tasks/{task.id}"
            )

        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def delete_task(db: Session, task_id: int, user_id: int) -> None:
        """
        Soft delete a task.

        Args:
            db: Database session
            task_id: ID of the task
            user_id: ID of the current user

        Raises:
            HTTPException 403: User lacks permission
        """
        task = TaskService.get_task_by_id(db, task_id, user_id)

        member = db.query(ProjectMember).filter(
            ProjectMember.project_id == task['project_id'],
            ProjectMember.user_id == user_id,
            ProjectMember.role.in_(["Owner", "Admin"]),
            ProjectMember.is_deleted == False
        ).first()

        if not member and task['reporter_id'] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only reporter, Admin, or Owner can delete this task"
            )

        db.query(Notification).filter(Notification.task_id == task_id).delete()

        task_obj = db.query(Task).filter(Task.id == task_id).first()
        if task_obj:
            task_obj.is_deleted = True
            db.commit()

    @staticmethod
    def add_comment(
        db: Session,
        task_id: int,
        user_id: int,
        content: str,
        mentions: List[int] = []
    ) -> dict:
        """
        Add a comment to a task with support for mentions.

        Args:
            db: Database session
            task_id: ID of the task
            user_id: ID of the comment author
            content: Comment content
            mentions: List of mentioned user IDs

        Returns:
            The newly created comment object with author information

        Raises:
            HTTPException 404: Task not found
            HTTPException 403: User is not a project member
        """
        task = db.query(Task).filter(
            Task.id == task_id,
            Task.is_deleted == False
        ).first()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        member = db.query(ProjectMember).filter(
            ProjectMember.project_id == task.project_id,
            ProjectMember.user_id == user_id,
            ProjectMember.is_deleted == False
        ).first()
        if not member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this project"
            )

        new_comment = Comment(
            content=content,
            task_id=task_id,
            author_id=user_id,
            mentions=mentions
        )
        db.add(new_comment)
        db.flush()

        # Get author name
        author = db.query(User).filter(User.id == user_id).first()
        author_name = author.name if author else "Unknown"

        ActivityService.log_activity(
            db=db,
            user_id=user_id,
            project_id=task.project_id,
            task_id=task_id,
            action=f"Added comment on task '{task.title}'",
            details={
                "comment": content[:100] + ("..." if len(content) > 100 else ""),
                "task_title": task.title
            }
        )

        if mentions:
            for mentioned_user_id in mentions:
                if mentioned_user_id != user_id:
                    NotificationService.create_notification(
                        db=db,
                        user_id=mentioned_user_id,
                        notif_type="Mentioned",
                        title="Someone mentioned you in a comment",
                        content=f"You were mentioned in a comment on task '{task.title}'",
                        task_id=task_id,
                        project_id=task.project_id,
                        action_url=f"/tasks/{task_id}"
                    )

        if task.assignee_id and task.assignee_id != user_id:
            NotificationService.create_notification(
                db=db,
                user_id=task.assignee_id,
                notif_type="CommentAdded",
                title=f"New comment on task: {task.title}",
                content=f"{author_name} commented on task '{task.title}'",
                task_id=task_id,
                project_id=task.project_id,
                action_url=f"/tasks/{task_id}"
            )

        db.commit()
        db.refresh(new_comment)

        # Return comment with author_name
        return {
            "id": new_comment.id,
            "content": new_comment.content,
            "task_id": new_comment.task_id,
            "author_id": new_comment.author_id,
            "author_name": author_name,
            "mentions": new_comment.mentions,
            "created_at": new_comment.created_at,
            "updated_at": new_comment.updated_at,
        }

    @staticmethod
    def get_task_comments(db: Session, task_id: int, user_id: int) -> List[dict]:
        """
        Get all comments for a task with author information.

        Args:
            db: Database session
            task_id: ID of the task
            user_id: ID of the current user

        Returns:
            List of comment dictionaries

        Raises:
            HTTPException 404: Task not found
            HTTPException 403: User is not a project member
        """
        task = db.query(Task).filter(
            Task.id == task_id,
            Task.is_deleted == False
        ).first()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        member = db.query(ProjectMember).filter(
            ProjectMember.project_id == task.project_id,
            ProjectMember.user_id == user_id,
            ProjectMember.is_deleted == False
        ).first()
        if not member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this project"
            )

        comments = db.query(Comment).filter(
            Comment.task_id == task_id,
            Comment.is_deleted == False
        ).all()

        result = []
        for comment in comments:
            author = db.query(User).filter(
                User.id == comment.author_id,
                User.is_deleted == False
            ).first()
            result.append({
                "id": comment.id,
                "content": comment.content,
                "task_id": comment.task_id,
                "author_id": comment.author_id,
                "author_name": author.name if author else "Unknown",
                "mentions": comment.mentions,
                "created_at": comment.created_at,
                "updated_at": comment.updated_at,
            })

        return result

    @staticmethod
    def delete_comment(db: Session, comment_id: int, user_id: int) -> None:
        """
        Soft delete a comment.

        Args:
            db: Database session
            comment_id: ID of the comment
            user_id: ID of the current user

        Raises:
            HTTPException 404: Comment not found
            HTTPException 403: User lacks permission
        """
        comment = db.query(Comment).filter(
            Comment.id == comment_id,
            Comment.is_deleted == False
        ).first()
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )

        task = db.query(Task).filter(
            Task.id == comment.task_id,
            Task.is_deleted == False
        ).first()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        member = db.query(ProjectMember).filter(
            ProjectMember.project_id == task.project_id,
            ProjectMember.user_id == user_id,
            ProjectMember.role.in_(["Owner", "Admin"]),
            ProjectMember.is_deleted == False
        ).first()

        if not member and comment.author_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only author, Admin, or Owner can delete this comment"
            )

        comment.is_deleted = True
        db.commit()

    @staticmethod
    def add_collaborator(
        db: Session,
        task_id: int,
        current_user_id: int,
        email: str
    ) -> dict:
        """
        Add a collaborator to a task.

        Args:
            db: Database session
            task_id: ID of the task
            current_user_id: ID of the current user
            email: Email of the user to add

        Returns:
            Success message

        Raises:
            HTTPException 404: Task or user not found
            HTTPException 403: User lacks permission
            HTTPException 400: User is already a collaborator
        """
        task = db.query(Task).filter(
            Task.id == task_id,
            Task.is_deleted == False
        ).first()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        member = db.query(ProjectMember).filter(
            ProjectMember.project_id == task.project_id,
            ProjectMember.user_id == current_user_id,
            ProjectMember.is_deleted == False
        ).first()
        if not member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this project"
            )

        admin_member = db.query(ProjectMember).filter(
            ProjectMember.project_id == task.project_id,
            ProjectMember.user_id == current_user_id,
            ProjectMember.role.in_(["Owner", "Admin"]),
            ProjectMember.is_deleted == False
        ).first()

        if not admin_member and task.reporter_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only reporter, Admin, or Owner can add collaborators"
            )

        user = db.query(User).filter(
            User.email == email,
            User.is_deleted == False
        ).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if user in task.collaborators:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a collaborator"
            )

        task.collaborators.append(user)
        db.commit()

        NotificationService.create_notification(
            db=db,
            user_id=user.id,
            notif_type="CollaboratorAdded",
            title="Added as collaborator to task",
            content=f"You have been added as a collaborator to task '{task.title}'",
            task_id=task.id,
            project_id=task.project_id,
            action_url=f"/tasks/{task.id}"
        )

        return {"message": f"Collaborator {email} added successfully"}

    @staticmethod
    def remove_collaborator(
        db: Session,
        task_id: int,
        current_user_id: int,
        user_id: int
    ) -> dict:
        """
        Remove a collaborator from a task.

        Args:
            db: Database session
            task_id: ID of the task
            current_user_id: ID of the current user
            user_id: ID of the collaborator to remove

        Returns:
            Success message

        Raises:
            HTTPException 404: Task or user not found
            HTTPException 403: User lacks permission
            HTTPException 400: User is not a collaborator
        """
        task = db.query(Task).filter(
            Task.id == task_id,
            Task.is_deleted == False
        ).first()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        member = db.query(ProjectMember).filter(
            ProjectMember.project_id == task.project_id,
            ProjectMember.user_id == current_user_id,
            ProjectMember.is_deleted == False
        ).first()
        if not member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this project"
            )

        admin_member = db.query(ProjectMember).filter(
            ProjectMember.project_id == task.project_id,
            ProjectMember.user_id == current_user_id,
            ProjectMember.role.in_(["Owner", "Admin"]),
            ProjectMember.is_deleted == False
        ).first()

        if not admin_member and task.reporter_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only reporter, Admin, or Owner can remove collaborators"
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

        if user not in task.collaborators:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not a collaborator"
            )

        task.collaborators.remove(user)
        db.commit()
        return {"message": "Collaborator removed successfully"}

    @staticmethod
    def add_watcher(
        db: Session,
        task_id: int,
        current_user_id: int,
        email: str
    ) -> dict:
        """
        Add a watcher to a task.

        Args:
            db: Database session
            task_id: ID of the task
            current_user_id: ID of the current user
            email: Email of the user to add

        Returns:
            Success message

        Raises:
            HTTPException 404: Task or user not found
            HTTPException 403: User lacks permission
            HTTPException 400: User is already a watcher
        """
        task = db.query(Task).filter(
            Task.id == task_id,
            Task.is_deleted == False
        ).first()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        member = db.query(ProjectMember).filter(
            ProjectMember.project_id == task.project_id,
            ProjectMember.user_id == current_user_id,
            ProjectMember.is_deleted == False
        ).first()
        if not member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this project"
            )

        admin_member = db.query(ProjectMember).filter(
            ProjectMember.project_id == task.project_id,
            ProjectMember.user_id == current_user_id,
            ProjectMember.role.in_(["Owner", "Admin"]),
            ProjectMember.is_deleted == False
        ).first()

        if not admin_member and task.reporter_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only reporter, Admin, or Owner can add watchers"
            )

        user = db.query(User).filter(
            User.email == email,
            User.is_deleted == False
        ).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if user in task.watchers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a watcher"
            )

        task.watchers.append(user)
        db.commit()

        NotificationService.create_notification(
            db=db,
            user_id=user.id,
            notif_type="WatcherAdded",
            title="Added as watcher to task",
            content=f"You have been added as a watcher to task '{task.title}'",
            task_id=task.id,
            project_id=task.project_id,
            action_url=f"/tasks/{task.id}"
        )

        return {"message": f"Watcher {email} added successfully"}

    @staticmethod
    def remove_watcher(
        db: Session,
        task_id: int,
        current_user_id: int,
        user_id: int
    ) -> dict:
        """
        Remove a watcher from a task.

        Args:
            db: Database session
            task_id: ID of the task
            current_user_id: ID of the current user
            user_id: ID of the watcher to remove

        Returns:
            Success message

        Raises:
            HTTPException 404: Task or user not found
            HTTPException 403: User lacks permission
            HTTPException 400: User is not a watcher
        """
        task = db.query(Task).filter(
            Task.id == task_id,
            Task.is_deleted == False
        ).first()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        member = db.query(ProjectMember).filter(
            ProjectMember.project_id == task.project_id,
            ProjectMember.user_id == current_user_id,
            ProjectMember.is_deleted == False
        ).first()
        if not member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this project"
            )

        admin_member = db.query(ProjectMember).filter(
            ProjectMember.project_id == task.project_id,
            ProjectMember.user_id == current_user_id,
            ProjectMember.role.in_(["Owner", "Admin"]),
            ProjectMember.is_deleted == False
        ).first()

        if not admin_member and task.reporter_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only reporter, Admin, or Owner can remove watchers"
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

        if user not in task.watchers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not a watcher"
            )

        task.watchers.remove(user)
        db.commit()
        return {"message": "Watcher removed successfully"}

    @staticmethod
    def get_recent_tasks(db: Session, user_id: int, limit: int = 5) -> List[Task]:
        """
        Get the most recent tasks for a user.

        Args:
            db: Database session
            user_id: ID of the user
            limit: Maximum number of tasks to return

        Returns:
            List of recent Task objects
        """
        member_projects = db.query(ProjectMember).filter(
            ProjectMember.user_id == user_id,
            ProjectMember.is_deleted == False
        ).all()
        project_ids = [mp.project_id for mp in member_projects]

        if not project_ids:
            return []

        return db.query(Task).filter(
            Task.project_id.in_(project_ids),
            Task.is_deleted == False
        ).order_by(
            Task.created_at.desc()
        ).limit(limit).all()

    @staticmethod
    def get_overdue_tasks(db: Session, user_id: int) -> List[Task]:
        """
        Get overdue tasks for a user.

        Args:
            db: Database session
            user_id: ID of the user

        Returns:
            List of overdue Task objects
        """
        member_projects = db.query(ProjectMember).filter(
            ProjectMember.user_id == user_id,
            ProjectMember.is_deleted == False
        ).all()
        project_ids = [mp.project_id for mp in member_projects]

        if not project_ids:
            return []

        now = datetime.now(timezone.utc)
        return db.query(Task).filter(
            Task.project_id.in_(project_ids),
            Task.due_date.isnot(None),
            Task.due_date < now,
            Task.status != "Done",
            Task.is_deleted == False
        ).order_by(
            Task.due_date.asc()
        ).all()

    @staticmethod
    def get_my_tasks(db: Session, user_id: int) -> List[Task]:
        """
        Get tasks assigned to the current user.

        Args:
            db: Database session
            user_id: ID of the user

        Returns:
            List of Task objects assigned to the user
        """
        return db.query(Task).filter(
            Task.assignee_id == user_id,
            Task.is_deleted == False,
            Task.status != "Done"
        ).order_by(
            Task.created_at.desc()
        ).all()