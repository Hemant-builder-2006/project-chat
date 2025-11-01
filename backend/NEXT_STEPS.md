# Next Steps - Getting Started Guide

## 🎉 Backend Complete!
All 5 development phases are now complete with 56+ API endpoints, file upload support, real-time WebSocket communication, and comprehensive documentation.

## Quick Start

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Setup Database
```bash
# Install PostgreSQL if not already installed
# Windows: Download from https://www.postgresql.org/download/windows/
# macOS: brew install postgresql
# Linux: sudo apt-get install postgresql

# Create database
createdb collaboration_db

# Or using psql
psql -U postgres
CREATE DATABASE collaboration_db;
\q
```

### 3. Configure Environment
```bash
# Copy example environment file
copy .env.example .env    # Windows
# cp .env.example .env    # Linux/Mac

# Edit .env file with your settings:
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/collaboration_db
JWT_SECRET_KEY=your-super-secret-key-change-this-in-production
```

### 4. Run the Server
```bash
# Development mode with auto-reload
python main.py

# Or with uvicorn directly
uvicorn main:app --reload
```

### 5. Test the API
```bash
# Open your browser to:
http://localhost:8000/docs

# Try these endpoints:
# 1. POST /api/auth/register - Create an account
# 2. POST /api/auth/login - Get JWT token
# 3. Use "Authorize" button in Swagger UI to add token
# 4. Try other endpoints!
```

## Testing File Uploads

### Upload a File
```bash
# Register and login first to get token
curl -X POST http://localhost:8000/api/files/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@test.pdf"
```

### Upload Avatar
```bash
curl -X POST http://localhost:8000/api/files/avatar \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@avatar.jpg"
```

## Frontend Integration

### 1. Update Frontend API Base URL
Edit `frontend/src/services/api.ts`:
```typescript
const API_BASE_URL = 'http://localhost:8000';
```

### 2. Install Frontend Dependencies
```bash
cd frontend
npm install
```

### 3. Run Frontend
```bash
npm run dev
```

### 4. Open Frontend
```
http://localhost:5173
```

## What You Can Do Now

### ✅ Available Features
1. **User Authentication**
   - Register new users
   - Login with JWT tokens
   - Protected routes

2. **Group Management**
   - Create workspaces/servers
   - Invite members
   - Role-based permissions (owner, admin, member)

3. **Channel System**
   - 5 channel types: CHAT, VOICE, TODO, DOC, KANBAN
   - Create, edit, delete channels
   - Channel-specific features

4. **Real-time Chat**
   - Send/receive messages via WebSocket
   - Threaded conversations (replies)
   - Emoji reactions
   - Message editing and deletion
   - Full-text search
   - **File attachments** 📎

5. **TODO Lists**
   - Create tasks in TODO channels
   - Assign to team members
   - Mark complete/incomplete
   - Drag-drop reordering

6. **Collaborative Documents**
   - Rich text editing (one doc per DOC channel)
   - Version tracking
   - Last editor info
   - Auto-save

7. **Kanban Boards**
   - Create columns and cards
   - Drag-drop cards between columns
   - Reorder columns and cards
   - Full project management

8. **Voice/Video Calls**
   - WebRTC signaling via WebSocket
   - Voice channels
   - Video calls (peer-to-peer)

9. **File Uploads** 📁
   - Upload attachments to messages
   - User profile avatars
   - File download
   - Permission-based deletion
   - 10MB file size limit

## Directory Structure

```
project/
├── backend/                    # FastAPI backend (COMPLETE ✅)
│   ├── app/
│   │   ├── api/endpoints/     # 56+ API endpoints
│   │   ├── models/            # 11 database models
│   │   ├── schemas/           # 30+ Pydantic schemas
│   │   ├── services/          # WebSocket & file storage
│   │   └── core/              # Config & security
│   ├── uploads/               # File storage directory
│   ├── main.py                # App entry point
│   ├── requirements.txt       # Python dependencies
│   └── [Documentation files]
│
└── frontend/                   # React + TypeScript (COMPLETE ✅)
    ├── src/
    │   ├── components/        # UI components
    │   ├── pages/            # Login, Chat pages
    │   ├── contexts/         # Auth, WebRTC
    │   ├── hooks/            # Custom hooks
    │   ├── services/         # API client
    │   └── types/            # TypeScript types
    ├── package.json
    └── vite.config.ts
```

## Common Issues & Solutions

### Database Connection Error
```
Error: connection to server failed
```
**Solution**: Ensure PostgreSQL is running and DATABASE_URL is correct in `.env`

### Import Errors
```
ModuleNotFoundError: No module named 'fastapi'
```
**Solution**: Install dependencies with `pip install -r requirements.txt`

### CORS Errors in Frontend
```
Access-Control-Allow-Origin blocked
```
**Solution**: Check CORS_ORIGINS in `.env` includes your frontend URL

### File Upload 413 Error
```
413 Request Entity Too Large
```
**Solution**: File exceeds 10MB limit. Increase MAX_FILE_SIZE in config or compress file

### WebSocket Connection Failed
```
WebSocket connection failed
```
**Solution**: Ensure backend is running and WebSocket endpoint is correct

## Development Workflow

### 1. Start Backend
```bash
cd backend
python main.py
```

### 2. Start Frontend
```bash
cd frontend
npm run dev
```

