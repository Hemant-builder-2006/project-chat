"""
Kanban models for board/card functionality.
"""
from sqlalchemy import String, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, generate_uuid
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.channel import Channel


class KanbanColumn(Base):
    """
    KanbanColumn model representing columns in a Kanban board.
    
    Structure:
    - Each KANBAN channel has multiple columns (To Do, In Progress, Done, etc.)
    - order field allows custom column ordering
    - Can be reordered by updating order values
    """
    __tablename__ = "kanban_columns"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    channel_id: Mapped[str] = mapped_column(
        String, ForeignKey("channels.id", ondelete="CASCADE"), nullable=False
    )
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    channel: Mapped["Channel"] = relationship("Channel", back_populates="kanban_columns")
    cards: Mapped[List["KanbanCard"]] = relationship(
        "KanbanCard", back_populates="column", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<KanbanColumn(id={self.id}, title={self.title}, order={self.order})>"


class KanbanCard(Base):
    """
    KanbanCard model representing individual cards within Kanban columns.
    
    Ordering strategy:
    - Each card has an order field within its column
    - When creating: assign max(order) + 1 in the column
    - When moving: update column_id and recalculate order
    - When reordering within column: update order values
    
    This maintains visual order without complex position calculations:
    1. Query: ORDER BY order ASC to get cards in correct sequence
    2. Move between columns: change column_id, set new order
    3. Reorder within column: update order for affected cards
    4. Simple integer comparison for sorting
    """
    __tablename__ = "kanban_cards"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    column_id: Mapped[str] = mapped_column(
        String, ForeignKey("kanban_columns.id", ondelete="CASCADE"), nullable=False
    )
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    column: Mapped["KanbanColumn"] = relationship("KanbanColumn", back_populates="cards")

    def __repr__(self) -> str:
        return f"<KanbanCard(id={self.id}, content={self.content[:30]}..., order={self.order})>"
