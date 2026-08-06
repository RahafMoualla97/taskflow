"""
Application configuration and settings management.
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    # ========== Database ==========
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://taskflow_user:taskflow_pass@localhost:5433/taskflow_db"
    )

    # ========== JWT Authentication ==========
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

    # ========== Google OAuth ==========
    GOOGLE_CLIENT_ID: Optional[str] = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: Optional[str] = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI: str = os.getenv(
        "GOOGLE_REDIRECT_URI",
        "http://localhost:8000/api/v1/auth/google/callback"
    )

    # ========== Frontend ==========
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")

    # ========== Email Configuration ==========
    # Option 1: SMTP (Traditional) - Works with Gmail, SendGrid, Brevo SMTP
    EMAIL_HOST: str = os.getenv("EMAIL_HOST", "smtp.gmail.com")
    EMAIL_PORT: int = int(os.getenv("EMAIL_PORT", "465"))  # 465 for SSL
    EMAIL_USERNAME: str = os.getenv("EMAIL_USERNAME", "")
    EMAIL_PASSWORD: str = os.getenv("EMAIL_PASSWORD", "")
    
    # Option 2: HTTP API (Recommended for production)
    BREVO_API_KEY: str = os.getenv("BREVO_API_KEY", "")
    
    # Sender email address
    FROM_EMAIL: str = os.getenv("FROM_EMAIL", "noreply@taskflow.com")

    # ========== Environment ==========
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


settings = Settings()