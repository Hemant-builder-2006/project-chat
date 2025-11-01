from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.group import Group
from app.models.membership import Membership
from app.schemas.group import GroupCreate, GroupUpdate, GroupRead

router = APIRouter(prefix="/groups", tags=["Groups"])


@router.get("", response_model=List[GroupRead])
async def list_groups(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get all groups the current user is a member of."""
    
    result = await db.execute(
        select(Group)
        .join(Membership)
        .where(Membership.user_id == current_user.id)
        .options(selectinload(Group.owner))
    )
    groups = result.scalars().all()
    
    return groups


@router.post("", response_model=GroupRead, status_code=status.HTTP_201_CREATED)
async def create_group(
    group_data: GroupCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Create a new group."""
    
    # Create group
    group = Group(
        name=group_data.name,
        description=group_data.description,
        icon_url=group_data.icon_url,
        owner_id=current_user.id
    )
    
    db.add(group)
    await db.flush()  # Get the group ID
    
    # Add creator as owner membership
    membership = Membership(
        user_id=current_user.id,
        group_id=group.id,
        role="owner"
    )
    db.add(membership)
    
    await db.commit()
    await db.refresh(group)
    
    return group


@router.get("/{group_id}", response_model=GroupRead)
async def get_group(
    group_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get a specific group."""
    
    # Check if user is a member
    result = await db.execute(
        select(Membership).where(
            Membership.group_id == group_id,
            Membership.user_id == current_user.id
        )
    )
    membership = result.scalar_one_or_none()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this group"
        )
    
    # Get group
    result = await db.execute(
        select(Group)
        .where(Group.id == group_id)
        .options(selectinload(Group.owner))
    )
    group = result.scalar_one_or_none()
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    
    return group


@router.put("/{group_id}", response_model=GroupRead)
async def update_group(
    group_id: str,
    group_data: GroupUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Update a group (admin or owner only)."""
    
    # Check if user is admin or owner
    result = await db.execute(
        select(Membership).where(
            Membership.group_id == group_id,
            Membership.user_id == current_user.id
        )
    )
    membership = result.scalar_one_or_none()
    
    if not membership or membership.role not in ["admin", "owner"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    # Get group
    result = await db.execute(select(Group).where(Group.id == group_id))
    group = result.scalar_one_or_none()
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    
    # Update fields
    if group_data.name is not None:
        group.name = group_data.name
    if group_data.description is not None:
        group.description = group_data.description
    if group_data.icon_url is not None:
        group.icon_url = group_data.icon_url
    
    await db.commit()
    await db.refresh(group)
    
    return group


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(
    group_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> None:
    """Delete a group (owner only)."""
    
    # Get group
    result = await db.execute(select(Group).where(Group.id == group_id))
    group = result.scalar_one_or_none()
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    
    # Check if user is owner
    if group.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the group owner can delete the group"
        )
    
    await db.delete(group)
    await db.commit()
