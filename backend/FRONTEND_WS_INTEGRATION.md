# Frontend WebSocket Integration Guide

This guide shows how to integrate WebSocket real-time features into your React frontend.

## WebSocket Connection Setup

### Update useWebSocket Hook

```typescript
// src/hooks/useWebSocket.ts
import { useState, useEffect, useRef, useCallback } from 'react';
import { authService } from '../services/authService';

interface Message {
  id: string;
  content: string;
  sender_id: string;
  sender_username: string;
  channel_id: string;
  created_at: string;
}

interface UseWebSocketOptions {
  channelId?: string;
  dmUserId?: string;
  onWebRTCSignal?: (signal: any) => void;
}

export const useWebSocket = ({ channelId, dmUserId, onWebRTCSignal }: UseWebSocketOptions) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [onlineUsers, setOnlineUsers] = useState<string[]>([]);
  const [connected, setConnected] = useState(false);
  const [typingUsers, setTypingUsers] = useState<Set<string>>(new Set());
  const ws = useRef<WebSocket | null>(null);
  const reconnectTimeout = useRef<NodeJS.Timeout | null>(null);

  const connect = useCallback(() => {
    const token = authService.getAccessToken();
    if (!token) {
      console.error('No auth token available');
      return;
    }

    if (!channelId && !dmUserId) {
      console.error('Either channelId or dmUserId must be provided');
      return;
    }

    // Determine WebSocket URL
    const wsUrl = channelId
      ? `ws://localhost:8000/ws/channel/${channelId}?token=${token}`
      : `ws://localhost:8000/ws/dm/${dmUserId}?token=${token}`;

    console.log('Connecting to WebSocket:', wsUrl);
    ws.current = new WebSocket(wsUrl);

    ws.current.onopen = () => {
      console.log('✅ WebSocket connected');
      setConnected(true);
      
      // Clear reconnect timeout
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current);
        reconnectTimeout.current = null;
      }
    };

    ws.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('📨 Received:', data.type, data);

        switch (data.type) {
          case 'online_users':
            setOnlineUsers(data.users);
            break;

          case 'user_joined':
            console.log(`👋 ${data.username} joined`);
            // Add to online users if not already there
            setOnlineUsers(prev => 
              prev.includes(data.user_id) ? prev : [...prev, data.user_id]
            );
            break;

          case 'user_left':
            console.log(`👋 ${data.username} left`);
            setOnlineUsers(prev => prev.filter(id => id !== data.user_id));
            break;

          case 'message':
            setMessages(prev => [...prev, data]);
            break;

          case 'dm_message':
            setMessages(prev => [...prev, data]);
            break;

          case 'typing':
            if (data.is_typing) {
              setTypingUsers(prev => new Set(prev).add(data.username));
            } else {
              setTypingUsers(prev => {
                const next = new Set(prev);
                next.delete(data.username);
                return next;
              });
            }
            // Auto-clear typing after 3 seconds
            setTimeout(() => {
              setTypingUsers(prev => {
                const next = new Set(prev);
                next.delete(data.username);
                return next;
              });
            }, 3000);
            break;

          case 'dm_typing':
            if (data.is_typing) {
              setTypingUsers(prev => new Set(prev).add(data.username));
            } else {
              setTypingUsers(prev => {
                const next = new Set(prev);
                next.delete(data.username);
                return next;
              });
            }
            break;

          case 'dm_user_online':
            console.log(`✅ ${data.username} is online`);
            break;

          case 'dm_user_offline':
            console.log(`⚫ ${data.username} is offline`);
            break;

          case 'webrtc_offer':
          case 'webrtc_answer':
          case 'webrtc_ice_candidate':
            if (onWebRTCSignal) {
              onWebRTCSignal(data);
            }
            break;

          default:
            console.log('Unknown message type:', data.type);
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    ws.current.onerror = (error) => {
      console.error('❌ WebSocket error:', error);
    };

    ws.current.onclose = (event) => {
      console.log('🔌 WebSocket disconnected:', event.code, event.reason);
      setConnected(false);
      setOnlineUsers([]);

      // Auto-reconnect after 3 seconds
      if (event.code !== 1000) { // Not normal closure
        reconnectTimeout.current = setTimeout(() => {
          console.log('🔄 Attempting to reconnect...');
          connect();
        }, 3000);
      }
    };
  }, [channelId, dmUserId, onWebRTCSignal]);

  useEffect(() => {
    connect();

    return () => {
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current);
      }
      if (ws.current) {
        ws.current.close(1000, 'Component unmounted');
      }
    };
  }, [connect]);

  const sendMessage = useCallback((content: string) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      const messageType = channelId ? 'message' : 'dm_message';
      ws.current.send(JSON.stringify({
        type: messageType,
        content
      }));
    } else {
      console.error('WebSocket not connected');
    }
  }, [channelId]);

  const sendTyping = useCallback((isTyping: boolean) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      const typingType = channelId ? 'typing' : 'dm_typing';
      ws.current.send(JSON.stringify({
        type: typingType,
        is_typing: isTyping
      }));
    }
  }, [channelId]);

  const sendWebRTCSignal = useCallback((
    type: 'offer' | 'answer' | 'ice_candidate',
    targetUserId: string,
    data: any
  ) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({
        type: `webrtc_${type}`,
        target_user_id: targetUserId,
        data
      }));
    }
  }, []);

  return {
    messages,
    onlineUsers,
    connected,
    typingUsers: Array.from(typingUsers),
    sendMessage,
    sendTyping,
    sendWebRTCSignal,
  };
};
```

## Updated ChatView Component

```typescript
// src/components/ChatView.tsx
import React, { useState, useEffect, useRef } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';

