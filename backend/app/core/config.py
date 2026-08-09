"""
Application configuration and settings management.

Loads environment variables and provides centralized access
to all application settings.
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database Configuration
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://taskflow_user:taskflow_pass@localhost:5433/taskflow_db"
    )

    # JWT Authentication Configuration
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY",
        "your_super_secret_key_change_this_in_production"
    )
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(
        os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7")
    )

    # Google OAuth Configuration
    GOOGLE_CLIENT_ID: Optional[str] = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: Optional[str] = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI: str = os.getenv(
        "GOOGLE_REDIRECT_URI",
        "http://localhost:8000/api/v1/auth/google/callback"
    )

    # Frontend Application URL
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")

    # Email Service Configuration (Maileroo HTTP API)
    MAILEROO_API_KEY: str = os.getenv("MAILEROO_API_KEY", "")
    FROM_EMAIL: str = os.getenv("FROM_EMAIL", "rahafmoualla31297@60e4162f569905c4.maileroo.org")

    # Runtime Environment Settings
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


settings = Settings()