from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.group import Group
from app.models.channel import Channel, ChannelType
from app.models.membership import Membership
from app.schemas.channel import ChannelCreate, ChannelUpdate, ChannelRead

router = APIRouter(prefix="/channels", tags=["Channels"])


async def check_group_membership(
    group_id: str,
    user_id: str,
    db: AsyncSession,
    required_role: str = None
) -> Membership:
    """Check if user is a member of the group with optional role requirement."""
    
    result = await db.execute(
        select(Membership).where(
            Membership.group_id == group_id,
            Membership.user_id == user_id
        )
    )
    membership = result.scalar_one_or_none()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this group"
        )
    
    if required_role and membership.role not in [required_role, "owner"]:
        if required_role == "admin" and membership.role == "admin":
            pass  # admin can do admin things
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
    
    return membership


@router.get("/groups/{group_id}/channels", response_model=List[ChannelRead])
async def list_channels(
    group_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get all channels in a group."""
    
    # Check membership
    await check_group_membership(group_id, current_user.id, db)
    
    # Get channels
    result = await db.execute(
        select(Channel)
        .where(Channel.group_id == group_id)
        .order_by(Channel.created_at)
    )
    channels = result.scalars().all()
    
    return channels


@router.post("/groups/{group_id}/channels", response_model=ChannelRead, status_code=status.HTTP_201_CREATED)
async def create_channel(
    group_id: str,
    channel_data: ChannelCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Create a new channel (admin or owner only)."""
    
    # Check admin/owner permission
    await check_group_membership(group_id, current_user.id, db, required_role="admin")
    
    # Verify group exists
    result = await db.execute(select(Group).where(Group.id == group_id))
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    
    # Create channel
    channel = Channel(
        name=channel_data.name,
        group_id=group_id,
        type=channel_data.type,
        description=channel_data.description
    )
    
    db.add(channel)
    await db.commit()
    await db.refresh(channel)
    
    return channel


@router.get("/{channel_id}", response_model=ChannelRead)
async def get_channel(
    channel_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get a specific channel."""
    
    # Get channel
    result = await db.execute(
        select(Channel)
        .where(Channel.id == channel_id)
        .options(selectinload(Channel.group))
    )
    channel = result.scalar_one_or_none()
    
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Channel not found"
        )
    
    # Check membership
    await check_group_membership(channel.group_id, current_user.id, db)
    
    return channel


@router.put("/{channel_id}", response_model=ChannelRead)
async def update_channel(
    channel_id: str,
    channel_data: ChannelUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Update a channel (admin or owner only)."""
    
    # Get channel
    result = await db.execute(select(Channel).where(Channel.id == channel_id))
    channel = result.scalar_one_or_none()
    
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Channel not found"
        )
    
    # Check admin/owner permission
    await check_group_membership(channel.group_id, current_user.id, db, required_role="admin")
    
    # Update fields
    if channel_data.name is not None:
        channel.name = channel_data.name
    if channel_data.description is not None:
        channel.description = channel_data.description
    if channel_data.type is not None:
        channel.type = channel_data.type
    
    await db.commit()
    await db.refresh(channel)
    
    return channel


@router.delete("/{channel_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_channel(
    channel_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> None:
    """Delete a channel (admin or owner only)."""
    
    # Get channel
    result = await db.execute(select(Channel).where(Channel.id == channel_id))
    channel = result.scalar_one_or_none()
    
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Channel not found"
        )
    
    # Check admin/owner permission
    await check_group_membership(channel.group_id, current_user.id, db, required_role="admin")
    
    await db.delete(channel)
    await db.commit()
