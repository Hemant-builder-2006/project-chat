"""
Main FastAPI application entry point.

This file initializes the FastAPI app with:
- CORS middleware for frontend communication
- API routers for different endpoints
- Lifespan events for startup/shutdown tasks
- Error handlers and middleware
- SQLAdmin panel for database management
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from contextlib import asynccontextmanager
import os
import asyncio
from dotenv import load_dotenv

from app.core.config import settings
from app.db.session import create_tables, engine
from app.api.endpoints import auth, groups, channels, memberships, websocket, messages, tasks, documents, kanban, files, ai, webrtc
from app.core.tasks import run_periodic_data_retention, run_periodic_file_cleanup, run_periodic_health_check

load_dotenv()

# Background task handles
background_tasks = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    
    Startup tasks:
    - Initialize database connections
    - Create database tables
    - Create upload directories
    - Start background tasks
    
    Shutdown tasks:
    - Cancel background tasks
    - Close database connections
    - Cleanup resources
    """
    # Startup
    print("🚀 Application startup")
    await create_tables()
    print("✅ Database tables created")
    
    # Create upload directories
    upload_dir = settings.UPLOAD_DIR
    os.makedirs(upload_dir, exist_ok=True)
    os.makedirs(os.path.join(upload_dir, "avatars"), exist_ok=True)
    os.makedirs(os.path.join(upload_dir, "attachments"), exist_ok=True)
    os.makedirs(os.path.join(upload_dir, "documents"), exist_ok=True)
    os.makedirs(os.path.join(upload_dir, "images"), exist_ok=True)
    print("✅ Upload directories created")
    
    # Start background tasks
    print("🔄 Starting background tasks...")
    
    # Data retention cleanup task
    task1 = asyncio.create_task(run_periodic_data_retention())
    background_tasks.append(task1)
    print("  ✓ Data retention task started")
    
    # File cleanup task (optional, controlled by FILE_CLEANUP_ENABLED)
    task2 = asyncio.create_task(run_periodic_file_cleanup())
    background_tasks.append(task2)
    print("  ✓ File cleanup task started")
    
    # Health check task (optional, controlled by HEALTH_CHECK_ENABLED)
    task3 = asyncio.create_task(run_periodic_health_check())
    background_tasks.append(task3)
    print("  ✓ Health check task started")
    
    print("✅ All background tasks started")
    
    yield
    
    # Shutdown
    print("👋 Application shutdown")
    print("🛑 Stopping background tasks...")
    
    # Cancel all background tasks
    for task in background_tasks:
        task.cancel()
    
    # Wait for tasks to complete cancellation
    await asyncio.gather(*background_tasks, return_exceptions=True)
    print("✅ Background tasks stopped")


# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Backend API for self-hosted collaboration platform",
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# Session Middleware (required for SQLAdmin authentication)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.JWT_SECRET_KEY,  # Use same secret as JWT
    session_cookie="admin_session",
    max_age=3600,  # 1 hour session
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy", "version": settings.APP_VERSION}


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
    }


# API Routers
app.include_router(auth.router, prefix="/api")
app.include_router(groups.router, prefix="/api")
app.include_router(channels.router, prefix="/api")
app.include_router(memberships.router, prefix="/api")
app.include_router(messages.router, prefix="/api")
app.include_router(tasks.router, prefix="/api")
app.include_router(documents.router, prefix="/api")
app.include_router(kanban.router, prefix="/api")
app.include_router(files.router, prefix="/api/files", tags=["files"])
app.include_router(ai.router, prefix="/api")
app.include_router(webrtc.router, prefix="/api")
app.include_router(websocket.router)  # WebSocket routes don't need /api prefix

# Mount static files for uploads (after creating directories in lifespan)
if os.path.exists(settings.UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Setup SQLAdmin
from app.admin import setup_admin
admin = setup_admin(app, engine)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload in development
    )
