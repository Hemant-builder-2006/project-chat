/**
 * API Service Functions
 * 
 * This file contains all API calls to the backend.
 * Organized by feature: Auth, Groups, Channels, Messages, Tasks, Documents, Kanban, AI, WebRTC
 */

import api from './api';
import { 
  User, 
  Group, 
  Channel, 
  Message, 
  Task,
  LoginCredentials,
  RegisterCredentials,
  AuthResponse 
} from '../types';

// ============================================================================
// Authentication API
// ============================================================================

export const authAPI = {
  /**
   * Login user
   * POST /api/auth/login
   */
  login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
    const formData = new URLSearchParams();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);
    
    const response = await api.post<AuthResponse>('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  },

  /**
   * Register new user
   * POST /api/auth/register
   */
  register: async (credentials: RegisterCredentials): Promise<User> => {
    const response = await api.post<User>('/auth/register', credentials);
    return response.data;
  },

  /**
   * Get current user
   * GET /api/auth/me
   */
  getCurrentUser: async (): Promise<User> => {
    const response = await api.get<User>('/auth/me');
    return response.data;
  },

  /**
   * Refresh access token
   * POST /api/auth/refresh
   */
  refreshToken: async (refreshToken: string): Promise<{ access_token: string }> => {
    const response = await api.post('/auth/refresh', { refresh_token: refreshToken });
    return response.data;
  },
};

// ============================================================================
// Groups API
// ============================================================================

export const groupsAPI = {
  /**
   * Get all groups user is member of
   * GET /api/groups
   */
  getAll: async (): Promise<Group[]> => {
    const response = await api.get<Group[]>('/groups');
    return response.data;
  },

  /**
   * Get specific group details
   * GET /api/groups/{group_id}
   */
  getById: async (groupId: string): Promise<Group> => {
    const response = await api.get<Group>(`/groups/${groupId}`);
    return response.data;
  },

  /**
   * Create new group
   * POST /api/groups
   */
  create: async (name: string): Promise<Group> => {
    const response = await api.post<Group>('/groups', { name });
    return response.data;
  },

  /**
   * Get group members
   * GET /api/groups/{group_id}/members
   */
  getMembers: async (groupId: string): Promise<User[]> => {
    const response = await api.get<User[]>(`/groups/${groupId}/members`);
    return response.data;
  },

  /**
   * Add member to group
   * POST /api/groups/{group_id}/members
   */
  addMember: async (groupId: string, userId: string, role: string = 'member'): Promise<void> => {
    await api.post(`/groups/${groupId}/members`, { user_id: userId, role });
  },
};

// ============================================================================
// Channels API
// ============================================================================

export const channelsAPI = {
  /**
   * Get all channels in a group
   * GET /api/groups/{group_id}/channels
   */
  getByGroup: async (groupId: string): Promise<Channel[]> => {
    const response = await api.get<Channel[]>(`/groups/${groupId}/channels`);
    return response.data;
  },

  /**
   * Create new channel
   * POST /api/groups/{group_id}/channels
   */
  create: async (groupId: string, name: string, type: string): Promise<Channel> => {
    const response = await api.post<Channel>(`/groups/${groupId}/channels`, { name, type });
    return response.data;
  },
};

// ============================================================================
// Messages API
// ============================================================================

export const messagesAPI = {
  /**
   * Get messages in a channel
   * GET /api/channels/{channel_id}/messages
   */
  getByChannel: async (channelId: string, limit: number = 50, skip: number = 0): Promise<Message[]> => {
    const response = await api.get<Message[]>(`/channels/${channelId}/messages`, {
      params: { limit, skip }
    });
    return response.data;
  },

  /**
   * Send message to channel
   * POST /api/channels/{channel_id}/messages
   */
  send: async (channelId: string, content: string, parentId?: string): Promise<Message> => {
    const response = await api.post<Message>(`/channels/${channelId}/messages`, {
      content,
      parent_message_id: parentId
    });
    return response.data;
  },

  /**
   * Delete message
   * DELETE /api/messages/{message_id}
   */
  delete: async (messageId: string): Promise<void> => {
    await api.delete(`/messages/${messageId}`);
  },
};

// ============================================================================
// Tasks API (Todo Lists)
// ============================================================================

export const tasksAPI = {
  /**
   * Get tasks in a TODO channel
   * GET /api/channels/{channel_id}/tasks
   */
  getByChannel: async (channelId: string): Promise<Task[]> => {
    const response = await api.get<Task[]>(`/channels/${channelId}/tasks`);
    return response.data;
  },

  /**
   * Create new task
   * POST /api/channels/{channel_id}/tasks
   */
  create: async (channelId: string, content: string, assigneeId?: string): Promise<Task> => {
    const response = await api.post<Task>(`/channels/${channelId}/tasks`, {
      content,
      assignee_id: assigneeId
    });
    return response.data;
  },

  /**
   * Update task
   * PUT /api/tasks/{task_id}
   */
  update: async (taskId: string, updates: Partial<Task>): Promise<Task> => {
    const response = await api.put<Task>(`/tasks/${taskId}`, updates);
    return response.data;
  },

  /**
   * Delete task
   * DELETE /api/tasks/{task_id}
   */
  delete: async (taskId: string): Promise<void> => {
    await api.delete(`/tasks/${taskId}`);
  },
};