interface ChatViewProps {
  channelId: string;
  channelName: string;
  channelType: string;
}

export const ChatView: React.FC<ChatViewProps> = ({
  channelId,
  channelName,
  channelType
}) => {
  const {
    messages,
    onlineUsers,
    connected,
    typingUsers,
    sendMessage,
    sendTyping
  } = useWebSocket({ channelId });

  const [inputValue, setInputValue] = useState('');
  const typingTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const handleInputChange = (value: string) => {
    setInputValue(value);

    // Send typing indicator
    sendTyping(true);

    // Clear previous timeout
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
    }

    // Stop typing after 2 seconds of inactivity
    typingTimeoutRef.current = setTimeout(() => {
      sendTyping(false);
    }, 2000);
  };

  const handleSendMessage = () => {
    if (inputValue.trim()) {
      sendMessage(inputValue.trim());
      setInputValue('');
      sendTyping(false);

      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }
    }
  };

  useEffect(() => {
    return () => {
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }
    };
  }, []);

  return (
    <div className="flex flex-col h-full bg-gray-800">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-700">
        <div>
          <h2 className="text-xl font-bold text-white">#{channelName}</h2>
          <p className="text-sm text-gray-400">
            {connected ? (
              <>
                {onlineUsers.length} user{onlineUsers.length !== 1 ? 's' : ''} online
              </>
            ) : (
              'Connecting...'
            )}
          </p>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto">
        <MessageList messages={messages} />
        
        {/* Typing Indicator */}
        {typingUsers.length > 0 && (
          <div className="px-4 py-2 text-sm text-gray-400 italic">
            {typingUsers.join(', ')} {typingUsers.length === 1 ? 'is' : 'are'} typing...
          </div>
        )}
      </div>

      {/* Input */}
      <MessageInput
        value={inputValue}
        onChange={handleInputChange}
        onSend={handleSendMessage}
        placeholder={`Message #${channelName}`}
        disabled={!connected}
      />
    </div>
  );
};
```

## WebRTC Integration with WebSocket

```typescript
// src/hooks/useWebRTC.ts (updated)
import { useState, useEffect, useRef, useCallback } from 'react';
import { useWebSocket } from './useWebSocket';

