"""
Message and Reaction models for chat functionality.
"""
from sqlalchemy import String, ForeignKey, DateTime, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.db.base import Base, generate_uuid
from typing import List, Optional, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.channel import Channel
    from app.models.attachment import Attachment


class Message(Base):
    """
    Message model for chat messages in channels.
    
    Supports threaded conversations via self-referencing foreign key:
    - parent_message_id allows replies to messages (threads)
    - This creates a tree structure: parent message -> child replies
    - Enables nested conversations without additional tables
    - Frontend can group/display messages as threads
    - Null parent_message_id means top-level message
    """
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    channel_id: Mapped[str] = mapped_column(
        String, ForeignKey("channels.id", ondelete="CASCADE"), nullable=False
    )
    
    # Self-referencing FK for message threads
    parent_message_id: Mapped[Optional[str]] = mapped_column(
        String, ForeignKey("messages.id", ondelete="CASCADE"), nullable=True
    )

    # Relationships
    sender: Mapped["User"] = relationship("User", back_populates="messages")
    channel: Mapped["Channel"] = relationship("Channel", back_populates="messages")
    reactions: Mapped[List["Reaction"]] = relationship(
        "Reaction", back_populates="message", cascade="all, delete-orphan"
    )
    attachments: Mapped[List["Attachment"]] = relationship(
        "Attachment", back_populates="message", cascade="all, delete-orphan"
    )
    
    # Thread relationships
    parent_message: Mapped[Optional["Message"]] = relationship(
        "Message", remote_side=[id], back_populates="replies"
    )
    replies: Mapped[List["Message"]] = relationship(
        "Message", back_populates="parent_message", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Message(id={self.id}, channel_id={self.channel_id})>"


class Reaction(Base):
    """
    Reaction model for emoji reactions to messages.
    
    Implements the reaction feature (like Slack/Discord):
    - Users can react to messages with emojis
    - Each user can only react once with the same emoji to a message
    - UniqueConstraint prevents duplicate reactions
    """
    __tablename__ = "reactions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    emoji: Mapped[str] = mapped_column(String(50), nullable=False)
    user_id: Mapped[str] = mapped_column(
        String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    message_id: Mapped[str] = mapped_column(
        String, ForeignKey("messages.id", ondelete="CASCADE"), nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="reactions")
    message: Mapped["Message"] = relationship("Message", back_populates="reactions")

    # Ensure a user can only react once with the same emoji to a message
    __table_args__ = (
        UniqueConstraint("user_id", "message_id", "emoji", name="unique_user_message_emoji"),
    )

    def __repr__(self) -> str:
        return f"<Reaction(emoji={self.emoji}, user_id={self.user_id}, message_id={self.message_id})>"
