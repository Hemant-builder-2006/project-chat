# Frontend Integration Guide

This guide shows how to integrate your React frontend with the backend API.

## Base Configuration

```typescript
// src/config/api.ts
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
export const WS_BASE_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';

export const API_ENDPOINTS = {
  // Auth
  register: '/api/auth/register',
  login: '/api/auth/login',
  refresh: '/api/auth/refresh',
  logout: '/api/auth/logout',
  
  // Groups
  groups: '/api/groups',
  group: (id: string) => `/api/groups/${id}`,
  
  // Channels
  groupChannels: (groupId: string) => `/api/channels/groups/${groupId}/channels`,
  channel: (id: string) => `/api/channels/${id}`,
  
  // Memberships
  groupMembers: (groupId: string) => `/api/memberships/groups/${groupId}/members`,
  memberRole: (groupId: string, userId: string) => 
    `/api/memberships/groups/${groupId}/members/${userId}`,
};
```

## Authentication Service

```typescript
// src/services/authService.ts
import axios from 'axios';
import { API_BASE_URL, API_ENDPOINTS } from '../config/api';

interface LoginRequest {
  username: string;
  password: string;
}

interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  display_name?: string;
}

interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

interface User {
  id: string;
  username: string;
  email: string;
  display_name?: string;
  created_at: string;
}

class AuthService {
  private accessToken: string | null = null;
  private refreshToken: string | null = null;

  constructor() {
    // Load tokens from localStorage on init
    this.accessToken = localStorage.getItem('access_token');
    this.refreshToken = localStorage.getItem('refresh_token');
  }

  async register(data: RegisterRequest): Promise<User> {
    const response = await axios.post<User>(
      `${API_BASE_URL}${API_ENDPOINTS.register}`,
      data
    );
    return response.data;
  }

  async login(data: LoginRequest): Promise<TokenResponse> {
    const response = await axios.post<TokenResponse>(
      `${API_BASE_URL}${API_ENDPOINTS.login}`,
      data
    );
    
    const { access_token, refresh_token, token_type } = response.data;
    
    // Store tokens
    this.accessToken = access_token;
    this.refreshToken = refresh_token;
    localStorage.setItem('access_token', access_token);
    localStorage.setItem('refresh_token', refresh_token);
    
    return response.data;
  }

  async refreshAccessToken(): Promise<string> {
    if (!this.refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await axios.post<TokenResponse>(
      `${API_BASE_URL}${API_ENDPOINTS.refresh}`,
      { refresh_token: this.refreshToken }
    );
    
    const { access_token, refresh_token } = response.data;
    
    this.accessToken = access_token;
    this.refreshToken = refresh_token;
    localStorage.setItem('access_token', access_token);
    localStorage.setItem('refresh_token', refresh_token);
    
    return access_token;
  }

  logout(): void {
    this.accessToken = null;
    this.refreshToken = null;
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }

  getAccessToken(): string | null {
    return this.accessToken;
  }

  isAuthenticated(): boolean {
    return this.accessToken !== null;
  }
}

export const authService = new AuthService();
```

## Axios Instance with Interceptors

```typescript
// src/services/apiClient.ts
import axios, { AxiosError } from 'axios';
import { API_BASE_URL } from '../config/api';
import { authService } from './authService';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = authService.getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - handle token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config;

    // If 401 and haven't retried yet, try to refresh token
    if (error.response?.status === 401 && originalRequest) {
      try {
        const newToken = await authService.refreshAccessToken();
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        // Refresh failed, logout user
        authService.logout();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);
```

## React Hooks for API Calls

```typescript
// src/hooks/useAuth.ts
import { useState } from 'react';
import { authService } from '../services/authService';
import { useNavigate } from 'react-router-dom';

export const useAuth = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const login = async (username: string, password: string) => {
    setLoading(true);
    setError(null);
    try {
      await authService.login({ username, password });
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const register = async (username: string, email: string, password: string, displayName?: string) => {
    setLoading(true);
    setError(null);
    try {
      await authService.register({ 
        username, 
        email, 
        password, 
        display_name: displayName 
      });
      // Auto-login after registration
      await login(username, password);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    authService.logout();
    navigate('/login');
  };

  return {
    login,
    register,
    logout,
    loading,
    error,
    isAuthenticated: authService.isAuthenticated(),
  };
};
```

