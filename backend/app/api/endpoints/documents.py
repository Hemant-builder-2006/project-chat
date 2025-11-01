"""Document endpoints for collaborative document editing."""
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.channel import Channel, ChannelType
from app.models.document import DocumentPage
from app.models.membership import Membership
from app.schemas.document import DocumentPageCreate, DocumentPageUpdate, DocumentPageRead

router = APIRouter(prefix="/documents", tags=["Documents"])


async def check_doc_channel_access(channel_id: str, user_id: str, db: AsyncSession) -> Channel:
    """Verify user has access to DOC channel."""
    result = await db.execute(
        select(Channel).where(Channel.id == channel_id)
    )
    channel = result.scalar_one_or_none()
    
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Channel not found"
        )
    
    if channel.type != ChannelType.DOC:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Channel is not a DOC channel"
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


@router.get("/channels/{channel_id}", response_model=DocumentPageRead)
async def get_document(
    channel_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get the document for a DOC channel."""
    
    # Verify access
    await check_doc_channel_access(channel_id, current_user.id, db)
    
    # Get document
    result = await db.execute(
        select(DocumentPage)
        .where(DocumentPage.channel_id == channel_id)
        .options(selectinload(DocumentPage.last_editor))
    )
    document = result.scalar_one_or_none()
    
    if not document:
        # Create empty document if doesn't exist
        document = DocumentPage(
            channel_id=channel_id,
            content="",
            version=1,
            last_edited_by_id=current_user.id
        )
        db.add(document)
        await db.commit()
        await db.refresh(document, ["last_editor"])
    
    return document


@router.put("/channels/{channel_id}", response_model=DocumentPageRead)
async def update_document(
    channel_id: str,
    document_data: DocumentPageUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Update the document content for a DOC channel."""
    
    # Verify access
    await check_doc_channel_access(channel_id, current_user.id, db)
    
    # Get or create document
    result = await db.execute(
        select(DocumentPage).where(DocumentPage.channel_id == channel_id)
    )
    document = result.scalar_one_or_none()
    
    if not document:
        # Create new document
        document = DocumentPage(
            channel_id=channel_id,
            content=document_data.content or "",
            version=1,
            last_edited_by_id=current_user.id
        )
        db.add(document)
    else:
        # Update existing document
        document.content = document_data.content or ""
        document.version += 1
        document.last_edited_by_id = current_user.id
    
    await db.commit()
    await db.refresh(document, ["last_editor"])
    
    return document


@router.post("/channels/{channel_id}/save", response_model=DocumentPageRead)
async def save_document(
    channel_id: str,
    document_data: DocumentPageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Save document content (alternative endpoint for create/update)."""
    
    # Verify access
    await check_doc_channel_access(channel_id, current_user.id, db)
    
    # Get or create document
    result = await db.execute(
        select(DocumentPage).where(DocumentPage.channel_id == channel_id)
    )
    document = result.scalar_one_or_none()
    
    if not document:
        # Create new
        document = DocumentPage(
            channel_id=channel_id,
            content=document_data.content,
            version=1,
            last_edited_by_id=current_user.id
        )
        db.add(document)
    else:
        # Update
        document.content = document_data.content
        document.version += 1
        document.last_edited_by_id = current_user.id
    
    await db.commit()
    await db.refresh(document, ["last_editor"])
    
    return document
