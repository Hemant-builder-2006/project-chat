import React from 'react';
import ChatView from './ChatView';

interface MainContentViewProps {
  selectedChannelId: string | null;
  isDmView: boolean;
}

/**
 * MainContentView Component
 * 
 * Main content area (rightmost column) that renders different views based on context
 * Currently renders:
 * - ChatView (for TEXT channels and DMs)
 * 
 * Future enhancements will conditionally render:
 * - TodoListView (for TODO channels)
 * - KanbanView (for KANBAN channels)
 * - VoiceView (for VOICE channels)
 * - VideoView (for VIDEO channels)
 */
const MainContentView: React.FC<MainContentViewProps> = ({
  selectedChannelId,
  isDmView,
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

  // Render ChatView for selected channel or DM
  return (
    <ChatView 
      channelId={isDmView ? null : selectedChannelId}
      dmId={isDmView ? selectedChannelId : null}
    />
  );
};

export default MainContentView;
