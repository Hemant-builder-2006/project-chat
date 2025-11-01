"""
File upload and download endpoints.
Handles file uploads, downloads, and attachment management.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.attachment import Attachment
from app.models.message import Message
from app.schemas.attachment import AttachmentRead, AttachmentUploadResponse
from app.services.file_storage import FileStorageService
from typing import Optional
import os

router = APIRouter()


@router.post("/upload", response_model=AttachmentUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    message_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a file and create an attachment record.
    
    - **file**: The file to upload
    - **message_id**: Optional message ID to attach file to
    
    Returns attachment information and download URL.
    """
    file_service = FileStorageService()
    
    try:
        # Save the file to disk
        file_info = await file_service.save_attachment(file)
        
        # Create attachment record in database
        new_attachment = Attachment(
            filename=file_info["filename"],
            stored_filename=file_info["stored_filename"],
            file_path=file_info["path"],
            file_size=file_info["size"],
            content_type=file_info["content_type"],
            message_id=message_id,
            uploaded_by_id=current_user.id
        )
        
        db.add(new_attachment)
        await db.commit()
        await db.refresh(new_attachment)
        
        # Generate download URL
        download_url = f"/api/files/download/{file_info['stored_filename']}"
        
        return AttachmentUploadResponse(
            attachment=AttachmentRead.model_validate(new_attachment),
            download_url=download_url
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Clean up file if database operation fails
        if 'file_info' in locals():
            file_service.delete_file(file_info["path"])
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )


@router.get("/download/{stored_filename}")
async def download_file(
    stored_filename: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Download a file by its stored filename.
    
    - **stored_filename**: The UUID-based filename stored on disk
    
    Returns the file for download.
    """
    file_service = FileStorageService()
    
    # Get attachment record from database
    result = await db.execute(
        select(Attachment).where(Attachment.stored_filename == stored_filename)
    )
    attachment = result.scalar_one_or_none()
    
    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Check if file exists on disk
    file_path = file_service.get_file_path(attachment.file_path)
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on server"
        )
    
    # Return file with original filename
    return FileResponse(
        path=file_path,
        filename=attachment.filename,
        media_type=attachment.content_type
    )


@router.delete("/{attachment_id}")
async def delete_attachment(
    attachment_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete an attachment and its file.
    
    - **attachment_id**: The ID of the attachment to delete
    
    Only the uploader or message sender can delete attachments.
    """
    # Get attachment
    result = await db.execute(
        select(Attachment).where(Attachment.id == attachment_id)
    )
    attachment = result.scalar_one_or_none()
    
    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found"
        )
    
    # Check permissions: uploader or message sender
    is_uploader = attachment.uploaded_by_id == current_user.id
    is_message_sender = False
    
    if attachment.message_id:
        msg_result = await db.execute(
            select(Message).where(Message.id == attachment.message_id)
        )
        message = msg_result.scalar_one_or_none()
        if message:
            is_message_sender = message.user_id == current_user.id
    
    if not (is_uploader or is_message_sender):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this attachment"
        )
    
    # Delete file from disk
    file_service = FileStorageService()
    file_service.delete_file(attachment.file_path)
    
    # Delete database record
    await db.delete(attachment)
    await db.commit()
    
    return {"message": "Attachment deleted successfully"}


@router.get("/message/{message_id}", response_model=list[AttachmentRead])
async def get_message_attachments(
    message_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all attachments for a specific message.
    
    - **message_id**: The ID of the message
    
    Returns list of attachments.
    """
    result = await db.execute(
        select(Attachment).where(Attachment.message_id == message_id)
    )
    attachments = result.scalars().all()
    
    return [AttachmentRead.model_validate(att) for att in attachments]


@router.post("/avatar", response_model=dict)
async def upload_avatar(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a user avatar image.
    
    - **file**: Image file (PNG, JPG, GIF, WebP)
    
    Returns the avatar URL.
    """
    file_service = FileStorageService()
    
    try:
        # Save avatar (validates it's an image)
        file_info = await file_service.save_avatar(file)
        
        # Update user's avatar URL
        avatar_url = f"/api/files/avatars/{file_info['stored_filename']}"
        current_user.avatar_url = avatar_url
        
        await db.commit()
        
        return {
            "message": "Avatar uploaded successfully",
            "avatar_url": avatar_url
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/avatars/{filename}")
async def get_avatar(filename: str):
    """
    Get a user avatar image.
    
    - **filename**: The avatar filename
    
    Returns the avatar image.
    """
    file_service = FileStorageService()
    file_path = file_service.get_file_path(f"avatars/{filename}")
    
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Avatar not found"
        )
    
    return FileResponse(path=file_path)
