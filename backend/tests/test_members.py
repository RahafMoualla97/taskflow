"""
Tests for member management endpoints.

Covers listing members, adding members, updating roles,
and removing members with soft delete.
"""
from fastapi import status
from app.models.member import ProjectMember


def test_get_project_members(client, db_session, auth_headers, test_user, test_project):
    """Test retrieving all members of a project."""
    response = client.get(
        f"/api/v1/projects/{test_project.id}/members",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 1
    assert any(m["user_id"] == test_user.id for m in data)
    assert data[0]["role"] == "Owner"


def test_add_project_member(client, db_session, auth_headers, test_user, test_user2, test_project):
    """Test adding a new member to a project."""
    response = client.post(
        f"/api/v1/projects/{test_project.id}/members",
        json={
            "user_id": test_user2.id,
            "role": "Member"
        },
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "Member added successfully" in data["message"]
    assert data["user_id"] == test_user2.id


def test_add_member_already_member(client, db_session, auth_headers, test_user, test_project):
    """Test adding a user who is already a member."""
    response = client.post(
        f"/api/v1/projects/{test_project.id}/members",
        json={
            "user_id": test_user.id,
            "role": "Member"
        },
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already a member" in response.text


def test_update_member_role(client, db_session, auth_headers, test_user, test_user2, test_project):
    """Test updating a member's role."""
    member = ProjectMember(
        project_id=test_project.id,
        user_id=test_user2.id,
        role="Member"
    )
    db_session.add(member)
    db_session.commit()
    
    response = client.put(
        f"/api/v1/projects/{test_project.id}/members/{test_user2.id}",
        json={"role": "Admin"},
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["new_role"] == "Admin"
    assert data["user_id"] == test_user2.id


def test_remove_project_member(client, db_session, auth_headers, test_user, test_user2, test_project):
    """Test soft deleting a member from a project."""
    member = ProjectMember(
        project_id=test_project.id,
        user_id=test_user2.id,
        role="Member"
    )
    db_session.add(member)
    db_session.commit()
    
    response = client.delete(
        f"/api/v1/projects/{test_project.id}/members/{test_user2.id}",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    deleted_member = db_session.query(ProjectMember).filter(
        ProjectMember.project_id == test_project.id,
        ProjectMember.user_id == test_user2.id
    ).first()
    assert deleted_member.is_deleted == True


def test_remove_owner_fails(client, db_session, auth_headers, test_user, test_project):
    """Test that removing the project owner is not allowed."""
    response = client.delete(
        f"/api/v1/projects/{test_project.id}/members/{test_user.id}",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Cannot remove Owner" in response.text