import axios, { AxiosInstance, InternalAxiosRequestConfig, AxiosError } from 'axios';

// Create axios instance with base configuration
const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

/**
 * Request Interceptor
 * Automatically adds the Authorization header with JWT token to all requests
 */
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Retrieve access token from localStorage
    const accessToken = localStorage.getItem('accessToken');
    
    if (accessToken && config.headers) {
      // Add Bearer token to Authorization header
      config.headers.Authorization = `Bearer ${accessToken}`;
    }
    
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

/**
 * Response Interceptor
 * Handles global error responses, particularly 401 Unauthorized
 */
api.interceptors.response.use(
  (response) => {
    // Pass through successful responses
    return response;
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    // Handle 401 Unauthorized errors
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      // TODO: Implement refresh token logic here
      // For now, we'll just clear tokens and redirect to login
      // Future implementation:
      // 1. Try to refresh the access token using the refresh token
      // 2. If successful, retry the original request with the new token
      // 3. If refresh fails, clear tokens and redirect to login
      
      // Clear authentication data
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      
      // Redirect to login page
      window.location.href = '/login';
      
      return Promise.reject(error);
    }

    // Handle other errors
    return Promise.reject(error);
  }
);

/**
 * How Interceptors Work:
 * 
 * Request Interceptor:
 * - Runs before every API request is sent
 * - Automatically retrieves the JWT token from localStorage
 * - Adds the token to the Authorization header
 * - This eliminates the need to manually add auth headers to each request
 * 
 * Response Interceptor:
 * - Runs after every API response is received
 * - Handles 401 errors globally (token expired/invalid)
 * - Can implement token refresh logic to seamlessly renew expired tokens
 * - Provides a centralized place for error handling
 * 
 * Benefits:
 * - DRY principle: Write authentication logic once
 * - Consistency: All API calls use the same auth mechanism
 * - Security: Centralized token management
 * - User Experience: Automatic token refresh (when implemented)
 */

export default api;