// ============================================================================
// Documents API
// ============================================================================

export const documentsAPI = {
  /**
   * Get document content
   * GET /api/channels/{channel_id}/document
   */
  get: async (channelId: string): Promise<{ content: string }> => {
    const response = await api.get(`/channels/${channelId}/document`);
    return response.data;
  },

  /**
   * Update document content
   * PUT /api/channels/{channel_id}/document
   */
  update: async (channelId: string, content: string): Promise<{ content: string }> => {
    const response = await api.put(`/channels/${channelId}/document`, { content });
    return response.data;
  },
};

// ============================================================================
// Kanban API
// ============================================================================

export const kanbanAPI = {
  /**
   * Get kanban board with columns and cards
   * GET /api/channels/{channel_id}/kanban
   */
  getBoard: async (channelId: string): Promise<any> => {
    const response = await api.get(`/channels/${channelId}/kanban`);
    return response.data;
  },

  /**
   * Create new column
   * POST /api/channels/{channel_id}/kanban/columns
   */
  createColumn: async (channelId: string, title: string, order: number): Promise<any> => {
    const response = await api.post(`/channels/${channelId}/kanban/columns`, { title, order });
    return response.data;
  },

  /**
   * Create new card
   * POST /api/kanban/columns/{column_id}/cards
   */
  createCard: async (columnId: string, content: string, order: number): Promise<any> => {
    const response = await api.post(`/kanban/columns/${columnId}/cards`, { content, order });
    return response.data;
  },

  /**
   * Update card
   * PUT /api/kanban/cards/{card_id}
   */
  updateCard: async (cardId: string, updates: any): Promise<any> => {
    const response = await api.put(`/kanban/cards/${cardId}`, updates);
    return response.data;
  },

  /**
   * Move card to different column
   * PUT /api/kanban/cards/{card_id}/move
   */
  moveCard: async (cardId: string, columnId: string, newOrder: number): Promise<any> => {
    const response = await api.put(`/kanban/cards/${cardId}/move`, {
      column_id: columnId,
      new_order: newOrder
    });
    return response.data;
  },
};

// ============================================================================
// AI API
// ============================================================================

export const aiAPI = {
  /**
   * Semantic search across documents
   * POST /api/ai/search
   */
  search: async (query: string, channelIds?: string[]): Promise<any> => {
    const response = await api.post('/ai/search', {
      query,
      channel_ids: channelIds
    });
    return response.data;
  },

  /**
   * Summarize channel messages
   * POST /api/ai/summarize/{channel_id}
   */
  summarize: async (channelId: string, style: 'concise' | 'detailed' | 'bullet' = 'concise'): Promise<any> => {
    const response = await api.post(`/ai/summarize/${channelId}`, { style });
    return response.data;
  },

  /**
   * Upload document for AI indexing
   * POST /api/ai/upload/{channel_id}
   */
  uploadDocument: async (channelId: string, file: File): Promise<any> => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post(`/ai/upload/${channelId}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  /**
   * Chat with AI
   * POST /api/ai/chat
   */
  chat: async (message: string, model?: string): Promise<any> => {
    const response = await api.post('/ai/chat', { message, model });
    return response.data;
  },

  /**
   * Check AI services health
   * GET /api/ai/health
   */
  checkHealth: async (): Promise<any> => {
    const response = await api.get('/ai/health');
    return response.data;
  },

  /**
   * List available AI models
   * GET /api/ai/models
   */
  listModels: async (): Promise<string[]> => {
    const response = await api.get('/ai/models');
    return response.data;
  },
};

// ============================================================================
// WebRTC API
// ============================================================================

export const webrtcAPI = {
  /**
   * Get TURN server credentials
   * GET /api/webrtc/turn-credentials
   */
  getTurnCredentials: async (): Promise<any> => {
    const response = await api.get('/webrtc/turn-credentials');
    return response.data;
  },

  /**
   * Get ICE servers configuration
   * GET /api/webrtc/ice-servers
   */
  getIceServers: async (): Promise<RTCConfiguration> => {
    const response = await api.get<RTCConfiguration>('/webrtc/ice-servers');
    return response.data;
  },
};

// ============================================================================
// Files API
// ============================================================================

export const filesAPI = {
  /**
   * Upload file
   * POST /api/files/upload
   */
  upload: async (file: File, type: 'avatar' | 'attachment' | 'document' | 'image' = 'attachment'): Promise<any> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('type', type);
    
    const response = await api.post('/files/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};

// ============================================================================
// Health Check API
// ============================================================================

export const healthAPI = {
  /**
   * Check API health
   * GET /health
   */
  check: async (): Promise<{ status: string; version: string }> => {
    const response = await api.get('/health');
    return response.data;
  },
};
