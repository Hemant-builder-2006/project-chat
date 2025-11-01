"""Message endpoints for chat functionality."""
from typing import List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc
from sqlalchemy.orm import selectinload

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.channel import Channel
from app.models.message import Message, Reaction
from app.models.membership import Membership
from app.schemas.message import (
    MessageCreate,
    MessageUpdate,
    MessageRead,
    ReactionCreate,
    ReactionRead
)

router = APIRouter(prefix="/messages", tags=["Messages"])


async def check_channel_access(channel_id: str, user_id: str, db: AsyncSession) -> Channel:
    """Verify user has access to the channel."""
    result = await db.execute(
        select(Channel).where(Channel.id == channel_id)
    )
    channel = result.scalar_one_or_none()
    
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Channel not found"
        )
    
    # Check group membership
    result = await db.execute(
        select(Membership).where(
            Membership.group_id == channel.group_id,
            Membership.user_id == user_id
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this group"
        )
    
    return channel


@router.get("/channels/{channel_id}", response_model=List[MessageRead])
async def get_channel_messages(
    channel_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    before: Optional[str] = None,  # Message ID for pagination
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get messages from a channel with pagination."""
    
    # Verify access
    await check_channel_access(channel_id, current_user.id, db)
    
    # Build query
    query = select(Message).where(Message.channel_id == channel_id)
    
    # Pagination by ID (for infinite scroll)
    if before:
        query = query.where(Message.id < before)
    
    # Order and limit
    query = query.order_by(desc(Message.created_at)).offset(skip).limit(limit)
    
    # Execute with relationships
    result = await db.execute(
        query.options(
            selectinload(Message.sender),
            selectinload(Message.reactions)
        )
    )
    messages = result.scalars().all()
    
    # Reverse to chronological order
    return list(reversed(messages))


@router.post("/channels/{channel_id}", response_model=MessageRead, status_code=status.HTTP_201_CREATED)
async def create_message(
    channel_id: str,
    message_data: MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Create a new message in a channel."""
    
    # Verify access
    await check_channel_access(channel_id, current_user.id, db)
    
    # Verify parent message if replying
    if message_data.parent_message_id:
        result = await db.execute(
            select(Message).where(
                Message.id == message_data.parent_message_id,
                Message.channel_id == channel_id
            )
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent message not found"
            )
    
    # Create message
    message = Message(
        content=message_data.content,
        sender_id=current_user.id,
        channel_id=channel_id,
        parent_message_id=message_data.parent_message_id
    )
    
    db.add(message)
    await db.commit()
    await db.refresh(message, ["sender", "reactions"])
    
    return message


@router.get("/{message_id}", response_model=MessageRead)
async def get_message(
    message_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get a specific message."""
    
    result = await db.execute(
        select(Message)
        .where(Message.id == message_id)
        .options(
            selectinload(Message.sender),
            selectinload(Message.channel),
            selectinload(Message.reactions),
            selectinload(Message.replies)
        )
    )
    message = result.scalar_one_or_none()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # Verify access
    await check_channel_access(message.channel_id, current_user.id, db)
    
    return message


@router.put("/{message_id}", response_model=MessageRead)
async def update_message(
    message_id: str,
    message_data: MessageUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Update a message (sender only)."""
    
    result = await db.execute(
        select(Message).where(Message.id == message_id)
    )
    message = result.scalar_one_or_none()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # Verify access
    await check_channel_access(message.channel_id, current_user.id, db)
    
    # Only sender can edit
    if message.sender_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only edit your own messages"
        )
    
    # Update content
    if message_data.content is not None:
        message.content = message_data.content
        message.is_edited = True
    
    await db.commit()
    await db.refresh(message, ["sender", "reactions"])
    
    return message


@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_message(
    message_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> None:
    """Delete a message (sender or admin)."""
    
    result = await db.execute(
        select(Message)
        .where(Message.id == message_id)
        .options(selectinload(Message.channel))
    )
    message = result.scalar_one_or_none()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # Verify access
    channel = await check_channel_access(message.channel_id, current_user.id, db)
    
    # Check permission (sender or group admin/owner)
    if message.sender_id != current_user.id:
        result = await db.execute(
            select(Membership).where(
                Membership.group_id == channel.group_id,
                Membership.user_id == current_user.id
            )
        )
        membership = result.scalar_one_or_none()
        
        if not membership or membership.role not in ["admin", "owner"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
    
    await db.delete(message)
    await db.commit()


@router.post("/{message_id}/reactions", response_model=ReactionRead, status_code=status.HTTP_201_CREATED)
async def add_reaction(
    message_id: str,
    reaction_data: ReactionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Add a reaction to a message."""
    
    # Get message
    result = await db.execute(
        select(Message).where(Message.id == message_id)
    )
    message = result.scalar_one_or_none()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # Verify access
    await check_channel_access(message.channel_id, current_user.id, db)
    
    # Check if reaction already exists
    result = await db.execute(
        select(Reaction).where(
            and_(
                Reaction.message_id == message_id,
                Reaction.user_id == current_user.id,
                Reaction.emoji == reaction_data.emoji
            )
        )
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        return existing
    
    # Create reaction
    reaction = Reaction(
        message_id=message_id,
        user_id=current_user.id,
        emoji=reaction_data.emoji
    )
    
    db.add(reaction)
    await db.commit()
    await db.refresh(reaction)
    
    return reaction


@router.delete("/{message_id}/reactions/{emoji}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_reaction(
    message_id: str,
    emoji: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> None:
    """Remove a reaction from a message."""
    
    # Get message
    result = await db.execute(
        select(Message).where(Message.id == message_id)
    )
    message = result.scalar_one_or_none()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # Verify access
    await check_channel_access(message.channel_id, current_user.id, db)
    
    # Find reaction
    result = await db.execute(
        select(Reaction).where(
            and_(
                Reaction.message_id == message_id,
                Reaction.user_id == current_user.id,
                Reaction.emoji == emoji
            )
        )
    )
    reaction = result.scalar_one_or_none()
    
    if reaction:
        await db.delete(reaction)
        await db.commit()


@router.get("/search/{channel_id}", response_model=List[MessageRead])
async def search_messages(
    channel_id: str,
    q: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Search messages in a channel."""
    
    # Verify access
    await check_channel_access(channel_id, current_user.id, db)
    
    # Search messages (case-insensitive)
    result = await db.execute(
        select(Message)
        .where(
            and_(
                Message.channel_id == channel_id,
                Message.content.ilike(f"%{q}%")
            )
        )
        .order_by(desc(Message.created_at))
        .limit(limit)
        .options(selectinload(Message.sender))
    )
    messages = result.scalars().all()
    
    return messages
