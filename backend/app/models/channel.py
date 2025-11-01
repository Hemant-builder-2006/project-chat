"""
Channel model for different types of communication and collaboration spaces.
"""
from sqlalchemy import String, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, generate_uuid
from typing import List, Optional, TYPE_CHECKING
import enum

if TYPE_CHECKING:
    from app.models.group import Group
    from app.models.message import Message
    from app.models.task import Task
    from app.models.document import DocumentPage
    from app.models.kanban import KanbanColumn


class ChannelType(str, enum.Enum):
    """
    Enum for different channel types.
    
    How does the Channel.type field enable different functionalities?
    - TEXT: Traditional chat with messages
    - VOICE: Audio-only WebRTC channels
    - TODO: Task management with todo list
    - DOC: Collaborative document editing
    - KANBAN: Visual project boards with columns and cards
    
    The type field allows a single Channel model to support multiple use cases:
    1. Frontend can render different UI based on type
    2. Backend can validate operations (e.g., only TODO channels can have tasks)
    3. Permissions can be scoped per channel type
    4. Reduces database complexity vs. having separate tables for each type
    """
    TEXT = "TEXT"
    VOICE = "VOICE"
    TODO = "TODO"
    DOC = "DOC"
    KANBAN = "KANBAN"
    VIDEO = "VIDEO"


class Channel(Base):
    """
    Channel model representing a communication/collaboration space within a group.
    """
    __tablename__ = "channels"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    group_id: Mapped[str] = mapped_column(
        String, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False
    )
    type: Mapped[ChannelType] = mapped_column(
        SQLEnum(ChannelType), nullable=False, default=ChannelType.TEXT
    )
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Relationships
    group: Mapped["Group"] = relationship("Group", back_populates="channels")
    messages: Mapped[List["Message"]] = relationship(
        "Message", back_populates="channel", cascade="all, delete-orphan"
    )
    tasks: Mapped[List["Task"]] = relationship(
        "Task", back_populates="channel", cascade="all, delete-orphan"
    )
    document_page: Mapped[Optional["DocumentPage"]] = relationship(
        "DocumentPage", back_populates="channel", uselist=False, cascade="all, delete-orphan"
    )
    kanban_columns: Mapped[List["KanbanColumn"]] = relationship(
        "KanbanColumn", back_populates="channel", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Channel(id={self.id}, name={self.name}, type={self.type})>"
