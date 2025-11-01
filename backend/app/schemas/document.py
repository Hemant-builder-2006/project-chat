"""
Pydantic schemas for DocumentPage model.
"""
from pydantic import BaseModel, ConfigDict
from typing import Optional


class DocumentPageBase(BaseModel):
    """Base schema with common document fields."""
    content: str = ""


class DocumentPageCreate(DocumentPageBase):
    """Schema for creating a new document."""
    channel_id: str


class DocumentPageUpdate(BaseModel):
    """Schema for updating document content."""
    content: str


class DocumentPageRead(DocumentPageBase):
    """Schema for reading document information."""
    id: str
    channel_id: str
    last_edited_by_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
