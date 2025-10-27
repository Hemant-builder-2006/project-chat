import React from 'react';

interface GroupHeaderProps {
  title: string;
}

/**
 * GroupHeader Component
 * 
 * Displays the current group or "Direct Messages" title
 * at the top of the middle column
 */
const GroupHeader: React.FC<GroupHeaderProps> = ({ title }) => {
  return (
    <div className="h-12 px-4 flex items-center border-b border-gray-700 shadow-md bg-gray-800">
      <h2 className="text-white font-semibold text-sm truncate">
        {title}
      </h2>
    </div>
  );
};

export default GroupHeader;
