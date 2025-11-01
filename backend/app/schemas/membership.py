"""
Pydantic schemas for Membership model.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class MembershipBase(BaseModel):
    """Base schema with common membership fields."""
    role: str = Field(..., pattern="^(admin|member|viewer)$")


class MembershipCreate(MembershipBase):
    """Schema for creating a new membership (inviting user to group)."""
    user_id: str
    group_id: str


class MembershipUpdate(BaseModel):
    """Schema for updating membership (e.g., changing role)."""
    role: Optional[str] = Field(None, pattern="^(admin|member|viewer)$")


class MembershipRead(MembershipBase):
    """Schema for reading membership information."""
    id: str
    user_id: str
    group_id: str

    model_config = ConfigDict(from_attributes=True)
