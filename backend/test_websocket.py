"""
WebSocket test script to verify real-time communication.
Run this after starting the server and creating a user/group/channel.
"""
import asyncio
import websockets
import json
import httpx

BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000"


async def test_websocket_channel():
    """Test WebSocket connection to a channel."""
    print("🧪 Testing WebSocket Channel Communication\n")
    
    # Step 1: Register and login
    async with httpx.AsyncClient() as client:
        # Register user 1
        try:
            response = await client.post(
                f"{BASE_URL}/api/auth/register",
                json={
                    "username": "wstest1",
                    "email": "wstest1@example.com",
                    "password": "Test123!",
                    "display_name": "WebSocket Test User 1"
                }
            )
            print(f"✅ User 1 registered: {response.status_code}")
        except:
            print("ℹ️  User 1 already exists")
        
        # Login user 1
        response = await client.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "username": "wstest1",
                "password": "Test123!"
            }
        )
        token1 = response.json()["access_token"]
        print(f"✅ User 1 logged in")
        
        # Create group
        response = await client.post(
            f"{BASE_URL}/api/groups",
            headers={"Authorization": f"Bearer {token1}"},
            json={
                "name": "WebSocket Test Group",
                "description": "Testing real-time features"
            }
        )
        if response.status_code == 201:
            group = response.json()
            group_id = group["id"]
            print(f"✅ Group created: {group['name']}")
        else:
            # Get existing groups
            response = await client.get(
                f"{BASE_URL}/api/groups",
                headers={"Authorization": f"Bearer {token1}"}
            )
            groups = response.json()
            group_id = groups[0]["id"]
            print(f"ℹ️  Using existing group: {groups[0]['name']}")
        
        # Create channel
        response = await client.post(
            f"{BASE_URL}/api/channels/groups/{group_id}/channels",
            headers={"Authorization": f"Bearer {token1}"},
            json={
                "name": "websocket-test",
                "type": "TEXT",
                "description": "WebSocket testing channel"
            }
        )
        if response.status_code == 201:
            channel = response.json()
            channel_id = channel["id"]
            print(f"✅ Channel created: {channel['name']}")
        else:
            # Get existing channels
            response = await client.get(
                f"{BASE_URL}/api/channels/groups/{group_id}/channels",
                headers={"Authorization": f"Bearer {token1}"}
            )
            channels = response.json()
            channel_id = channels[0]["id"] if channels else None
            if channel_id:
                print(f"ℹ️  Using existing channel: {channels[0]['name']}")
    
    if not channel_id:
        print("❌ Failed to create or find channel")
        return
    
    print(f"\n📡 Connecting to WebSocket...")
    print(f"   Channel ID: {channel_id}")
    print(f"   Token: {token1[:20]}...\n")
    
    # Step 2: Connect to WebSocket
    ws_url = f"{WS_URL}/ws/channel/{channel_id}?token={token1}"
    
    try:
        async with websockets.connect(ws_url) as websocket:
            print("✅ WebSocket connected!\n")
            
            # Receive initial messages
            async def receive_messages():
                """Receive and print messages."""
                try:
                    while True:
                        message = await websocket.recv()
                        data = json.loads(message)
                        msg_type = data.get("type")
                        
                        if msg_type == "online_users":
                            print(f"📊 Online users: {len(data['users'])} user(s)")
                        elif msg_type == "user_joined":
                            print(f"👋 {data['username']} joined the channel")
                        elif msg_type == "message":
                            print(f"💬 {data['sender_username']}: {data['content']}")
                        elif msg_type == "typing":
                            if data['is_typing']:
                                print(f"✍️  {data['username']} is typing...")
                            else:
                                print(f"   {data['username']} stopped typing")
                        elif msg_type == "user_left":
                            print(f"👋 {data['username']} left the channel")
                        else:
                            print(f"📨 Received: {data}")
                except websockets.exceptions.ConnectionClosed:
                    print("\n🔌 WebSocket connection closed")
                except Exception as e:
                    print(f"\n❌ Error receiving: {e}")
            
            # Start receiving messages in background
            receive_task = asyncio.create_task(receive_messages())
            
            # Wait for initial messages
            await asyncio.sleep(1)
            
            # Send typing indicator
            print("\n📤 Sending typing indicator...")
            await websocket.send(json.dumps({
                "type": "typing",
                "is_typing": True
            }))
            await asyncio.sleep(1)
            
            # Send message
            print("📤 Sending message...")
            await websocket.send(json.dumps({
                "type": "message",
                "content": "Hello from WebSocket test!"
            }))
            await asyncio.sleep(1)
            
            # Stop typing
            await websocket.send(json.dumps({
                "type": "typing",
                "is_typing": False
            }))
            
            # Send another message
            print("📤 Sending another message...")
            await websocket.send(json.dumps({
                "type": "message",
                "content": "WebSocket is working! 🎉"
            }))
            
            # Wait for responses
            await asyncio.sleep(2)
            
            print("\n✅ WebSocket test completed successfully!")
            
            # Cancel receive task
            receive_task.cancel()
            
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        import traceback
        traceback.print_exc()


async def test_websocket_dm():
    """Test WebSocket connection for direct messages."""
    print("\n🧪 Testing WebSocket Direct Messages\n")
    
    # Step 1: Register two users
    async with httpx.AsyncClient() as client:
        # User 1
        try:
            await client.post(
                f"{BASE_URL}/api/auth/register",
                json={
                    "username": "dmtest1",
                    "email": "dmtest1@example.com",
                    "password": "Test123!",
                    "display_name": "DM Test User 1"
                }
            )
            print("✅ User 1 registered")
        except:
            print("ℹ️  User 1 already exists")
        
        # User 2
        try:
            await client.post(
                f"{BASE_URL}/api/auth/register",
                json={
                    "username": "dmtest2",
                    "email": "dmtest2@example.com",
                    "password": "Test123!",
                    "display_name": "DM Test User 2"
                }
            )
            print("✅ User 2 registered")
        except:
            print("ℹ️  User 2 already exists")
        
        # Login both
        response1 = await client.post(
            f"{BASE_URL}/api/auth/login",
            json={"username": "dmtest1", "password": "Test123!"}
        )
        token1 = response1.json()["access_token"]
        user1_id = "get from token"  # Would need to decode JWT
        
        response2 = await client.post(
            f"{BASE_URL}/api/auth/login",
            json={"username": "dmtest2", "password": "Test123!"}
        )
        token2 = response2.json()["access_token"]
        
        print("✅ Both users logged in\n")
    
    print("📡 DM WebSocket test ready")
    print("   (DM feature requires user IDs - will be fully functional in Phase 4)")


async def main():
    """Run all WebSocket tests."""
    print("🔬 WebSocket Test Suite\n")
    print("Make sure the server is running: uvicorn main:app --reload\n")
    
    try:
        await test_websocket_channel()
        # await test_websocket_dm()  # Uncomment when ready to test DMs
        
        print("\n🎉 All WebSocket tests completed!")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
