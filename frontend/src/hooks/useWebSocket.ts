import { useState, useEffect, useRef, useCallback } from 'react';
import { Message, WebSocketContext } from '../types';
import { useWebRTCContext } from '../contexts/WebRTCContext';

interface UseWebSocketResult {
  messages: Message[];
  sendMessage: (content: string) => void;
  isConnected: boolean;
}

/**
 * useWebSocket Hook
 * 
 * Context-aware WebSocket connection for real-time messaging
 * 
 * Parameters:
 * - context: Object specifying the conversation type and ID
 *   { type: 'channel' | 'dm', id: string }
 * 
 * How it handles different conversation contexts:
 * 1. Constructs WebSocket URL based on context type and ID
 *    - Channel: ws://localhost:8000/ws/channel/{id}
 *    - DM: ws://localhost:8000/ws/dm/{id}
 * 2. Only connects when context is not null
 * 3. Reconnects automatically when context changes
 * 4. Cleans up connection when context becomes null or component unmounts
 * 
 * Features:
 * - Automatic reconnection on connection loss
 * - Message history management
 * - Connection status tracking
 * - Proper cleanup to prevent memory leaks
 */
export const useWebSocket = (context: WebSocketContext | null): UseWebSocketResult => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const contextRef = useRef<WebSocketContext | null>(context);
  
  // Get WebRTC context for signaling
  const webrtcContext = useWebRTCContext();

  // Update context ref when it changes
  useEffect(() => {
    contextRef.current = context;
  }, [context]);

  /**
   * Connect to WebSocket
   */
  const connect = useCallback(() => {
    if (!contextRef.current) return;

    const { type, id } = contextRef.current;
    // Backend WebSocket routes: /ws/channel/{channel_id} or /ws/dm/{other_user_id}
    const wsUrl = `${import.meta.env.VITE_WS_URL}/ws/${type}/${id}`;
    
    // Get token for authentication (backend expects token as query param)
    const token = localStorage.getItem('accessToken');
    const wsUrlWithToken = token ? `${wsUrl}?token=${token}` : wsUrl;

    try {
      const ws = new WebSocket(wsUrlWithToken);

      ws.onopen = () => {
        console.log('WebSocket connected to', type, id);
        setIsConnected(true);
        // Clear any pending reconnection attempts
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current);
          reconnectTimeoutRef.current = null;
        }
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          // Handle different message types from backend
          
          // Chat messages
          if (data.type === 'message') {
            const newMessage: Message = {
              id: data.id,
              content: data.content,
              senderName: data.sender_username,
              senderId: data.sender_id,
              timestamp: data.created_at,
              isOwnMessage: data.sender_id === localStorage.getItem('userId'),
              avatarUrl: data.avatar_url,
            };
            setMessages((prev) => [...prev, newMessage]);
            return;
          }
          
          // User joined/left events
          if (data.type === 'user_joined' || data.type === 'user_left') {
            console.log(`User ${data.username} ${data.type === 'user_joined' ? 'joined' : 'left'}`);
            // Could show a notification or update presence
            return;
          }
          
          // Online users list
          if (data.type === 'online_users') {
            console.log('Online users:', data.users);
            // Could update UI to show online status
            return;
          }
          
          // Typing indicators
          if (data.type === 'typing' || data.type === 'dm_typing') {
            console.log(`${data.username} is ${data.is_typing ? 'typing' : 'stopped typing'}`);
            // Could show typing indicator in UI
            return;
          }
          
          // WebRTC signaling messages
          if (data.type === 'webrtc_offer') {
            console.log('Received WebRTC offer from:', data.from_user_id);
            if (webrtcContext.onOffer) {
              webrtcContext.onOffer(data.data, data.from_user_id);
            }
            return;
          }
          
          if (data.type === 'webrtc_answer') {
            console.log('Received WebRTC answer from:', data.from_user_id);
            if (webrtcContext.onAnswer) {
              webrtcContext.onAnswer(data.data, data.from_user_id);
            }
            return;
          }
          
          if (data.type === 'webrtc_ice_candidate') {
            console.log('Received ICE candidate from:', data.from_user_id);
            if (webrtcContext.onIceCandidate) {
              webrtcContext.onIceCandidate(data.data, data.from_user_id);
            }
            return;
          }
          
          // Error messages from backend
          if (data.type === 'error') {
            console.error('WebSocket error message:', data.message);
            // Could show error notification to user
            return;
          }
          
          // DM messages
          if (data.type === 'dm_message') {
            const newMessage: Message = {
              id: data.id,
              content: data.content,
              senderName: data.sender_username,
              senderId: data.sender_id,
              timestamp: data.created_at || new Date().toISOString(),
              isOwnMessage: data.sender_id === localStorage.getItem('userId'),
            };
            setMessages((prev) => [...prev, newMessage]);
            return;
          }
          
          // DM user online/offline
          if (data.type === 'dm_user_online' || data.type === 'dm_user_offline') {
            console.log(`DM user ${data.username} is ${data.type === 'dm_user_online' ? 'online' : 'offline'}`);
            return;
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);
        wsRef.current = null;

        // Attempt to reconnect after 3 seconds if context still exists
        if (contextRef.current) {
          reconnectTimeoutRef.current = setTimeout(() => {
            console.log('Attempting to reconnect...');
            connect();
          }, 3000);
        }
      };

      wsRef.current = ws;
    } catch (error) {
      console.error('Error creating WebSocket connection:', error);
    }
  }, []);

  /**
   * Send a message through WebSocket
   * Backend expects: { "type": "message", "content": "..." }
   */
  const sendMessage = useCallback((content: string) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      const message = {
        type: 'message',  // For channel messages
        content,
      };
      // Use 'dm_message' type if in DM context
      if (contextRef.current?.type === 'dm') {
        message.type = 'dm_message';
      }
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.error('WebSocket is not connected');
    }
  }, []);

  /**
   * Register WebRTC signal sender with context
   * This allows useWebRTC hook to send WebRTC signals through WebSocket
   */
  useEffect(() => {
    const sendSignal = (signal: any) => {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify(signal));
      } else {
        console.error('WebSocket is not connected, cannot send signal');
      }
    };
    
    webrtcContext.registerSignalSender(sendSignal);
  }, [webrtcContext]);

  /**
   * Effect to manage WebSocket connection
   */
  useEffect(() => {
    if (context) {
      // Clear existing messages when context changes
      setMessages([]);
      connect();
    } else {
      // Disconnect if context becomes null
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
      setIsConnected(false);
      setMessages([]);
    }

    // Cleanup function
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = null;
      }
    };
  }, [context, connect]);

  return { messages, sendMessage, isConnected };
};
