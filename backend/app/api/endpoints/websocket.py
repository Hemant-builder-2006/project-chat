"""WebSocket endpoints for real-time communication."""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
import logging
from typing import Optional

from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User
from app.models.channel import Channel
from app.models.membership import Membership
from app.models.message import Message
from app.services.connection_manager import connection_manager
from app.schemas.message import MessageCreate

logger = logging.getLogger(__name__)
router = APIRouter(tags=["WebSocket"])


async def get_user_from_token(token: str, db: AsyncSession) -> Optional[User]:
    """Authenticate user from JWT token."""
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        return user if user and user.is_active else None
    except Exception as e:
        logger.error(f"Token validation error: {e}")
        return None


@router.websocket("/ws/channel/{channel_id}")
async def websocket_channel_endpoint(
    websocket: WebSocket,
    channel_id: str,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """
    WebSocket endpoint for channel communication.
    
    Handles:
    - Real-time messages in channels
    - Typing indicators
    - User presence
    - WebRTC signaling (if in VOICE/VIDEO channel)
    """
    connection_id = str(uuid.uuid4())
    
    # Authenticate user
    user = await get_user_from_token(token, db)
    if not user:
        await websocket.close(code=1008, reason="Authentication failed")
        return
    
    # Verify channel exists and user has access
    result = await db.execute(select(Channel).where(Channel.id == channel_id))
    channel = result.scalar_one_or_none()
    
    if not channel:
        await websocket.close(code=1008, reason="Channel not found")
        return
    
    # Check user is member of the group
    result = await db.execute(
        select(Membership).where(
            Membership.group_id == channel.group_id,
            Membership.user_id == user.id
        )
    )
    membership = result.scalar_one_or_none()
    
    if not membership:
        await websocket.close(code=1008, reason="Not a member of this group")
        return
    
    # Connect and subscribe
    await connection_manager.connect(websocket, connection_id, str(user.id), user.username)
    connection_manager.subscribe_to_channel(connection_id, channel_id)
    
    # Notify others of user joining
    await connection_manager.broadcast_to_channel(
        channel_id,
        {
            "type": "user_joined",
            "user_id": str(user.id),
            "username": user.username,
            "channel_id": channel_id
        },
        exclude_connection=connection_id
    )
    
    # Send online users list to new connection
    online_users = connection_manager.get_online_users_in_channel(channel_id)
    await connection_manager.send_personal_message(
        connection_id,
        {
            "type": "online_users",
            "users": list(online_users),
            "channel_id": channel_id
        }
    )
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            message_type = data.get("type")
            
            if message_type == "message":
                # Chat message
                content = data.get("content", "").strip()
                if not content:
                    continue
                
                # Save to database
                message = Message(
                    content=content,
                    sender_id=user.id,
                    channel_id=channel_id
                )
                db.add(message)
                await db.commit()
                await db.refresh(message)
                
                # Broadcast to channel
                await connection_manager.broadcast_to_channel(
                    channel_id,
                    {
                        "type": "message",
                        "id": str(message.id),
                        "content": message.content,
                        "sender_id": str(user.id),
                        "sender_username": user.username,
                        "channel_id": channel_id,
                        "created_at": message.created_at.isoformat(),
                    }
                )
                
                # Check for AI trigger (@AI)
                if content.startswith("@AI ") or content.startswith("@ai "):
                    # Extract query after @AI
                    query = content[4:].strip()
                    
                    if query:
                        try:
                            # Import AI service
                            from app.services.ai_service import get_ollama_completion
                            
                            # Get recent messages for context
                            recent_messages_result = await db.execute(
                                select(Message)
                                .where(Message.channel_id == channel_id)
                                .order_by(Message.created_at.desc())
                                .limit(10)
                            )
                            recent_messages = recent_messages_result.scalars().all()
                            
                            # Format context
                            context_lines = []
                            for msg in reversed(recent_messages[-9:]):  # Exclude the @AI message
                                context_lines.append(f"{msg.content}")
                            
                            context = "\n".join(context_lines) if context_lines else ""
                            
                            # Build prompt with context
                            prompt = f"""Previous conversation:
{context}

User question: {query}

Provide a helpful response based on the conversation context."""
                            
                            # Get AI response
                            ai_response = await get_ollama_completion(
                                prompt=prompt,
                                system_prompt="You are a helpful AI assistant in a chat channel. Be conversational and helpful."
                            )
                            
                            # Save AI response as message
                            ai_message = Message(
                                content=f"🤖 {ai_response['response']}",
                                sender_id=user.id,  # Or create a bot user
                                channel_id=channel_id
                            )
                            db.add(ai_message)
                            await db.commit()
                            await db.refresh(ai_message)
                            
                            # Broadcast AI response
                            await connection_manager.broadcast_to_channel(
                                channel_id,
                                {
                                    "type": "message",
                                    "id": str(ai_message.id),
                                    "content": ai_message.content,
                                    "sender_id": "ai",
                                    "sender_username": "AI Assistant",
                                    "channel_id": channel_id,
                                    "created_at": ai_message.created_at.isoformat(),
                                    "is_ai": True,
                                }
                            )
                            
                        except Exception as e:
                            # Send error message
                            await connection_manager.send_to_connection(
                                connection_id,
                                {
                                    "type": "error",
                                    "message": f"AI service error: {str(e)}"
                                }
                            )
            
            elif message_type == "typing":
                # Typing indicator
                is_typing = data.get("is_typing", False)
                await connection_manager.broadcast_to_channel(
                    channel_id,
                    {
                        "type": "typing",
                        "user_id": str(user.id),
                        "username": user.username,
                        "is_typing": is_typing,
                        "channel_id": channel_id
                    },
                    exclude_connection=connection_id
                )
            
            elif message_type in ["webrtc_offer", "webrtc_answer", "webrtc_ice_candidate"]:
                # WebRTC signaling - relay to target user
                target_user_id = data.get("target_user_id")
                signal_data = data.get("data", {})
                
                if target_user_id:
                    signal_type = message_type.replace("webrtc_", "")
                    await connection_manager.relay_webrtc_signal(
                        target_user_id=target_user_id,
                        signal_type=signal_type,
                        signal_data=signal_data,
                        sender_user_id=str(user.id),
                        sender_username=user.username
                    )
            
            else:
                logger.warning(f"Unknown message type: {message_type}")
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {connection_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        # Cleanup
        connection_manager.disconnect(connection_id)
        
        # Notify others of user leaving
        await connection_manager.broadcast_to_channel(
            channel_id,
            {
                "type": "user_left",
                "user_id": str(user.id),
                "username": user.username,
                "channel_id": channel_id
            }
        )


@router.websocket("/ws/dm/{other_user_id}")
async def websocket_dm_endpoint(
    websocket: WebSocket,
    other_user_id: str,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """
    WebSocket endpoint for direct messages.
    
    Handles:
    - Real-time DMs between two users
    - Typing indicators
    - WebRTC signaling for 1-on-1 calls
    """
    connection_id = str(uuid.uuid4())
    
    # Authenticate user
    user = await get_user_from_token(token, db)
    if not user:
        await websocket.close(code=1008, reason="Authentication failed")
        return
    
    # Verify other user exists
    result = await db.execute(select(User).where(User.id == other_user_id))
    other_user = result.scalar_one_or_none()
    
    if not other_user:
        await websocket.close(code=1008, reason="User not found")
        return
    
    # Connect and subscribe to DM
    await connection_manager.connect(websocket, connection_id, str(user.id), user.username)
    connection_manager.subscribe_to_dm(connection_id, str(user.id), other_user_id)
    
    # Notify other user
    await connection_manager.send_to_user(
        other_user_id,
        {
            "type": "dm_user_online",
            "user_id": str(user.id),
            "username": user.username
        }
    )
    
    try:
        while True:
            data = await websocket.receive_json()
            message_type = data.get("type")
            
            if message_type == "dm_message":
                # Direct message
                content = data.get("content", "").strip()
                if not content:
                    continue
                
                # For now, just broadcast (Phase 4 will add DB storage)
                message_data = {
                    "type": "dm_message",
                    "id": str(uuid.uuid4()),
                    "content": content,
                    "sender_id": str(user.id),
                    "sender_username": user.username,
                    "recipient_id": other_user_id,
                    "created_at": None  # Will add timestamp in Phase 4
                }
                
                # Send to both users
                await connection_manager.broadcast_to_dm(
                    str(user.id),
                    other_user_id,
                    message_data
                )
            
            elif message_type == "dm_typing":
                # Typing indicator in DM
                is_typing = data.get("is_typing", False)
                await connection_manager.send_to_user(
                    other_user_id,
                    {
                        "type": "dm_typing",
                        "user_id": str(user.id),
                        "username": user.username,
                        "is_typing": is_typing
                    }
                )
            
            elif message_type in ["webrtc_offer", "webrtc_answer", "webrtc_ice_candidate"]:
                # WebRTC signaling for 1-on-1 calls
                signal_data = data.get("data", {})
                signal_type = message_type.replace("webrtc_", "")
                
                await connection_manager.relay_webrtc_signal(
                    target_user_id=other_user_id,
                    signal_type=signal_type,
                    signal_data=signal_data,
                    sender_user_id=str(user.id),
                    sender_username=user.username
                )
    
    except WebSocketDisconnect:
        logger.info(f"DM WebSocket disconnected: {connection_id}")
    except Exception as e:
        logger.error(f"DM WebSocket error: {e}")
    finally:
        # Cleanup
        connection_manager.disconnect(connection_id)
        
        # Notify other user
        await connection_manager.send_to_user(
            other_user_id,
            {
                "type": "dm_user_offline",
                "user_id": str(user.id),
                "username": user.username
            }
        )
