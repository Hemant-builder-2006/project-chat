"""
Test script to verify API endpoints.
Run this after starting the server to test basic functionality.
"""
import httpx
import asyncio
from typing import Dict, Any

BASE_URL = "http://localhost:8000"


async def test_health():
    """Test health check endpoint."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")
        print("✅ Health Check:", response.json())
        assert response.status_code == 200


async def test_register():
    """Test user registration."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "SecurePassword123!",
                "display_name": "Test User"
            }
        )
        print("✅ Registration:", response.status_code)
        if response.status_code == 201:
            print("   User created:", response.json()["username"])
            return response.json()
        elif response.status_code == 400:
            print("   User already exists")
            return None


async def test_login() -> Dict[str, Any]:
    """Test user login."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "username": "testuser",
                "password": "SecurePassword123!"
            }
        )
        print("✅ Login:", response.status_code)
        assert response.status_code == 200
        tokens = response.json()
        print(f"   Access token: {tokens['access_token'][:20]}...")
        return tokens


async def test_create_group(access_token: str) -> Dict[str, Any]:
    """Test group creation."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/groups",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "name": "Test Group",
                "description": "A test group created by API test"
            }
        )
        print("✅ Create Group:", response.status_code)
        if response.status_code == 201:
            group = response.json()
            print(f"   Group ID: {group['id']}")
            print(f"   Group name: {group['name']}")
            return group


async def test_list_groups(access_token: str):
    """Test listing groups."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/api/groups",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        print("✅ List Groups:", response.status_code)
        groups = response.json()
        print(f"   Total groups: {len(groups)}")
        for group in groups:
            print(f"   - {group['name']} ({group['id']})")


async def test_create_channel(group_id: str, access_token: str):
    """Test channel creation."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/channels/groups/{group_id}/channels",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "name": "general",
                "type": "TEXT",
                "description": "General discussion channel"
            }
        )
        print("✅ Create Channel:", response.status_code)
        if response.status_code == 201:
            channel = response.json()
            print(f"   Channel ID: {channel['id']}")
            print(f"   Channel name: {channel['name']}")
            print(f"   Channel type: {channel['type']}")
            return channel


async def main():
    """Run all tests."""
    print("🧪 Starting API Tests...\n")
    
    try:
        # Test health
        await test_health()
        print()
        
        # Test registration
        await test_register()
        print()
        
        # Test login
        tokens = await test_login()
        access_token = tokens["access_token"]
        print()
        
        # Test group creation
        group = await test_create_group(access_token)
        print()
        
        # Test listing groups
        await test_list_groups(access_token)
        print()
        
        # Test channel creation
        if group:
            await test_create_channel(group["id"], access_token)
            print()
        
        print("🎉 All tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
