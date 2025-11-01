"""
Pydantic schemas for Message and Reaction models.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


class MessageBase(BaseModel):
    """Base schema with common message fields."""
    content: str = Field(..., min_length=1, max_length=4000)


class MessageCreate(MessageBase):
    """Schema for creating a new message."""
    parent_message_id: Optional[str] = None


class MessageUpdate(BaseModel):
    """Schema for updating message content."""
    content: Optional[str] = Field(None, min_length=1, max_length=4000)


# Forward references for circular imports
class AttachmentRead(BaseModel):
    """Minimal attachment info for message responses."""
    id: str
    filename: str
    content_type: str
    file_size: int
    stored_filename: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class MessageRead(MessageBase):
    """Schema for reading message information."""
    id: str
    user_id: str
    channel_id: str
    created_at: datetime
    parent_message_id: Optional[str] = None
    attachments: List[AttachmentRead] = []

    model_config = ConfigDict(from_attributes=True)


# Reaction Schemas
class ReactionBase(BaseModel):
    """Base schema with common reaction fields."""
    emoji: str = Field(..., min_length=1, max_length=50)


class ReactionCreate(ReactionBase):
    """Schema for creating a reaction."""
    message_id: str


class ReactionRead(ReactionBase):
    """Schema for reading reaction information."""
    id: str
    user_id: str
    message_id: str

    model_config = ConfigDict(from_attributes=True)
