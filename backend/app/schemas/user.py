"""
Pydantic schemas for User model.
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional


class UserBase(BaseModel):
    """Base schema with common user fields."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8, max_length=100)


class UserRead(UserBase):
    """
    Schema for reading user information.
    
    Why exclude hashed_password?
    - Security: Never expose password hashes in API responses
    - Privacy: Users shouldn't see their hashed passwords
    - Best Practice: Separate internal authentication data from public user info
    """
    id: str
    is_active: bool
    is_superuser: bool
    avatar_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class UserInDB(UserRead):
    """Schema for user with hashed password (internal use only)."""
    hashed_password: str
