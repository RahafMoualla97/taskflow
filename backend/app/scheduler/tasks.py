"""
Scheduled background tasks for the application.

This module contains tasks that run periodically:
- Deadline reminders: Sent every 12 hours to users with tasks due within 24 hours
"""
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.task import Task
from app.models.notification import Notification
from app.models.user import User


def send_deadline_reminders() -> None:
    """
    Send deadline reminders to assignees of tasks due within the next 24 hours.

    This function runs every 12 hours via the APScheduler.
    It finds tasks that:
    - Are not completed (status != "Done")
    - Have a due date set
    - Are due within the next 24 hours
    - Have not had a reminder sent yet

    For each qualifying task, a notification is created for the assignee
    and the task's reminder_sent flag is updated to prevent duplicate reminders.

    Returns:
        None
    """
    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        tomorrow = now + timedelta(hours=24)

        tasks = db.query(Task).filter(
            Task.status != "Done",
            Task.due_date.isnot(None),
            Task.due_date >= now,
            Task.due_date <= tomorrow,
            Task.reminder_sent == False
        ).all()

        for task in tasks:
            assignee = db.query(User).filter(User.id == task.assignee_id).first()
            if not assignee:
                continue

            notification = Notification(
                user_id=assignee.id,
                type="DeadlineReminder",
                title=f"Deadline Reminder: {task.title}",
                content=f"Task '{task.title}' is due within 24 hours!",
                task_id=task.id,
                project_id=task.project_id,
                action_url=f"/tasks/{task.id}"
            )
            db.add(notification)

            task.reminder_sent = True

        db.commit()

    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()