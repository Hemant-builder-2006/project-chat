import React from 'react';
import GroupHeader from './GroupHeader';
import ChannelList from './ChannelList';
import { Channel, DM } from '../types';

interface ChannelColumnProps {
  groupName: string | null;
  channels: Channel[];
  directMessages: DM[];
  selectedChannelId: string | null;
  isDmView: boolean;
  onSelectChannel: (channelId: string, isDm: boolean) => void;
}

/**
 * ChannelColumn Component
 * 
 * Orchestrates the middle column display:
 * - GroupHeader at the top (shows group name or "Direct Messages")
 * - ChannelList below (shows channels or DMs based on isDmView)
 * 
 * How it determines what to display:
 * - If isDmView is true: Display "Direct Messages" header and DM list
 * - If isDmView is false: Display group name and channel list
 * - Passes down all necessary props to child components
 */
const ChannelColumn: React.FC<ChannelColumnProps> = ({
  groupName,
  channels,
  directMessages,
  selectedChannelId,
  isDmView,
  onSelectChannel,
}) => {
  const displayTitle = isDmView ? 'Direct Messages' : (groupName || 'Select a group');

  return (
    <div className="flex flex-col h-full">
      <GroupHeader title={displayTitle} />
      <ChannelList
        channels={channels}
        directMessages={directMessages}
        selectedChannelId={selectedChannelId}
        isDmView={isDmView}
        onSelectChannel={onSelectChannel}
      />
    </div>
  );
};

export default ChannelColumn;
