import React from 'react';
import { Channel, DM } from '../types';

interface ChannelListProps {
  channels: Channel[];
  directMessages: DM[];
  selectedChannelId: string | null;
  isDmView: boolean;
  onSelectChannel: (channelId: string, isDm: boolean) => void;
}

/**
 * ChannelList Component
 * 
 * Conditionally renders either:
 * - Channels (grouped by type: TEXT, TODO, KANBAN, VOICE, VIDEO)
 * - Direct Messages
 * 
 * Conditional Rendering Logic:
 * 1. Check `isDmView` prop
 * 2. If true: Map over `directMessages` array
 * 3. If false: Group and map over `channels` array by type
 * 4. Highlight selected channel/DM with background color
 * 5. Use appropriate icons for different channel types
 */
const ChannelList: React.FC<ChannelListProps> = ({
  channels,
  directMessages,
  selectedChannelId,
  isDmView,
  onSelectChannel,
}) => {
  /**
   * Get icon for channel type
   */
  const getChannelIcon = (type: string): string => {
    switch (type) {
      case 'TEXT':
        return '#';
      case 'TODO':
        return '✓';
      case 'KANBAN':
        return '📋';
      case 'VOICE':
        return '🔊';
      case 'VIDEO':
        return '📹';
      default:
        return '#';
    }
  };

  /**
   * Group channels by type
   */
  const groupedChannels = channels.reduce((acc, channel) => {
    if (!acc[channel.type]) {
      acc[channel.type] = [];
    }
    acc[channel.type].push(channel);
    return acc;
  }, {} as Record<string, Channel[]>);

  if (isDmView) {
    // Render Direct Messages
    return (
      <div className="flex-1 overflow-y-auto py-2">
        {directMessages.length === 0 ? (
          <div className="px-4 py-8 text-center text-gray-400 text-sm">
            No direct messages yet
          </div>
        ) : (
          directMessages.map((dm) => (
            <button
              key={dm.id}
              onClick={() => onSelectChannel(dm.id, true)}
              className={`w-full px-4 py-2 flex items-center space-x-3 hover:bg-gray-700/50 transition-colors duration-150 ${
                selectedChannelId === dm.id ? 'bg-gray-700/70' : ''
              }`}
            >
              {/* Avatar */}
              <div className="w-8 h-8 rounded-full bg-accent-primary flex items-center justify-center text-white text-sm font-medium flex-shrink-0">
                {dm.avatarUrl ? (
                  <img src={dm.avatarUrl} alt={dm.userName} className="w-full h-full rounded-full" />
                ) : (
                  dm.userName[0].toUpperCase()
                )}
              </div>
              
              {/* User Info */}
              <div className="flex-1 text-left overflow-hidden">
                <p className="text-gray-200 text-sm font-medium truncate">{dm.userName}</p>
                {dm.lastMessage && (
                  <p className="text-gray-400 text-xs truncate">{dm.lastMessage}</p>
                )}
              </div>
              
              {/* Unread Badge */}
              {dm.unreadCount && dm.unreadCount > 0 && (
                <div className="bg-red-600 text-white text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center">
                  {dm.unreadCount > 9 ? '9+' : dm.unreadCount}
                </div>
              )}
            </button>
          ))
        )}
      </div>
    );
  }

  // Render Channels (grouped by type)
  return (
    <div className="flex-1 overflow-y-auto py-2">
      {channels.length === 0 ? (
        <div className="px-4 py-8 text-center text-gray-400 text-sm">
          No channels available
        </div>
      ) : (
        Object.entries(groupedChannels).map(([type, typeChannels]) => (
          <div key={type} className="mb-4">
            {/* Type Header */}
            <div className="px-4 py-1 text-xs font-semibold text-gray-400 uppercase tracking-wider">
              {type.toLowerCase()} Channels
            </div>
            
            {/* Channels of this type */}
            {typeChannels.map((channel) => (
              <button
                key={channel.id}
                onClick={() => onSelectChannel(channel.id, false)}
                className={`w-full px-4 py-2 flex items-center space-x-2 hover:bg-gray-700/50 transition-colors duration-150 ${
                  selectedChannelId === channel.id ? 'bg-gray-700/70' : ''
                }`}
              >
                <span className="text-gray-400 text-sm font-medium">
                  {getChannelIcon(channel.type)}
                </span>
                <span className={`text-sm flex-1 text-left truncate ${
                  selectedChannelId === channel.id ? 'text-white font-medium' : 'text-gray-300'
                }`}>
                  {channel.name}
                </span>
              </button>
            ))}
          </div>
        ))
      )}
    </div>
  );
};

export default ChannelList;