```typescript
// src/hooks/useGroups.ts (Updated with API integration)
import { useState, useEffect } from 'react';
import { apiClient } from '../services/apiClient';
import { API_ENDPOINTS } from '../config/api';

interface Group {
  id: string;
  name: string;
  description?: string;
  icon_url?: string;
  owner_id: string;
  created_at: string;
}

export const useGroups = () => {
  const [groups, setGroups] = useState<Group[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchGroups = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.get<Group[]>(API_ENDPOINTS.groups);
      setGroups(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch groups');
    } finally {
      setLoading(false);
    }
  };

  const createGroup = async (name: string, description?: string, iconUrl?: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.post<Group>(API_ENDPOINTS.groups, {
        name,
        description,
        icon_url: iconUrl,
      });
      setGroups([...groups, response.data]);
      return response.data;
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create group');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const updateGroup = async (id: string, data: Partial<Group>) => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.put<Group>(API_ENDPOINTS.group(id), data);
      setGroups(groups.map(g => g.id === id ? response.data : g));
      return response.data;
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update group');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const deleteGroup = async (id: string) => {
    setLoading(true);
    setError(null);
    try {
      await apiClient.delete(API_ENDPOINTS.group(id));
      setGroups(groups.filter(g => g.id !== id));
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete group');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGroups();
  }, []);

  return {
    groups,
    loading,
    error,
    createGroup,
    updateGroup,
    deleteGroup,
    refetch: fetchGroups,
  };
};
```

```typescript
// src/hooks/useChannels.ts (Updated with API integration)
import { useState, useEffect } from 'react';
import { apiClient } from '../services/apiClient';
import { API_ENDPOINTS } from '../config/api';

type ChannelType = 'TEXT' | 'VOICE' | 'VIDEO' | 'TODO' | 'DOC' | 'KANBAN';

interface Channel {
  id: string;
  name: string;
  group_id: string;
  type: ChannelType;
  description?: string;
  created_at: string;
}

export const useChannels = (groupId: string) => {
  const [channels, setChannels] = useState<Channel[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchChannels = async () => {
    if (!groupId) return;
    
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.get<Channel[]>(
        API_ENDPOINTS.groupChannels(groupId)
      );
      setChannels(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch channels');
    } finally {
      setLoading(false);
    }
  };

  const createChannel = async (
    name: string, 
    type: ChannelType, 
    description?: string
  ) => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.post<Channel>(
        API_ENDPOINTS.groupChannels(groupId),
        { name, type, description }
      );
      setChannels([...channels, response.data]);
      return response.data;
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create channel');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const updateChannel = async (id: string, data: Partial<Channel>) => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.put<Channel>(
        API_ENDPOINTS.channel(id),
        data
      );
      setChannels(channels.map(c => c.id === id ? response.data : c));
      return response.data;
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update channel');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const deleteChannel = async (id: string) => {
    setLoading(true);
    setError(null);
    try {
      await apiClient.delete(API_ENDPOINTS.channel(id));
      setChannels(channels.filter(c => c.id !== id));
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete channel');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchChannels();
  }, [groupId]);

  return {
    channels,
    loading,
    error,
    createChannel,
    updateChannel,
    deleteChannel,
    refetch: fetchChannels,
  };
};
```

## Environment Variables

Create `.env` file in frontend directory:

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

## Updated Login Page Example

```typescript
// src/pages/LoginPage.tsx
import React, { useState } from 'react';
import { useAuth } from '../hooks/useAuth';

export const LoginPage: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const { login, loading, error } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await login(username, password);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-900">
      <div className="bg-gray-800 p-8 rounded-lg shadow-lg w-96">
        <h1 className="text-2xl font-bold text-white mb-6">Login</h1>
        
        {error && (
          <div className="bg-red-500/10 border border-red-500 text-red-500 px-4 py-2 rounded mb-4">
            {error}
          </div>
        )}
        
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full bg-gray-700 text-white px-4 py-2 rounded mb-4"
            required
          />
          
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full bg-gray-700 text-white px-4 py-2 rounded mb-4"
            required
          />
          
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded disabled:opacity-50"
          >
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>
      </div>
    </div>
  );
};
```

## Testing Checklist

- [ ] User can register with username, email, password
- [ ] User can login and receive JWT tokens
- [ ] Tokens are stored in localStorage
- [ ] Tokens are included in API requests (Authorization header)
- [ ] Token refresh works on 401 errors
- [ ] User can create groups
- [ ] User can view their groups
- [ ] User can create channels in groups
- [ ] User can view channels in a group
- [ ] Permission errors (403) are handled properly
- [ ] Logout clears tokens and redirects to login

## Next Steps

Once Phase 3 (WebSocket) is complete, you'll need to:
1. Update `useWebSocket` hook to authenticate with JWT token
2. Connect to WebSocket: `ws://localhost:8000/ws/channel/{channel_id}?token={access_token}`
3. Handle real-time message broadcasting
4. Integrate WebRTC signaling through WebSocket
