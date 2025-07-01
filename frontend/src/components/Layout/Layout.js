import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import './Layout.css';
import Dashboard from '../Dashboard/Dashboard';

const Layout = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [activeTab, setActiveTab] = useState('sectoral');
  const [selectedStock, setSelectedStock] = useState('');
  const [stocks, setStocks] = useState([]);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const checkAuth = () => {
      const token = localStorage.getItem('token');
      const userData = localStorage.getItem('user');
      
      console.log('Layout checkAuth:', { token: !!token, userData: !!userData });
      
      if (token && userData) {
        setIsAuthenticated(true);
        setUser(JSON.parse(userData));
        // Set initial active tab to sectoral when authenticated
        setActiveTab('sectoral');
        // Open sidebar by default when authenticated
        setSidebarOpen(true);
        console.log('User authenticated, setting activeTab to sectoral');
      } else {
        setIsAuthenticated(false);
        setUser(null);
        setSidebarOpen(false);
        console.log('User not authenticated');
      }
    };

    checkAuth();
  }, []);

  useEffect(() => {
    // Fetch stocks for dropdown
    const fetchStocks = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/stocks');
        if (response.ok) {
          const data = await response.json();
          setStocks(data.stocks || []);
        }
      } catch (error) {
        console.error('Error fetching stocks:', error);
      }
    };

    if (isAuthenticated) {
      fetchStocks();
    }
  }, [isAuthenticated]);

  // Update active tab when location changes
  useEffect(() => {
    if (isAuthenticated && location.pathname === '/dashboard') {
      // Keep the current active tab when on dashboard
    }
  }, [location.pathname, isAuthenticated]);

  // Listen for authentication state changes
  useEffect(() => {
    const handleStorageChange = (e) => {
      if (e.key === 'token' || e.key === 'user') {
        const token = localStorage.getItem('token');
        const userData = localStorage.getItem('user');
        
        if (token && userData) {
          setIsAuthenticated(true);
          setUser(JSON.parse(userData));
          setActiveTab('sectoral');
          setSidebarOpen(true);
        } else {
          setIsAuthenticated(false);
          setUser(null);
          setSidebarOpen(false);
        }
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setIsAuthenticated(false);
    setUser(null);
    setSidebarOpen(false);
    navigate('/');
  };

  const handleTabChange = (tab) => {
    setActiveTab(tab);
    // Navigate to dashboard when switching tabs
    navigate('/dashboard');
  };

  const handleStockChange = (event) => {
    setSelectedStock(event.target.value);
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
          <h3>Market Sentiment</h3>
        </div>
        
        <div className="stock-selector">
          <label htmlFor="stock-select">Select Stock:</label>
          <select 
            id="stock-select" 
            value={selectedStock} 
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
              className={`sidebar-tab ${activeTab === tab.key ? 'active' : ''}`}
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
    console.log('Layout renderContent:', { 
      isAuthenticated, 
      pathname: location.pathname, 
      activeTab, 
      selectedStock 
    });

    // If not authenticated, show the children (Home, SignIn, SignUp)
    if (!isAuthenticated) {
      return children;
    }

    // If authenticated and on dashboard route, show Dashboard with props
    if (location.pathname === '/dashboard') {
      console.log('Rendering Dashboard with props:', { activeTab, selectedStock, isAuthenticated });
      return (
        <Dashboard 
          activeTab={activeTab} 
          selectedStock={selectedStock} 
          isAuthenticated={isAuthenticated} 
        />
      );
    }

    // For other authenticated routes, just show children
    return children;
  };

  return (
    <div className="layout">
      <header className="header">
        <div className="header-content">
          <div className="header-left">
            <div className="logo">
              <h1>Market Sentiment Analysis</h1>
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