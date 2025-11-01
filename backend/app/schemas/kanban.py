"""
Pydantic schemas for Kanban models.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List


class KanbanColumnBase(BaseModel):
    """Base schema with common column fields."""
    title: str = Field(..., min_length=1, max_length=100)


class KanbanColumnCreate(KanbanColumnBase):
    """Schema for creating a new Kanban column."""
    order: Optional[int] = 0


class KanbanColumnUpdate(BaseModel):
    """Schema for updating column information."""
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    order: Optional[int] = None


class KanbanColumnRead(KanbanColumnBase):
    """Schema for reading column information."""
    id: str
    channel_id: str
    order: int

    model_config = ConfigDict(from_attributes=True)


# Kanban Card Schemas
class KanbanCardBase(BaseModel):
    """Base schema with common card fields."""
    content: str = Field(..., min_length=1)


class KanbanCardCreate(KanbanCardBase):
    """Schema for creating a new Kanban card."""
    order: Optional[int] = 0


class KanbanCardUpdate(BaseModel):
    """Schema for updating card information."""
    content: Optional[str] = Field(None, min_length=1)
    order: Optional[int] = None


class KanbanCardMove(BaseModel):
    """Schema for moving a card to a different column."""
    column_id: str
    new_order: int


class KanbanCardRead(KanbanCardBase):
    """Schema for reading card information."""
    id: str
    column_id: str
    order: int

    model_config = ConfigDict(from_attributes=True)


# Nested schema for full board view
class KanbanColumnWithCards(KanbanColumnRead):
    """Schema for column with nested cards."""
    cards: List[KanbanCardRead] = []


class KanbanBoardRead(BaseModel):
    """Schema for reading entire Kanban board."""
    columns: List[KanbanColumnWithCards]
