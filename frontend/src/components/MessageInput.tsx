import React, { useState, FormEvent, KeyboardEvent } from 'react';

interface MessageInputProps {
  sendMessage: (content: string) => void;
}

/**
 * MessageInput Component
 * 
 * Input field for composing and sending messages
 * 
 * State Management:
 * - Uses controlled component pattern with useState
 * - Input value stored in state and updated via onChange
 * - State is cleared after sending message
 * 
 * Features:
 * - Send on Enter key press (Shift+Enter for new line)
 * - Send button click
 * - Disabled state while input is empty
 * - Auto-resize textarea (not implemented yet)
 */
const MessageInput: React.FC<MessageInputProps> = ({ sendMessage }) => {
  const [message, setMessage] = useState('');

  /**
   * Handle form submission
   */
  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (message.trim()) {
      sendMessage(message.trim());
      setMessage(''); // Clear input after sending
    }
  };

  /**
   * Handle Enter key press
   * Enter alone: Send message
   * Shift+Enter: New line
   */
  const handleKeyPress = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (message.trim()) {
        sendMessage(message.trim());
        setMessage('');
      }
    }
  };

  return (
    <div className="border-t border-gray-600 bg-gray-700 p-4">
      <form onSubmit={handleSubmit} className="flex items-end space-x-2">
        {/* Message Input */}
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type a message..."
          className="flex-1 bg-gray-600 text-white rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-accent-primary resize-none max-h-32 min-h-[44px]"
          rows={1}
        />
        
        {/* Send Button */}
        <button
          type="submit"
          disabled={!message.trim()}
          className="bg-accent-primary hover:bg-accent-hover disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-lg px-6 py-3 font-medium transition-colors duration-200 flex items-center space-x-2"
        >
          <span>Send</span>
          <svg
            className="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
            />
          </svg>
        </button>
      </form>
    </div>
  );
};

export default MessageInput;
