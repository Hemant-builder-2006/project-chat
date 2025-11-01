"""
Pytest configuration and fixtures for testing.

Provides:
- Test database with SQLite in-memory
- Isolated test sessions with automatic rollback
- HTTP client with test app
- Authentication helpers
"""
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.core.security import get_password_hash, create_access_token
from app.models.user import User
from main import app


# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """
    Create an event loop for the test session.
    
    This fixture ensures all async tests share the same event loop.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def test_engine():
    """
    Create a test database engine.
    
    Uses SQLite in-memory database for fast, isolated tests.
    StaticPool ensures the same connection is reused.
    """
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,  # Set to True for SQL debug output
        poolclass=StaticPool,
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Drop all tables after test
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture(scope="function")
async def test_db(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Create an isolated database session for each test.
    
    Each test gets a fresh session that automatically rolls back
    all changes, ensuring test isolation.
    """
    # Create session factory
    async_session_maker = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    # Create session
    async with async_session_maker() as session:
        yield session
        await session.rollback()


@pytest.fixture(scope="function")
async def client(test_db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Create an HTTP client for testing the API.
    
    Overrides the database dependency to use the test database.
    """
    # Override database dependency
    async def override_get_db():
        yield test_db
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Create async client
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def test_user(test_db: AsyncSession) -> User:
    """
    Create a test user in the database.
    
    Returns:
        User instance with credentials:
        - username: testuser
        - email: test@example.com
        - password: testpass123
    """
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpass123"),
        is_active=True,
        is_superuser=False,
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user


@pytest.fixture(scope="function")
async def test_superuser(test_db: AsyncSession) -> User:
    """
    Create a test superuser in the database.
    
    Returns:
        Superuser instance with credentials:
        - username: admin
        - email: admin@example.com
        - password: adminpass123
    """
    user = User(
        username="admin",
        email="admin@example.com",
        hashed_password=get_password_hash("adminpass123"),
        is_active=True,
        is_superuser=True,
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user


@pytest.fixture(scope="function")
def auth_headers(test_user: User) -> dict:
    """
    Create authorization headers for test user.
    
    Returns:
        Dict with Authorization header containing valid JWT token
    """
    access_token = create_access_token({"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture(scope="function")
def admin_headers(test_superuser: User) -> dict:
    """
    Create authorization headers for admin user.
    
    Returns:
        Dict with Authorization header containing valid JWT token
    """
    access_token = create_access_token({"sub": str(test_superuser.id)})
    return {"Authorization": f"Bearer {access_token}"}
