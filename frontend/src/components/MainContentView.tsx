import React from 'react';
import ChatView from './ChatView';
import TodoListView from './views/TodoListView';
import DocumentEditorView from './views/DocumentEditorView';
import KanbanView from './views/KanbanView';
import VoiceChannelUI from './views/VoiceChannelUI';
import { ChannelType } from '../types';

interface MainContentViewProps {
  selectedChannelId: string | null;
  isDmView: boolean;
  channelType?: ChannelType;
}

/**
 * MainContentView Component
 * 
 * Main content area (rightmost column) that renders different views based on context
 * Conditionally renders:
 * - ChatView (for TEXT channels and DMs)
 * - TodoListView (for TODO channels)
 * - DocumentEditorView (for DOC channels)
 * - KanbanView (for KANBAN channels)
 * - VoiceView (for VOICE channels - coming soon)
 */
const MainContentView: React.FC<MainContentViewProps> = ({
  selectedChannelId,
  isDmView,
  channelType,
}) => {
  if (!selectedChannelId) {
    return (
      <div className="flex items-center justify-center h-full bg-gray-700">
        <div className="text-center space-y-4 px-8">
          <div className="w-24 h-24 mx-auto bg-gray-600 rounded-full flex items-center justify-center">
            <svg
              className="w-12 h-12 text-gray-400"
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
          </div>
          <div>
            <h2 className="text-xl font-semibold text-gray-200 mb-2">
              Welcome to Your Workspace
            </h2>
            <p className="text-gray-400">
              Select a channel or direct message to start collaborating
            </p>
          </div>
        </div>
      </div>
    );
  }

  // For DM view, always render ChatView
  if (isDmView) {
    return <ChatView channelId={null} dmId={selectedChannelId} />;
  }

  // For channels, render appropriate view based on channel type
  switch (channelType) {
    case 'TEXT':
      return <ChatView channelId={selectedChannelId} dmId={null} />;
    
    case 'TODO':
      return <TodoListView channelId={selectedChannelId} />;
    
    case 'DOC':
      return <DocumentEditorView channelId={selectedChannelId} />;
    
    case 'KANBAN':
      return <KanbanView channelId={selectedChannelId} />;
    
    case 'VOICE':
      return <VoiceChannelUI channelId={selectedChannelId} />;
    
    case 'VIDEO':
      // Placeholder for video channels (group video meetings)
      return (
        <div className="flex items-center justify-center h-full bg-gray-700">
          <div className="text-center space-y-4 px-8">
            <div className="w-24 h-24 mx-auto bg-gray-600 rounded-full flex items-center justify-center">
              <svg
                className="w-12 h-12 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
                />
              </svg>
            </div>
            <div>
              <h2 className="text-xl font-semibold text-gray-200 mb-2">
                Video Channel
              </h2>
              <p className="text-gray-400">
                Video group channels are coming soon!
              </p>
            </div>
          </div>
        </div>
      );
    
    default:
      // Default to ChatView if type is undefined or unknown
      return <ChatView channelId={selectedChannelId} dmId={null} />;
  }
};

export default MainContentView;
