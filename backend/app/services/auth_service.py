"""
Authentication service for user management and JWT token generation.

Handles user registration with password hashing, user login with credential
verification, Google OAuth user creation/retrieval, and JWT token generation.
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import timedelta

from app.models.user import User
from app.schemas.auth import UserCreate
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token
)
from app.core.config import settings


class AuthService:
    """Service for authentication-related operations."""

    @staticmethod
    def register_user(db: Session, user_data: UserCreate) -> User:
        """
        Register a new user account.

        Args:
            db: Database session
            user_data: User registration data

        Returns:
            The newly created User object

        Raises:
            HTTPException 400: Email already registered
        """
        existing_user = db.query(User).filter(
            User.email == user_data.email,
            User.is_deleted == False
        ).first()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        hashed_password = get_password_hash(user_data.password)

        new_user = User(
            email=user_data.email,
            name=user_data.name,
            hashed_password=hashed_password,
            is_active=True
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user

    @staticmethod
    def login_user(db: Session, email: str, password: str) -> str:
        """
        Authenticate a user and generate an access token.

        Args:
            db: Database session
            email: User's email address
            password: User's password

        Returns:
            JWT access token string

        Raises:
            HTTPException 401: Invalid credentials
        """
        user = db.query(User).filter(
            User.email == email,
            User.is_deleted == False
        ).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        if not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        access_token = create_access_token(
            data={"sub": user.email, "user_id": user.id}
        )

        return access_token

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> User:
        """
        Retrieve a user by email address.

        Args:
            db: Database session
            email: User's email address

        Returns:
            User object

        Raises:
            HTTPException 404: User not found
        """
        user = db.query(User).filter(
            User.email == email,
            User.is_deleted == False
        ).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return user

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> User:
        """
        Retrieve a user by ID.

        Args:
            db: Database session
            user_id: User's ID

        Returns:
            User object

        Raises:
            HTTPException 404: User not found
        """
        user = db.query(User).filter(
            User.id == user_id,
            User.is_deleted == False
        ).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return user

    @staticmethod
    def create_or_get_google_user(
        db: Session,
        email: str,
        name: str,
        avatar_url: str
    ) -> User:
        """
        Create a new user from Google OAuth or retrieve existing user.

        Args:
            db: Database session
            email: User's email from Google
            name: User's name from Google
            avatar_url: User's avatar URL from Google

        Returns:
            User object (existing or newly created)
        """
        user = db.query(User).filter(
            User.email == email,
            User.is_deleted == False
        ).first()

        if not user:
            user = User(
                email=email,
                name=name,
                avatar_url=avatar_url,
                hashed_password=None,
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            if avatar_url and user.avatar_url != avatar_url:
                user.avatar_url = avatar_url
            if name and user.name != name:
                user.name = name
            db.commit()
            db.refresh(user)

        return user

    @staticmethod
    def generate_token_for_user(user: User) -> str:
        """
        Generate a JWT access token for a user.

        Args:
            user: User object

        Returns:
            JWT access token string
        """
        return create_access_token(
            data={"sub": user.email, "user_id": user.id}
        )