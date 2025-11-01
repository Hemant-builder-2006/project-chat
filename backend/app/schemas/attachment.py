"""
Pydantic schemas for file attachments.
"""
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class AttachmentBase(BaseModel):
    """Base schema with common attachment fields."""
    filename: str
    content_type: str
    file_size: int


class AttachmentCreate(AttachmentBase):
    """Schema for creating a new attachment (after file upload)."""
    stored_filename: str
    file_path: str
    message_id: str
    uploaded_by_id: str


class AttachmentRead(AttachmentBase):
    """Schema for reading attachment information."""
    id: str
    stored_filename: str
    file_path: str
    message_id: str
    uploaded_by_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AttachmentUploadResponse(BaseModel):
    """Response after successful file upload."""
    attachment: AttachmentRead
    download_url: str


class FileUploadInfo(BaseModel):
    """Information about an uploaded file (before DB record creation)."""
    filename: str
    stored_filename: str
    path: str
    size: int
    content_type: str
