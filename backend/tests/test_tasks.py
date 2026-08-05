"""
Tests for task endpoints.
"""
from fastapi import status
from app.models.task import Task


def test_create_task(client, db_session, auth_headers, test_user, test_project):
    """Test creating a new task."""
    response = client.post(
        "/api/v1/tasks/",
        json={
            "title": "New Task",
            "description": "Task description",
            "project_id": test_project.id,
            "assignee_id": test_user.id,
            "priority": "High"
        },
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == "New Task"
    assert data["description"] == "Task description"
    assert data["project_id"] == test_project.id
    assert data["status"] == "ToDo"
    assert data["priority"] == "High"


def test_get_project_tasks(client, db_session, auth_headers, test_user, test_project, test_task):
    """Test getting tasks for a project."""
    response = client.get(
        f"/api/v1/tasks/project/{test_project.id}",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 1
    assert any(t["id"] == test_task.id for t in data)


def test_get_project_tasks_with_status_filter(client, db_session, auth_headers, test_user, test_project, test_task):
    """Test getting tasks filtered by status."""
    response = client.get(
        f"/api/v1/tasks/project/{test_project.id}?status=ToDo",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert all(t["status"] == "ToDo" for t in data)


def test_get_task_by_id(client, db_session, auth_headers, test_user, test_task):
    """Test getting a specific task by ID."""
    response = client.get(
        f"/api/v1/tasks/{test_task.id}",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_task.id
    assert data["title"] == test_task.title


def test_update_task(client, db_session, auth_headers, test_user, test_task):
    """Test updating a task."""
    response = client.put(
        f"/api/v1/tasks/{test_task.id}",
        json={
            "title": "Updated Task Title",
            "description": "Updated description"
        },
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == "Updated Task Title"
    assert data["description"] == "Updated description"


def test_update_task_status(client, db_session, auth_headers, test_user, test_task):
    """Test updating task status."""
    response = client.patch(
        f"/api/v1/tasks/{test_task.id}/status",
        json={"status": "InProgress"},
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "InProgress"


def test_update_task_status_invalid_transition(client, db_session, auth_headers, test_user, test_task):
    """Test invalid status transition (ToDo -> Done)."""
    # First set to ToDo (default)
    response = client.patch(
        f"/api/v1/tasks/{test_task.id}/status",
        json={"status": "Done"},
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Cannot move from ToDo to Done directly" in response.text


def test_delete_task(client, db_session, auth_headers, test_user, test_task):
    """Test soft deleting a task."""
    response = client.delete(
        f"/api/v1/tasks/{test_task.id}",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify task is soft deleted
    task = db_session.query(Task).filter(Task.id == test_task.id).first()
    assert task.is_deleted == True


def test_search_tasks(client, db_session, auth_headers, test_user, test_project, test_task):
    """Test searching for tasks."""
    response = client.get(
        f"/api/v1/tasks/search?q=Test&project_id={test_project.id}",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 1
    assert any("Test" in t["title"] or "Test" in t["description"] for t in data)