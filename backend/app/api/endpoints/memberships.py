from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.group import Group
from app.models.membership import Membership
from app.schemas.membership import MembershipCreate, MembershipUpdate, MembershipRead
from app.schemas.user import UserRead

router = APIRouter(prefix="/memberships", tags=["Memberships"])


@router.get("/groups/{group_id}/members", response_model=List[MembershipRead])
async def list_group_members(
    group_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get all members of a group."""
    
    # Check if user is a member
    result = await db.execute(
        select(Membership).where(
            Membership.group_id == group_id,
            Membership.user_id == current_user.id
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this group"
        )
    
    # Get all members
    result = await db.execute(
        select(Membership).where(Membership.group_id == group_id)
    )
    memberships = result.scalars().all()
    
    return memberships


@router.post("/groups/{group_id}/members", response_model=MembershipRead, status_code=status.HTTP_201_CREATED)
async def add_member(
    group_id: str,
    membership_data: MembershipCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Add a member to a group (admin or owner only)."""
    
    # Check if current user is admin/owner
    result = await db.execute(
        select(Membership).where(
            Membership.group_id == group_id,
            Membership.user_id == current_user.id
        )
    )
    current_membership = result.scalar_one_or_none()
    
    if not current_membership or current_membership.role not in ["admin", "owner"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    # Check if user to add exists
    result = await db.execute(select(User).where(User.id == membership_data.user_id))
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if membership already exists
    result = await db.execute(
        select(Membership).where(
            and_(
                Membership.group_id == group_id,
                Membership.user_id == membership_data.user_id
            )
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member"
        )
    
    # Create membership
    membership = Membership(
        user_id=membership_data.user_id,
        group_id=group_id,
        role=membership_data.role or "member"
    )
    
    db.add(membership)
    await db.commit()
    await db.refresh(membership)
    
    return membership


@router.put("/groups/{group_id}/members/{user_id}", response_model=MembershipRead)
async def update_member_role(
    group_id: str,
    user_id: str,
    membership_data: MembershipUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Update a member's role (owner only, cannot change owner role)."""
    
    # Get group
    result = await db.execute(select(Group).where(Group.id == group_id))
    group = result.scalar_one_or_none()
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    
    # Check if current user is owner
    if group.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the group owner can update member roles"
        )
    
    # Get membership to update
    result = await db.execute(
        select(Membership).where(
            and_(
                Membership.group_id == group_id,
                Membership.user_id == user_id
            )
        )
    )
    membership = result.scalar_one_or_none()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Membership not found"
        )
    
    # Prevent changing owner's role
    if membership.role == "owner":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change the owner's role"
        )
    
    # Update role
    if membership_data.role is not None:
        membership.role = membership_data.role
    
    await db.commit()
    await db.refresh(membership)
    
    return membership


@router.delete("/groups/{group_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    group_id: str,
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> None:
    """Remove a member from a group (admin/owner or self)."""
    
    # Get membership to remove
    result = await db.execute(
        select(Membership).where(
            and_(
                Membership.group_id == group_id,
                Membership.user_id == user_id
            )
        )
    )
    membership = result.scalar_one_or_none()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Membership not found"
        )
    
    # Check permissions
    is_self = user_id == current_user.id
    
    if not is_self:
        # Check if current user is admin/owner
        result = await db.execute(
            select(Membership).where(
                and_(
                    Membership.group_id == group_id,
                    Membership.user_id == current_user.id
                )
            )
        )
        current_membership = result.scalar_one_or_none()
        
        if not current_membership or current_membership.role not in ["admin", "owner"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
    
    # Cannot remove owner
    if membership.role == "owner":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove the group owner"
        )
    
    await db.delete(membership)
    await db.commit()
