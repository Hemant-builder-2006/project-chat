"""
DocumentPage model for collaborative document editing.
"""
from sqlalchemy import String, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, generate_uuid
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.channel import Channel


class DocumentPage(Base):
    """
    DocumentPage model for DOC-type channels.
    
    One-to-one relationship with Channel:
    - Each DOC channel has exactly one document
    - UniqueConstraint on channel_id enforces this
    - Content field stores the document HTML/Markdown
    - Tracks the last user who edited the document
    
    This design:
    1. Simplifies document management (no versioning complexity)
    2. Each DOC channel is a single collaborative document
    3. Can be extended with versioning/history later if needed
    """
    __tablename__ = "document_pages"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    channel_id: Mapped[str] = mapped_column(
        String, ForeignKey("channels.id", ondelete="CASCADE"), nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    last_edited_by_id: Mapped[Optional[str]] = mapped_column(
        String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # Relationships
    channel: Mapped["Channel"] = relationship("Channel", back_populates="document_page")
    last_editor: Mapped[Optional["User"]] = relationship(
        "User", back_populates="edited_documents", foreign_keys=[last_edited_by_id]
    )

    # Ensure one document per channel
    __table_args__ = (
        UniqueConstraint("channel_id", name="unique_channel_document"),
    )

    def __repr__(self) -> str:
        return f"<DocumentPage(id={self.id}, channel_id={self.channel_id})>"
