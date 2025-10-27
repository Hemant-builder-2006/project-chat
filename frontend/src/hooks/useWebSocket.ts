import { useState, useEffect, useRef, useCallback } from 'react';
import { Message, WebSocketContext } from '../types';

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
    const wsUrl = `${import.meta.env.VITE_WS_URL}/ws/${type}/${id}`;
    
    // Get token for authentication
    const token = localStorage.getItem('accessToken');
    const wsUrlWithToken = token ? `${wsUrl}?token=${token}` : wsUrl;

    try {
      const ws = new WebSocket(wsUrlWithToken);

      ws.onopen = () => {
        console.log('WebSocket connected');
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
          
          // Handle different message types
          if (data.type === 'message') {
            const message: Message = {
              id: data.id || Date.now().toString(),
              content: data.content,
              senderName: data.sender_name,
              senderId: data.sender_id,
              timestamp: data.timestamp || new Date().toISOString(),
              isOwnMessage: data.is_own_message || false,
              avatarUrl: data.avatar_url,
            };
            setMessages(prev => [...prev, message]);
          } else if (data.type === 'history') {
            // Load message history
            const historyMessages: Message[] = data.messages.map((msg: any) => ({
              id: msg.id,
              content: msg.content,
              senderName: msg.sender_name,
              senderId: msg.sender_id,
              timestamp: msg.timestamp,
              isOwnMessage: msg.is_own_message,
              avatarUrl: msg.avatar_url,
            }));
            setMessages(historyMessages);
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
   */
  const sendMessage = useCallback((content: string) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      const message = {
        type: 'message',
        content,
      };
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.error('WebSocket is not connected');
    }
  }, []);

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
