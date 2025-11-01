"""
Pydantic schemas for Channel model.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from enum import Enum


class ChannelType(str, Enum):
    """
    Enum for channel types.
    
    Using Enums in Pydantic:
    - Provides automatic validation
    - Auto-generates OpenAPI schema with allowed values
    - Type-safe in Python code
    - Clear documentation of valid options
    """
    TEXT = "TEXT"
    VOICE = "VOICE"
    TODO = "TODO"
    DOC = "DOC"
    KANBAN = "KANBAN"
    VIDEO = "VIDEO"


class ChannelBase(BaseModel):
    """Base schema with common channel fields."""
    name: str = Field(..., min_length=1, max_length=100)
    type: ChannelType = ChannelType.TEXT
    description: Optional[str] = Field(None, max_length=500)


class ChannelCreate(ChannelBase):
    """Schema for creating a new channel."""
    pass


class ChannelUpdate(BaseModel):
    """Schema for updating channel information."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class ChannelRead(ChannelBase):
    """
    Schema for reading channel information.
    
    How schemas are used:
    1. Input Validation: ChannelCreate validates POST request body
    2. Output Formatting: ChannelRead serializes database model to JSON
    3. Type Safety: Ensures consistent data structure across API
    4. Documentation: Auto-generates OpenAPI/Swagger docs
    """
    id: str
    group_id: str

    model_config = ConfigDict(from_attributes=True)
