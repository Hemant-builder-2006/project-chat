import React from 'react';
import { KanbanCard as KanbanCardType } from '../../types';

interface KanbanCardProps {
  card: KanbanCardType;
  onEdit?: (cardId: string, newContent: string) => void;
  onDelete?: (cardId: string) => void;
}

const KanbanCard: React.FC<KanbanCardProps> = ({ card, onEdit, onDelete }) => {
  const [isEditing, setIsEditing] = React.useState(false);
  const [editContent, setEditContent] = React.useState(card.content);

  const handleSave = () => {
    if (onEdit && editContent.trim()) {
      onEdit(card.id, editContent);
      setIsEditing(false);
    }
  };

  const handleCancel = () => {
    setEditContent(card.content);
    setIsEditing(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSave();
    } else if (e.key === 'Escape') {
      handleCancel();
    }
  };

  return (
    <div className="bg-dark-surface rounded-lg p-3 mb-2 shadow-md border border-gray-700 hover:border-gray-600 transition-colors group">
      {isEditing ? (
        <div className="space-y-2">
          <textarea
            value={editContent}
            onChange={(e) => setEditContent(e.target.value)}
            onKeyDown={handleKeyDown}
            className="w-full bg-dark-bg text-white p-2 rounded border border-gray-600 focus:border-accent-primary focus:outline-none resize-none"
            rows={3}
            autoFocus
          />
          <div className="flex gap-2">
            <button
              onClick={handleSave}
              className="px-3 py-1 bg-accent-primary text-white rounded text-sm hover:bg-accent-primary/90 transition-colors"
            >
              Save
            </button>
            <button
              onClick={handleCancel}
              className="px-3 py-1 bg-gray-700 text-white rounded text-sm hover:bg-gray-600 transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      ) : (
        <div className="flex items-start justify-between gap-2">
          <p 
            className="text-white text-sm flex-1 cursor-pointer"
            onClick={() => setIsEditing(true)}
          >
            {card.content}
          </p>
          <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
            <button
              onClick={() => setIsEditing(true)}
              className="p-1 text-gray-400 hover:text-accent-primary transition-colors"
              title="Edit card"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </button>
            {onDelete && (
              <button
                onClick={() => onDelete(card.id)}
                className="p-1 text-gray-400 hover:text-red-500 transition-colors"
                title="Delete card"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default KanbanCard;
