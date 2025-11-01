import React, { useState, useEffect } from 'react';
import api from '../../services/api';
import { KanbanColumn, KanbanCard as KanbanCardType } from '../../types';
import KanbanCard from './KanbanCard';

interface KanbanViewProps {
  channelId: string;
}

const KanbanView: React.FC<KanbanViewProps> = ({ channelId }) => {
  const [columns, setColumns] = useState<KanbanColumn[]>([]);
  const [cards, setCards] = useState<KanbanCardType[]>([]);
  const [isAddingColumn, setIsAddingColumn] = useState(false);
  const [newColumnTitle, setNewColumnTitle] = useState('');
  const [addingCardToColumn, setAddingCardToColumn] = useState<string | null>(null);
  const [newCardContent, setNewCardContent] = useState('');

  // Fetch Kanban board data on mount
  useEffect(() => {
    const fetchKanbanData = async () => {
      try {
        const response = await api.get(`/channels/${channelId}/kanban`);
        setColumns(response.data.columns || []);
        setCards(response.data.cards || []);
      } catch (error) {
        console.error('Error fetching kanban data:', error);
        // Initialize with default columns if none exist
        setColumns([
          { id: '1', title: 'To Do', cardIds: [] },
          { id: '2', title: 'In Progress', cardIds: [] },
          { id: '3', title: 'Done', cardIds: [] },
        ]);
        setCards([]);
      }
    };

    fetchKanbanData();
  }, [channelId]);

  // Add new column
  const handleAddColumn = async () => {
    if (!newColumnTitle.trim()) return;

    try {
      const response = await api.post(`/channels/${channelId}/kanban/columns`, {
        title: newColumnTitle,
      });
      setColumns([...columns, response.data]);
      setNewColumnTitle('');
      setIsAddingColumn(false);
    } catch (error) {
      console.error('Error adding column:', error);
      // Fallback for demo
      const newColumn: KanbanColumn = {
        id: Date.now().toString(),
        title: newColumnTitle,
        cardIds: [],
      };
      setColumns([...columns, newColumn]);
      setNewColumnTitle('');
      setIsAddingColumn(false);
    }
  };

  // Add new card to column
  const handleAddCard = async (columnId: string) => {
    if (!newCardContent.trim()) return;

    try {
      const response = await api.post(`/channels/${channelId}/kanban/cards`, {
        columnId,
        content: newCardContent,
      });
      const newCard: KanbanCardType = response.data;
      setCards([...cards, newCard]);
      setColumns(columns.map(col =>
        col.id === columnId
          ? { ...col, cardIds: [...col.cardIds, newCard.id] }
          : col
      ));
      setNewCardContent('');
      setAddingCardToColumn(null);
    } catch (error) {
      console.error('Error adding card:', error);
      // Fallback for demo
      const newCard: KanbanCardType = {
        id: Date.now().toString(),
        content: newCardContent,
        columnId,
      };
      setCards([...cards, newCard]);
      setColumns(columns.map(col =>
        col.id === columnId
          ? { ...col, cardIds: [...col.cardIds, newCard.id] }
          : col
      ));
      setNewCardContent('');
      setAddingCardToColumn(null);
    }
  };

  // Edit card content
  const handleEditCard = async (cardId: string, newContent: string) => {
    try {
      await api.put(`/channels/${channelId}/kanban/cards/${cardId}`, {
        content: newContent,
      });
      setCards(cards.map(card =>
        card.id === cardId ? { ...card, content: newContent } : card
      ));
    } catch (error) {
      console.error('Error editing card:', error);
      // Fallback for demo
      setCards(cards.map(card =>
        card.id === cardId ? { ...card, content: newContent } : card
      ));
    }
  };

  // Delete card
  const handleDeleteCard = async (cardId: string) => {
    try {
      await api.delete(`/channels/${channelId}/kanban/cards/${cardId}`);
      const card = cards.find(c => c.id === cardId);
      if (card) {
        setColumns(columns.map(col =>
          col.id === card.columnId
            ? { ...col, cardIds: col.cardIds.filter(id => id !== cardId) }
            : col
        ));
      }
      setCards(cards.filter(c => c.id !== cardId));
    } catch (error) {
      console.error('Error deleting card:', error);
      // Fallback for demo
      const card = cards.find(c => c.id === cardId);
      if (card) {
        setColumns(columns.map(col =>
          col.id === card.columnId
            ? { ...col, cardIds: col.cardIds.filter(id => id !== cardId) }
            : col
        ));
      }
      setCards(cards.filter(c => c.id !== cardId));
    }
  };

  // Delete column
  const handleDeleteColumn = async (columnId: string) => {
    if (!confirm('Delete this column and all its cards?')) return;

    try {
      await api.delete(`/channels/${channelId}/kanban/columns/${columnId}`);
      setColumns(columns.filter(col => col.id !== columnId));
      setCards(cards.filter(card => card.columnId !== columnId));
    } catch (error) {
      console.error('Error deleting column:', error);
      // Fallback for demo
      setColumns(columns.filter(col => col.id !== columnId));
      setCards(cards.filter(card => card.columnId !== columnId));
    }
  };

  return (
    <div className="flex flex-col h-full bg-dark-bg">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-3 bg-dark-surface border-b border-gray-700">
        <h2 className="text-lg font-semibold text-white">Kanban Board</h2>
        <button
          onClick={() => setIsAddingColumn(true)}
          className="px-4 py-2 bg-accent-primary text-white rounded-lg hover:bg-accent-primary/90 transition-colors"
        >
          + Add Column
        </button>
      </div>

      {/* Kanban Board */}
      <div className="flex-1 overflow-x-auto overflow-y-hidden">
        <div className="flex h-full p-4 gap-4">
          {/* Columns */}
          {columns.map(column => {
            const columnCards = cards.filter(card =>
              column.cardIds.includes(card.id)
            );

            return (
              <div
                key={column.id}
                className="flex-shrink-0 w-72 bg-gray-800 rounded-lg flex flex-col"
              >
                {/* Column Header */}
                <div className="flex items-center justify-between p-3 border-b border-gray-700">
                  <div className="flex items-center gap-2">
                    <h3 className="font-semibold text-white">{column.title}</h3>
                    <span className="text-xs text-gray-400 bg-gray-700 px-2 py-1 rounded">
                      {columnCards.length}
                    </span>
                  </div>
                  <button
                    onClick={() => handleDeleteColumn(column.id)}
                    className="p-1 text-gray-400 hover:text-red-500 transition-colors"
                    title="Delete column"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>

                {/* Cards Container */}
                <div className="flex-1 overflow-y-auto p-3">
                  {columnCards.map(card => (
                    <KanbanCard
                      key={card.id}
                      card={card}
                      onEdit={handleEditCard}
                      onDelete={handleDeleteCard}
                    />
                  ))}

                  {/* Add Card Form */}
                  {addingCardToColumn === column.id ? (
                    <div className="bg-dark-surface rounded-lg p-3 border border-accent-primary">
                      <textarea
                        value={newCardContent}
                        onChange={(e) => setNewCardContent(e.target.value)}
                        placeholder="Enter card content..."
                        className="w-full bg-dark-bg text-white p-2 rounded border border-gray-600 focus:border-accent-primary focus:outline-none resize-none mb-2"
                        rows={3}
                        autoFocus
                        onKeyDown={(e) => {
                          if (e.key === 'Enter' && !e.shiftKey) {
                            e.preventDefault();
                            handleAddCard(column.id);
                          } else if (e.key === 'Escape') {
                            setAddingCardToColumn(null);
                            setNewCardContent('');
                          }
                        }}
                      />
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleAddCard(column.id)}
                          className="px-3 py-1 bg-accent-primary text-white rounded text-sm hover:bg-accent-primary/90 transition-colors"
                        >
                          Add Card
                        </button>
                        <button
                          onClick={() => {
                            setAddingCardToColumn(null);
                            setNewCardContent('');
                          }}
                          className="px-3 py-1 bg-gray-700 text-white rounded text-sm hover:bg-gray-600 transition-colors"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : (
                    <button
                      onClick={() => setAddingCardToColumn(column.id)}
                      className="w-full p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg transition-colors text-sm text-left"
                    >
                      + Add a card
                    </button>
                  )}
                </div>
              </div>
            );
          })}

          {/* Add Column Form */}
          {isAddingColumn && (
            <div className="flex-shrink-0 w-72 bg-gray-800 rounded-lg p-3">
              <input
                type="text"
                value={newColumnTitle}
                onChange={(e) => setNewColumnTitle(e.target.value)}
                placeholder="Enter column title..."
                className="w-full bg-dark-bg text-white p-2 rounded border border-gray-600 focus:border-accent-primary focus:outline-none mb-2"
                autoFocus
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    handleAddColumn();
                  } else if (e.key === 'Escape') {
                    setIsAddingColumn(false);
                    setNewColumnTitle('');
                  }
                }}
              />
              <div className="flex gap-2">
                <button
                  onClick={handleAddColumn}
                  className="px-3 py-1 bg-accent-primary text-white rounded text-sm hover:bg-accent-primary/90 transition-colors"
                >
                  Add Column
                </button>
                <button
                  onClick={() => {
                    setIsAddingColumn(false);
                    setNewColumnTitle('');
                  }}
                  className="px-3 py-1 bg-gray-700 text-white rounded text-sm hover:bg-gray-600 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default KanbanView;
