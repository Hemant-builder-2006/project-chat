"""
User model for authentication and authorization.
"""
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, generate_uuid
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.group import Group
    from app.models.membership import Membership
    from app.models.message import Message, Reaction
    from app.models.task import Task
    from app.models.document import DocumentPage


class User(Base):
    """
    User model representing a user in the system.
    
    Users can:
    - Belong to multiple groups (via Membership)
    - Own groups
    - Send messages
    - Be assigned tasks
    - React to messages
    """
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Relationships
    owned_groups: Mapped[List["Group"]] = relationship(
        "Group", back_populates="owner", cascade="all, delete-orphan"
    )
    memberships: Mapped[List["Membership"]] = relationship(
        "Membership", back_populates="user", cascade="all, delete-orphan"
    )
    messages: Mapped[List["Message"]] = relationship(
        "Message", back_populates="sender", cascade="all, delete-orphan"
    )
    reactions: Mapped[List["Reaction"]] = relationship(
        "Reaction", back_populates="user", cascade="all, delete-orphan"
    )
    assigned_tasks: Mapped[List["Task"]] = relationship(
        "Task", back_populates="assignee", foreign_keys="Task.assignee_id"
    )
    edited_documents: Mapped[List["DocumentPage"]] = relationship(
        "DocumentPage", back_populates="last_editor", foreign_keys="DocumentPage.last_edited_by_id"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username})>"
