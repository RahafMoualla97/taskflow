"""
Tests for project endpoints.
"""
from fastapi import status
from app.models.project import Project
from app.models.member import ProjectMember


def test_create_project(client, db_session, auth_headers, test_user):
    """Test creating a new project."""
    response = client.post(
        "/api/v1/projects/",
        json={
            "name": "New Project",
            "description": "New project description"
        },
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "New Project"
    assert data["description"] == "New project description"
    assert data["owner_id"] == test_user.id
    assert "key" in data
    assert data["key"].startswith("PROJ-")


def test_get_projects(client, db_session, auth_headers, test_user, test_project):
    """Test getting user's projects."""
    response = client.get(
        "/api/v1/projects/",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 1
    assert any(p["id"] == test_project.id for p in data)


def test_get_project_by_id(client, db_session, auth_headers, test_user, test_project):
    """Test getting a specific project by ID."""
    response = client.get(
        f"/api/v1/projects/{test_project.id}",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_project.id
    assert data["name"] == test_project.name
    assert data["description"] == test_project.description


def test_get_project_not_member(client, db_session, auth_headers, test_user2, test_project):
    """Test getting a project user is not a member of."""
    # Create token for test_user2
    from app.core.security import create_access_token
    token2 = create_access_token(data={"sub": test_user2.email, "user_id": test_user2.id})
    
    response = client.get(
        f"/api/v1/projects/{test_project.id}",
        headers={"Authorization": f"Bearer {token2}"}
    )
    
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_update_project(client, db_session, auth_headers, test_user, test_project):
    """Test updating a project."""
    response = client.put(
        f"/api/v1/projects/{test_project.id}",
        json={
            "name": "Updated Project Name",
            "description": "Updated description"
        },
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Updated Project Name"
    assert data["description"] == "Updated description"


def test_delete_project(client, db_session, auth_headers, test_user, test_project):
    """Test soft deleting a project."""
    response = client.delete(
        f"/api/v1/projects/{test_project.id}",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify project is soft deleted
    project = db_session.query(Project).filter(Project.id == test_project.id).first()
    assert project.is_deleted == True


def test_search_projects(client, db_session, auth_headers, test_user, test_project):
    """Test searching for projects."""
    response = client.get(
        f"/api/v1/projects/search?q=Test",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 1
    assert any("Test" in p["name"] or "Test" in p["description"] for p in data)