"""WebRTC-related API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from typing import List
import hmac
import hashlib
import time
import base64
import os
from datetime import datetime, timedelta

from app.core.security import get_current_user
from app.models.user import User
from pydantic import BaseModel


router = APIRouter(prefix="/webrtc", tags=["WebRTC"])


class TURNCredentials(BaseModel):
    """TURN server credentials response."""
    username: str
    credential: str
    ttl: int
    uris: List[str]


class ICEServer(BaseModel):
    """ICE server configuration."""
    urls: List[str]
    username: str | None = None
    credential: str | None = None


class RTCConfiguration(BaseModel):
    """WebRTC configuration with ICE servers."""
    iceServers: List[ICEServer]


def generate_turn_credentials(username: str, secret: str, ttl: int = 86400) -> tuple[str, str]:
    """
    Generate temporary TURN credentials using HMAC-SHA1.
    
    Compatible with Coturn's 'lt-cred-mech' (long-term credential mechanism).
    
    Args:
        username: Base username (usually user ID or email)
        secret: Shared secret configured in TURN server
        ttl: Time-to-live in seconds (default 24 hours)
    
    Returns:
        Tuple of (username_with_timestamp, credential)
    """
    # Generate timestamp-based username
    timestamp = int(time.time()) + ttl
    temp_username = f"{timestamp}:{username}"
    
    # Generate HMAC-SHA1 credential
    credential = hmac.new(
        secret.encode('utf-8'),
        temp_username.encode('utf-8'),
        hashlib.sha1
    ).digest()
    
    # Base64 encode the credential
    credential_base64 = base64.b64encode(credential).decode('utf-8')
    
    return temp_username, credential_base64


@router.get("/turn-credentials", response_model=TURNCredentials)
async def get_turn_credentials(
    current_user: User = Depends(get_current_user)
):
    """
    Get temporary TURN server credentials for WebRTC connections.
    
    Generates time-limited credentials using HMAC authentication.
    These credentials expire after the TTL period (default 24 hours).
    
    Security:
    - Credentials are temporary and time-bound
    - Generated using shared secret (not exposed to clients)
    - Each user gets unique credentials
    - Compatible with Coturn's long-term credential mechanism
    
    Returns:
        TURNCredentials with username, credential, TTL, and server URIs
    """
    # Get TURN server configuration from environment
    turn_secret = os.getenv("TURN_SECRET")
    if not turn_secret:
        raise HTTPException(
            status_code=503,
            detail="TURN server not configured. Set TURN_SECRET environment variable."
        )
    
    turn_host = os.getenv("TURN_HOST", "localhost")
    turn_port = os.getenv("TURN_PORT", "3478")
    turn_port_tls = os.getenv("TURN_PORT_TLS", "5349")
    
    # TTL in seconds (24 hours by default)
    ttl = int(os.getenv("TURN_TTL", "86400"))
    
    # Generate credentials
    username, credential = generate_turn_credentials(
        username=current_user.username,
        secret=turn_secret,
        ttl=ttl
    )
    
    # Build URIs
    uris = [
        f"turn:{turn_host}:{turn_port}?transport=udp",
        f"turn:{turn_host}:{turn_port}?transport=tcp",
        f"turns:{turn_host}:{turn_port_tls}?transport=tcp",  # TLS
    ]
    
    return TURNCredentials(
        username=username,
        credential=credential,
        ttl=ttl,
        uris=uris
    )


@router.get("/ice-servers", response_model=RTCConfiguration)
async def get_ice_servers(
    current_user: User = Depends(get_current_user)
):
    """
    Get complete ICE server configuration for WebRTC.
    
    Returns both STUN and TURN servers in WebRTC RTCConfiguration format.
    Ready to use directly in RTCPeerConnection constructor.
    
    Example usage in frontend:
    ```javascript
    const response = await fetch('/api/webrtc/ice-servers', {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    const config = await response.json();
    const peerConnection = new RTCPeerConnection(config);
    ```
    
    Returns:
        RTCConfiguration with iceServers array
    """
    ice_servers = []
    
    # Add public STUN servers (free, no credentials needed)
    stun_servers = os.getenv("STUN_SERVERS", "stun:stun.l.google.com:19302,stun:stun1.l.google.com:19302")
    if stun_servers:
        stun_urls = [url.strip() for url in stun_servers.split(",")]
        ice_servers.append(ICEServer(urls=stun_urls))
    
    # Add TURN server with credentials (if configured)
    turn_secret = os.getenv("TURN_SECRET")
    if turn_secret:
        turn_host = os.getenv("TURN_HOST", "localhost")
        turn_port = os.getenv("TURN_PORT", "3478")
        turn_port_tls = os.getenv("TURN_PORT_TLS", "5349")
        ttl = int(os.getenv("TURN_TTL", "86400"))
        
        # Generate TURN credentials
        username, credential = generate_turn_credentials(
            username=current_user.username,
            secret=turn_secret,
            ttl=ttl
        )
        
        # TURN URIs
        turn_urls = [
            f"turn:{turn_host}:{turn_port}?transport=udp",
            f"turn:{turn_host}:{turn_port}?transport=tcp",
            f"turns:{turn_host}:{turn_port_tls}?transport=tcp",
        ]
        
        ice_servers.append(ICEServer(
            urls=turn_urls,
            username=username,
            credential=credential
        ))
    
    return RTCConfiguration(iceServers=ice_servers)
