import React, { useMemo, useState } from 'react';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import { useWebSocket } from '../hooks/useWebSocket';
import { WebSocketContext } from '../types';
import VideoCallView from './views/VideoCallView';

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
  const [showVideoCall, setShowVideoCall] = useState(false);
  
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
      {/* Header with Call Button (for DMs only) */}
      {dmId && (
        <div className="bg-dark-surface border-b border-gray-700 px-6 py-3 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-white">Direct Message</h2>
          <button
            onClick={() => setShowVideoCall(true)}
            className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
            Video Call
          </button>
        </div>
      )}
      
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
      
      {/* Video Call Modal */}
      {showVideoCall && dmId && (
        <VideoCallView
          targetUserId={dmId}
          onClose={() => setShowVideoCall(false)}
        />
      )}
    </div>
  );
};

export default ChatView;
