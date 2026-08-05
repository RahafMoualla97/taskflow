"""
Tests for authentication endpoints.
"""
from fastapi import status
from app.core.security import create_access_token, verify_password


def test_register_user(client, db_session):
    """Test user registration."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "name": "New User",
            "password": "password123"
        }
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["name"] == "New User"
    assert "id" in data
    assert "hashed_password" not in data  # Password should not be returned


def test_register_duplicate_email(client, db_session, test_user):
    """Test registration with already existing email."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": test_user.email,
            "name": "Another User",
            "password": "password123"
        }
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Email already registered" in response.text


def test_login_success(client, db_session, test_user):
    """Test successful login."""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.email,
            "password": "password123"
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_password(client, db_session, test_user):
    """Test login with invalid password."""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.email,
            "password": "wrongpassword"
        }
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Incorrect email or password" in response.text


def test_login_nonexistent_user(client, db_session):
    """Test login with non-existent user."""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "nonexistent@example.com",
            "password": "password123"
        }
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Incorrect email or password" in response.text


def test_get_current_user(client, db_session, auth_headers, test_user):
    """Test getting current user profile."""
    response = client.get(
        "/api/v1/auth/users/me",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == test_user.email
    assert data["name"] == test_user.name
    assert data["id"] == test_user.id


def test_get_current_user_unauthorized(client):
    """Test getting user profile without authentication."""
    response = client.get("/api/v1/auth/users/me")
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_update_user_profile(client, db_session, auth_headers, test_user):
    """Test updating user profile."""
    response = client.put(
        "/api/v1/auth/users/me",
        json={  
            "name": "Updated Name",
            "avatar_url": "https://example.com/avatar.jpg"
        },
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["avatar_url"] == "https://example.com/avatar.jpg"
    
    # Verify database was updated
    db_session.refresh(test_user)
    assert test_user.name == "Updated Name"
    assert test_user.avatar_url == "https://example.com/avatar.jpg"