"""
WebSocket Connection Manager for real-time communication.

Handles:
- WebSocket connection lifecycle
- User presence tracking
- Message broadcasting to channels and DMs
- WebRTC signaling relay
- Typing indicators
"""
from typing import Dict, Set, Optional
from fastapi import WebSocket
import json
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for real-time communication."""
    
    def __init__(self):
        # Active connections: {connection_id: WebSocket}
        self.active_connections: Dict[str, WebSocket] = {}
        
        # User connections: {user_id: Set[connection_id]}
        self.user_connections: Dict[str, Set[str]] = {}
        
        # Channel subscriptions: {channel_id: Set[connection_id]}
        self.channel_subscriptions: Dict[str, Set[str]] = {}
        
        # DM subscriptions: {dm_key: Set[connection_id]}
        # dm_key format: "user1_id:user2_id" (sorted)
        self.dm_subscriptions: Dict[str, Set[str]] = {}
        
        # Connection metadata: {connection_id: {user_id, username, ...}}
        self.connection_metadata: Dict[str, dict] = {}
        
        # Typing indicators: {channel_id: {user_id: timestamp}}
        self.typing_users: Dict[str, Dict[str, float]] = {}
    
    async def connect(
        self,
        websocket: WebSocket,
        connection_id: str,
        user_id: str,
        username: str,
    ):
        """Register a new WebSocket connection."""
        await websocket.accept()
        
        # Store connection
        self.active_connections[connection_id] = websocket
        
        # Track user connections
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(connection_id)
        
        # Store metadata
        self.connection_metadata[connection_id] = {
            "user_id": user_id,
            "username": username,
        }
        
        logger.info(f"User {username} ({user_id}) connected with connection {connection_id}")
    
    def disconnect(self, connection_id: str):
        """Remove a WebSocket connection."""
        if connection_id not in self.active_connections:
            return
        
        # Get metadata
        metadata = self.connection_metadata.get(connection_id, {})
        user_id = metadata.get("user_id")
        username = metadata.get("username", "unknown")
        
        # Remove from active connections
        del self.active_connections[connection_id]
        
        # Remove from user connections
        if user_id and user_id in self.user_connections:
            self.user_connections[user_id].discard(connection_id)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        
        # Remove from channel subscriptions
        for channel_id in list(self.channel_subscriptions.keys()):
            self.channel_subscriptions[channel_id].discard(connection_id)
            if not self.channel_subscriptions[channel_id]:
                del self.channel_subscriptions[channel_id]
        
        # Remove from DM subscriptions
        for dm_key in list(self.dm_subscriptions.keys()):
            self.dm_subscriptions[dm_key].discard(connection_id)
            if not self.dm_subscriptions[dm_key]:
                del self.dm_subscriptions[dm_key]
        
        # Remove metadata
        if connection_id in self.connection_metadata:
            del self.connection_metadata[connection_id]
        
        logger.info(f"User {username} ({user_id}) disconnected connection {connection_id}")
    
    def subscribe_to_channel(self, connection_id: str, channel_id: str):
        """Subscribe a connection to a channel."""
        if channel_id not in self.channel_subscriptions:
            self.channel_subscriptions[channel_id] = set()
        self.channel_subscriptions[channel_id].add(connection_id)
        logger.debug(f"Connection {connection_id} subscribed to channel {channel_id}")
    
    def unsubscribe_from_channel(self, connection_id: str, channel_id: str):
        """Unsubscribe a connection from a channel."""
        if channel_id in self.channel_subscriptions:
            self.channel_subscriptions[channel_id].discard(connection_id)
            if not self.channel_subscriptions[channel_id]:
                del self.channel_subscriptions[channel_id]
        logger.debug(f"Connection {connection_id} unsubscribed from channel {channel_id}")
    
    def subscribe_to_dm(self, connection_id: str, user_id1: str, user_id2: str):
        """Subscribe a connection to a DM conversation."""
        dm_key = self._get_dm_key(user_id1, user_id2)
        if dm_key not in self.dm_subscriptions:
            self.dm_subscriptions[dm_key] = set()
        self.dm_subscriptions[dm_key].add(connection_id)
        logger.debug(f"Connection {connection_id} subscribed to DM {dm_key}")
    
    def unsubscribe_from_dm(self, connection_id: str, user_id1: str, user_id2: str):
        """Unsubscribe a connection from a DM conversation."""
        dm_key = self._get_dm_key(user_id1, user_id2)
        if dm_key in self.dm_subscriptions:
            self.dm_subscriptions[dm_key].discard(connection_id)
            if not self.dm_subscriptions[dm_key]:
                del self.dm_subscriptions[dm_key]
        logger.debug(f"Connection {connection_id} unsubscribed from DM {dm_key}")
    
    async def send_personal_message(self, connection_id: str, message: dict):
        """Send a message to a specific connection."""
        if connection_id in self.active_connections:
            websocket = self.active_connections[connection_id]
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error sending to connection {connection_id}: {e}")
                self.disconnect(connection_id)
    
    async def broadcast_to_channel(self, channel_id: str, message: dict, exclude_connection: Optional[str] = None):
        """Broadcast a message to all connections subscribed to a channel."""
        if channel_id not in self.channel_subscriptions:
            return
        
        connections = self.channel_subscriptions[channel_id].copy()
        if exclude_connection:
            connections.discard(exclude_connection)
        
        disconnected = []
        for connection_id in connections:
            if connection_id in self.active_connections:
                websocket = self.active_connections[connection_id]
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to {connection_id}: {e}")
                    disconnected.append(connection_id)
        
        # Clean up disconnected connections
        for connection_id in disconnected:
            self.disconnect(connection_id)
    
    async def broadcast_to_dm(self, user_id1: str, user_id2: str, message: dict, exclude_connection: Optional[str] = None):
        """Broadcast a message to a DM conversation."""
        dm_key = self._get_dm_key(user_id1, user_id2)
        if dm_key not in self.dm_subscriptions:
            return
        
        connections = self.dm_subscriptions[dm_key].copy()
        if exclude_connection:
            connections.discard(exclude_connection)
        
        disconnected = []
        for connection_id in connections:
            if connection_id in self.active_connections:
                websocket = self.active_connections[connection_id]
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to {connection_id}: {e}")
                    disconnected.append(connection_id)
        
        # Clean up disconnected connections
        for connection_id in disconnected:
            self.disconnect(connection_id)
    
    async def send_to_user(self, user_id: str, message: dict):
        """Send a message to all connections of a specific user."""
        if user_id not in self.user_connections:
            return
        
        connections = self.user_connections[user_id].copy()
        disconnected = []
        
        for connection_id in connections:
            if connection_id in self.active_connections:
                websocket = self.active_connections[connection_id]
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending to user {user_id}: {e}")
                    disconnected.append(connection_id)
        
        # Clean up disconnected connections
        for connection_id in disconnected:
            self.disconnect(connection_id)
    
    def is_user_online(self, user_id: str) -> bool:
        """Check if a user has any active connections."""
        return user_id in self.user_connections and len(self.user_connections[user_id]) > 0
    
    def get_online_users_in_channel(self, channel_id: str) -> Set[str]:
        """Get list of online user IDs in a channel."""
        if channel_id not in self.channel_subscriptions:
            return set()
        
        online_users = set()
        for connection_id in self.channel_subscriptions[channel_id]:
            if connection_id in self.connection_metadata:
                user_id = self.connection_metadata[connection_id]["user_id"]
                online_users.add(user_id)
        
        return online_users
    
    def _get_dm_key(self, user_id1: str, user_id2: str) -> str:
        """Generate a consistent key for DM conversations."""
        return ":".join(sorted([user_id1, user_id2]))
    
    async def relay_webrtc_signal(
        self,
        target_user_id: str,
        signal_type: str,
        signal_data: dict,
        sender_user_id: str,
        sender_username: str
    ):
        """
        Relay WebRTC signaling messages to a specific user.
        
        Signal types: 'offer', 'answer', 'ice_candidate'
        """
        message = {
            "type": f"webrtc_{signal_type}",
            "from_user_id": sender_user_id,
            "from_username": sender_username,
            "data": signal_data
        }
        
        await self.send_to_user(target_user_id, message)
        logger.debug(f"Relayed WebRTC {signal_type} from {sender_user_id} to {target_user_id}")


# Global connection manager instance
connection_manager = ConnectionManager()
