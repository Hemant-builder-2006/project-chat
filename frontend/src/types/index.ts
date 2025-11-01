// User types
export interface User {
  id: string;
  username: string;
  email: string;
  avatarUrl?: string;
}

// Group types
export interface Group {
  id: string;
  name: string;
  iconUrl?: string;
}

// Channel types
export type ChannelType = 'TEXT' | 'TODO' | 'DOC' | 'KANBAN' | 'VOICE' | 'VIDEO';

export interface Channel {
  id: string;
  name: string;
  groupId: string;
  type: ChannelType;
  description?: string;
}

// Direct Message types
export interface DM {
  id: string;
  userName: string;
  avatarUrl?: string;
  lastMessage?: string;
  unreadCount?: number;
}

// Message types
export interface Message {
  id: string;
  content: string;
  senderName: string;
  senderId: string;
  timestamp: string;
  isOwnMessage: boolean;
  avatarUrl?: string;
}

// Auth types
export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterCredentials {
  username: string;
  email: string;
  password: string;
}

export interface AuthTokens {
  accessToken: string;
  refreshToken?: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token?: string;
  token_type: string;
  user: User;
}

// WebSocket types
export interface WebSocketContext {
  type: 'channel' | 'dm';
  id: string;
}

export interface WebSocketMessage {
  type: 'message' | 'typing' | 'presence';
  data: any;
}

// Productivity Feature Types

/**
 * Task Interface - For To-Do List Channels
 * 
 * Purpose: Represents a single task item in a todo list
 * - id: Unique identifier for the task
 * - content: The task description/text
 * - isCompleted: Tracks completion status
 * - assigneeId: Optional user assignment for collaboration
 */
export interface Task {
  id: string;
  content: string;
  isCompleted: boolean;
  assigneeId?: string;
  createdAt?: string;
  completedAt?: string;
}

/**
 * KanbanCard Interface - For Kanban Board Channels
 * 
 * Purpose: Represents a card in a Kanban column
 * - id: Unique card identifier
 * - content: Card text/description
 * - columnId: Reference to parent column
 */
export interface KanbanCard {
  id: string;
  content: string;
  columnId: string;
  order?: number;
  assigneeId?: string;
  createdAt?: string;
}

/**
 * KanbanColumn Interface - For Kanban Board Channels
 * 
 * Purpose: Represents a column in a Kanban board (e.g., "To Do", "In Progress", "Done")
 * - id: Unique column identifier
 * - title: Column name
 * - cardIds: Array of card IDs in this column (for ordering)
 */
export interface KanbanColumn {
  id: string;
  title: string;
  cardIds: string[];
  order?: number;
}

/**
 * DocumentPage Interface - For Document Channels
 * 
 * Purpose: Represents a rich-text document
 * - id: Unique document identifier
 * - content: HTML/Markdown content from rich text editor
 */
export interface DocumentPage {
  id: string;
  title?: string;
  content: string;
  lastEditedBy?: string;
  lastEditedAt?: string;
}
