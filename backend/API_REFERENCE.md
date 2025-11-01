# Complete API Reference

Base URL: `http://localhost:8000`

## Authentication

All endpoints except `/auth/register` and `/auth/login` require JWT authentication.

**Header:**
```
Authorization: Bearer {access_token}
```

---

## Auth Endpoints

### POST /api/auth/register
Register a new user.

**Request:**
```json
{
  "username": "string",
  "email": "email@example.com",
  "password": "string",
  "display_name": "string" // optional
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "username": "string",
  "email": "email",
  "display_name": "string",
  "created_at": "datetime"
}
```

### POST /api/auth/login
Login and get tokens.

**Request:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "jwt_token",
  "refresh_token": "jwt_token",
  "token_type": "bearer"
}
```

### POST /api/auth/refresh
Refresh access token.

**Request:**
```json
{
  "refresh_token": "string"
}
```

**Response:** `200 OK` (same as login)

---

## Groups

### GET /api/groups
List user's groups.

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "name": "string",
    "description": "string",
    "icon_url": "string",
    "owner_id": "uuid",
    "created_at": "datetime"
  }
]
```

### POST /api/groups
Create a new group.

**Request:**
```json
{
  "name": "string",
  "description": "string", // optional
  "icon_url": "string"      // optional
}
```

**Response:** `201 Created` (Group object)

### GET /api/groups/{id}
Get group details.

### PUT /api/groups/{id}
Update group (admin/owner only).

### DELETE /api/groups/{id}
Delete group (owner only).

---

## Channels

### GET /api/channels/groups/{group_id}/channels
List all channels in a group.

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "name": "string",
    "group_id": "uuid",
    "type": "TEXT|VOICE|VIDEO|TODO|DOC|KANBAN",
    "description": "string",
    "created_at": "datetime"
  }
]
```

### POST /api/channels/groups/{group_id}/channels
Create a new channel (admin/owner only).

**Request:**
```json
{
  "name": "string",
  "type": "TEXT|VOICE|VIDEO|TODO|DOC|KANBAN",
  "description": "string" // optional
}
```

**Response:** `201 Created` (Channel object)

### GET /api/channels/{id}
Get channel details.

### PUT /api/channels/{id}
Update channel (admin/owner only).

### DELETE /api/channels/{id}
Delete channel (admin/owner only).

---

## Memberships

### GET /api/memberships/groups/{group_id}/members
List group members.

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "user_id": "uuid",
    "group_id": "uuid",
    "role": "owner|admin|member",
    "joined_at": "datetime"
  }
]
```

### POST /api/memberships/groups/{group_id}/members
Add a member (admin/owner only).

**Request:**
```json
{
  "user_id": "uuid",
  "role": "member|admin" // optional, default: member
}
```

**Response:** `201 Created` (Membership object)

### PUT /api/memberships/groups/{group_id}/members/{user_id}
Update member role (owner only).

**Request:**
```json
{
  "role": "member|admin"
}
```

### DELETE /api/memberships/groups/{group_id}/members/{user_id}
Remove member (admin/owner or self).

---

## Messages

### GET /api/messages/channels/{channel_id}
Get messages from a channel.

**Query Parameters:**
- `skip`: Offset (default: 0)
- `limit`: Max results (default: 50, max: 100)
- `before`: Message ID for pagination

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "content": "string",
    "sender_id": "uuid",
    "sender_username": "string",
    "channel_id": "uuid",
    "parent_message_id": "uuid", // null for top-level
    "is_edited": false,
    "created_at": "datetime",
    "reactions": [
      {
        "id": "uuid",
        "emoji": "👍",
        "user_id": "uuid"
      }
    ]
  }
]
```

### POST /api/messages/channels/{channel_id}
Create a new message.

**Request:**
```json
{
  "content": "string",
  "parent_message_id": "uuid" // optional, for threading
}
```

**Response:** `201 Created` (Message object)

### GET /api/messages/{message_id}
Get a specific message.

### PUT /api/messages/{message_id}
Edit a message (sender only).

**Request:**
```json
{
  "content": "string"
}
```

### DELETE /api/messages/{message_id}
Delete a message (sender or admin).

### POST /api/messages/{message_id}/reactions
Add a reaction.

**Request:**
```json
{
  "emoji": "👍"
}
```

**Response:** `201 Created` (Reaction object)

### DELETE /api/messages/{message_id}/reactions/{emoji}
Remove a reaction.

### GET /api/messages/search/{channel_id}
Search messages.

**Query Parameters:**
- `q`: Search query (required)
- `limit`: Max results (default: 20, max: 100)

**Response:** `200 OK` (Array of Message objects)

---

## Tasks

### GET /api/tasks/channels/{channel_id}
Get all tasks in a TODO channel.

**Query Parameters:**
- `completed`: Filter by completion status (optional)

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "content": "string",
    "is_completed": false,
    "channel_id": "uuid",
    "created_by_id": "uuid",
    "assigned_to_id": "uuid", // nullable
    "position": 0,
    "created_at": "datetime"
  }
]
```

