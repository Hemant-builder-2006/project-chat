import React, { useState, useEffect, FormEvent } from 'react';
import TodoItem from './TodoItem';
import { Task } from '../../types';
import api from '../../services/api';

interface TodoListViewProps {
  channelId: string;
}

/**
 * TodoListView Component
 * 
 * Main view for To-Do List channels
 * 
 * Data Fetching & Updates:
 * -------------------------
 * This component would fetch and update tasks using REST API endpoints:
 * 
 * 1. **Fetch Tasks** (useEffect on mount):
 *    GET /api/channels/{channelId}/tasks
 *    Returns: Task[]
 * 
 * 2. **Create Task** (handleAddTask):
 *    POST /api/channels/{channelId}/tasks
 *    Body: { content: string }
 *    Returns: Task
 * 
 * 3. **Toggle Task** (handleToggleTask):
 *    PATCH /api/channels/{channelId}/tasks/{taskId}
 *    Body: { isCompleted: boolean }
 *    Returns: Task
 * 
 * 4. **Delete Task** (handleDeleteTask):
 *    DELETE /api/channels/{channelId}/tasks/{taskId}
 *    Returns: 204 No Content
 * 
 * For real-time updates, we could also integrate WebSocket messages
 * to sync task changes across users in the same channel.
 */
const TodoListView: React.FC<TodoListViewProps> = ({ channelId }) => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [newTaskContent, setNewTaskContent] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  /**
   * Fetch tasks on component mount
   */
  useEffect(() => {
    const fetchTasks = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const response = await api.get<Task[]>(`/channels/${channelId}/tasks`);
        setTasks(response.data);
      } catch (err: any) {
        console.error('Error fetching tasks:', err);
        setError(err.response?.data?.detail || 'Failed to load tasks');
        // Use placeholder data for demo
        setTasks([
          {
            id: '1',
            content: 'Complete project documentation',
            isCompleted: false,
          },
          {
            id: '2',
            content: 'Review pull requests',
            isCompleted: true,
          },
          {
            id: '3',
            content: 'Update deployment pipeline',
            isCompleted: false,
            assigneeId: 'user1',
          },
        ]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchTasks();
  }, [channelId]);

  /**
   * Add a new task
   */
  const handleAddTask = async (e: FormEvent) => {
    e.preventDefault();
    if (!newTaskContent.trim()) return;

    try {
      const response = await api.post<Task>(`/channels/${channelId}/tasks`, {
        content: newTaskContent.trim(),
      });
      setTasks([...tasks, response.data]);
      setNewTaskContent('');
    } catch (err) {
      console.error('Error creating task:', err);
      // Fallback: Add locally with generated ID
      const newTask: Task = {
        id: Date.now().toString(),
        content: newTaskContent.trim(),
        isCompleted: false,
      };
      setTasks([...tasks, newTask]);
      setNewTaskContent('');
    }
  };

  /**
   * Toggle task completion status
   */
  const handleToggleTask = async (taskId: string) => {
    const task = tasks.find(t => t.id === taskId);
    if (!task) return;

    const updatedTask = { ...task, isCompleted: !task.isCompleted };

    // Optimistic update
    setTasks(tasks.map(t => (t.id === taskId ? updatedTask : t)));

    try {
      await api.patch(`/channels/${channelId}/tasks/${taskId}`, {
        isCompleted: updatedTask.isCompleted,
      });
    } catch (err) {
      console.error('Error toggling task:', err);
      // Revert on error
      setTasks(tasks.map(t => (t.id === taskId ? task : t)));
    }
  };

  /**
   * Delete a task
   */
  const handleDeleteTask = async (taskId: string) => {
    // Optimistic update
    setTasks(tasks.filter(t => t.id !== taskId));

    try {
      await api.delete(`/channels/${channelId}/tasks/${taskId}`);
    } catch (err) {
      console.error('Error deleting task:', err);
      // In production, you'd want to revert this or show an error
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-accent-primary mb-4"></div>
          <p className="text-gray-400">Loading tasks...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full bg-gray-700">
      {/* Header */}
      <div className="border-b border-gray-600 p-4">
        <h2 className="text-xl font-semibold text-white mb-4">To-Do List</h2>

        {/* Add Task Form */}
        <form onSubmit={handleAddTask} className="flex gap-2">
          <input
            type="text"
            value={newTaskContent}
            onChange={(e) => setNewTaskContent(e.target.value)}
            placeholder="Add a new task..."
            className="flex-1 bg-gray-600 text-white rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-accent-primary"
          />
          <button
            type="submit"
            disabled={!newTaskContent.trim()}
            className="bg-accent-primary hover:bg-accent-hover disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-lg px-6 py-2 font-medium transition-colors duration-200"
          >
            Add Task
          </button>
        </form>
      </div>

      {/* Task List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-2">
        {error && (
          <div className="bg-yellow-900/50 border border-yellow-700 rounded-lg p-3 mb-4">
            <p className="text-sm text-yellow-200">
              {error} (Using demo data)
            </p>
          </div>
        )}

        {tasks.length === 0 ? (
          <div className="text-center py-12">
            <svg
              className="w-16 h-16 mx-auto mb-4 text-gray-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
              />
            </svg>
            <p className="text-gray-400 text-lg">No tasks yet</p>
            <p className="text-gray-500 text-sm mt-2">Add your first task to get started!</p>
          </div>
        ) : (
          <>
            {/* Statistics */}
            <div className="flex items-center gap-4 text-sm text-gray-400 mb-4">
              <span>
                Total: <span className="text-white font-medium">{tasks.length}</span>
              </span>
              <span>
                Completed:{' '}
                <span className="text-green-400 font-medium">
                  {tasks.filter(t => t.isCompleted).length}
                </span>
              </span>
              <span>
                Pending:{' '}
                <span className="text-blue-400 font-medium">
                  {tasks.filter(t => !t.isCompleted).length}
                </span>
              </span>
            </div>

            {/* Task Items */}
            {tasks.map((task) => (
              <TodoItem
                key={task.id}
                task={task}
                onToggle={handleToggleTask}
                onDelete={handleDeleteTask}
              />
            ))}
          </>
        )}
      </div>
    </div>
  );
};

export default TodoListView;
