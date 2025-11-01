import React from 'react';
import { Task } from '../../types';

interface TodoItemProps {
  task: Task;
  onToggle: (taskId: string) => void;
  onDelete: (taskId: string) => void;
}

/**
 * TodoItem Component
 * 
 * Renders a single task item with checkbox, content, and delete button
 * 
 * Tailwind Utility Classes for "Completed" State:
 * - `line-through`: Applies strikethrough text decoration when completed
 * - `text-gray-400`: Dims the text color for completed tasks
 * - `opacity-60`: Reduces overall opacity for visual de-emphasis
 * 
 * The conditional className uses template literals to toggle these classes
 * based on the `task.isCompleted` boolean value
 */
const TodoItem: React.FC<TodoItemProps> = ({ task, onToggle, onDelete }) => {
  return (
    <div className="flex items-center gap-3 p-3 bg-gray-700 rounded-lg hover:bg-gray-600 transition-colors duration-150 group">
      {/* Custom Checkbox */}
      <button
        onClick={() => onToggle(task.id)}
        className={`flex-shrink-0 w-5 h-5 rounded border-2 transition-all duration-200 flex items-center justify-center ${
          task.isCompleted
            ? 'bg-accent-primary border-accent-primary'
            : 'border-gray-500 hover:border-accent-primary'
        }`}
        aria-label={task.isCompleted ? 'Mark as incomplete' : 'Mark as complete'}
      >
        {task.isCompleted && (
          <svg
            className="w-3 h-3 text-white"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={3}
              d="M5 13l4 4L19 7"
            />
          </svg>
        )}
      </button>

      {/* Task Content */}
      <div className="flex-1 min-w-0">
        <p
          className={`text-sm transition-all duration-200 ${
            task.isCompleted
              ? 'line-through text-gray-400 opacity-60'
              : 'text-white'
          }`}
        >
          {task.content}
        </p>
      </div>

      {/* Assignee Avatar Placeholder */}
      {task.assigneeId && (
        <div className="w-6 h-6 rounded-full bg-accent-primary flex items-center justify-center text-xs text-white font-medium">
          {task.assigneeId.slice(0, 2).toUpperCase()}
        </div>
      )}

      {/* Delete Button */}
      <button
        onClick={() => onDelete(task.id)}
        className="flex-shrink-0 w-6 h-6 rounded flex items-center justify-center text-gray-400 hover:text-red-500 hover:bg-red-900/20 transition-colors duration-150 opacity-0 group-hover:opacity-100"
        aria-label="Delete task"
      >
        <svg
          className="w-4 h-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M6 18L18 6M6 6l12 12"
          />
        </svg>
      </button>
    </div>
  );
};

export default TodoItem;
