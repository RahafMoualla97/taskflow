"""
Tests for timesheet endpoints.

Covers creating, retrieving, and deleting timesheet entries,
as well as weekly summary generation.
"""
from fastapi import status
from datetime import date, timedelta
from app.models.timesheet import Timesheet


def test_create_timesheet(client, db_session, auth_headers, test_user, test_task):
    """Test creating a timesheet entry."""
    today = date.today()
    response = client.post(
        "/api/v1/timesheets/",
        json={
            "task_id": test_task.id,
            "date": today.isoformat(),
            "hours": 2.5,
            "description": "Worked on task"
        },
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["task_id"] == test_task.id
    assert data["user_id"] == test_user.id
    assert data["hours"] == 2.5
    assert data["description"] == "Worked on task"


def test_get_task_timesheets(client, db_session, auth_headers, test_user, test_task):
    """Test retrieving timesheets for a task."""
    response = client.get(
        f"/api/v1/timesheets/task/{test_task.id}",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)


def test_get_my_timesheets(client, db_session, auth_headers, test_user):
    """Test retrieving the current user's timesheets."""
    response = client.get(
        "/api/v1/timesheets/my",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)


def test_get_weekly_summary(client, db_session, auth_headers, test_user):
    """Test retrieving weekly summary of hours."""
    response = client.get(
        "/api/v1/timesheets/weekly-summary",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "week_start" in data
    assert "week_end" in data
    assert "total_hours" in data
    assert "daily" in data


def test_delete_timesheet(client, db_session, auth_headers, test_user, test_task):
    """Test deleting a timesheet entry."""
    today = date.today()
    timesheet = Timesheet(
        task_id=test_task.id,
        user_id=test_user.id,
        date=today,
        hours=1.5,
        description="Test entry"
    )
    db_session.add(timesheet)
    db_session.commit()
    db_session.refresh(timesheet)
    
    response = client.delete(
        f"/api/v1/timesheets/{timesheet.id}",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    deleted = db_session.query(Timesheet).filter(Timesheet.id == timesheet.id).first()
    assert deleted is None