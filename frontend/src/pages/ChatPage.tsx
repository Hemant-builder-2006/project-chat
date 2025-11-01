import React, { useState, useEffect } from 'react';
import AppLayout from '../components/AppLayout';
import GroupList from '../components/GroupList';
import ChannelColumn from '../components/ChannelColumn';
import MainContentView from '../components/MainContentView';
import { useGroups } from '../hooks/useGroups';
import { useChannels } from '../hooks/useChannels';
import { useDirectMessages } from '../hooks/useDirectMessages';
import { ChannelType } from '../types';

/**
 * ChatPage Component
 * 
 * Main container for the entire application interface
 * Manages state and data flow between all sub-components
 * 
 * State Management:
 * - selectedGroupId: Which group is currently selected
 * - selectedChannelId: Which channel/DM is currently selected
 * - isDmView: Whether viewing DMs or group channels
 * 
 * Data Flow Example (User clicks group icon -> channel name):
 * 1. User clicks group icon in GroupList
 * 2. handleSelectGroup is called with groupId
 * 3. setSelectedGroupId updates state
 * 4. setIsDmView(false) switches to group view
 * 5. useChannels hook detects groupId change and fetches new channels
 * 6. ChannelColumn receives new channels and re-renders
 * 7. User clicks channel name in ChannelList
 * 8. handleSelectChannel is called with channelId
 * 9. setSelectedChannelId updates state
 * 10. MainContentView receives new channelId and re-renders
 */
const ChatPage: React.FC = () => {
  // State for navigation
  const [selectedGroupId, setSelectedGroupId] = useState<string | null>(null);
  const [selectedChannelId, setSelectedChannelId] = useState<string | null>(null);
  const [selectedChannelType, setSelectedChannelType] = useState<ChannelType | undefined>(undefined);
  const [isDmView, setIsDmView] = useState(false);

  // Fetch data using custom hooks
  const { groups, isLoading: groupsLoading, error: groupsError } = useGroups();
  const { channels } = useChannels(selectedGroupId);
  const { directMessages, isLoading: dmsLoading, error: dmsError } = useDirectMessages();

  /**
   * Auto-select first group on initial load
   */
  useEffect(() => {
    if (!groupsLoading && groups.length > 0 && !selectedGroupId && !isDmView) {
      setSelectedGroupId(groups[0].id);
    }
  }, [groups, groupsLoading, selectedGroupId, isDmView]);

  /**
   * Handler: Select a group
   */
  const handleSelectGroup = (groupId: string) => {
    setSelectedGroupId(groupId);
    setIsDmView(false);
    setSelectedChannelId(null); // Clear channel selection when switching groups
  };

  /**
   * Handler: Select DMs view
   */
  const handleSelectDMs = () => {
    setIsDmView(true);
    setSelectedGroupId(null);
    setSelectedChannelId(null); // Clear channel selection when switching to DMs
  };

  /**
   * Handler: Select a channel or DM
   */
  const handleSelectChannel = (channelId: string, isDm: boolean) => {
    setSelectedChannelId(channelId);
    // Ensure isDmView matches the selection type
    if (isDm && !isDmView) {
      setIsDmView(true);
      setSelectedChannelType(undefined);
    } else if (!isDm) {
      // Find the channel type from the channels array
      const selectedChannel = channels.find(c => c.id === channelId);
      setSelectedChannelType(selectedChannel?.type);
    }
  };

  /**
   * Determine current group name for display
   */
  const currentGroupName = selectedGroupId
    ? groups.find(g => g.id === selectedGroupId)?.name || null
    : null;

  /**
   * Show loading spinner while initial data loads
   */
  if (groupsLoading || dmsLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-900">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-accent-primary"></div>
          <p className="mt-4 text-gray-400">Loading workspace...</p>
        </div>
      </div>
    );
  }

  /**
   * Show error if data fetch failed
   */
  if (groupsError || dmsError) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-900">
        <div className="text-center space-y-4 max-w-md">
          <div className="text-red-500 text-5xl">⚠️</div>
          <h2 className="text-xl font-semibold text-white">Failed to Load Workspace</h2>
          <p className="text-gray-400">{groupsError || dmsError}</p>
          <button
            onClick={() => window.location.reload()}
            className="btn-primary"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  /**
   * Render main layout
   */
  return (
    <AppLayout
      groupList={
        <GroupList
          groups={groups}
          selectedGroupId={selectedGroupId}
          onSelectGroup={handleSelectGroup}
          onSelectDMs={handleSelectDMs}
        />
      }
      channelColumn={
        <ChannelColumn
          groupName={currentGroupName}
          channels={channels}
          directMessages={directMessages}
          selectedChannelId={selectedChannelId}
          isDmView={isDmView}
          onSelectChannel={handleSelectChannel}
        />
      }
      mainContent={
        <MainContentView
          selectedChannelId={selectedChannelId}
          isDmView={isDmView}
          channelType={selectedChannelType}
        />
      }
    />
  );
};

export default ChatPage;