export const useWebRTC = (channelId: string, localUserId: string) => {
  const [peerConnections, setPeerConnections] = useState<Map<string, RTCPeerConnection>>(new Map());
  const [localStream, setLocalStream] = useState<MediaStream | null>(null);
  const [remoteStreams, setRemoteStreams] = useState<Map<string, MediaStream>>(new Map());

  // WebRTC signal handler
  const handleWebRTCSignal = useCallback(async (signal: any) => {
    const { type, from_user_id, data } = signal;

    console.log('📡 Received WebRTC signal:', type, 'from', from_user_id);

    if (type === 'webrtc_offer') {
      // Create peer connection if doesn't exist
      let pc = peerConnections.get(from_user_id);
      if (!pc) {
        pc = createPeerConnection(from_user_id);
        setPeerConnections(prev => new Map(prev).set(from_user_id, pc!));
      }

      // Set remote description
      await pc.setRemoteDescription(new RTCSessionDescription(data));

      // Create and send answer
      const answer = await pc.createAnswer();
      await pc.setLocalDescription(answer);

      sendWebRTCSignal('answer', from_user_id, {
        type: 'answer',
        sdp: pc.localDescription?.sdp
      });
    } else if (type === 'webrtc_answer') {
      const pc = peerConnections.get(from_user_id);
      if (pc) {
        await pc.setRemoteDescription(new RTCSessionDescription(data));
      }
    } else if (type === 'webrtc_ice_candidate') {
      const pc = peerConnections.get(from_user_id);
      if (pc && data.candidate) {
        await pc.addIceCandidate(new RTCIceCandidate(data));
      }
    }
  }, [peerConnections]);

  // Initialize WebSocket with WebRTC handler
  const { sendWebRTCSignal } = useWebSocket({
    channelId,
    onWebRTCSignal: handleWebRTCSignal
  });

  const createPeerConnection = useCallback((remoteUserId: string) => {
    const pc = new RTCPeerConnection({
      iceServers: [
        { urls: 'stun:stun.l.google.com:19302' }
      ]
    });

    // Add local tracks
    if (localStream) {
      localStream.getTracks().forEach(track => {
        pc.addTrack(track, localStream);
      });
    }

    // Handle remote track
    pc.ontrack = (event) => {
      console.log('📺 Received remote track from', remoteUserId);
      setRemoteStreams(prev => new Map(prev).set(remoteUserId, event.streams[0]));
    };

    // Handle ICE candidates
    pc.onicecandidate = (event) => {
      if (event.candidate) {
        sendWebRTCSignal('ice_candidate', remoteUserId, {
          candidate: event.candidate.candidate,
          sdpMid: event.candidate.sdpMid,
          sdpMLineIndex: event.candidate.sdpMLineIndex
        });
      }
    };

    return pc;
  }, [localStream, sendWebRTCSignal]);

  const startCall = useCallback(async (remoteUserId: string) => {
    // Get local media
    const stream = await navigator.mediaDevices.getUserMedia({
      video: true,
      audio: true
    });
    setLocalStream(stream);

    // Create peer connection
    const pc = createPeerConnection(remoteUserId);
    setPeerConnections(prev => new Map(prev).set(remoteUserId, pc));

    // Create offer
    const offer = await pc.createOffer();
    await pc.setLocalDescription(offer);

    // Send offer via WebSocket
    sendWebRTCSignal('offer', remoteUserId, {
      type: 'offer',
      sdp: pc.localDescription?.sdp
    });
  }, [createPeerConnection, sendWebRTCSignal]);

  const endCall = useCallback(() => {
    // Close all peer connections
    peerConnections.forEach(pc => pc.close());
    setPeerConnections(new Map());

    // Stop local stream
    if (localStream) {
      localStream.getTracks().forEach(track => track.stop());
      setLocalStream(null);
    }

    // Clear remote streams
    setRemoteStreams(new Map());
  }, [peerConnections, localStream]);

  return {
    startCall,
    endCall,
    localStream,
    remoteStreams,
    peerConnections
  };
};
```

## Environment Variables

Update your frontend `.env`:

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

## Testing Checklist

- [ ] WebSocket connects with JWT token
- [ ] User receives "online_users" on connect
- [ ] Sending messages works (appears in real-time)
- [ ] Typing indicators show/hide correctly
- [ ] User join/leave events broadcast
- [ ] Multiple browser tabs connect successfully
- [ ] Auto-reconnect after connection drop
- [ ] WebRTC signals relay through WebSocket
- [ ] DM WebSocket connects and works
- [ ] Connection cleanup on unmount

## Troubleshooting

### WebSocket won't connect
- Check server is running: `uvicorn main:app --reload`
- Verify JWT token is valid
- Check browser console for errors
- Ensure CORS is configured correctly

### Messages not appearing
- Check `connected` state is true
- Verify `sendMessage()` is called
- Check WebSocket message format
- Look at server logs for errors

### Typing indicators stuck
- Implement auto-clear timeout (3 seconds)
- Send `is_typing: false` on input blur
- Clear timeout on component unmount

### WebRTC signals not relaying
- Verify `target_user_id` is correct
- Check user is online and in same channel
- Look for WebRTC handler in useWebSocket
- Ensure signal format matches backend

## Next Steps

With WebSocket working, you can now:
1. ✅ Send/receive real-time messages
2. ✅ Show typing indicators
3. ✅ Display online users
4. ✅ Relay WebRTC signals for calls
5. ⏳ Load message history (Phase 4)
6. ⏳ Add reactions and threading (Phase 4)
