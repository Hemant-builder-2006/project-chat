import React, { useMemo } from 'react';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import { useWebSocket } from '../hooks/useWebSocket';
import { WebSocketContext } from '../types';

interface ChatViewProps {
  channelId: string | null;
  dmId: string | null;
}

/**
 * ChatView Component
 * 
 * Orchestrates the chat interface for a channel or DM
 * 
 * How it works:
 * 1. Receives either channelId or dmId from parent
 * 2. Determines the WebSocket context based on which is set
 * 3. Passes context to useWebSocket hook
 * 4. Hook manages connection and message state
 * 5. Renders MessageList with messages from hook
 * 6. Renders MessageInput with sendMessage function from hook
 * 
 * Context Determination:
 * - If channelId is set: { type: 'channel', id: channelId }
 * - If dmId is set: { type: 'dm', id: dmId }
 * - If neither: null (no connection)
 */
const ChatView: React.FC<ChatViewProps> = ({ channelId, dmId }) => {
  /**
   * Determine WebSocket context
   * Uses useMemo to prevent unnecessary recalculations
   */
  const context: WebSocketContext | null = useMemo(() => {
    if (channelId) {
      return { type: 'channel', id: channelId };
    }
    if (dmId) {
      return { type: 'dm', id: dmId };
    }
    return null;
  }, [channelId, dmId]);

  // Connect to WebSocket and get messages/sendMessage
  const { messages, sendMessage, isConnected } = useWebSocket(context);

  if (!context) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-gray-400">No conversation selected</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Connection Status Bar */}
      {!isConnected && (
        <div className="bg-yellow-600 text-white text-sm px-4 py-2 text-center">
          Connecting to chat...
        </div>
      )}

      {/* Messages Area */}
      <MessageList messages={messages} />

      {/* Input Area */}
      <MessageInput sendMessage={sendMessage} />
    </div>
  );
};

export default ChatView;
