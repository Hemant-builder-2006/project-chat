"""
Pydantic schemas for Group model.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class GroupBase(BaseModel):
    """Base schema with common group fields."""
    name: str = Field(..., min_length=1, max_length=100)


class GroupCreate(GroupBase):
    """Schema for creating a new group."""
    pass


class GroupUpdate(BaseModel):
    """Schema for updating group information."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)


class GroupRead(GroupBase):
    """
    Schema for reading group information.
    
    Used for:
    - Listing user's groups
    - Getting group details
    - API responses
    """
    id: str
    owner_id: str

    model_config = ConfigDict(from_attributes=True)
