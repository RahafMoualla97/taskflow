"""
Tests for dashboard endpoints.

Covers statistics, recent tasks, overdue tasks,
and advanced analytics.
"""
from fastapi import status


def test_get_dashboard_stats(client, db_session, auth_headers, test_user, test_project, test_task):
    """Test retrieving dashboard statistics."""
    response = client.get(
        "/api/v1/dashboard/stats",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "total_projects" in data
    assert "total_tasks" in data
    assert "completed_tasks" in data
    assert "overdue_tasks" in data
    assert "my_tasks" in data
    assert data["total_projects"] >= 1
    assert data["total_tasks"] >= 1


def test_get_recent_tasks(client, db_session, auth_headers, test_user, test_project, test_task):
    """Test retrieving recent tasks."""
    response = client.get(
        "/api/v1/dashboard/tasks/recent?limit=5",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 1
    assert any(t["id"] == test_task.id for t in data)


def test_get_overdue_tasks(client, db_session, auth_headers, test_user):
    """Test retrieving overdue tasks (should be empty initially)."""
    response = client.get(
        "/api/v1/dashboard/tasks/overdue",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)


def test_get_my_tasks(client, db_session, auth_headers, test_user, test_task):
    """Test retrieving tasks assigned to the current user."""
    response = client.get(
        "/api/v1/dashboard/tasks/my",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 1
    assert all(t["assignee_id"] == test_user.id for t in data)


def test_get_advanced_stats(client, db_session, auth_headers, test_user, test_project, test_task):
    """Test retrieving advanced dashboard statistics."""
    response = client.get(
        "/api/v1/dashboard/advanced-stats",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "tasks_by_status" in data
    assert "tasks_by_priority" in data
    assert "tasks_by_project" in data
    assert "weekly_activity" in data
    assert "total_tasks" in data
    assert "completion_rate" in data
    assert "overdue_count" in data