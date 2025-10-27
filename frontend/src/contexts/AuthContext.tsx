import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import api from '../services/api';
import { User, LoginCredentials, RegisterCredentials, AuthResponse } from '../types';

/**
 * Authentication Context Interface
 * Defines the shape of the authentication state and actions
 */
interface AuthContextType {
  isAuthenticated: boolean;
  user: User | null;
  accessToken: string | null;
  isLoading: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (credentials: RegisterCredentials) => Promise<void>;
  logout: () => void;
}

// Create the context with undefined default value
const AuthContext = createContext<AuthContextType | undefined>(undefined);

/**
 * Custom hook to access the AuthContext
 * Throws an error if used outside of AuthProvider
 */
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

/**
 * AuthProvider Component
 * Manages authentication state and provides auth functions to the app
 * 
 * Why use React Context for authentication?
 * - Global state: Auth status needs to be accessible throughout the app
 * - Prop drilling avoidance: No need to pass auth state through every component
 * - Centralized logic: All auth-related logic in one place
 * - Re-render optimization: Only components using useAuth re-render on auth changes
 */
export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  /**
   * Initial Authentication Check
   * Runs once on app mount to restore session from localStorage
   * 
   * Purpose of isLoading state:
   * - Prevents flickering: Don't show login screen if user is already logged in
   * - Better UX: Show a loading spinner while checking authentication status
   * - Avoids premature redirects: Wait for auth check before deciding where to route
   */
  useEffect(() => {
    const initAuth = async () => {
      try {
        const storedToken = localStorage.getItem('accessToken');
        
        if (storedToken) {
          // Token exists, validate it by fetching user data
          const response = await api.get<User>('/users/me');
          
          setAccessToken(storedToken);
          setUser(response.data);
          setIsAuthenticated(true);
        }
      } catch (error) {
        // Token is invalid or expired, clear it
        console.error('Auth initialization failed:', error);
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
      } finally {
        setIsLoading(false);
      }
    };

    initAuth();
  }, []);

  /**
   * Login Function
   * Authenticates user and stores tokens
   * 
   * Security Note: Storing JWTs in localStorage
   * PROS:
   * - Persists across browser sessions
   * - Simple to implement
   * - Works across tabs
   * 
   * CONS:
   * - Vulnerable to XSS attacks (malicious scripts can access localStorage)
   * - Should use httpOnly cookies for production for better security
   * 
   * Mitigations:
   * - Sanitize all user inputs to prevent XSS
   * - Use Content Security Policy (CSP) headers
   * - Keep tokens short-lived and implement refresh tokens
   * - Consider using httpOnly cookies in production
   */
  const login = async (credentials: LoginCredentials): Promise<void> => {
    try {
      // Call the login endpoint
      const response = await api.post<AuthResponse>('/token', credentials);
      
      const { access_token, refresh_token, user: userData } = response.data;
      
      // Store tokens in localStorage
      localStorage.setItem('accessToken', access_token);
      if (refresh_token) {
        localStorage.setItem('refreshToken', refresh_token);
      }
      
      // Update state
      setAccessToken(access_token);
      setUser(userData);
      setIsAuthenticated(true);
    } catch (error: any) {
      console.error('Login failed:', error);
      throw new Error(error.response?.data?.detail || 'Login failed');
    }
  };

  /**
   * Register Function
   * Creates a new user account and automatically logs them in
   */
  const register = async (credentials: RegisterCredentials): Promise<void> => {
    try {
      // Call the registration endpoint
      await api.post('/register', credentials);
      
      // Automatically log in after successful registration
      await login({
        username: credentials.username,
        password: credentials.password,
      });
    } catch (error: any) {
      console.error('Registration failed:', error);
      throw new Error(error.response?.data?.detail || 'Registration failed');
    }
  };

  /**
   * Logout Function
   * Clears authentication state and tokens
   */
  const logout = (): void => {
    // Clear tokens from localStorage
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    
    // Reset state
    setAccessToken(null);
    setUser(null);
    setIsAuthenticated(false);
  };

  const value: AuthContextType = {
    isAuthenticated,
    user,
    accessToken,
    isLoading,
    login,
    register,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
