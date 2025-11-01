"""
Pydantic schemas for authentication and tokens.
"""
from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for data extracted from JWT token."""
    user_id: Optional[str] = None
    username: Optional[str] = None


class LoginRequest(BaseModel):
    """Schema for login request."""
    username: str
    password: str
