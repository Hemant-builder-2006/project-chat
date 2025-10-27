import React, { ReactNode } from 'react';

interface AppLayoutProps {
  groupList: ReactNode;
  channelColumn: ReactNode;
  mainContent: ReactNode;
}

/**
 * AppLayout Component
 * 
 * Implements the 3-column layout structure:
 * 1. Left Column (GroupList): Narrow fixed width - w-18 (72px)
 * 2. Middle Column (ChannelColumn): Medium flex width - w-60/w-72 (240px/288px)
 * 3. Right Column (MainContent): Wide flex to fill remaining space
 * 
 * Layout Choice: Flexbox
 * Why Flexbox over Grid?
 * - Flexbox is better for one-dimensional layouts (row-based here)
 * - Easier to make columns responsive and flexible
 * - Natural content-based sizing for middle column
 * - Better browser support for complex responsive behavior
 * - Simpler to handle dynamic content that might grow/shrink
 * 
 * Grid would be preferable for:
 * - Complex 2D layouts with rows and columns
 * - When you need precise alignment in both directions
 * - When you want to overlap elements
 * 
 * Dark Theme Colors:
 * - bg-gray-900 (#111827): Darkest - for outer column
 * - bg-gray-800 (#1f2937): Medium - for middle column
 * - bg-gray-700 (#374151): Lightest - for main content area
 */
const AppLayout: React.FC<AppLayoutProps> = ({ groupList, channelColumn, mainContent }) => {
  return (
    <div className="flex h-screen w-full overflow-hidden bg-gray-900">
      {/* Left Column - Group List (Narrow Fixed Width) */}
      <div className="w-18 flex-shrink-0 bg-gray-900 border-r border-gray-800">
        {groupList}
      </div>

      {/* Middle Column - Channel List (Medium Flex Width) */}
      <div className="w-60 flex-shrink-0 bg-gray-800 border-r border-gray-700">
        {channelColumn}
      </div>

      {/* Right Column - Main Content (Wide Flex) */}
      <div className="flex-1 bg-gray-700 overflow-hidden">
        {mainContent}
      </div>
    </div>
  );
};

export default AppLayout;
