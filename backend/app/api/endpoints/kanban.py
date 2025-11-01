"""Kanban endpoints for project board functionality."""
from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.channel import Channel, ChannelType
from app.models.kanban import KanbanColumn, KanbanCard
from app.models.membership import Membership
from app.schemas.kanban import (
    KanbanColumnCreate,
    KanbanColumnUpdate,
    KanbanColumnRead,
    KanbanCardCreate,
    KanbanCardUpdate,
    KanbanCardRead,
    KanbanBoardView
)

router = APIRouter(prefix="/kanban", tags=["Kanban"])


async def check_kanban_channel_access(channel_id: str, user_id: str, db: AsyncSession) -> Channel:
    """Verify user has access to KANBAN channel."""
    result = await db.execute(
        select(Channel).where(Channel.id == channel_id)
    )
    channel = result.scalar_one_or_none()
    
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Channel not found"
        )
    
    if channel.type != ChannelType.KANBAN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Channel is not a KANBAN channel"
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


@router.get("/channels/{channel_id}/board", response_model=KanbanBoardView)
async def get_kanban_board(
    channel_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get the entire Kanban board with all columns and cards."""
    
    # Verify access
    await check_kanban_channel_access(channel_id, current_user.id, db)
    
    # Get all columns with cards
    result = await db.execute(
        select(KanbanColumn)
        .where(KanbanColumn.channel_id == channel_id)
        .order_by(KanbanColumn.position)
        .options(selectinload(KanbanColumn.cards))
    )
    columns = result.scalars().all()
    
    return {
        "channel_id": channel_id,
        "columns": columns
    }


# Column endpoints
@router.post("/channels/{channel_id}/columns", response_model=KanbanColumnRead, status_code=status.HTTP_201_CREATED)
async def create_column(
    channel_id: str,
    column_data: KanbanColumnCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Create a new Kanban column."""
    
    # Verify access
    await check_kanban_channel_access(channel_id, current_user.id, db)
    
    # Get max position
    result = await db.execute(
        select(KanbanColumn.position)
        .where(KanbanColumn.channel_id == channel_id)
        .order_by(KanbanColumn.position.desc())
        .limit(1)
    )
    max_position = result.scalar_one_or_none()
    next_position = (max_position or 0) + 1
    
    # Create column
    column = KanbanColumn(
        title=column_data.title,
        channel_id=channel_id,
        position=next_position
    )
    
    db.add(column)
    await db.commit()
    await db.refresh(column, ["cards"])
    
    return column


@router.put("/columns/{column_id}", response_model=KanbanColumnRead)
async def update_column(
    column_id: str,
    column_data: KanbanColumnUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Update a Kanban column."""
    
    result = await db.execute(
        select(KanbanColumn).where(KanbanColumn.id == column_id)
    )
    column = result.scalar_one_or_none()
    
    if not column:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Column not found"
        )
    
    # Verify access
    await check_kanban_channel_access(column.channel_id, current_user.id, db)
    
    # Update fields
    if column_data.title is not None:
        column.title = column_data.title
    
    if column_data.position is not None:
        column.position = column_data.position
    
    await db.commit()
    await db.refresh(column, ["cards"])
    
    return column


@router.delete("/columns/{column_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_column(
    column_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> None:
    """Delete a Kanban column and all its cards."""
    
    result = await db.execute(
        select(KanbanColumn).where(KanbanColumn.id == column_id)
    )
    column = result.scalar_one_or_none()
    
    if not column:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Column not found"
        )
    
    # Verify access
    await check_kanban_channel_access(column.channel_id, current_user.id, db)
    
    await db.delete(column)
    await db.commit()


# Card endpoints
@router.post("/columns/{column_id}/cards", response_model=KanbanCardRead, status_code=status.HTTP_201_CREATED)
async def create_card(
    column_id: str,
    card_data: KanbanCardCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Create a new Kanban card."""
    
    # Get column
    result = await db.execute(
        select(KanbanColumn).where(KanbanColumn.id == column_id)
    )
    column = result.scalar_one_or_none()
    
    if not column:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Column not found"
        )
    
    # Verify access
    await check_kanban_channel_access(column.channel_id, current_user.id, db)
    
    # Get max position
    result = await db.execute(
        select(KanbanCard.position)
        .where(KanbanCard.column_id == column_id)
        .order_by(KanbanCard.position.desc())
        .limit(1)
    )
    max_position = result.scalar_one_or_none()
    next_position = (max_position or 0) + 1
    
    # Create card
    card = KanbanCard(
        content=card_data.content,
        column_id=column_id,
        position=next_position
    )
    
    db.add(card)
    await db.commit()
    await db.refresh(card)
    
    return card


@router.put("/cards/{card_id}", response_model=KanbanCardRead)
async def update_card(
    card_id: str,
    card_data: KanbanCardUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Update a Kanban card."""
    
    result = await db.execute(
        select(KanbanCard)
        .where(KanbanCard.id == card_id)
        .options(selectinload(KanbanCard.column))
    )
    card = result.scalar_one_or_none()
    
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found"
        )
    
    # Verify access
    await check_kanban_channel_access(card.column.channel_id, current_user.id, db)
    
    # Update fields
    if card_data.content is not None:
        card.content = card_data.content
    
    if card_data.position is not None:
        card.position = card_data.position
    
    # Move to different column
    if card_data.column_id is not None and card_data.column_id != card.column_id:
        # Verify new column exists in same channel
        result = await db.execute(
            select(KanbanColumn).where(KanbanColumn.id == card_data.column_id)
        )
        new_column = result.scalar_one_or_none()
        
        if not new_column:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target column not found"
            )
        
        if new_column.channel_id != card.column.channel_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot move card to column in different channel"
            )
        
        card.column_id = card_data.column_id
        
        # Get max position in new column
        result = await db.execute(
            select(KanbanCard.position)
            .where(KanbanCard.column_id == card_data.column_id)
            .order_by(KanbanCard.position.desc())
            .limit(1)
        )
        max_position = result.scalar_one_or_none()
        card.position = (max_position or 0) + 1
    
    await db.commit()
    await db.refresh(card)
    
    return card


@router.delete("/cards/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_card(
    card_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> None:
    """Delete a Kanban card."""
    
    result = await db.execute(
        select(KanbanCard)
        .where(KanbanCard.id == card_id)
        .options(selectinload(KanbanCard.column))
    )
    card = result.scalar_one_or_none()
    
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found"
        )
    
    # Verify access
    await check_kanban_channel_access(card.column.channel_id, current_user.id, db)
    
    await db.delete(card)
    await db.commit()


@router.put("/channels/{channel_id}/columns/reorder", response_model=List[KanbanColumnRead])
async def reorder_columns(
    channel_id: str,
    column_ids: List[str],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Reorder columns in a Kanban board."""
    
    # Verify access
    await check_kanban_channel_access(channel_id, current_user.id, db)
    
    # Update positions
    for position, column_id in enumerate(column_ids):
        result = await db.execute(
            select(KanbanColumn).where(
                and_(
                    KanbanColumn.id == column_id,
                    KanbanColumn.channel_id == channel_id
                )
            )
        )
        column = result.scalar_one_or_none()
        
        if column:
            column.position = position
    
    await db.commit()
    
    # Return updated list
    result = await db.execute(
        select(KanbanColumn)
        .where(KanbanColumn.channel_id == channel_id)
        .order_by(KanbanColumn.position)
        .options(selectinload(KanbanColumn.cards))
    )
    columns = result.scalars().all()
    
    return columns


@router.put("/columns/{column_id}/cards/reorder", response_model=List[KanbanCardRead])
async def reorder_cards(
    column_id: str,
    card_ids: List[str],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Reorder cards within a column."""
    
    # Get column
    result = await db.execute(
        select(KanbanColumn).where(KanbanColumn.id == column_id)
    )
    column = result.scalar_one_or_none()
    
    if not column:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Column not found"
        )
    
    # Verify access
    await check_kanban_channel_access(column.channel_id, current_user.id, db)
    
    # Update positions
    for position, card_id in enumerate(card_ids):
        result = await db.execute(
            select(KanbanCard).where(
                and_(
                    KanbanCard.id == card_id,
                    KanbanCard.column_id == column_id
                )
            )
        )
        card = result.scalar_one_or_none()
        
        if card:
            card.position = position
    
    await db.commit()
    
    # Return updated list
    result = await db.execute(
        select(KanbanCard)
        .where(KanbanCard.column_id == column_id)
        .order_by(KanbanCard.position)
    )
    cards = result.scalars().all()
    
    return cards
