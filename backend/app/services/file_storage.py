"""File upload and storage service."""
import os
import uuid
import shutil
from pathlib import Path
from typing import Optional, BinaryIO
from fastapi import UploadFile, HTTPException, status
import mimetypes

from app.core.config import settings


class FileStorageService:
    """Handle file upload, storage, and retrieval."""
    
    def __init__(self):
        self.base_upload_dir = Path(settings.UPLOAD_DIR)
        self.max_file_size = settings.MAX_FILE_SIZE  # bytes
        self.allowed_extensions = {
            'images': {'.jpg', '.jpeg', '.png', '.gif', '.webp'},
            'documents': {'.pdf', '.doc', '.docx', '.txt', '.md'},
            'archives': {'.zip', '.rar', '.tar', '.gz'},
            'code': {'.py', '.js', '.ts', '.json', '.html', '.css'},
            'all': {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.pdf', '.doc', 
                   '.docx', '.txt', '.md', '.zip', '.rar', '.tar', '.gz',
                   '.py', '.js', '.ts', '.json', '.html', '.css', '.mp3',
                   '.mp4', '.wav', '.avi', '.mov'}
        }
        
        # Create upload directories
        self._create_directories()
    
    def _create_directories(self):
        """Create necessary upload directories."""
        directories = [
            self.base_upload_dir,
            self.base_upload_dir / 'avatars',
            self.base_upload_dir / 'attachments',
            self.base_upload_dir / 'documents',
            self.base_upload_dir / 'images',
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _validate_file(
        self,
        file: UploadFile,
        allowed_types: Optional[set] = None
    ) -> None:
        """Validate file size and type."""
        # Check file size (read first chunk to verify it's not empty)
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning
        
        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File is empty"
            )
        
        if file_size > self.max_file_size:
            max_mb = self.max_file_size / (1024 * 1024)
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum allowed size of {max_mb}MB"
            )
        
        # Check file extension
        if allowed_types:
            file_ext = Path(file.filename or '').suffix.lower()
            if file_ext not in allowed_types:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File type {file_ext} not allowed. Allowed types: {allowed_types}"
                )
    
    def _generate_unique_filename(self, original_filename: str) -> str:
        """Generate a unique filename while preserving extension."""
        file_ext = Path(original_filename).suffix.lower()
        unique_name = f"{uuid.uuid4()}{file_ext}"
        return unique_name
    
    async def save_file(
        self,
        file: UploadFile,
        subdirectory: str,
        allowed_types: Optional[set] = None
    ) -> dict:
        """
        Save uploaded file to disk.
        
        Returns dict with file info:
        {
            'filename': 'original.jpg',
            'stored_filename': 'uuid.jpg',
            'path': 'uploads/images/uuid.jpg',
            'size': 12345,
            'content_type': 'image/jpeg'
        }
        """
        # Validate file
        self._validate_file(file, allowed_types)
        
        # Generate unique filename
        stored_filename = self._generate_unique_filename(file.filename or 'file')
        
        # Create subdirectory if needed
        target_dir = self.base_upload_dir / subdirectory
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file
        file_path = target_dir / stored_filename
        
        try:
            with open(file_path, 'wb') as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save file: {str(e)}"
            )
        finally:
            await file.close()
        
        # Get file size
        file_size = file_path.stat().st_size
        
        # Determine content type
        content_type = file.content_type or mimetypes.guess_type(file.filename or '')[0] or 'application/octet-stream'
        
        # Return relative path for storage in database
        relative_path = f"{subdirectory}/{stored_filename}"
        
        return {
            'filename': file.filename,
            'stored_filename': stored_filename,
            'path': relative_path,
            'size': file_size,
            'content_type': content_type
        }
    
    async def save_avatar(self, file: UploadFile) -> dict:
        """Save user avatar image."""
        return await self.save_file(
            file,
            subdirectory='avatars',
            allowed_types=self.allowed_extensions['images']
        )
    
    async def save_attachment(self, file: UploadFile) -> dict:
        """Save message attachment."""
        return await self.save_file(
            file,
            subdirectory='attachments',
            allowed_types=self.allowed_extensions['all']
        )
    
    async def save_document_attachment(self, file: UploadFile) -> dict:
        """Save document attachment."""
        return await self.save_file(
            file,
            subdirectory='documents',
            allowed_types=self.allowed_extensions['documents']
        )
    
    async def save_image(self, file: UploadFile) -> dict:
        """Save image file."""
        return await self.save_file(
            file,
            subdirectory='images',
            allowed_types=self.allowed_extensions['images']
        )
    
    def delete_file(self, file_path: str) -> bool:
        """Delete a file from storage."""
        try:
            full_path = self.base_upload_dir / file_path
            if full_path.exists() and full_path.is_file():
                full_path.unlink()
                return True
            return False
        except Exception:
            return False
    
    def get_file_path(self, relative_path: str) -> Path:
        """Get full file path from relative path."""
        return self.base_upload_dir / relative_path
    
    def file_exists(self, relative_path: str) -> bool:
        """Check if file exists."""
        full_path = self.get_file_path(relative_path)
        return full_path.exists() and full_path.is_file()


# Global file storage service instance
file_storage = FileStorageService()