### POST /api/tasks/channels/{channel_id}
Create a new task.

**Request:**
```json
{
  "content": "string",
  "assigned_to_id": "uuid" // optional
}
```

**Response:** `201 Created` (Task object)

### GET /api/tasks/{task_id}
Get a specific task.

### PUT /api/tasks/{task_id}
Update a task.

**Request:**
```json
{
  "content": "string",           // optional
  "is_completed": true,          // optional
  "assigned_to_id": "uuid",      // optional
  "position": 0                  // optional
}
```

### DELETE /api/tasks/{task_id}
Delete a task.

### POST /api/tasks/{task_id}/complete
Toggle task completion.

**Response:** `200 OK` (Updated Task object)

### PUT /api/tasks/channels/{channel_id}/reorder
Reorder tasks.

**Request:** Array of task IDs in new order
```json
["task-id-1", "task-id-2", "task-id-3"]
```

**Response:** `200 OK` (Array of updated Task objects)

---

## Documents

### GET /api/documents/channels/{channel_id}
Get the document for a DOC channel.

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "channel_id": "uuid",
  "content": "string",           // HTML content
  "version": 1,
  "last_edited_by_id": "uuid",
  "last_edited_at": "datetime"
}
```

### PUT /api/documents/channels/{channel_id}
Update the document.

**Request:**
```json
{
  "content": "string"  // HTML content
}
```

**Response:** `200 OK` (Updated DocumentPage object)

### POST /api/documents/channels/{channel_id}/save
Save document (alternative to PUT).

**Request:**
```json
{
  "content": "string"
}
```

**Response:** `200 OK` (DocumentPage object)

---

## Kanban

### GET /api/kanban/channels/{channel_id}/board
Get the entire Kanban board.

**Response:** `200 OK`
```json
{
  "channel_id": "uuid",
  "columns": [
    {
      "id": "uuid",
      "title": "string",
      "channel_id": "uuid",
      "position": 0,
      "cards": [
        {
          "id": "uuid",
          "content": "string",
          "column_id": "uuid",
          "position": 0
        }
      ]
    }
  ]
}
```

### POST /api/kanban/channels/{channel_id}/columns
Create a new column.

**Request:**
```json
{
  "title": "string"
}
```

**Response:** `201 Created` (KanbanColumn object)

### PUT /api/kanban/columns/{column_id}
Update a column.

**Request:**
```json
{
  "title": "string",    // optional
  "position": 0         // optional
}
```

### DELETE /api/kanban/columns/{column_id}
Delete a column (and all its cards).

### POST /api/kanban/columns/{column_id}/cards
Create a new card.

**Request:**
```json
{
  "content": "string"
}
```

**Response:** `201 Created` (KanbanCard object)

### PUT /api/kanban/cards/{card_id}
Update or move a card.

**Request:**
```json
{
  "content": "string",   // optional
  "column_id": "uuid",   // optional, for moving
  "position": 0          // optional
}
```

### DELETE /api/kanban/cards/{card_id}
Delete a card.

### PUT /api/kanban/channels/{channel_id}/columns/reorder
Reorder columns.

**Request:** Array of column IDs
```json
["col-1", "col-2", "col-3"]
```

**Response:** `200 OK` (Array of updated KanbanColumn objects)

### PUT /api/kanban/columns/{column_id}/cards/reorder
Reorder cards within a column.

**Request:** Array of card IDs
```json
["card-1", "card-2", "card-3"]
```

**Response:** `200 OK` (Array of updated KanbanCard objects)

---

## WebSocket

### WS /ws/channel/{channel_id}?token={jwt}
WebSocket endpoint for channel communication.

**Client → Server Messages:**
```json
{ "type": "message", "content": "string" }
{ "type": "typing", "is_typing": true }
{ "type": "webrtc_offer", "target_user_id": "uuid", "data": {...} }
{ "type": "webrtc_answer", "target_user_id": "uuid", "data": {...} }
{ "type": "webrtc_ice_candidate", "target_user_id": "uuid", "data": {...} }
```

**Server → Client Messages:**
```json
{ "type": "online_users", "users": ["uuid"], "channel_id": "uuid" }
{ "type": "user_joined", "user_id": "uuid", "username": "string" }
{ "type": "user_left", "user_id": "uuid", "username": "string" }
{ "type": "message", ...message object... }
{ "type": "typing", "user_id": "uuid", "username": "string", "is_typing": true }
{ "type": "webrtc_*", "from_user_id": "uuid", "data": {...} }
```

### WS /ws/dm/{other_user_id}?token={jwt}
WebSocket endpoint for direct messages.

**Client → Server Messages:**
```json
{ "type": "dm_message", "content": "string" }
{ "type": "dm_typing", "is_typing": true }
{ "type": "webrtc_*", "data": {...} }
```

**Server → Client Messages:**
```json
{ "type": "dm_user_online", "user_id": "uuid", "username": "string" }
{ "type": "dm_user_offline", "user_id": "uuid", "username": "string" }
{ "type": "dm_message", ...message object... }
{ "type": "dm_typing", "user_id": "uuid", "username": "string", "is_typing": true }
{ "type": "webrtc_*", "from_user_id": "uuid", "data": {...} }
```

---

## Error Responses

All endpoints may return these error codes:

### 400 Bad Request
```json
{
  "detail": "Error message"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "Insufficient permissions"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "field"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## File Upload Endpoints

### POST /api/files/upload
Upload a file and create attachment record.

**Headers:**
```
Authorization: Bearer {token}
Content-Type: multipart/form-data
```

**Request:**
```
file: File (required)
message_id: string (optional)
```

**Response:** `200 OK`
```json
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

**Errors:**
- `400`: File too large, invalid type, or empty file
- `500`: Upload failed

### GET /api/files/download/{stored_filename}
Download a file by its stored filename.

**Headers:**
```
Authorization: Bearer {token}
```

**Response:** File download with original filename

**Errors:**
- `404`: File not found in database or on disk

### DELETE /api/files/{attachment_id}
Delete an attachment and its file.

**Headers:**
```
Authorization: Bearer {token}
```

**Response:** `200 OK`
```json
{
  "message": "Attachment deleted successfully"
}
```

**Permissions:**
- Uploader can delete
- Message sender can delete attachments on their message

**Errors:**
- `403`: Not authorized to delete
- `404`: Attachment not found

### GET /api/files/message/{message_id}
Get all attachments for a message.

**Headers:**
```
Authorization: Bearer {token}
```

**Response:** `200 OK`
```json
[
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

### POST /api/files/avatar
Upload user avatar image.

**Headers:**
```
Authorization: Bearer {token}
Content-Type: multipart/form-data
```

**Request:**
```
file: Image File (PNG, JPG, GIF, WebP)
```

**Response:** `200 OK`
```json
{
  "message": "Avatar uploaded successfully",
  "avatar_url": "/api/files/avatars/uuid.png"
}
```

**Errors:**
- `400`: Invalid image format or file too large

### GET /api/files/avatars/{filename}
Get user avatar image (public endpoint).

**Response:** Avatar image file

**Errors:**
- `404`: Avatar not found

---

## File Upload Configuration

**Maximum File Size**: 10MB (configurable via `MAX_FILE_SIZE`)

**Allowed File Types**:
- **Images**: .png, .jpg, .jpeg, .gif, .webp
- **Documents**: .pdf, .doc, .docx, .txt, .md
- **All Types**: Depends on upload endpoint

**Storage Structure**:
```
uploads/
├── avatars/          # User profile pictures
├── attachments/      # Message attachments
├── documents/        # Document files
└── images/          # General images
```

---

## Rate Limiting

Currently no rate limiting. For production, consider:
- 100 requests/minute per user for REST APIs
- 10 messages/second per user for WebSocket
- Use Redis for distributed rate limiting

---

## API Documentation

Interactive API documentation available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
