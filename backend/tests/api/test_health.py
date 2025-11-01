"""Tests for health check and basic endpoints."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test the /health endpoint returns 200 OK."""
    response = await client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    """Test the root endpoint returns API information."""
    response = await client.get("/")
    assert response.status_code == 200
    
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert data["docs"] == "/docs"
    assert data["health"] == "/health"


@pytest.mark.asyncio
async def test_docs_accessible(client: AsyncClient):
    """Test that OpenAPI docs are accessible."""
    response = await client.get("/docs")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_openapi_json(client: AsyncClient):
    """Test that OpenAPI JSON schema is accessible."""
    response = await client.get("/openapi.json")
    assert response.status_code == 200
    
    data = response.json()
    assert "openapi" in data
    assert "info" in data
    assert "paths" in data
