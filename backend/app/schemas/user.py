"""
User Pydantic schemas.

Defines request/response schemas for:
- User registration and login
- User profile responses
- User profile updates
- Password change with validation
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    """
    Schema for user registration with enterprise-grade password validation.

    Attributes:
        email: User's email address
        name: User's full name
        password: Password with strong security requirements
        confirm_password: Password confirmation for validation
    """
    email: EmailStr = Field(..., description="User's email address")
    name: str = Field(..., min_length=2, max_length=100, description="User's full name")
    password: str = Field(..., min_length=8, description="Password (minimum 8 characters)")
    confirm_password: str = Field(..., min_length=8, description="Confirm password")

    @validator('password')
    def validate_password(cls, v: str) -> str:
        """
        Enterprise-grade password validation:
        - Minimum 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one number
        - At least one special character
        - No common passwords
        - No repeated characters (max 3)
        - No sequential characters (abc, 123)
        - At least 3 different character types
        """
        errors = []

        # 1. Minimum length
        if len(v) < 8:
            errors.append("at least 8 characters long")
        
        # 2. Uppercase letter
        if not any(c.isupper() for c in v):
            errors.append("at least one uppercase letter")
        
        # 3. Lowercase letter
        if not any(c.islower() for c in v):
            errors.append("at least one lowercase letter")
        
        # 4. Number
        if not any(c.isdigit() for c in v):
            errors.append("at least one number")
        
        # 5. Special character
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in v):
            errors.append("at least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)")
        
        # 6. No common passwords
        common_passwords = {
            'password', '12345678', 'qwerty', 'admin', 'welcome',
            'letmein', 'monkey', 'dragon', 'master', 'hello',
            'freedom', 'whatever', 'trustno1', 'princess', 'sunshine',
            'iloveyou', '123456789', '123456', '1234567', '1234567890',
            'qwertyuiop', 'asdfghjkl', 'zxcvbnm', 'password123'
        }
        if v.lower() in common_passwords:
            errors.append("not be a common password")
        
        # 7. No repeated characters (max 3 times in a row)
        for i in range(len(v) - 3):
            if len(set(v[i:i+4])) == 1:
                errors.append("no repeated characters (e.g., 'aaaa')")
                break
        
        # 8. No sequential characters
        sequential = ['abc', 'bcd', 'cde', 'def', 'efg', 'fgh', 'ghi', 'hij',
                     'ijk', 'jkl', 'klm', 'lmn', 'mno', 'nop', 'opq', 'pqr',
                     'qrs', 'rst', 'stu', 'tuv', 'uvw', 'vwx', 'wxy', 'xyz',
                     '123', '234', '345', '456', '567', '678', '789', '890']
        lower_v = v.lower()
        for seq in sequential:
            if seq in lower_v:
                errors.append("no sequential characters (e.g., 'abc', '123')")
                break
        
        # 9. At least 3 unique character types
        types = 0
        if any(c.isupper() for c in v): types += 1
        if any(c.islower() for c in v): types += 1
        if any(c.isdigit() for c in v): types += 1
        if any(c in special_chars for c in v): types += 1
        if types < 3:
            errors.append("use at least 3 different character types (uppercase, lowercase, numbers, special)")
        
        if errors:
            raise ValueError(f"Password must have: {', '.join(errors)}")
        
        return v

    @validator('confirm_password')
    def passwords_match(cls, v: str, values: dict) -> str:
        """
        Validate that password and confirm_password match.
        """
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v


class UserOut(BaseModel):
    """
    Schema for user response.

    Attributes:
        id: User ID
        email: User's email address
        name: User's full name
        avatar_url: Optional profile picture URL
        created_at: Account creation timestamp
    """
    id: int
    email: EmailStr
    name: str
    avatar_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """
    Schema for updating user profile.

    Attributes:
        name: Updated name
        avatar_url: Updated avatar URL
        email: Updated email address
    """
    name: Optional[str] = Field(None, min_length=2, max_length=100, description="Updated name")
    avatar_url: Optional[str] = Field(None, description="Updated avatar URL")
    email: Optional[EmailStr] = Field(None, description="Updated email address")


class ChangePassword(BaseModel):
    """
    Schema for changing password with validation.

    Attributes:
        current_password: Current password for verification
        new_password: New password with strong requirements
        confirm_password: Password confirmation
    """
    current_password: str = Field(..., min_length=1, description="Current password")
    new_password: str = Field(..., min_length=8, description="New password (minimum 8 characters)")
    confirm_password: str = Field(..., min_length=8, description="Confirm new password")

    @validator('new_password')
    def validate_new_password(cls, v: str) -> str:
        """
        Apply the same enterprise-grade password validation to new password.
        """
        return UserCreate.validate_password(cls, v)

    @validator('confirm_password')
    def passwords_match(cls, v: str, values: dict) -> str:
        """
        Validate that new_password and confirm_password match.
        """
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v