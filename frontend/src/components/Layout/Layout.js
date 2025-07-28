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
  const [portfolio, setPortfolio] = useState([]);
  const [selectedPortfolioStock, setSelectedPortfolioStock] = useState('');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [isHeaderHidden, setIsHeaderHidden] = useState(false);
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

  // Load portfolio data when authenticated
  useEffect(() => {
    const loadPortfolio = async () => {
      if (!isAuthenticated) return;
      
      const userData = localStorage.getItem('user');
      if (!userData) return;
      
      try {
        const user = JSON.parse(userData);
        const email = user.email;
        
        if (!email) {
          console.log('⚠️ No user email found, skipping portfolio load');
          return;
        }

        console.log('📡 Loading portfolio for sidebar...');
        const response = await fetch(`${config.backendUrl}/api/portfolio?email=${encodeURIComponent(email)}`);
        if (response.ok) {
          const data = await response.json();
          setPortfolio(data.portfolio || []);
          console.log('✅ Portfolio loaded in sidebar:', data.portfolio?.length || 0, 'stocks');
        } else {
          console.error('❌ Failed to load portfolio:', response.status);
        }
      } catch (error) {
        console.error('❌ Error loading portfolio:', error);
      }
    };

    loadPortfolio();
  }, [isAuthenticated]);

  useEffect(() => {
    const handleScroll = () => {
      const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
      // Consider header hidden when scrolled down more than 80px (header height)
      setIsHeaderHidden(scrollTop > 80);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

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

  // const handleTabChange = (tab) => {
  //   onTabChange(tab);
  //   navigate('/dashboard');
  //   if (window.innerWidth <= 900) {
  //     setSidebarOpen(false);
  //   }
  // };

  const handleTabChange = (tab) => {
    onTabChange(tab);
    if (tab === 'exchange-sentiment') {
      navigate('/exchange-sentiment');
    } else {
      navigate('/dashboard');
    }
    if (window.innerWidth <= 900) {
      setSidebarOpen(false);
    }
  };

  const handleStockChange = (event) => {
    onStockChange(event.target.value);
    if (window.innerWidth <= 900) {
      setSidebarOpen(false);
    }
  };

  const handlePortfolioStockSelect = (event) => {
    const selectedStock = event.target.value;
    setSelectedPortfolioStock(selectedStock);
    if (onStockChange) {
      onStockChange(selectedStock);
    }
    if (window.innerWidth <= 900) {
      setSidebarOpen(false);
    }
  };

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  const renderAuthButtons = () => {
    if (isAuthenticated) {
      return (
        <div className="auth-buttons">
          <span className="user-name">Hi, {user?.name || 'User'}</span>
          {/* <button className="settings-btn" onClick={() => handleTabChange('settings')} title="User Settings">
            <span role="img" aria-label="settings">👤</span>
          </button> */}
          <button className="profile-btn" title="Profile">
            <span role="img" aria-label="profile">👤</span>
          </button>
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
    { key: 'portfolio', label: 'My Portfolio', icon: '💼' },
    { key: 'top-stocks', label: 'Top Stocks', icon: '🏆' },
    { key: 'sector-analysis', label: 'Peer Comparison', icon: '📈' },
    { key: 'sectoral', label: 'Sector View', icon: '📊' },
    { key: 'exchange-sentiment', label: 'Exchange Sentiment', icon: '🌐' }
    // Market Sentiment and Fundamental Analysis are also sub-tabs within Portfolio
  ];

    return (
      <div className={`sidebar ${sidebarOpen ? 'open' : ''} ${isHeaderHidden ? 'full-height' : ''}`}>
        <div className="sidebar-header">
          <h3>Dashboard</h3>
        </div>
        <div className="stock-selector">
          <label htmlFor="stock-select">Select Stock:</label>
          <div className='select-wrapper'>
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
        </div>
        {portfolio.length > 0 && (
          <div className="portfolio-selector">
            <label htmlFor="portfolio-select">Portfolio Stock:</label>
            <div className='select-wrapper'>
            <select 
              id="portfolio-select" 
              value={selectedPortfolioStock} 
              onChange={handlePortfolioStockSelect}
              className="portfolio-dropdown"
            >
              <option value="">Select from portfolio...</option>
              {portfolio.map(item => (
                <option key={item.stock_symbol} value={item.stock_symbol}>
                  {item.stock_symbol} - {item.stock_name}
                </option>
              ))}
            </select>
            </div>
          </div>
        )}
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
    <div className={`layout${isAuthenticated ? ' authenticated' : ''}`}>
      <header className="header">
        <div className="header-content">
          <div className="header-left">
            <div className="logo" style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <img src="/FullLogo_NoBuffer.png" alt="Logo" style={{ height: '68px', width: 'auto', maxWidth: '300px' }} />
            </div>
            {isAuthenticated && (
              <button className="sidebar-toggle" onClick={toggleSidebar}>
                {sidebarOpen ? (
                  // Show ">" when sidebar is open (click to close)
                  <svg width="24" height="24" viewBox="0 0 24 24">
                    <path d="M16 19l-8-7 8-7" fill="none" stroke="currentColor" strokeWidth="2"/>
                  </svg>
                ) : (
                  // Show "<" when sidebar is closed (click to open)
                  <svg width="24" height="24" viewBox="0 0 24 24">
                    <path d="M8 5l8 7-8 7" fill="none" stroke="currentColor" strokeWidth="2"/>
                  </svg>
                )}
              </button>
            )}
          </div>
          <div className="header-right">
            {renderAuthButtons()}
            {/* {isAuthenticated && (
              <button className="sidebar-toggle" onClick={toggleSidebar}>
                <span className="hamburger">
                  <span></span>
                  <span></span>
                  <span></span>
                </span>
              </button>
            )} */}
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