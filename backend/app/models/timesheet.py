"""
Timesheet model for tracking work hours on tasks.

This model handles:
- Logging work hours for specific tasks
- User attribution for time entries
- Date-based tracking and description
"""
from sqlalchemy import Column, Integer, ForeignKey, Float, Text, Date
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Timesheet(BaseModel):
    """
    Time entry for work logged on a task.

    Attributes:
        task_id: ID of the task work was performed on
        user_id: ID of the user who logged the time
        date: Date the work was performed
        hours: Number of hours worked
        description: Optional description of the work done
    """
    __tablename__ = "timesheets"

    task_id = Column(
        Integer,
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID of the task work was performed on"
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID of the user who logged the time"
    )
    date = Column(
        Date,
        nullable=False,
        comment="Date the work was performed"
    )
    hours = Column(
        Float,
        nullable=False,
        default=0,
        comment="Number of hours worked"
    )
    description = Column(
        Text,
        nullable=True,
        comment="Optional description of the work done"
    )

    task = relationship("Task", back_populates="timesheets")
    user = relationship("User", back_populates="timesheets")