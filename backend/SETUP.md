# Backend Setup Guide

## Prerequisites

- Python 3.10 or higher
- PostgreSQL 14 or higher
- pip (Python package manager)

## Installation Steps

### 1. Set up PostgreSQL Database

```bash
# Create database (using psql or pgAdmin)
createdb chatapp

# Or via psql:
psql -U postgres
CREATE DATABASE chatapp;
\q
```

### 2. Create Python Virtual Environment

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the backend directory:

```env
# Database Configuration
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/chatapp

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-key-change-this-in-production-min-32-chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Application
APP_NAME=ChatApp API
APP_VERSION=1.0.0
DEBUG=True
```

**Important:** Change the `JWT_SECRET_KEY` to a strong random string in production!

### 5. Initialize Database

The database tables will be created automatically when you start the server.

Alternatively, you can use Alembic for migrations:

```bash
# Initialize alembic (if not already done)
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial migration"

# Apply migration
alembic upgrade head
```

### 6. Run the Server

```bash
# Development mode (with auto-reload)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or use the built-in runner:
python main.py
```

The API will be available at: `http://localhost:8000`

## API Documentation

Once the server is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Testing the API

### 1. Health Check

```bash
curl http://localhost:8000/health
```

### 2. Register a User

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecurePassword123!",
    "display_name": "Test User"
  }'
```

### 3. Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "SecurePassword123!"
  }'
```

Response will include `access_token` and `refresh_token`.

### 4. Create a Group (Authenticated)

```bash
curl -X POST http://localhost:8000/api/groups \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "name": "My First Group",
    "description": "A test group"
  }'
```

### 5. Create a Channel

```bash
curl -X POST http://localhost:8000/api/channels/groups/GROUP_ID/channels \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "name": "general",
    "type": "TEXT",
    "description": "General discussion"
  }'
```

## Available Channel Types

- `TEXT` - Text chat channel
- `VOICE` - Voice channel
- `VIDEO` - Video channel
- `TODO` - Todo list
- `DOC` - Document editor
- `KANBAN` - Kanban board

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get tokens
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/logout` - Logout (client-side)

### Groups
- `GET /api/groups` - List user's groups
- `POST /api/groups` - Create group
- `GET /api/groups/{id}` - Get group details
- `PUT /api/groups/{id}` - Update group (admin/owner)
- `DELETE /api/groups/{id}` - Delete group (owner only)

### Channels
- `GET /api/channels/groups/{group_id}/channels` - List channels
- `POST /api/channels/groups/{group_id}/channels` - Create channel (admin/owner)
- `GET /api/channels/{id}` - Get channel details
- `PUT /api/channels/{id}` - Update channel (admin/owner)
- `DELETE /api/channels/{id}` - Delete channel (admin/owner)

### Memberships
- `GET /api/memberships/groups/{group_id}/members` - List members
- `POST /api/memberships/groups/{group_id}/members` - Add member (admin/owner)
- `PUT /api/memberships/groups/{group_id}/members/{user_id}` - Update role (owner)
- `DELETE /api/memberships/groups/{group_id}/members/{user_id}` - Remove member

## Troubleshooting

### Database Connection Error
- Ensure PostgreSQL is running
- Check DATABASE_URL in .env file
- Verify database exists

### Import Errors
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt` again

### Port Already in Use
```bash
# Change port in main.py or use different port
uvicorn main:app --reload --port 8001
```

## Next Steps

After Phase 2 is working:
- **Phase 3:** WebSocket layer for real-time messaging
- **Phase 4:** Productivity APIs (Messages, Tasks, Documents, Kanban)
- **Phase 5:** Deployment configuration
- **Phase 6:** AI integration
