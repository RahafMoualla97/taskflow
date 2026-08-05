"""
Authentication API endpoints.

This module handles user registration, login (email/password and Google OAuth),
and user profile management.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from authlib.integrations.starlette_client import OAuth
from starlette.responses import RedirectResponse
from typing import Optional
import urllib.parse

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_active_user
from app.core.config import settings
from app.schemas.auth import UserCreate, UserOut, Token
from app.schemas.user import UserUpdate
from app.services.auth_service import AuthService
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ========== Registration ==========

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user account.

    Args:
        user_data: User registration data (email, name, password)
        db: Database session

    Returns:
        The newly created user object (without password)

    Raises:
        HTTPException 400: Email already registered
    """
    return AuthService.register_user(db, user_data)


# ========== Login ==========

@router.post("/login", response_model=Token)
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Authenticate a user with email and password.

    Args:
        form_data: OAuth2 password request form (username=email, password)
        db: Database session

    Returns:
        JWT access token

    Raises:
        HTTPException 401: Invalid credentials
    """
    access_token = AuthService.login_user(db, form_data.username, form_data.password)
    return {"access_token": access_token, "token_type": "bearer"}


# ========== Google OAuth ==========

# Initialize OAuth client for Google
oauth = OAuth()
oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


@router.get("/google")
async def google_login(
    request: Request,
    return_url: str = Query("/", description="URL to return after successful login")
):
    """
    Redirect user to Google OAuth login page.

    Args:
        request: FastAPI request object
        return_url: URL to redirect after successful authentication

    Returns:
        RedirectResponse to Google OAuth
    """
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    request.session['return_url'] = return_url
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback")
async def google_callback(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Handle Google OAuth callback after user authorization.

    This endpoint receives the authorization code from Google,
    exchanges it for an access token, and either creates a new user
    or logs in an existing user.

    Args:
        request: FastAPI request object
        db: Database session

    Returns:
        RedirectResponse to frontend with JWT token

    Raises:
        HTTPException 400: Google authentication failed
    """
    try:
        token = await oauth.google.authorize_access_token(request)
        if not token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get access token from Google"
            )

        user_info = token.get("userinfo")
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get user info from Google"
            )

        email = user_info.get("email")
        name = user_info.get("name")
        avatar_url = user_info.get("picture")

        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not provided by Google"
            )

        user = AuthService.create_or_get_google_user(db, email, name, avatar_url)
        access_token = AuthService.generate_token_for_user(user)

        return_url = request.session.get('return_url', '/')

        if return_url == '/':
            redirect_url = f"{settings.FRONTEND_URL}/auth/callback?token={access_token}"
        else:
            separator = '&' if '?' in return_url else '?'
            redirect_url = f"{settings.FRONTEND_URL}{return_url}{separator}token={access_token}"

        return RedirectResponse(redirect_url)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Google authentication failed: {str(e)}"
        )


# ========== User Profile ==========

@router.get("/users/me", response_model=UserOut)
def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get the current authenticated user's profile.

    Args:
        current_user: Authenticated user object

    Returns:
        User profile data
    """
    return current_user


@router.put("/users/me", response_model=UserOut)
def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update the current user's profile.

    Args:
        user_data: Updated user data (name, avatar_url)
        current_user: Authenticated user object
        db: Database session

    Returns:
        Updated user object
    """
    if user_data.name is not None:
        current_user.name = user_data.name
    if user_data.avatar_url is not None:
        current_user.avatar_url = user_data.avatar_url

    db.commit()
    db.refresh(current_user)
    return current_user