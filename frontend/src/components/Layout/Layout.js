import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import './Layout.css';
import Dashboard from '../Dashboard/Dashboard';
import config from '../../config/config';

const Layout = ({ 
  children, 
  isAuthenticated: authFromProps, 
  activeTab: activeTabProp, 
  selectedStock: selectedStockProp,
  onTabChange,
  onStockChange
}) => {
  const [user, setUser] = useState(null);
  const [stocks, setStocks] = useState([]);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  // Use authentication state from props instead of managing it here
  const isAuthenticated = authFromProps;

  useEffect(() => {
    if (isAuthenticated) {
      // Load user data when authenticated
      const userData = localStorage.getItem('user');
      if (userData) {
        try {
          setUser(JSON.parse(userData));
          setSidebarOpen(true);
          console.log('✅ User loaded from storage:', JSON.parse(userData));
        } catch (error) {
          console.error('❌ Error parsing user data:', error);
        }
      }
    } else {
      // Clear user data when not authenticated
      setUser(null);
      setSidebarOpen(false);
      console.log('🚫 User not authenticated, clearing data');
      
      // If we're on a protected route, redirect to home
      if (location.pathname === '/dashboard') {
        console.log('🔄 Redirecting to home after logout');
        navigate('/', { replace: true });
      }
    }
  }, [isAuthenticated, location.pathname, navigate]);

  useEffect(() => {
    // Fetch stocks for dropdown only when authenticated
    const fetchStocks = async () => {
      if (!isAuthenticated) return;
      
      try {
        console.log('📡 Fetching stocks for dropdown...');
        const response = await fetch(`${config.backendUrl}/api/stocks`);
        if (response.ok) {
          const data = await response.json();
          setStocks(data.stocks || []);
          console.log('✅ Stocks loaded:', data.stocks?.length || 0, 'items');
        } else {
          console.error('❌ Failed to fetch stocks:', response.status);
        }
      } catch (error) {
        console.error('❌ Error fetching stocks:', error);
      }
    };

    fetchStocks();
  }, [isAuthenticated]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
    setSidebarOpen(false);
    console.log('🚪 User logged out');
    
    // Dispatch custom logout event
    window.dispatchEvent(new Event('logout'));
    
    // Navigate to home page
    navigate('/', { replace: true });
  };

  const handleTabChange = (tab) => {
    onTabChange(tab);
    navigate('/dashboard');
  };

  const handleStockChange = (event) => {
    onStockChange(event.target.value);
  };

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  const renderAuthButtons = () => {
    if (isAuthenticated) {
      return (
        <div className="auth-buttons">
          <span className="user-name">Hi, {user?.name || 'User'}</span>
          <button className="logout-btn" onClick={handleLogout}>
            Logout
          </button>
        </div>
      );
    } else {
      return (
        <div className="auth-buttons">
          <button className="signin-btn" onClick={() => navigate('/signin')}>
            Sign In
          </button>
          <button className="signup-btn" onClick={() => navigate('/signup')}>
            Sign Up
          </button>
        </div>
      );
    }
  };

  const renderSidebar = () => {
    if (!isAuthenticated) return null;

    const tabs = [
      { key: 'sectoral', label: 'Sector View', icon: '📊' },
      { key: 'market', label: 'Market Sentiment', icon: '📈' },
      { key: 'fundamental', label: 'Fundamental Analysis', icon: '📋' },
      { key: 'settings', label: 'User Settings', icon: '⚙️' }
    ];

    return (
      <div className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <h3>Dashboard</h3>
        </div>
        
        <div className="stock-selector">
          <label htmlFor="stock-select">Select Stock:</label>
          <select 
            id="stock-select" 
            value={selectedStockProp} 
            onChange={handleStockChange}
            className="stock-dropdown"
          >
            <option value="">Choose a stock...</option>
            {stocks.map(stock => (
              <option key={stock} value={stock}>{stock}</option>
            ))}
          </select>
        </div>

        <nav className="sidebar-nav">
          {tabs.map(tab => (
            <button
              key={tab.key}
              className={`sidebar-tab ${activeTabProp === tab.key ? 'active' : ''}`}
              onClick={() => handleTabChange(tab.key)}
            >
              <span className="tab-icon">{tab.icon}</span>
              <span className="tab-label">{tab.label}</span>
            </button>
          ))}
        </nav>
      </div>
    );
  };

  const renderContent = () => {
    console.log('🔍 Layout renderContent:', { 
      isAuthenticated, 
      pathname: location.pathname, 
      activeTab: activeTabProp, 
      selectedStock: selectedStockProp 
    });

    // Always render children - the App component handles routing
    return children;
  };

  return (
    <div className="layout">
      <header className="header">
        <div className="header-content">
          <div className="header-left">
            <div className="logo">
              <h1>Stock Analysis</h1>
            </div>
          </div>
          <div className="header-right">
            {renderAuthButtons()}
            {isAuthenticated && (
              <button className="sidebar-toggle" onClick={toggleSidebar}>
                <span className="hamburger">
                  <span></span>
                  <span></span>
                  <span></span>
                </span>
              </button>
            )}
          </div>
        </div>
      </header>

      <div className="main-content">
        {renderSidebar()}
        <main className={`content ${sidebarOpen && isAuthenticated ? 'with-sidebar' : ''}`}>
          {renderContent()}
        </main>
      </div>
    </div>
  );
};

export default Layout; 