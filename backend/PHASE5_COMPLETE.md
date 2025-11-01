# Phase 5: File Uploads & Media Management - COMPLETE ✅

## Overview
Phase 5 adds complete file upload and media management functionality to the collaboration platform. Users can now upload attachments to messages, set profile avatars, and manage files securely.

## Features Implemented

### 1. File Storage Service
**Location**: `app/services/file_storage.py`

A comprehensive file storage service that handles:
- **File Validation**: Size limits (10MB), extension whitelist, empty file detection
- **Unique Filename Generation**: UUID-based filenames preserving original extensions
- **Directory Management**: Automatic creation of organized subdirectories
- **Multiple Upload Types**: Specialized methods for different file types

**Key Methods**:
```python
# Save different types of files
save_avatar(file)              # For user avatars (images only)
save_attachment(file)          # For message attachments (all types)
save_document_attachment(file) # For document files
save_image(file)              # For image uploads

# File utilities
delete_file(path)             # Remove file from disk
file_exists(path)             # Check file existence
get_file_path(path)           # Get absolute file path
```

**Directory Structure**:
```
uploads/
├── avatars/          # User profile pictures
├── attachments/      # Message attachments
├── documents/        # Document files
└── images/          # General images
```

### 2. Database Model
**Location**: `app/models/attachment.py`

New `Attachment` model tracks file metadata:

**Fields**:
- `id`: UUID primary key
- `filename`: Original filename from user
- `stored_filename`: UUID-based filename on disk
- `file_path`: Relative path from uploads directory
- `file_size`: Size in bytes
- `content_type`: MIME type (e.g., "image/png", "application/pdf")
- `message_id`: Foreign key to message (CASCADE delete)
- `uploaded_by_id`: Foreign key to user who uploaded

**Relationships**:
- `message`: Link to parent message
- `uploader`: Link to user who uploaded

**Cascade Behavior**:
- When a message is deleted, all attachments are automatically deleted
- Physical files are also removed from disk

### 3. Pydantic Schemas
**Location**: `app/schemas/attachment.py`

**Schemas**:
- `AttachmentBase`: Common fields (filename, content_type, file_size)
- `AttachmentCreate`: For creating database records
- `AttachmentRead`: For API responses with full metadata
- `AttachmentUploadResponse`: Response after successful upload
- `FileUploadInfo`: Temporary file information before DB creation

### 4. API Endpoints
**Location**: `app/api/endpoints/files.py`

#### File Upload
```http
POST /api/files/upload
Content-Type: multipart/form-data

Parameters:
- file: The file to upload (required)
- message_id: Optional message ID to attach to

Response:
{
  "attachment": {
    "id": "uuid",
    "filename": "document.pdf",
    "stored_filename": "uuid.pdf",
    "file_path": "attachments/uuid.pdf",
    "file_size": 123456,
    "content_type": "application/pdf",
    "message_id": "msg-uuid",
    "uploaded_by_id": "user-uuid",
    "created_at": "2024-01-01T00:00:00Z"
  },
  "download_url": "/api/files/download/uuid.pdf"
}
```

**Features**:
- Validates file size and type
- Creates database record
- Returns download URL
- Cleans up file if database operation fails

#### File Download
```http
GET /api/files/download/{stored_filename}
Authorization: Bearer <token>

Response: File download with original filename
```

**Features**:
- Validates file exists in database
- Checks physical file exists
- Returns file with original filename
- Proper content-type headers

#### Delete Attachment
```http
DELETE /api/files/{attachment_id}
Authorization: Bearer <token>

Response:
{
  "message": "Attachment deleted successfully"
}
```

**Permissions**:
- Uploader can delete their attachment
- Message sender can delete attachments on their message
- Returns 403 if not authorized

#### Get Message Attachments
```http
GET /api/files/message/{message_id}
Authorization: Bearer <token>

Response: [
  {
    "id": "uuid",
    "filename": "image.jpg",
    "content_type": "image/jpeg",
    "file_size": 50000,
    "stored_filename": "uuid.jpg",
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

#### Avatar Upload
```http
POST /api/files/avatar
Content-Type: multipart/form-data

Parameters:
- file: Image file (PNG, JPG, GIF, WebP)

Response:
{
  "message": "Avatar uploaded successfully",
  "avatar_url": "/api/files/avatars/uuid.png"
}
```

**Features**:
- Validates file is an image
- Updates user's avatar_url field
- Overwrites previous avatar (optional: delete old file)

#### Get Avatar
```http
GET /api/files/avatars/{filename}

Response: Avatar image file
```

**Note**: This endpoint is public (no auth) for displaying avatars.

### 5. User Model Updates
**Location**: `app/models/user.py`

Added `avatar_url` field:
```python
avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
```

Updated user schema to include avatar:
```python
class UserRead(UserBase):
    avatar_url: Optional[str] = None
