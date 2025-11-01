"""
Membership model for managing user roles within groups.
"""
from sqlalchemy import String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, generate_uuid
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.group import Group


class Membership(Base):
    """
    Membership model representing the many-to-many relationship between Users and Groups.
    
    Why is this table necessary?
    - Users can belong to multiple groups
    - Groups can have multiple users
    - Each membership has a role (admin, member, etc.)
    - This provides fine-grained access control at the group level
    
    The association table pattern allows us to:
    1. Store additional data about the relationship (role)
    2. Query memberships independently
    3. Implement permission checks efficiently
    """
    __tablename__ = "memberships"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(
        String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    group_id: Mapped[str] = mapped_column(
        String, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[str] = mapped_column(
        String(20), nullable=False, default="member"
    )  # 'admin', 'member', 'viewer', etc.

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="memberships")
    group: Mapped["Group"] = relationship("Group", back_populates="memberships")

    # Ensure a user can only have one membership per group
    __table_args__ = (
        UniqueConstraint("user_id", "group_id", name="unique_user_group_membership"),
    )

    def __repr__(self) -> str:
        return f"<Membership(user_id={self.user_id}, group_id={self.group_id}, role={self.role})>"
