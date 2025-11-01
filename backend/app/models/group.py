"""
Group model for organizing users and channels.
"""
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, generate_uuid
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.membership import Membership
    from app.models.channel import Channel


class Group(Base):
    """
    Group model representing a workspace/team.
    
    Groups contain:
    - Multiple channels (text, voice, todo, doc, kanban)
    - Multiple members (via Membership table)
    - One owner
    
    This enables multi-tenant collaboration where users can be members of multiple groups.
    """
    __tablename__ = "groups"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    owner_id: Mapped[str] = mapped_column(
        String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="owned_groups")
    memberships: Mapped[List["Membership"]] = relationship(
        "Membership", back_populates="group", cascade="all, delete-orphan"
    )
    channels: Mapped[List["Channel"]] = relationship(
        "Channel", back_populates="group", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Group(id={self.id}, name={self.name})>"