```

### 6. Message Model Updates
**Location**: `app/models/message.py`

Added `attachments` relationship:
```python
attachments: Mapped[List["Attachment"]] = relationship(
    "Attachment", back_populates="message", cascade="all, delete-orphan"
)
```

Updated message schema to include attachments:
```python
class MessageRead(MessageBase):
    attachments: List[AttachmentRead] = []
```

### 7. Static File Serving
**Location**: `main.py`

**Configuration**:
- Mounted `/uploads` route with StaticFiles
- Automatic directory creation on startup
- CORS configured for file access

**Startup Tasks**:
```python
# Create upload directories on app startup
uploads/
├── avatars/
├── attachments/
├── documents/
└── images/
```

## Configuration

### Environment Variables
**Location**: `app/core/config.py`

```python
UPLOAD_DIR: str = "uploads"              # Base upload directory
MAX_FILE_SIZE: int = 10 * 1024 * 1024   # 10MB max file size
```

### Allowed File Types
**Images**: .png, .jpg, .jpeg, .gif, .webp
**Documents**: .pdf, .doc, .docx, .txt, .md
**All Types**: Images + documents + video/audio extensions

## Security Features

### 1. File Validation
- Maximum file size limit (10MB)
- Extension whitelist (prevents .exe, .sh, etc.)
- Empty file detection
- MIME type validation

### 2. Authentication
- All upload endpoints require JWT authentication
- User ID tracked for all uploads
- Permission checks on deletion

### 3. Authorization
- Users can only delete their own attachments
- Message senders can delete attachments on their messages
- No direct file system access

### 4. File Storage Security
- UUID-based filenames prevent guessing
- Files stored outside web root
- Served through FastAPI (not direct web server access)
- Original filenames preserved in database only

## Frontend Integration

### Upload File to Message
```typescript
const uploadFile = async (file: File, messageId?: string) => {
  const formData = new FormData();
  formData.append('file', file);
  if (messageId) {
    formData.append('message_id', messageId);
  }

  const response = await fetch('/api/files/upload', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    },
    body: formData
  });

  const data = await response.json();
  return data; // { attachment, download_url }
};
```

### Download File
```typescript
const downloadFile = (storedFilename: string) => {
  return `/api/files/download/${storedFilename}`;
};

// In component
<a href={downloadFile(attachment.stored_filename)} download>
  {attachment.filename}
