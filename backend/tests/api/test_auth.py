"""Tests for authentication endpoints."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    """Test user registration endpoint."""
    response = await client.post(
        "/api/auth/register",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "securepass123"
        }
    )
    assert response.status_code == 200
    
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    assert "id" in data
    assert "hashed_password" not in data  # Should not expose password


@pytest.mark.asyncio
async def test_register_duplicate_username(client: AsyncClient, test_user: User):
    """Test that registering with duplicate username fails."""
    response = await client.post(
        "/api/auth/register",
        json={
            "username": test_user.username,
            "email": "different@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user: User):
    """Test successful login with correct credentials."""
    response = await client.post(
        "/api/auth/login",
        data={
            "username": "testuser",
            "password": "testpass123"
        }
    )
    assert response.status_code == 200
    
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, test_user: User):
    """Test login fails with wrong password."""
    response = await client.post(
        "/api/auth/login",
        data={
            "username": "testuser",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    """Test login fails with nonexistent user."""
    response = await client.post(
        "/api/auth/login",
        data={
            "username": "nonexistent",
            "password": "password123"
        }
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, test_user: User, auth_headers: dict):
    """Test getting current user information with valid token."""
    response = await client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["username"] == test_user.username
    assert data["email"] == test_user.email
    assert data["id"] == str(test_user.id)


@pytest.mark.asyncio
async def test_get_current_user_no_token(client: AsyncClient):
    """Test that accessing /me without token fails."""
    response = await client.get("/api/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient, test_user: User):
    """Test token refresh endpoint."""
    # First login to get tokens
    login_response = await client.post(
        "/api/auth/login",
        data={
            "username": "testuser",
            "password": "testpass123"
        }
    )
    tokens = login_response.json()
    refresh_token = tokens["refresh_token"]
    
    # Use refresh token to get new access token
    response = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert response.status_code == 200
    
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
