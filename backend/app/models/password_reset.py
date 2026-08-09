"""
Password Reset model for managing password reset tokens.
"""
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class PasswordReset(BaseModel):
    """
    Password reset token for secure password recovery.
    
    Attributes:
        user_id: ID of the user requesting the reset
        token: Unique UUID token
        expires_at: Expiration timestamp (1 hour from creation)
        used: Flag indicating if token has been used
    """
    __tablename__ = "password_resets"

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID of the user requesting the reset"
    )
    token = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique UUID token for password reset"
    )
    expires_at = Column(
        DateTime(timezone=True),
        nullable=False,
        comment="Expiration timestamp (1 hour from creation)"
    )
    used = Column(
        Boolean,
        default=False,
        index=True,
        comment="Flag indicating if token has been used"
    )

    user = relationship("User", back_populates="password_resets")