import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import './App.css';
import Layout from './components/Layout/Layout';
import Home from './components/Home/Home';
import SignIn from './components/Auth/SignIn';
import SignUp from './components/Auth/SignUp';
import Dashboard from './components/Dashboard/Dashboard';

function App() {
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [activeTab, setActiveTab] = useState('sectoral');
  const [selectedStock, setSelectedStock] = useState('');

  useEffect(() => {
    const checkAuth = () => {
      const token = localStorage.getItem('token');
      const userData = localStorage.getItem('user');
      const authenticated = !!(token && userData);
      setIsAuthenticated(authenticated);
      setLoading(false);
      console.log('🔐 Auth check:', { authenticated, token: !!token, userData: !!userData });
    };

    checkAuth();

    const handleStorageChange = (e) => {
      if (e.key === 'token' || e.key === 'user') {
        console.log('🔄 Storage changed:', e.key, e.newValue);
        // Small delay to ensure localStorage is updated
        setTimeout(checkAuth, 100);
      }
    };

    // Listen for storage changes (including logout)
    window.addEventListener('storage', handleStorageChange);
    
    // Also listen for custom logout event
    const handleLogout = () => {
      console.log('🚪 Logout event detected');
      setIsAuthenticated(false);
    };
    
    window.addEventListener('logout', handleLogout);
    
    return () => {
      window.removeEventListener('storage', handleStorageChange);
      window.removeEventListener('logout', handleLogout);
    };
  }, []);

  // Handle tab changes from Layout
  const handleTabChange = (tab) => {
    setActiveTab(tab);
  };

  // Handle stock selection from Layout
  const handleStockChange = (stock) => {
    setSelectedStock(stock);
  };

  // Protected Route Component
  const ProtectedRoute = ({ children }) => {
    const location = useLocation();
    
    if (!isAuthenticated) {
      console.log('🚫 Access denied, redirecting to signin from:', location.pathname);
      return <Navigate to="/signin" state={{ from: location }} replace />;
    }
    
    return children;
  };

  // Public Route Component (only for non-authenticated users)
  const PublicRoute = ({ children }) => {
    const location = useLocation();
    
    if (isAuthenticated) {
      console.log('✅ User authenticated, redirecting to dashboard from:', location.pathname);
      return <Navigate to="/dashboard" replace />;
    }
    
    return children;
  };

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="spinner"></div>
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <Router>
      <Layout 
        isAuthenticated={isAuthenticated}
        activeTab={activeTab}
        selectedStock={selectedStock}
        onTabChange={handleTabChange}
        onStockChange={handleStockChange}
      >
        <Routes>
          {/* Home route - redirects to dashboard if authenticated */}
          <Route
            path="/"
            element={
              isAuthenticated ? (
                <Navigate to="/dashboard" replace />
              ) : (
                <Home />
              )
            }
          />
          
          {/* Public routes - only accessible when NOT authenticated */}
          <Route 
            path="/signin" 
            element={
              <PublicRoute>
                <SignIn />
              </PublicRoute>
            } 
          />
          <Route 
            path="/signup" 
            element={
              <PublicRoute>
                <SignUp />
              </PublicRoute>
            } 
          />
          
          {/* Legacy routes - redirect to appropriate page */}
          <Route path="/market-sentiment" element={<Navigate to="/" replace />} />
          <Route path="/market-sentiment-analysis" element={<Navigate to="/" replace />} />
          
          {/* Protected routes - only accessible when authenticated */}
          <Route 
            path="/dashboard" 
            element={
              <ProtectedRoute>
                <Dashboard 
                  activeTab={activeTab}
                  selectedStock={selectedStock}
                  isAuthenticated={isAuthenticated}
                />
              </ProtectedRoute>
            } 
          />
          
          {/* Catch all unknown routes */}
          <Route
            path="*"
            element={
              isAuthenticated ? (
                <Navigate to="/dashboard" replace />
              ) : (
                <Navigate to="/" replace />
              )
            }
          />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
