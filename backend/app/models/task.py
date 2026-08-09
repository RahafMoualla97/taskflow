"""
Task model for managing work items within projects.

Handles task creation with title, description, and metadata,
status tracking (ToDo, InProgress, Done), assignment to users,
collaborators and watchers via many-to-many relationships,
time tracking, and soft deletion support.
"""
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Boolean, Table
from sqlalchemy.orm import relationship

from app.models.base import BaseModel
from app.core.database import Base


# Association Tables for Many-to-Many Relationships

task_collaborators = Table(
    'task_collaborators',
    Base.metadata,
    Column(
        'task_id',
        Integer,
        ForeignKey('tasks.id', ondelete='CASCADE'),
        primary_key=True,
        comment="ID of the task"
    ),
    Column(
        'user_id',
        Integer,
        ForeignKey('users.id', ondelete='CASCADE'),
        primary_key=True,
        comment="ID of the collaborator user"
    ),
    comment="Many-to-many relationship between tasks and collaborator users"
)

task_watchers = Table(
    'task_watchers',
    Base.metadata,
    Column(
        'task_id',
        Integer,
        ForeignKey('tasks.id', ondelete='CASCADE'),
        primary_key=True,
        comment="ID of the task"
    ),
    Column(
        'user_id',
        Integer,
        ForeignKey('users.id', ondelete='CASCADE'),
        primary_key=True,
        comment="ID of the watcher user"
    ),
    comment="Many-to-many relationship between tasks and watcher users"
)


class Task(BaseModel):
    """
    Task entity within a project.

    Attributes:
        title: Task title
        description: Optional detailed description
        status: Current status (ToDo, InProgress, Done)
        priority: Task priority (Low, Medium, High)
        project_id: ID of the parent project
        assignee_id: ID of the user assigned to the task
        reporter_id: ID of the user who created the task
        due_date: Optional due date
        estimated_hours: Estimated hours to complete
        logged_hours: Actual hours logged (sum of timesheets)
        reminder_sent: Flag for deadline reminders
        is_deleted: Soft delete flag
    """
    __tablename__ = "tasks"

    title = Column(
        String(255),
        nullable=False,
        comment="Task title"
    )
    description = Column(
        String(2000),
        nullable=True,
        comment="Optional detailed description"
    )
    status = Column(
        String(50),
        nullable=False,
        default="ToDo",
        index=True,
        comment="Current status: ToDo, InProgress, or Done"
    )
    priority = Column(
        String(20),
        nullable=False,
        default="Medium",
        comment="Task priority: Low, Medium, or High"
    )
    project_id = Column(
        Integer,
        ForeignKey("projects.id", ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="ID of the parent project"
    )
    assignee_id = Column(
        Integer,
        ForeignKey("users.id", ondelete='SET NULL'),
        nullable=True,
        index=True,
        comment="ID of the user assigned to the task"
    )
    reporter_id = Column(
        Integer,
        ForeignKey("users.id", ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="ID of the user who created the task"
    )
    due_date = Column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="Optional due date"
    )
    estimated_hours = Column(
        Integer,
        nullable=True,
        comment="Estimated hours to complete the task"
    )
    logged_hours = Column(
        Integer,
        default=0,
        comment="Actual hours logged (sum of timesheet entries)"
    )
    reminder_sent = Column(
        Boolean,
        default=False,
        comment="Flag for deadline reminder sent"
    )
    is_deleted = Column(
        Boolean,
        default=False,
        index=True,
        comment="Soft delete flag"
    )

    project = relationship("Project", back_populates="tasks")
    assignee = relationship(
        "User",
        foreign_keys=[assignee_id],
        back_populates="tasks_assigned"
    )
    reporter = relationship(
        "User",
        foreign_keys=[reporter_id],
        back_populates="tasks_reported"
    )

    collaborators = relationship(
        "User",
        secondary=task_collaborators,
        back_populates="collaborated_tasks",
        lazy="selectin"
    )
    watchers = relationship(
        "User",
        secondary=task_watchers,
        back_populates="watched_tasks",
        lazy="selectin"
    )

    comments = relationship(
        "Comment",
        back_populates="task",
        cascade="all, delete-orphan"
    )
    invitations = relationship("Invitation", back_populates="task")
    notifications = relationship("Notification", back_populates="task")
    activities = relationship("Activity", back_populates="task")
    timesheets = relationship(
        "Timesheet",
        back_populates="task",
        cascade="all, delete-orphan"
    )