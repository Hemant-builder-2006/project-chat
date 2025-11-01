"""Attachment model for file uploads."""
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.message import Message
    from app.models.user import User


class Attachment(Base):
    """File attachments for messages."""
    
    __tablename__ = "attachments"
    
    # File information
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Relationships
    message_id: Mapped[str] = mapped_column(ForeignKey("messages.id", ondelete="CASCADE"), nullable=False)
    uploaded_by_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    
    # Relationships
    message: Mapped["Message"] = relationship(back_populates="attachments")
    uploader: Mapped["User"] = relationship()
