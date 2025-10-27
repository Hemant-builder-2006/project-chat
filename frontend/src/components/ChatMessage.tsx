import React from 'react';
import { Message } from '../types';

interface ChatMessageProps {
  message: Message;
}

/**
 * ChatMessage Component
 * 
 * Renders an individual chat message
 * 
 * Visual Differentiation:
 * - Own messages: Aligned right, blue background
 * - Other messages: Aligned left, gray background with avatar
 * - Shows sender name and timestamp
 * - Avatar displayed for other users' messages
 */
const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const formatTimestamp = (timestamp: string): string => {
    const date = new Date(timestamp);
    const now = new Date();
    const isToday = date.toDateString() === now.toDateString();
    
    if (isToday) {
      return date.toLocaleTimeString('en-US', { 
        hour: 'numeric', 
        minute: '2-digit',
        hour12: true 
      });
    }
    
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });
  };

  if (message.isOwnMessage) {
    // Own message - aligned right
    return (
      <div className="flex justify-end mb-4 px-4">
        <div className="max-w-md">
          <div className="bg-accent-primary text-white rounded-lg px-4 py-2">
            <p className="text-sm whitespace-pre-wrap break-words">{message.content}</p>
          </div>
          <p className="text-xs text-gray-400 mt-1 text-right">
            {formatTimestamp(message.timestamp)}
          </p>
        </div>
      </div>
    );
  }

  // Other user's message - aligned left with avatar
  return (
    <div className="flex items-start mb-4 px-4">
      {/* Avatar */}
      <div className="w-10 h-10 rounded-full bg-gray-600 flex items-center justify-center text-white text-sm font-medium mr-3 flex-shrink-0">
        {message.avatarUrl ? (
          <img 
            src={message.avatarUrl} 
            alt={message.senderName} 
            className="w-full h-full rounded-full"
          />
        ) : (
          message.senderName[0].toUpperCase()
        )}
      </div>
      
      {/* Message Content */}
      <div className="flex-1 max-w-md">
        <div className="flex items-baseline space-x-2 mb-1">
          <span className="text-sm font-semibold text-gray-200">{message.senderName}</span>
          <span className="text-xs text-gray-400">{formatTimestamp(message.timestamp)}</span>
        </div>
        <div className="bg-gray-600 text-white rounded-lg px-4 py-2">
          <p className="text-sm whitespace-pre-wrap break-words">{message.content}</p>
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;
