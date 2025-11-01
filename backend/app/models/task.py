"""
Task model for TODO list functionality.
"""
from sqlalchemy import String, ForeignKey, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, generate_uuid
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.channel import Channel


class Task(Base):
    """
    Task model for TODO list items in TODO-type channels.
    
    Features:
    - Content: Task description
    - is_completed: Track completion status
    - assignee: Optional user assignment
    - order: Integer for custom sorting/reordering
    """
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    content: Mapped[str] = mapped_column(String(500), nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    channel_id: Mapped[str] = mapped_column(
        String, ForeignKey("channels.id", ondelete="CASCADE"), nullable=False
    )
    assignee_id: Mapped[Optional[str]] = mapped_column(
        String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    channel: Mapped["Channel"] = relationship("Channel", back_populates="tasks")
    assignee: Mapped[Optional["User"]] = relationship(
        "User", back_populates="assigned_tasks", foreign_keys=[assignee_id]
    )

    def __repr__(self) -> str:
        return f"<Task(id={self.id}, content={self.content[:30]}..., completed={self.is_completed})>"
