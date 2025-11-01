# Collaboration Workspace Backend

Backend API for a self-hosted, real-time collaboration workspace with multi-group support, integrated communication, productivity tools, and AI capabilities.

## Tech Stack

- **FastAPI**: Modern async web framework
- **SQLAlchemy (async)**: Database ORM with PostgreSQL
- **Pydantic**: Data validation
- **JWT**: Authentication
- **WebSockets**: Real-time communication
- **WebRTC**: Voice/video calling (signaling)
- **Redis**: Caching and pub/sub
- **Ollama**: Local LLM integration
- **ChromaDB**: Vector database for RAG
- **Docker**: Containerization

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── endpoints/          # API route handlers
│   ├── core/                   # Core utilities (config, security)
│   ├── db/                     # Database configuration
│   ├── models/                 # SQLAlchemy models
│   ├── schemas/                # Pydantic schemas
│   └── services/               # Business logic
├── main.py                     # FastAPI app entry point
├── requirements.txt            # Python dependencies
└── .env.example               # Environment variables template
```

## Setup

### 1. Create Virtual Environment

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 4. Initialize Database

```bash
# Create PostgreSQL database
createdb collaboration_workspace

# Run migrations (after setting up Alembic)
alembic upgrade head
```

### 5. Run Development Server

```bash
# From backend directory
python main.py

# Or with uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Features

### Phase 1: Foundation ✅
- Multi-group data models
- User authentication
- Database configuration
- Pydantic schemas

### Phase 2: Authentication & APIs (Next)
- JWT authentication
- Group management
- Channel management
- Permission system

### Phase 3: Real-time (Planned)
- WebSocket gateway
- Chat messaging
- WebRTC signaling

### Phase 4: Productivity (Planned)
- Todo lists
- Document editing
- Kanban boards

### Phase 5: Deployment (Planned)
- Docker containers
- SQLAdmin panel
- Nginx configuration

### Phase 6: AI Integration (Planned)
- Ollama LLM
- RAG with ChromaDB
- AI search & summarization

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Development

### Code Style

Follow PEP 8 and use type hints throughout the codebase.

### Testing

```bash
pytest
```

## License

[Your License Here]
