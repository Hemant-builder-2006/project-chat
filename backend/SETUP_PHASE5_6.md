# Quick Setup Guide: Phases 5 & 6

## Prerequisites
- Python 3.10+
- PostgreSQL running
- Ollama installed
- ChromaDB running

---

## 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

This will install:
- SQLAdmin for admin panel
- Ollama client for AI
- ChromaDB for vector storage
- Sentence Transformers for embeddings
- LangChain for document processing
- PyPDF2 for PDF extraction

---

## 2. Setup Ollama (AI Models)

### Install Ollama

**Windows**:
```powershell
winget install Ollama.Ollama
```

Or download from: https://ollama.ai/download

**Verify Installation**:
```bash
ollama --version
```

### Pull AI Models

```bash
# Default model (recommended)
ollama pull llama2

# Alternative models
ollama pull mistral    # Better quality
ollama pull phi        # Lightweight
```

### Verify Models
```bash
ollama list
```

---

## 3. Setup ChromaDB (Vector Database)

### Option A: Docker (Recommended)
```bash
docker run -d -p 8000:8000 --name chromadb chromadb/chroma
```

### Option B: Standalone
```bash
# Already installed with requirements.txt
chroma run --host localhost --port 8000
```

### Verify ChromaDB
```bash
curl http://localhost:8000/api/v1/heartbeat
```

---

## 4. Update Environment Variables

Edit `.env` file:

```env
# Existing configuration...

# AI Configuration (ADD THESE)
OLLAMA_HOST=http://localhost:11434
OLLAMA_DEFAULT_MODEL=llama2
OLLAMA_TIMEOUT=120

CHROMA_HOST=localhost
CHROMA_PORT=8000

EMBEDDING_MODEL=all-MiniLM-L6-v2
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

---

## 5. Create Superuser (for Admin Panel)

### Method 1: SQL
```sql
-- Connect to your database
psql -U postgres -d collaboration_workspace

-- Update existing user to superuser
UPDATE users SET is_superuser = true WHERE username = 'your_username';
```

### Method 2: Python Script

Create `create_superuser.py`:

```python
import asyncio
from app.models.user import User
from app.core.security import get_password_hash
from app.db.session import AsyncSessionLocal

async def create_superuser():
    async with AsyncSessionLocal() as session:
        # Check if superuser exists
        from sqlalchemy import select
        result = await session.execute(
            select(User).where(User.username == "admin")
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            print("Admin user already exists")
            return
        
        # Create superuser
        user = User(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("admin123"),
            is_active=True,
            is_superuser=True
        )
        session.add(user)
        await session.commit()
        print("✅ Superuser created: admin / admin123")

if __name__ == "__main__":
    asyncio.run(create_superuser())
```

Run it:
```bash
python create_superuser.py
```

---

## 6. Start the Server

```bash
python main.py
```

Expected output:
```
🚀 Application startup
✅ Database tables created
✅ Upload directories created
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## 7. Test Admin Panel

1. Open browser: http://localhost:8000/admin
2. Login with superuser credentials (admin / admin123)
3. Verify all 11 model views are visible
4. Try viewing Users, Groups, Messages, etc.

---

## 8. Test AI Features

### Health Check
```bash
curl http://localhost:8000/api/ai/health
```

Expected response:
```json
{
  "status": "healthy",
  "services": {
    "ollama": {"status": "healthy", "available": true},
    "chromadb": {"status": "healthy", "available": true}
  }
}
```

### Test AI Chat
```bash
# Get your JWT token first (login via /api/auth/login)
TOKEN="your-jwt-token"

curl -X POST http://localhost:8000/api/ai/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, can you help me?"
  }'
```

### Upload and Search Document
```bash
# Upload a PDF to a channel
curl -X POST "http://localhost:8000/api/ai/upload/CHANNEL_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@document.pdf"

# Search uploaded documents
curl -X POST http://localhost:8000/api/ai/search \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the requirements?",
    "n_results": 5
  }'
```

### Test WebSocket AI Trigger
1. Connect to WebSocket: `ws://localhost:8000/ws?token=YOUR_TOKEN`
2. Send message:
   ```json
   {
     "type": "message",
     "channel_id": "your-channel-id",
     "content": "@AI What is the weather?"
   }
   ```
3. Receive AI response automatically

---

## 9. Verify Everything Works

### Checklist
- [ ] Backend running on port 8000
- [ ] Ollama running on port 11434
- [ ] ChromaDB running on port 8000
- [ ] PostgreSQL database accessible
- [ ] Superuser account created
- [ ] Admin panel accessible at /admin
- [ ] AI health check returns "healthy"
- [ ] Can upload documents
- [ ] Can search documents with AI
- [ ] Can chat with AI
- [ ] @AI trigger works in WebSocket

---

## Troubleshooting

### Ollama Not Found
```bash
# Windows - Add to PATH
$env:Path += ";C:\Users\$env:USERNAME\AppData\Local\Programs\Ollama"

# Or restart terminal after installation
```

### ChromaDB Connection Failed
```bash
# Check if running
docker ps | grep chromadb

# Or check port
netstat -an | findstr :8000

# Restart
docker restart chromadb
```

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Model Download Slow
```bash
# Ollama downloads models from internet
# First pull takes time (3-7GB models)
# Use smaller model: ollama pull phi (1.6GB)
```

### Admin Panel 403 Forbidden
```sql
-- Ensure user has is_superuser flag
SELECT username, is_superuser FROM users;
UPDATE users SET is_superuser = true WHERE username = 'your_username';
```

---

## Performance Tips

### For Development
- Use `phi` model (lightweight, 1.6GB)
- Single ChromaDB instance
- Default embedding model

### For Production
- Use GPU-accelerated Ollama
- Multiple Ollama instances with load balancer
- Persistent ChromaDB with volume mounts
- Larger embedding model for better quality
- Implement caching layer
- Rate limiting on AI endpoints

---

## What's Next?

After setup, you can:

1. **Upload Documents**: Use `/api/ai/upload/{channel_id}` to index PDFs
2. **AI Search**: Query documents with `/api/ai/search`
3. **Summarize Chats**: Use `/api/ai/summarize/{channel_id}`
4. **Chat with AI**: Direct chat with `/api/ai/chat`
5. **WebSocket AI**: Type `@AI question` in any channel
6. **Admin Panel**: Manage all data at `/admin`

---

## Documentation Files

- **PHASE5_6_COMPLETE.md**: Comprehensive documentation (this file's parent)
- **API_REFERENCE.md**: All API endpoints
- **backend.txt**: Original phase prompts
- **NEXT_STEPS.md**: General backend guide

---

## Quick Commands Reference

```bash
# Start services
python main.py                          # Backend
docker run -p 8000:8000 chromadb/chroma  # ChromaDB
ollama serve                            # Ollama (if needed)

# Pull models
ollama pull llama2
ollama pull mistral

# Create superuser
python create_superuser.py

# Test AI
curl http://localhost:8000/api/ai/health

# Access admin
http://localhost:8000/admin
```

---

**Setup Complete!** 🎉🤖

You now have:
- ✅ Admin panel for database management
- ✅ AI-powered document search (RAG)
- ✅ AI chat and summarization
- ✅ WebSocket AI assistant
- ✅ Local AI (privacy-focused)
