"""
Tests for comment endpoints.

Covers adding comments, retrieving task comments,
and soft deleting comments.
"""
from fastapi import status
from app.models.comment import Comment


def test_add_comment(client, db_session, auth_headers, test_user, test_task):
    """Test adding a comment to a task."""
    response = client.post(
        f"/api/v1/comments/task/{test_task.id}",
        json={
            "content": "This is a test comment",
            "mentions": []
        },
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["content"] == "This is a test comment"
    assert data["task_id"] == test_task.id
    assert data["author_id"] == test_user.id


def test_get_task_comments(client, db_session, auth_headers, test_user, test_task, test_comment):
    """Test retrieving all comments for a task."""
    response = client.get(
        f"/api/v1/comments/task/{test_task.id}",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 1
    assert any(c["id"] == test_comment.id for c in data)
    assert data[0]["author_name"] == test_user.name


def test_delete_comment(client, db_session, auth_headers, test_user, test_comment):
    """Test soft deleting a comment."""
    response = client.delete(
        f"/api/v1/comments/{test_comment.id}",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    comment = db_session.query(Comment).filter(Comment.id == test_comment.id).first()
    assert comment.is_deleted == True


def test_add_comment_with_mentions(client, db_session, auth_headers, test_user, test_user2, test_task):
    """Test adding a comment with user mentions."""
    response = client.post(
        f"/api/v1/comments/task/{test_task.id}",
        json={
            "content": "This comment mentions @user2",
            "mentions": [test_user2.id]
        },
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["content"] == "This comment mentions @user2"