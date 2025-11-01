"""
Pydantic schemas for Task model.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class TaskBase(BaseModel):
    """Base schema with common task fields."""
    content: str = Field(..., min_length=1, max_length=500)


class TaskCreate(TaskBase):
    """Schema for creating a new task."""
    assignee_id: Optional[str] = None


class TaskUpdate(BaseModel):
    """Schema for updating task information."""
    content: Optional[str] = Field(None, min_length=1, max_length=500)
    is_completed: Optional[bool] = None
    assignee_id: Optional[str] = None
    order: Optional[int] = None


class TaskRead(TaskBase):
    """Schema for reading task information."""
    id: str
    is_completed: bool
    channel_id: str
    assignee_id: Optional[str] = None
    order: int

    model_config = ConfigDict(from_attributes=True)
