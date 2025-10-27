import React from 'react';
import { Group } from '../types';

interface GroupListProps {
  groups: Group[];
  selectedGroupId: string | null;
  onSelectGroup: (groupId: string) => void;
  onSelectDMs: () => void;
}

/**
 * GroupList Component
 * 
 * Displays server/group icons in the leftmost narrow column
 * Features:
 * - DMs button at the top
 * - Group icons with initials fallback
 * - Visual indication of selected group (white side marker)
 * - Hover effects for better UX
 * - Tooltips showing group names
 * 
 * Styling Approach:
 * - Selected state: White left border (border-l-4 border-white)
 * - Hover state: Transforms to rounded-2xl shape (Discord-style)
 * - Default: rounded-3xl for pill shape
 * - Transition: smooth animation between states
 */
const GroupList: React.FC<GroupListProps> = ({
  groups,
  selectedGroupId,
  onSelectGroup,
  onSelectDMs,
}) => {
  /**
   * Generate initials from group name
   */
  const getInitials = (name: string): string => {
    return name
      .split(' ')
      .map(word => word[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  return (
    <div className="flex flex-col items-center py-3 space-y-2 h-full overflow-y-auto">
      {/* DMs Button - Always at top */}
      <button
        onClick={onSelectDMs}
        className="group relative w-12 h-12 flex items-center justify-center bg-accent-primary hover:bg-accent-hover rounded-3xl hover:rounded-2xl transition-all duration-200"
        title="Direct Messages"
      >
        <svg
          className="w-6 h-6 text-white"
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
        
        {/* Tooltip */}
        <span className="absolute left-full ml-4 px-2 py-1 bg-gray-900 text-white text-sm rounded opacity-0 group-hover:opacity-100 transition-opacity duration-200 whitespace-nowrap z-50">
          Direct Messages
        </span>
      </button>

      {/* Separator */}
      <div className="w-8 h-0.5 bg-gray-700 rounded-full"></div>

      {/* Group Icons */}
      {groups.map((group) => {
        const isSelected = selectedGroupId === group.id;
        
        return (
          <div key={group.id} className="relative">
            {/* Selection Indicator */}
            {isSelected && (
              <div className="absolute -left-3 top-1/2 transform -translate-y-1/2 w-1 h-10 bg-white rounded-r"></div>
            )}
            
            <button
              onClick={() => onSelectGroup(group.id)}
              className={`group relative w-12 h-12 flex items-center justify-center text-white font-semibold rounded-3xl transition-all duration-200 ${
                isSelected
                  ? 'bg-accent-primary rounded-2xl'
                  : 'bg-gray-700 hover:bg-accent-primary hover:rounded-2xl'
              }`}
              title={group.name}
            >
              {group.iconUrl ? (
                <img
                  src={group.iconUrl}
                  alt={group.name}
                  className="w-full h-full rounded-3xl group-hover:rounded-2xl transition-all duration-200"
                />
              ) : (
                <span className="text-sm">{getInitials(group.name)}</span>
              )}
              
              {/* Tooltip */}
              <span className="absolute left-full ml-4 px-2 py-1 bg-gray-900 text-white text-sm rounded opacity-0 group-hover:opacity-100 transition-opacity duration-200 whitespace-nowrap z-50">
                {group.name}
              </span>
            </button>
          </div>
        );
      })}

      {/* Add Group Button (Placeholder) */}
      <button
        className="group relative w-12 h-12 flex items-center justify-center bg-gray-700 hover:bg-green-600 text-green-500 hover:text-white rounded-3xl hover:rounded-2xl transition-all duration-200"
        title="Add a Server"
      >
        <svg
          className="w-6 h-6"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 4v16m8-8H4"
          />
        </svg>
        
        {/* Tooltip */}
        <span className="absolute left-full ml-4 px-2 py-1 bg-gray-900 text-white text-sm rounded opacity-0 group-hover:opacity-100 transition-opacity duration-200 whitespace-nowrap z-50">
          Add a Server
        </span>
      </button>
    </div>
  );
};

export default GroupList;