### 3. Make Changes
- Backend: Edit Python files, server auto-reloads
- Frontend: Edit React files, Vite auto-reloads
- Database: Create migration with Alembic

### 4. Test Changes
- Backend: Use Swagger UI at http://localhost:8000/docs
- Frontend: Test in browser at http://localhost:5173
- API: Use cURL or Postman

### 5. Check Logs
- Backend: Console output shows requests and errors
- Frontend: Browser console for React errors
- Database: Check PostgreSQL logs if needed

## Documentation Files

### Backend Documentation
1. **SETUP.md** - Installation and setup guide
2. **API_REFERENCE.md** - Complete API documentation (56+ endpoints)
3. **PHASE2_COMPLETE.md** - Auth & Core APIs
4. **PHASE3_COMPLETE.md** - WebSocket & Real-time
5. **PHASE4_COMPLETE.md** - Productivity APIs (Messages, Tasks, Docs, Kanban)
6. **PHASE5_COMPLETE.md** - File Upload & Media (NEW! 📁)
7. **BACKEND_SUMMARY.md** - Complete backend overview
8. **FRONTEND_INTEGRATION.md** - Frontend integration guide
9. **FRONTEND_WS_INTEGRATION.md** - WebSocket integration

### Frontend Documentation
1. **frontend/README.md** - Frontend overview

## Useful Commands

### Backend
```bash
# Run server
python main.py

# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Run tests
python test_api.py
python test_websocket.py
```

### Frontend
```bash
# Install dependencies
npm install

# Run dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Type check
npm run type-check
```

### Database
```bash
# Connect to database
psql -U postgres -d collaboration_db

# List tables
\dt

# Describe table
\d users

# Run query
SELECT * FROM users;

# Exit
\q
```

## Testing the Platform

### 1. Create Two Users
- Register user1 and user2
- Login with each to get tokens

### 2. Create a Group
- User1 creates a group
- User1 invites user2

### 3. Create Channels
- Create CHAT channel for messaging
- Create TODO channel for tasks
- Create DOC channel for documents
- Create KANBAN channel for project board
- Create VOICE channel for calls

### 4. Test Features
- **Chat**: Send messages, react, reply, **upload files** 📎
- **TODO**: Create tasks, assign, complete
- **Document**: Edit document, save versions
- **Kanban**: Create columns and cards, drag-drop
- **Voice**: Initiate call, test WebRTC

### 5. Test File Uploads (NEW!)
- Upload avatar in user settings
- Attach files to messages
- Download attachments
- Delete attachments

## Production Deployment

When ready for production:

### 1. Update Configuration
- Change JWT_SECRET_KEY to strong random value
- Use production database URL
- Set appropriate CORS_ORIGINS
- Configure file storage (S3/MinIO recommended)

### 2. Database Migration
- Export development database
- Import to production database
- Run migrations: `alembic upgrade head`

### 3. Deploy Backend
- Use Docker or traditional hosting
- Configure reverse proxy (Nginx)
- Enable HTTPS with SSL certificate
- Set up monitoring and logging

### 4. Deploy Frontend
- Build: `npm run build`
- Upload dist/ folder to hosting
- Configure environment variables
- Set up CDN for static assets

### 5. Configure File Storage
- Consider S3/MinIO instead of local storage
- Set up CDN for file delivery
- Implement backup strategy
- Configure file retention policies

## Need Help?

### Documentation
- **Swagger UI**: http://localhost:8000/docs (interactive API testing)
- **ReDoc**: http://localhost:8000/redoc (API reference)
- **Phase Docs**: Check PHASE*_COMPLETE.md files for detailed guides

### Common Tasks
- **Add new endpoint**: See existing endpoint files in `app/api/endpoints/`
- **Add database field**: Edit model, create migration with Alembic
- **Add WebSocket event**: Edit `app/api/endpoints/websocket.py`
- **Change file upload settings**: Edit `app/core/config.py`

### Troubleshooting
1. Check server console for backend errors
2. Check browser console for frontend errors
3. Check PostgreSQL is running: `pg_isready`
4. Verify `.env` file exists and is configured
5. Ensure all dependencies installed

## What's Next?

### Optional Enhancements
1. **Email Notifications**: Send email for mentions, invites
2. **Search**: Add Elasticsearch for better search
3. **Analytics**: Track user activity and usage
4. **Mobile App**: React Native or Flutter app
5. **Integrations**: Slack, Discord, GitHub webhooks
6. **Themes**: Dark mode, custom themes
7. **Localization**: Multi-language support
8. **Admin Panel**: User management dashboard
9. **File Previews**: Preview PDFs, images in browser
10. **Video Processing**: Transcode videos, generate thumbnails

### Production Checklist
- [ ] Strong JWT secret key
- [ ] Production database with backups
- [ ] HTTPS enabled
- [ ] Rate limiting configured
- [ ] Monitoring and alerting setup
- [ ] Logging centralized
- [ ] Error tracking (Sentry)
- [ ] CDN for static files
- [ ] Object storage (S3) for uploads
- [ ] Database connection pooling
- [ ] Caching layer (Redis)
- [ ] Load balancer setup
- [ ] Auto-scaling configured
- [ ] Backup and disaster recovery plan

---

**🎉 Congratulations!** Your full-stack collaboration platform is ready to use!

Start the backend and frontend, create an account, and explore all the features. Happy coding! 🚀
