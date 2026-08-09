"""
Pytest configuration and fixtures for TaskFlow tests.

Provides test database setup, fixtures for users, projects, tasks,
and authentication headers for integration testing.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db
from app.core.security import get_password_hash, create_access_token
from app.models.user import User
from app.models.project import Project
from app.models.member import ProjectMember
from app.models.task import Task
from app.models.comment import Comment
from app.models.invitation import Invitation
from app.models.notification import Notification
from app.models.activity import Activity
from app.models.timesheet import Timesheet


# Test Database Configuration
# Use SQLite in-memory for fast, isolated tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# Fixtures

@pytest.fixture(scope="function")
def db_session():
    """
    Create a fresh database session for each test.

    Creates all tables, yields a session, and cleans up after the test.
    """
    Base.metadata.create_all(bind=engine)
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """
    Create a test client with database session override.

    Overrides the get_db dependency to use the test database session.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    user = User(
        email="test@example.com",
        name="Test User",
        hashed_password=get_password_hash("password123"),
        is_active=True,
        is_deleted=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_user2(db_session):
    """Create a second test user."""
    user = User(
        email="test2@example.com",
        name="Test User 2",
        hashed_password=get_password_hash("password123"),
        is_active=True,
        is_deleted=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_project(db_session, test_user):
    """Create a test project with owner."""
    project = Project(
        name="Test Project",
        key="TEST-001",
        description="Test project description",
        owner_id=test_user.id
    )
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    
    member = ProjectMember(
        project_id=project.id,
        user_id=test_user.id,
        role="Owner"
    )
    db_session.add(member)
    db_session.commit()
    
    return project


@pytest.fixture
def test_task(db_session, test_project, test_user):
    """Create a test task."""
    task = Task(
        title="Test Task",
        description="Test task description",
        project_id=test_project.id,
        assignee_id=test_user.id,
        reporter_id=test_user.id,
        status="ToDo",
        priority="Medium"
    )
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)
    return task


@pytest.fixture
def test_token(test_user):
    """Generate a JWT token for test user."""
    return create_access_token(data={"sub": test_user.email, "user_id": test_user.id})


@pytest.fixture
def auth_headers(test_token):
    """Authentication headers for API requests."""
    return {"Authorization": f"Bearer {test_token}"}


@pytest.fixture
def test_admin_user(db_session):
    """Create an admin user."""
    user = User(
        email="admin@example.com",
        name="Admin User",
        hashed_password=get_password_hash("admin123"),
        is_active=True,
        is_deleted=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_admin_project(db_session, test_admin_user):
    """Create a project with admin user."""
    project = Project(
        name="Admin Project",
        key="ADMIN-001",
        description="Admin project description",
        owner_id=test_admin_user.id
    )
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    
    member = ProjectMember(
        project_id=project.id,
        user_id=test_admin_user.id,
        role="Admin"
    )
    db_session.add(member)
    db_session.commit()
    
    return project


@pytest.fixture
def test_comment(db_session, test_task, test_user):
    """Create a test comment."""
    comment = Comment(
        content="Test comment content",
        task_id=test_task.id,
        author_id=test_user.id,
        is_deleted=False
    )
    db_session.add(comment)
    db_session.commit()
    db_session.refresh(comment)
    return comment