</a>
```

### Upload Avatar
```typescript
const uploadAvatar = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch('/api/files/avatar', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    },
    body: formData
  });

  const data = await response.json();
  return data.avatar_url;
};
```

### Display Avatar
```typescript
const Avatar = ({ user }) => {
  const avatarUrl = user.avatar_url || '/default-avatar.png';
  return <img src={avatarUrl} alt={user.username} />;
};
```

### Delete Attachment
```typescript
const deleteAttachment = async (attachmentId: string) => {
  await fetch(`/api/files/${attachmentId}`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
};
```

### Get Message Attachments
```typescript
const getMessageAttachments = async (messageId: string) => {
  const response = await fetch(`/api/files/message/${messageId}`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  return await response.json(); // Array of attachments
};
```

### File Upload UI Example
```typescript
const FileUploadComponent = ({ messageId }) => {
  const [uploading, setUploading] = useState(false);

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    try {
      const result = await uploadFile(file, messageId);
      console.log('Upload success:', result);
      // Update UI with new attachment
    } catch (error) {
      console.error('Upload failed:', error);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div>
      <input
        type="file"
        onChange={handleFileSelect}
        disabled={uploading}
      />
      {uploading && <p>Uploading...</p>}
    </div>
  );
};
```

## Database Migrations

After implementing Phase 5, run migrations:

```bash
# Create migration
alembic revision --autogenerate -m "Add file upload support"

# Apply migration
alembic upgrade head
```

**Changes in migration**:
- Create `attachments` table
- Add `avatar_url` column to `users` table
- Add foreign key constraints
- Add cascade delete rules

## Error Handling

### File Too Large
```json
{
  "detail": "File size exceeds maximum allowed (10MB)"
}
```

### Invalid File Type
```json
{
  "detail": "File type not allowed. Allowed types: .png, .jpg, .pdf, ..."
}
```

### File Not Found
```json
{
  "detail": "File not found"
}
```

### Unauthorized Deletion
```json
{
  "detail": "Not authorized to delete this attachment"
}
```

### Empty File
```json
{
  "detail": "File is empty"
}
```

## Testing

### Manual Testing with cURL

**Upload File**:
```bash
curl -X POST http://localhost:8000/api/files/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@document.pdf" \
  -F "message_id=msg-123"
```

**Download File**:
```bash
curl -X GET http://localhost:8000/api/files/download/uuid.pdf \
  -H "Authorization: Bearer $TOKEN" \
  -O
```

**Upload Avatar**:
```bash
curl -X POST http://localhost:8000/api/files/avatar \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@avatar.png"
```

**Delete Attachment**:
```bash
curl -X DELETE http://localhost:8000/api/files/att-uuid \
  -H "Authorization: Bearer $TOKEN"
```

### Python Test Script
```python
import requests
from pathlib import Path

BASE_URL = "http://localhost:8000"
TOKEN = "your-jwt-token"

headers = {"Authorization": f"Bearer {TOKEN}"}

# Upload file
with open("test.pdf", "rb") as f:
    files = {"file": f}
    data = {"message_id": "msg-123"}
    response = requests.post(
        f"{BASE_URL}/api/files/upload",
        headers=headers,
        files=files,
        data=data
    )
    print(response.json())

# Download file
response = requests.get(
    f"{BASE_URL}/api/files/download/uuid.pdf",
    headers=headers
)
with open("downloaded.pdf", "wb") as f:
    f.write(response.content)

# Upload avatar
with open("avatar.png", "rb") as f:
    files = {"file": f}
    response = requests.post(
        f"{BASE_URL}/api/files/avatar",
        headers=headers,
        files=files
    )
    print(response.json())
```

## Performance Considerations

### File Size Limits
- Default: 10MB max
- Adjustable via `MAX_FILE_SIZE` config
- Consider CDN for larger files in production

### Storage Strategy
- Current: Local disk storage
- Production: Consider S3/MinIO for scalability
- Add file cleanup job for orphaned files

### Caching
- Static file serving can be cached
- Add cache headers for avatars
- Consider CDN for frequent downloads

### Optimization Tips
1. **Compress images** before storing
2. **Generate thumbnails** for image previews
3. **Use background tasks** for large file processing
4. **Implement chunked uploads** for large files
5. **Add virus scanning** for production

## Future Enhancements

### Planned Features
1. **Image Thumbnails**: Generate thumbnails for image previews
2. **Video Processing**: Transcode videos, generate previews
3. **File Previews**: In-browser preview for PDFs, images
4. **Drag & Drop**: Enhanced upload UI with drag-drop
5. **Progress Tracking**: Upload progress bars
6. **Batch Uploads**: Upload multiple files at once
7. **File Versioning**: Keep history of document changes
8. **Virus Scanning**: Integrate ClamAV or similar
9. **CDN Integration**: CloudFront, Cloudflare, etc.
10. **S3 Storage**: Replace local storage with object storage

### Production Recommendations
1. Use object storage (S3, MinIO, Google Cloud Storage)
2. Implement CDN for file delivery
3. Add virus scanning for uploads
4. Set up automated backups
5. Monitor storage usage
6. Implement file cleanup jobs
7. Add rate limiting for uploads
8. Enable file compression
9. Implement image optimization
10. Add upload quotas per user

## API Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/files/upload` | POST | Upload file and create attachment |
| `/api/files/download/{filename}` | GET | Download file by stored filename |
| `/api/files/{attachment_id}` | DELETE | Delete attachment and file |
| `/api/files/message/{message_id}` | GET | Get all attachments for message |
| `/api/files/avatar` | POST | Upload user avatar |
| `/api/files/avatars/{filename}` | GET | Get avatar image |

## Files Created/Modified

### New Files
1. `app/services/file_storage.py` - File storage service
2. `app/models/attachment.py` - Attachment model
3. `app/schemas/attachment.py` - Attachment schemas
4. `app/api/endpoints/files.py` - File endpoints
5. `backend/PHASE5_COMPLETE.md` - This documentation

### Modified Files
1. `app/models/user.py` - Added avatar_url field
2. `app/models/message.py` - Added attachments relationship
3. `app/schemas/user.py` - Added avatar_url to UserRead
4. `app/schemas/message.py` - Added attachments to MessageRead
5. `app/core/config.py` - Added UPLOAD_DIR and MAX_FILE_SIZE
6. `app/models/__init__.py` - Export Attachment model
7. `app/schemas/__init__.py` - Export attachment schemas
8. `app/api/endpoints/__init__.py` - Export files router
9. `main.py` - Added files router and static file serving

## Completion Status

✅ File storage service with validation
✅ Attachment database model
✅ File upload endpoint
✅ File download endpoint
✅ File deletion endpoint
✅ Avatar upload endpoint
✅ Message attachments relationship
✅ User avatar support
✅ Static file serving
✅ Directory structure setup
✅ Comprehensive documentation

**Phase 5 is now COMPLETE!** 🎉

The platform now supports full file upload and media management functionality, ready for frontend integration.
