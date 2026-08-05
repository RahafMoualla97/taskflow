"""
Task management API endpoints.

This module handles task CRUD operations including:
- Creating, updating, deleting tasks
- Getting tasks by project with filtering
- Advanced search with multiple filters
- Managing task collaborators and watchers
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.models.task import Task
from app.models.member import ProjectMember
from app.schemas.task import TaskCreate, TaskUpdate, TaskStatusUpdate, TaskOut
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["Tasks"])


# ========== Core CRUD Operations ==========

@router.post("/", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new task.

    The creator becomes the task reporter.
    An assignee can be optionally specified.

    Args:
        task_data: Task creation data
        current_user: Authenticated user
        db: Database session

    Returns:
        The newly created Task object

    Raises:
        HTTPException 404: Project not found
        HTTPException 403: User is not a project member
        HTTPException 400: Assignee is not a project member
    """
    return TaskService.create_task(db, task_data, current_user.id)


@router.get("/project/{project_id}", response_model=List[TaskOut])
def get_project_tasks(
    project_id: int,
    status: Optional[str] = Query(None, description="Filter by status (ToDo, InProgress, Done)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all tasks for a specific project.

    Args:
        project_id: ID of the project
        status: Optional status filter
        current_user: Authenticated user (must be a project member)
        db: Database session

    Returns:
        List of Task objects

    Raises:
        HTTPException 403: User is not a project member
    """
    return TaskService.get_project_tasks(db, project_id, current_user.id, status)


@router.get("/search", response_model=List[TaskOut])
def search_tasks(
    q: Optional[str] = Query(None, description="Search in title or description"),
    status: Optional[str] = Query(None, description="Filter by task status"),
    priority: Optional[str] = Query(None, description="Filter by priority (Low/Medium/High)"),
    assignee_id: Optional[int] = Query(None, description="Filter by assignee user ID"),
    project_id: Optional[int] = Query(None, description="Filter by project ID"),
    due_from: Optional[str] = Query(None, description="Due date from (ISO format, YYYY-MM-DD)"),
    due_to: Optional[str] = Query(None, description="Due date to (ISO format, YYYY-MM-DD)"),
    sort_by: Optional[str] = Query("created_at", description="Field to sort by"),
    sort_order: Optional[str] = Query("desc", description="Sort order (asc or desc)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Advanced search for tasks with multiple filters.

    Only searches tasks in projects the user is a member of.

    Args:
        q: Search term for title/description
        status: Filter by status
        priority: Filter by priority
        assignee_id: Filter by assignee
        project_id: Filter by project
        due_from: Filter tasks with due date after this date
        due_to: Filter tasks with due date before this date
        sort_by: Field to sort by
        sort_order: Sort order (asc or desc)
        current_user: Authenticated user
        db: Database session

    Returns:
        List of Task objects matching the filters
    """
    member_projects = db.query(ProjectMember).filter(
        ProjectMember.user_id == current_user.id,
        ProjectMember.is_deleted == False
    ).all()
    project_ids = [mp.project_id for mp in member_projects]

    if not project_ids:
        return []

    query = db.query(Task).filter(
        Task.project_id.in_(project_ids),
        Task.is_deleted == False
    )

    if q:
        query = query.filter(
            or_(
                Task.title.ilike(f"%{q}%"),
                Task.description.ilike(f"%{q}%")
            )
        )

    if status:
        query = query.filter(Task.status == status)

    if priority:
        query = query.filter(Task.priority == priority)

    if assignee_id:
        query = query.filter(Task.assignee_id == assignee_id)

    if project_id:
        query = query.filter(Task.project_id == project_id)

    if due_from:
        query = query.filter(Task.due_date >= due_from)
    if due_to:
        query = query.filter(Task.due_date <= due_to)

    sort_field = getattr(Task, sort_by, Task.created_at)
    if sort_order == "asc":
        query = query.order_by(sort_field.asc())
    else:
        query = query.order_by(sort_field.desc())

    return query.all()


@router.get("/{task_id}", response_model=TaskOut)
def get_task(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific task by ID.

    Args:
        task_id: ID of the task
        current_user: Authenticated user (must be a project member)
        db: Database session

    Returns:
        Task object with enriched data (assignee_name, reporter_name, etc.)

    Raises:
        HTTPException 404: Task not found
        HTTPException 403: User is not a project member
    """
    return TaskService.get_task_by_id(db, task_id, current_user.id)


@router.put("/{task_id}", response_model=TaskOut)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing task.

    Only the assignee, Admin, or Owner can update a task.

    Args:
        task_id: ID of the task
        task_data: Updated task data
        current_user: Authenticated user
        db: Database session

    Returns:
        The updated Task object

    Raises:
        HTTPException 404: Task not found
        HTTPException 403: User lacks permission
        HTTPException 400: Assignee is not a project member
    """
    return TaskService.update_task(db, task_id, current_user.id, task_data)


@router.patch("/{task_id}/status", response_model=TaskOut)
def update_task_status(
    task_id: int,
    status_data: TaskStatusUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update the status of a task.

    Status transitions: ToDo -> InProgress -> Done
    Direct ToDo -> Done is not allowed.

    Args:
        task_id: ID of the task
        status_data: New status
        current_user: Authenticated user
        db: Database session

    Returns:
        The updated Task object

    Raises:
        HTTPException 404: Task not found
        HTTPException 400: Invalid status or transition
        HTTPException 403: User lacks permission
    """
    return TaskService.update_task_status(
        db, task_id, current_user.id, status_data.status
    )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Soft delete a task.

    Only the reporter, Admin, or Owner can delete a task.
    Associated notifications are also deleted.

    Args:
        task_id: ID of the task
        current_user: Authenticated user
        db: Database session

    Returns:
        None (204 No Content)

    Raises:
        HTTPException 404: Task not found
        HTTPException 403: User lacks permission
    """
    TaskService.delete_task(db, task_id, current_user.id)
    return None


# ========== Collaborator & Watcher Management ==========

@router.post("/{task_id}/collaborators")
def add_collaborator(
    task_id: int,
    email: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Add a collaborator to a task.

    Collaborators are users who work on the task but are not responsible for it.

    Args:
        task_id: ID of the task
        email: Email of the user to add
        current_user: Authenticated user (must be reporter, Admin, or Owner)
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException 404: Task or user not found
        HTTPException 403: User lacks permission
        HTTPException 400: User is already a collaborator
    """
    return TaskService.add_collaborator(db, task_id, current_user.id, email)


@router.delete("/{task_id}/collaborators/{user_id}")
def remove_collaborator(
    task_id: int,
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Remove a collaborator from a task.

    Args:
        task_id: ID of the task
        user_id: ID of the collaborator to remove
        current_user: Authenticated user (must be reporter, Admin, or Owner)
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException 404: Task or user not found
        HTTPException 403: User lacks permission
        HTTPException 400: User is not a collaborator
    """
    TaskService.remove_collaborator(db, task_id, current_user.id, user_id)
    return {"message": "Collaborator removed successfully"}


@router.post("/{task_id}/watchers")
def add_watcher(
    task_id: int,
    email: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Add a watcher to a task.

    Watchers follow task progress without responsibility.

    Args:
        task_id: ID of the task
        email: Email of the user to add
        current_user: Authenticated user (must be reporter, Admin, or Owner)
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException 404: Task or user not found
        HTTPException 403: User lacks permission
        HTTPException 400: User is already a watcher
    """
    return TaskService.add_watcher(db, task_id, current_user.id, email)


@router.delete("/{task_id}/watchers/{user_id}")
def remove_watcher(
    task_id: int,
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Remove a watcher from a task.

    Args:
        task_id: ID of the task
        user_id: ID of the watcher to remove
        current_user: Authenticated user (must be reporter, Admin, or Owner)
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException 404: Task or user not found
        HTTPException 403: User lacks permission
        HTTPException 400: User is not a watcher
    """
    TaskService.remove_watcher(db, task_id, current_user.id, user_id)
    return {"message": "Watcher removed successfully"}