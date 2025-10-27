import React, { ReactNode } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

interface ProtectedRouteProps {
  children: ReactNode;
}

/**
 * ProtectedRoute Component
 * 
 * Purpose:
 * - Prevents unauthorized access to protected routes
 * - Redirects unauthenticated users to the login page
 * - Shows a loading spinner while checking authentication status
 * 
 * How it works:
 * 1. Uses the useAuth hook to check authentication status
 * 2. If still loading, displays a spinner (prevents flash of wrong content)
 * 3. If not authenticated, redirects to /login
 * 4. If authenticated, renders the protected content (children)
 * 
 * Usage in App.tsx:
 * <Route path="/app" element={
 *   <ProtectedRoute>
 *     <ChatPage />
 *   </ProtectedRoute>
 * } />
 */
const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  // Show loading spinner while checking authentication
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-900">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-accent-primary"></div>
          <p className="mt-4 text-gray-400">Loading...</p>
        </div>
      </div>
    );
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Render protected content if authenticated
  return <>{children}</>;
};

export default ProtectedRoute;
