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
export type ChannelType = 'TEXT' | 'TODO' | 'KANBAN' | 'VOICE' | 'VIDEO';

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
