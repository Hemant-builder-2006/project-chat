import React, { useRef, useEffect } from 'react';
import ChatMessage from './ChatMessage';
import { Message } from '../types';

interface MessageListProps {
  messages: Message[];
}

/**
 * MessageList Component
 * 
 * Displays a scrollable list of chat messages
 * 
 * Auto-scrolling Implementation:
 * 1. Uses useRef to reference the bottom of the message list
 * 2. useEffect watches the messages array
 * 3. When messages change, scrollIntoView is called
 * 4. This automatically scrolls to show the latest message
 * 5. smooth: true provides animated scrolling
 * 
 * Benefits:
 * - Users always see new messages without manual scrolling
 * - Smooth animation provides better UX
 * - Works for both initial load and new messages
 */
const MessageList: React.FC<MessageListProps> = ({ messages }) => {
  const bottomRef = useRef<HTMLDivElement>(null);

  /**
   * Auto-scroll to bottom when messages change
   */
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center text-gray-400">
          <svg
            className="w-16 h-16 mx-auto mb-4 opacity-50"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
            />
          </svg>
          <p className="text-lg">No messages yet</p>
          <p className="text-sm mt-2">Start the conversation!</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto py-4">
      {messages.map((message) => (
        <ChatMessage key={message.id} message={message} />
      ))}
      {/* Invisible element at the bottom for auto-scrolling */}
      <div ref={bottomRef} />
    </div>
  );
};

export default MessageList;
