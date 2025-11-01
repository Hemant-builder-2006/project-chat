import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { WebRTCProvider } from './contexts/WebRTCContext';
import ProtectedRoute from './components/ProtectedRoute';
import LoginPage from './pages/LoginPage';
import RegistrationPage from './pages/RegistrationPage';
import ChatPage from './pages/ChatPage';

/**
 * Main App Component
 * 
 * Architecture:
 * - BrowserRouter: Enables client-side routing
 * - AuthProvider: Wraps entire app to provide authentication state
 * - Routes: Defines all application routes
 * - ProtectedRoute: Guards routes that require authentication
 * 
 * How react-router-dom handles client-side navigation:
 * 1. Intercepts link clicks and browser navigation
 * 2. Updates the URL without triggering a full page reload
 * 3. Matches the new URL against defined routes
 * 4. Renders the corresponding component
 * 5. Updates browser history for back/forward buttons
 * 
 * Benefits:
 * - Fast navigation (no full page reloads)
 * - Smooth user experience (preserves app state)
 * - SEO-friendly with proper configuration
 * - Browser history works as expected
 */
function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <WebRTCProvider>
          <Routes>
            {/* Public Routes */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegistrationPage />} />
          
          {/* Protected Routes */}
          <Route
            path="/app"
            element={
              <ProtectedRoute>
                <ChatPage />
              </ProtectedRoute>
            }
          />
          
          {/* Default Redirect */}
          <Route path="/" element={<Navigate to="/app" replace />} />
          
          {/* 404 Fallback */}
          <Route path="*" element={<Navigate to="/app" replace />} />
        </Routes>
        </WebRTCProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
