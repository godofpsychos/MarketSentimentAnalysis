import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import FundamentalDashboard from '../../FundamentalDashboard';
import AdvancedCharts from '../../AdvancedCharts';
import { StockPriceChart } from '../../StockFinancialChart';
import './Dashboard.css';
import config from '../../config/config';
import { formatToIST, formatDateOnly } from '../../utils/dateUtils';
import { PieChart, Pie, Cell } from 'recharts';

const Dashboard = ({ activeTab, selectedStock, isAuthenticated, onTabChange, onStockChange }) => {
  const [sentimentData, setSentimentData] = useState([]);
  const [sectorData, setSectorData] = useState([]);
  const [fundamentalData, setFundamentalData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [portfolio, setPortfolio] = useState([]);
  const [portfolioLoading, setPortfolioLoading] = useState(false);
  const [lastFetchedTimestamp, setLastFetchedTimestamp] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(10);
  const [newsData, setNewsData] = useState(null);
  const [newsLoading, setNewsLoading] = useState(false);
  const [newsPage, setNewsPage] = useState(1);
  const [newsPerPage] = useState(5);
  const navigate = useNavigate();
  const [exchangeSentimentData, setExchangeSentimentData] = useState([]);
  const [exchangeSentimentLoading, setExchangeSentimentLoading] = useState(false);
  const [topStocksData, setTopStocksData] = useState([]);
  const [topStocksLoading, setTopStocksLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [sectorAnalysisData, setSectorAnalysisData] = useState([]);
  const [sectorAnalysisLoading, setSectorAnalysisLoading] = useState(false);
  const [selectedSector, setSelectedSector] = useState('');
  const [availableSectors, setAvailableSectors] = useState([]);
  const [sectorSearchTerm, setSectorSearchTerm] = useState('');

  // Get user email from localStorage
  const getUserEmail = () => {
    const userData = localStorage.getItem('user');
    if (userData) {
      try {
        const user = JSON.parse(userData);
        return user.email;
      } catch (e) {
        console.error('Error parsing user data:', e);
        return null;
      }
    }
    return null;
  };

  // Load portfolio from backend
  const loadPortfolio = async () => {
    const email = getUserEmail();
    if (!email) {
      console.log('⚠️ No user email found, skipping portfolio load');
      return;
    }

    setPortfolioLoading(true);
    try {
      const response = await fetch(`${config.backendUrl}/api/portfolio?email=${encodeURIComponent(email)}`);
      if (response.ok) {
        const data = await response.json();
        setPortfolio(data.portfolio || []);
        console.log('✅ Portfolio loaded:', data.portfolio?.length || 0, 'stocks');
      } else {
        console.error('❌ Failed to load portfolio:', response.status);
      }
    } catch (error) {
      console.error('❌ Error loading portfolio:', error);
    } finally {
      setPortfolioLoading(false);
    }
  };

  // Fetch top stocks data
  const fetchTopStocks = async () => {
    setTopStocksLoading(true);
    try {
      const apiUrl = `${config.backendUrl}/api/top-stocks`;
      const response = await fetch(apiUrl);
      
      if (response.ok) {
        const data = await response.json();
        setTopStocksData(data.top_stocks || []);
      } else {
        console.error('Failed to fetch top stocks:', response.status);
      }
    } catch (error) {
      console.error('Error fetching top stocks:', error);
    } finally {
      setTopStocksLoading(false);
    }
  };

  // Portfolio management functions
  const addToPortfolio = async (stock) => {
    const email = getUserEmail();
    if (!email) {
      console.log('⚠️ No user email found, cannot add to portfolio');
      return;
    }

    try {
      const response = await fetch(`${config.backendUrl}/api/portfolio/add`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: email,
          stock_symbol: stock.stock,
          stock_name: stock.stock_name
        })
      });

      if (response.ok) {
        // Reload portfolio to get updated data
        await loadPortfolio();
        console.log('✅ Stock added to portfolio:', stock.stock);
      } else {
        console.error('❌ Failed to add stock to portfolio:', response.status);
      }
    } catch (error) {
      console.error('❌ Error adding stock to portfolio:', error);
    }
  };

  const removeFromPortfolio = async (stockSymbol) => {
    const email = getUserEmail();
    if (!email) {
      console.log('⚠️ No user email found, cannot remove from portfolio');
      return;
    }

    try {
      const response = await fetch(`${config.backendUrl}/api/portfolio/remove`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: email,
          stock_symbol: stockSymbol
        })
      });

      if (response.ok) {
        // Reload portfolio to get updated data
        await loadPortfolio();
        console.log('✅ Stock removed from portfolio:', stockSymbol);
      } else {
        console.error('❌ Failed to remove stock from portfolio:', response.status);
      }
    } catch (error) {
      console.error('❌ Error removing stock from portfolio:', error);
    }
  };

  const isInPortfolio = (stockSymbol) => {
    return portfolio.some(item => item.stock_symbol === stockSymbol);
  };

  const handleAddButtonClick = (tabName) => {
    // Add the selected stock to portfolio if available
    if (selectedStock) {
      const stockData = {
        stock: selectedStock,
        stock_name: selectedStock,
        sentiment: sentimentData.find(item => item.stock === selectedStock)?.sentiment || 0,
        added_date: new Date().toISOString(),
        tab_source: tabName
      };
      addToPortfolio(stockData);
    }
  };

  // Calculate financial health score based on available data
  const calculateFinancialHealthScore = () => {
    if (!fundamentalData) {
      console.log('⚠️ No fundamental data available for health score calculation');
      return null;
    }
    
    // This would calculate based on real fundamental data
    // For now, return null since we don't have the calculation logic
    console.log('⚠️ Financial health score calculation not implemented');
    return null;
  };

  // Get sector score for the selected stock
  // Check if data is fresh (less than 24 hours old)
  const isDataFresh = (timestamp) => {
    if (!timestamp) return false;
    const dataTime = new Date(timestamp);
    const now = new Date();
    const hoursDiff = (now - dataTime) / (1000 * 60 * 60);
    return hoursDiff < 24;
  };

  const getSectorScoreForStock = () => {
    if (!selectedStock || sectorData.length === 0) {
      console.log('⚠️ No sector data available for stock:', selectedStock);
      return null;
    }

    // Try to determine the sector for the selected stock
    // This is a simplified mapping - in a real app, you'd get this from the stock data
    const stockSectorMap = {
      'RELIANCE': 'Energy',
      'TCS': 'Technology', 
      'INFY': 'Technology',
      'HDFC': 'Finance',
      'ICICIBANK': 'Finance',
      'AXISBANK': 'Finance',
      'HINDUNILVR': 'Consumer Goods',
      'ITC': 'Consumer Goods',
      'SUNPHARMA': 'Healthcare',
      'DRREDDY': 'Healthcare',
      'DLF': 'Real Estate',
      'GODREJPROP': 'Real Estate'
    };

    const stockSector = stockSectorMap[selectedStock];
    console.log(`Stock ${selectedStock} belongs to sector: ${stockSector}`);

    if (stockSector) {
      const sectorInfo = sectorData.find(sector => sector.sector_name === stockSector);
      if (sectorInfo) {
        console.log(`Found sector info for ${stockSector}:`, sectorInfo);
        return {
          score: sectorInfo.financial_health,
          sector: stockSector,
          sectorData: sectorInfo
        };
      }
    }

    // If we can't find the specific sector, return the average
    const averageScore = Math.round(sectorData.reduce((sum, sector) => sum + sector.financial_health, 0) / sectorData.length);
    return {
      score: averageScore,
      sector: 'Market Average',
      sectorData: null
    };
  };

  // Load portfolio when component mounts or user changes
  useEffect(() => {
    loadPortfolio();
  }, [isAuthenticated]);

  // Reset to first page when portfolio changes
  useEffect(() => {
    setCurrentPage(1);
  }, [portfolio.length]);

  useEffect(() => {
    const fetchData = async () => {
      console.log('🔍 Dashboard useEffect triggered');
      console.log('🔍 Current config:', {
        backendUrl: config.backendUrl,
        apiBaseUrl: config.apiBaseUrl,
        environment: process.env.NODE_ENV
      });
      setLoading(true);
      setError(null);
      console.log('🚀 Starting data fetch for Dashboard...');

      try {
        // Fetch available data
        console.log('📡 Fetching sentiment data from:', `${config.backendUrl}/api/sentiment`);
        console.log('📡 Fetching stocks data from:', `${config.backendUrl}/api/stocks`);
        
        const promises = [
          fetch(`${config.backendUrl}/api/sentiment`).then(res => {
            console.log('📡 Sentiment response status:', res.status);
            return res.json();
          }).catch(err => {
            console.error('❌ Sentiment fetch error:', err);
            return { data: [] };
          }),
          fetch(`${config.backendUrl}/api/stocks`).then(res => {
            console.log('📡 Stocks response status:', res.status);
            return res.json();
          }).catch(err => {
            console.error('❌ Stocks fetch error:', err);
            return { stocks: [] };
          }),
          fetch(`${config.backendUrl}/api/sentiment-db-timestamp`).then(res => {
            console.log('📡 Timestamp response status:', res.status);
            return res.json();
          }).catch(err => {
            console.error('❌ Timestamp fetch error:', err);
            return { error: 'Failed to fetch timestamp' };
          })
        ];

        const [sentimentResult, stocksResult, timestampResult] = await Promise.all(promises);
        
        console.log('📊 Sentiment result:', sentimentResult);
        console.log('📊 Stocks result:', stocksResult);
        console.log('📊 Timestamp result:', timestampResult);
        
        // Only set real data, no hardcoded values
        if (sentimentResult.data && sentimentResult.data.length > 0) {
          setSentimentData(sentimentResult.data);
          console.log('✅ Sentiment data set:', sentimentResult.data.length, 'items');
        } else {
          console.log('⚠️ No sentiment data available from API');
          setSentimentData([]);
        }
        
        // TEMPORARY: Add hardcoded sector data for development/testing
        console.log('🔧 Using hardcoded sector data temporarily');
        const baseSectorData = [
          { sector_name: 'Technology', base_performance: 85, base_financial_health: 85 },
          { sector_name: 'Healthcare', base_performance: 78, base_financial_health: 90 },
          { sector_name: 'Finance', base_performance: 72, base_financial_health: 80 },
          { sector_name: 'Energy', base_performance: 65, base_financial_health: 70 },
          { sector_name: 'Consumer Goods', base_performance: 80, base_financial_health: 85 },
          { sector_name: 'Real Estate', base_performance: 58, base_financial_health: 60 }
        ];
        
        // Add some variation to make scores more dynamic
        const timeVariation = Math.sin(Date.now() / 1000000) * 5; // ±5 points variation
        const sampleSectorData = baseSectorData.map(sector => ({
          sector_name: sector.sector_name,
          performance_score: Math.max(0, Math.min(100, sector.base_performance + timeVariation + (Math.random() - 0.5) * 10)),
          market_cap: 5000000000000 + (Math.random() - 0.5) * 2000000000000,
          risk_score: 65 + (Math.random() - 0.5) * 20,
          return_potential: 75 + (Math.random() - 0.5) * 15,
          profitability: 75 + (Math.random() - 0.5) * 15,
          valuation: 65 + (Math.random() - 0.5) * 15,
          growth: 70 + (Math.random() - 0.5) * 15,
          liquidity: 80 + (Math.random() - 0.5) * 15,
          financial_health: Math.max(0, Math.min(100, sector.base_financial_health + timeVariation + (Math.random() - 0.5) * 8)),
          market_position: 75 + (Math.random() - 0.5) * 15
        }));
        setSectorData(sampleSectorData);
        console.log('✅ Hardcoded sector data set:', sampleSectorData.length, 'sectors');
        
        // Set timestamp data
        if (timestampResult && !timestampResult.error) {
          setLastFetchedTimestamp(timestampResult);
          console.log('✅ Timestamp data set:', timestampResult);
        } else {
          console.log('⚠️ No timestamp data available from API');
          setLastFetchedTimestamp(null);
        }
        
        // If a stock is selected, fetch its data
        if (selectedStock) {
          console.log('📡 Fetching data for selected stock:', selectedStock);
          try {
            const [, fundamentalInfo] = await Promise.all([
              fetch(`${config.backendUrl}/api/stock-info/${selectedStock}`).then(res => res.json()).catch(() => null),
              fetch(`${config.backendUrl}/api/fundamental-analysis/${selectedStock}`).then(res => res.json()).catch(() => null)
            ]);
            if (fundamentalInfo) {
              setFundamentalData(fundamentalInfo);
              console.log('✅ Fundamental data set for:', selectedStock);
            } else {
              console.log('⚠️ No fundamental data available for:', selectedStock);
              setFundamentalData(null);
            }
            
            // Fetch and auto-select the stock's sector
            await fetchStockSector(selectedStock);
          } catch (stockError) {
            console.error('❌ Error fetching stock data:', stockError);
            setFundamentalData(null);
          }
        }

        setLoading(false);
        console.log('🎉 Dashboard data loaded successfully!');
        console.log('📊 Final state:', {
          sentimentDataLength: sentimentResult.data?.length || 0,
          sectorDataLength: sampleSectorData.length,
          selectedStock,
          loading: false
        });
      } catch (error) {
        console.error('❌ Error fetching data:', error);
        setError(error.message);
        setLoading(false);
      }
    };

    fetchData();
  }, [selectedStock]);

  // Helper to format date in dd/mm/yyyy format (using the utility function)
  const formatDateDDMMYYYY = (dateString) => {
    return formatDateOnly(dateString);
  };

  const handlePortfolioStockClick = (stockSymbol) => {
    if (onStockChange) onStockChange(stockSymbol);
    if (onTabChange) onTabChange('market');
  };

  // Fetch news for selected stock from database
  const fetchStockNews = async (stockSymbol, page = 1) => {
    if (!stockSymbol) return;
    
    setNewsLoading(true);
    try {
      const response = await fetch(`${config.backendUrl}/api/stock-news/${stockSymbol}?page=${page}&per_page=${newsPerPage}`);
      if (response.ok) {
        const data = await response.json();
        setNewsData(data);
        setNewsPage(page);
      } else {
        console.error('❌ Failed to fetch stock news:', response.status);
        const errorData = await response.json();
        console.error('❌ Error details:', errorData);
      }
    } catch (error) {
      console.error('❌ Error fetching stock news:', error);
    } finally {
      setNewsLoading(false);
    }
  };

  // for exchange-sentiments
  useEffect(() => {
    let intervalId;
  
    const fetchData = () => {
      setExchangeSentimentLoading(true);
      const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000/api';
      fetch(`${API_BASE_URL}/exchange-sentiment`)
        .then(res => res.json())
        .then(data => {
          setExchangeSentimentData(data);
          setExchangeSentimentLoading(false);
        })
        .catch(() => setExchangeSentimentLoading(false));
    };
  
    if (activeTab === 'exchange-sentiment') {
      fetchData(); // Initial fetch
      intervalId = setInterval(fetchData, 60000); // Fetch every 60 seconds
    }
  
    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [activeTab]);
  
  // Load news when selected stock changes
  useEffect(() => {
    if (selectedStock) {
      fetchStockNews(selectedStock, 1);
    }
  }, [selectedStock]);

  // Load top stocks when tab is active
  useEffect(() => {
    if (activeTab === 'top-stocks') {
      fetchTopStocks();
    }
  }, [activeTab]);

  // Fetch stock sector and auto-select it
  const fetchStockSector = async (stockSymbol) => {
    if (!stockSymbol) return;
    
    try {
      console.log('🔄 Fetching sector for stock:', stockSymbol);
      const response = await fetch(`${config.backendUrl}/api/stock-sector/${stockSymbol}`);
      
      if (response.ok) {
        const data = await response.json();
        console.log('✅ Stock sector data:', data);
        
        if (data.sector && data.sector !== 'N/A') {
          setSelectedSector(data.sector);
          console.log('✅ Auto-selected sector:', data.sector);
          
          // If we're on the sector analysis tab, fetch the sector analysis
          if (activeTab === 'sector-analysis') {
            fetchSectorAnalysis(data.sector);
          }
        } else {
          console.log('⚠️ No valid sector found for stock:', stockSymbol);
          setSelectedSector('');
        }
      } else {
        console.error('❌ Failed to fetch stock sector:', response.status);
        setSelectedSector('');
      }
    } catch (error) {
      console.error('❌ Error fetching stock sector:', error);
      setSelectedSector('');
    }
  };

  // Fetch available sectors
  const fetchAvailableSectors = async () => {
    try {
      console.log('🔄 Fetching available sectors...');
      const response = await fetch(`${config.backendUrl}/api/available-sectors`);
      if (response.ok) {
        const data = await response.json();
        setAvailableSectors(data.sectors || []);
        console.log('✅ Available sectors loaded:', data.sectors?.length || 0, 'sectors');
      } else {
        console.error('❌ Failed to fetch sectors:', response.status);
      }
    } catch (error) {
      console.error('❌ Error fetching sectors:', error);
    }
  };

  // Fetch sector analysis data
  const fetchSectorAnalysis = async (sectorName) => {
    if (!sectorName) return;
    
    console.log('🔄 Fetching sector analysis for:', sectorName);
    setSectorAnalysisLoading(true);
    try {
      const apiUrl = `${config.backendUrl}/api/sector-analysis-stocks/${encodeURIComponent(sectorName)}`;
      console.log('📡 API URL:', apiUrl);
      const response = await fetch(apiUrl);
      console.log('📡 Response status:', response.status);
      
      if (response.ok) {
        const data = await response.json();
        console.log('📊 Sector analysis data:', data);
        setSectorAnalysisData(data.sector_stocks || []);
        console.log('✅ Sector stocks loaded:', data.sector_stocks?.length || 0, 'stocks');
      } else {
        console.error('❌ Failed to fetch sector analysis:', response.status);
        const errorText = await response.text();
        console.error('❌ Error response:', errorText);
      }
    } catch (error) {
      console.error('❌ Error fetching sector analysis:', error);
    } finally {
      setSectorAnalysisLoading(false);
    }
  };

  // Load sectors when sector analysis tab is active
  useEffect(() => {
    console.log('🔄 useEffect triggered, activeTab:', activeTab);
    if (activeTab === 'sector-analysis') {
      console.log('📈 Peer Comparison tab activated, loading sectors...');
      fetchAvailableSectors();
      
      // If a stock is already selected, fetch its sector and auto-select it
      if (selectedStock) {
        console.log('📈 Stock already selected, fetching its sector:', selectedStock);
        fetchStockSector(selectedStock);
      }
    }
  }, [activeTab, selectedStock]);

  const getSentimentClass = (score) => {
    if (score <= 3) return "bearish";
    if (score <= 7) return "neutral";
    return "bullish";
  };


  const renderTopStocksView = () => {
    const getScoreColor = (score) => {
      if (score >= 80) return '#2e7d32'; // Green
      if (score >= 60) return '#1976d2'; // Blue
      if (score >= 40) return '#ed6c02'; // Orange
      return '#d32f2f'; // Red
    };

    const getGradeColor = (grade) => {
      if (grade === 'A+' || grade === 'A') return '#2e7d32';
      if (grade === 'B+' || grade === 'B') return '#1976d2';
      if (grade === 'C+' || grade === 'C') return '#ed6c02';
      if (grade === 'D' || grade === 'D-') return '#d32f2f';
      return '#666';
    };

    const getRecommendationColor = (recommendation) => {
      if (recommendation.includes('Buy')) return '#2e7d32';
      if (recommendation.includes('Hold')) return '#ed6c02';
      if (recommendation.includes('Sell')) return '#d32f2f';
      return '#666';
    };

    const getRiskColor = (risk) => {
      if (risk === 'Low') return '#2e7d32';
      if (risk === 'Medium') return '#ed6c02';
      if (risk === 'High') return '#d32f2f';
      return '#666';
    };

    return (
      <div className="top-stocks-container">
        <div className="top-stocks-header">
          <h2>🏆 Top Stocks Comparison</h2>
          <p>Comprehensive fundamental analysis comparison of all stocks</p>
          <button 
            onClick={fetchTopStocks} 
            style={{ 
              marginTop: '10px', 
              padding: '8px 16px', 
              background: '#667eea', 
              color: 'white', 
              border: 'none', 
              borderRadius: '5px', 
              cursor: 'pointer',
              fontSize: '14px'
            }}
          >
            🔄 Refresh Data
          </button>
        </div>

        {topStocksLoading ? (
          <div className="loading-container">
            <div className="spinner"></div>
            <p>Loading comprehensive stock analysis...</p>
          </div>
        ) : topStocksData.length === 0 ? (
          <div className="loading-container">
            <p>No data available. Please check console for errors.</p>
            <button onClick={fetchTopStocks} style={{ marginTop: '10px', padding: '10px 20px', background: '#667eea', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer' }}>
              Retry Fetch
            </button>
          </div>
        ) : (
          <div className="top-stocks-table-container">
            <div className="table-controls">
              <div className="search-container">
                <input
                  type="text"
                  placeholder="Search stocks by symbol, company name, or sector..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="search-input"
                />
                <span className="search-icon">🔍</span>
              </div>
              <div className="table-info">
                Showing {topStocksData.filter(stock => 
                  searchTerm === '' || 
                  stock.symbol?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                  stock.company_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                  stock.sector?.toLowerCase().includes(searchTerm.toLowerCase())
                ).length} of {topStocksData.length} stocks
              </div>

            </div>
            
            <div className="stocks-comparison-table">
              <table>
                <thead>
                  <tr>
                    <th>Rank</th>
                    <th>Stock</th>
                    <th>Company</th>
                    <th>Sector</th>
                    <th>Overall Score</th>
                    <th>Grade</th>
                    <th>Recommendation</th>
                    <th>Risk Level</th>
                    <th>Reliability</th>
                    <th>Growth</th>
                    <th>Valuation</th>
                    <th>ROE (%)</th>
                    <th>Profit Margin (%)</th>
                    <th>Current Ratio</th>
                    <th>Revenue Growth (%)</th>
                    <th>P/E Ratio</th>
                    <th>P/B Ratio</th>
                  </tr>
                </thead>
                <tbody>
                  {topStocksData.filter(stock => 
                    searchTerm === '' || 
                    stock.symbol?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                    stock.company_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                    stock.sector?.toLowerCase().includes(searchTerm.toLowerCase())
                  ).map((stock, index) => (
                    <tr key={stock.symbol} className="stock-row">
                      <td className="rank-cell">
                        <span className="rank-number">#{index + 1}</span>
                      </td>
                      <td className="symbol-cell">
                        <strong>{stock.symbol}</strong>
                      </td>
                      <td className="company-cell">
                        {stock.company_name}
                      </td>
                      <td className="sector-cell">
                        {stock.sector}
                      </td>
                      <td className="score-cell">
                        <span 
                          className="score-value"
                          style={{ color: getScoreColor(stock.overall_score) }}
                        >
                          {stock.overall_score}
                        </span>
                      </td>
                      <td className="grade-cell">
                        <span 
                          className="grade-badge"
                          style={{ 
                            backgroundColor: getGradeColor(stock.overall_grade),
                            color: 'white'
                          }}
                        >
                          {stock.overall_grade}
                        </span>
                      </td>
                      <td className="recommendation-cell">
                        <span 
                          className="recommendation-badge"
                          style={{ color: getRecommendationColor(stock.recommendation) }}
                        >
                          {stock.recommendation}
                        </span>
                      </td>
                      <td className="risk-cell">
                        <span 
                          className="risk-badge"
                          style={{ color: getRiskColor(stock.risk_level) }}
                        >
                          {stock.risk_level}
                        </span>
                      </td>
                      <td className="reliability-cell">
                        <span style={{ color: getScoreColor(stock.reliability_score) }}>
                          {stock.reliability_score}
                        </span>
                      </td>
                      <td className="growth-cell">
                        <span style={{ color: getScoreColor(stock.growth_score) }}>
                          {stock.growth_score}
                        </span>
                      </td>
                      <td className="valuation-cell">
                        <span style={{ color: getScoreColor(stock.valuation_score) }}>
                          {stock.valuation_score}
                        </span>
                      </td>
                      <td className="roe-cell">
                        {stock.roe !== null ? `${stock.roe}%` : 'N/A'}
                      </td>
                      <td className="profit-margin-cell">
                        {stock.profit_margin !== null ? `${stock.profit_margin}%` : 'N/A'}
                      </td>
                      <td className="current-ratio-cell">
                        {stock.current_ratio !== null ? stock.current_ratio : 'N/A'}
                      </td>
                      <td className="revenue-growth-cell">
                        {stock.revenue_growth !== null ? `${stock.revenue_growth}%` : 'N/A'}
                      </td>
                      <td className="pe-ratio-cell">
                        {stock.pe_ratio !== null ? stock.pe_ratio : 'N/A'}
                      </td>
                      <td className="pb-ratio-cell">
                        {stock.price_to_book !== null ? stock.price_to_book : 'N/A'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderSectorAnalysisView = () => {
    const getScoreColor = (score) => {
      if (score >= 80) return '#2e7d32'; // Green
      if (score >= 60) return '#1976d2'; // Blue
      if (score >= 40) return '#ed6c02'; // Orange
      return '#d32f2f'; // Red
    };

    const getGradeColor = (grade) => {
      switch (grade) {
        case 'A': return '#2e7d32';
        case 'B': return '#1976d2';
        case 'C': return '#ed6c02';
        case 'D': return '#d32f2f';
        case 'F': return '#d32f2f';
        default: return '#666';
      }
    };

    const getRecommendationColor = (recommendation) => {
      switch (recommendation) {
        case 'Buy': return '#2e7d32';
        case 'Hold': return '#ed6c02';
        case 'Sell': return '#d32f2f';
        default: return '#666';
      }
    };

    const getRiskColor = (risk) => {
      switch (risk) {
        case 'Low': return '#2e7d32';
        case 'Medium': return '#ed6c02';
        case 'High': return '#d32f2f';
        default: return '#666';
      }
    };

    return (
      <div className="peer-comparison-container">
        <div className="peer-comparison-header">
          <h2>📈 Peer Comparison</h2>
          <p>Compare stocks within the same sector for peer analysis</p>

          <div className="sector-selector-container">
            <select 
              value={selectedSector} 
              onChange={(e) => {
                setSelectedSector(e.target.value);
                if (e.target.value) {
                  fetchSectorAnalysis(e.target.value);
                }
              }}
              className="sector-select"
            >
              <option value="">Select a sector...</option>
              {availableSectors.map(sector => (
                <option key={sector} value={sector}>{sector}</option>
              ))}
            </select>
            <button 
              onClick={() => fetchSectorAnalysis(selectedSector)} 
              disabled={!selectedSector}
              className="sector-refresh-btn"
            >
              🔄 Refresh
            </button>
          </div>
        </div>
        
        {sectorAnalysisLoading ? (
          <div className="peer-comparison-loading">
            <div className="spinner"></div>
            <p>Loading peer comparison data...</p>
          </div>
        ) : sectorAnalysisData.length === 0 ? (
          <div className="peer-comparison-empty">
            <h3>📊 Select a Sector</h3>
            <p>Choose a sector from the dropdown above to view peer comparison analysis</p>
            <div className="sector-selector-container">
              <select 
                value={selectedSector} 
                onChange={(e) => {
                  setSelectedSector(e.target.value);
                  if (e.target.value) {
                    fetchSectorAnalysis(e.target.value);
                  }
                }}
                className="sector-select"
              >
                <option value="">Select a sector...</option>
                {availableSectors.map(sector => (
                  <option key={sector} value={sector}>{sector}</option>
                ))}
              </select>
              <button 
                onClick={() => fetchSectorAnalysis(selectedSector)} 
                disabled={!selectedSector}
                className="sector-refresh-btn"
              >
                🔄 Refresh
              </button>
            </div>
          </div>
        ) : (
          <div className="top-stocks-table-container">
            <div className="table-controls">
              <div className="search-container">
                <input
                  type="text"
                  placeholder="Search stocks by symbol, company name..."
                  value={sectorSearchTerm}
                  onChange={(e) => setSectorSearchTerm(e.target.value)}
                  className="search-input"
                />
                <span className="search-icon">🔍</span>
              </div>
              <div className="table-info">
                Showing {sectorAnalysisData.filter(stock => 
                  sectorSearchTerm === '' || 
                  stock.symbol?.toLowerCase().includes(sectorSearchTerm.toLowerCase()) ||
                  stock.company_name?.toLowerCase().includes(sectorSearchTerm.toLowerCase())
                ).length} of {sectorAnalysisData.length} stocks in {selectedSector}
              </div>
            </div>
            
            <div className="stocks-comparison-table">
              <table>
                <thead>
                  <tr>
                    <th>Rank</th><th>Stock</th><th>Company</th><th>Sector</th>
                    <th>Overall Score</th><th>Grade</th><th>Recommendation</th><th>Risk Level</th>
                    <th>Reliability</th><th>Growth</th><th>Valuation</th>
                    <th>ROE (%)</th><th>Profit Margin (%)</th><th>Current Ratio</th>
                    <th>Revenue Growth (%)</th><th>P/E Ratio</th><th>P/B Ratio</th>
                  </tr>
                </thead>
                <tbody>
                  {sectorAnalysisData.filter(stock => 
                    sectorSearchTerm === '' || 
                    stock.symbol?.toLowerCase().includes(sectorSearchTerm.toLowerCase()) ||
                    stock.company_name?.toLowerCase().includes(sectorSearchTerm.toLowerCase())
                  ).map((stock, index) => (
                    <tr key={stock.symbol} className="stock-row">
                      <td className="rank-cell">
                        <span className="rank-number">#{index + 1}</span>
                      </td>
                      <td className="symbol-cell">
                        <strong>{stock.symbol}</strong>
                      </td>
                      <td className="company-cell">
                        {stock.company_name}
                      </td>
                      <td className="sector-cell">
                        {stock.sector}
                      </td>
                      <td className="score-cell">
                        <span 
                          className="score-value"
                          style={{ color: getScoreColor(stock.overall_score) }}
                        >
                          {stock.overall_score}
                        </span>
                      </td>
                      <td className="grade-cell">
                        <span 
                          className="grade-badge"
                          style={{ 
                            backgroundColor: getGradeColor(stock.overall_grade),
                            color: 'white'
                          }}
                        >
                          {stock.overall_grade}
                        </span>
                      </td>
                      <td className="recommendation-cell">
                        <span 
                          className="recommendation-badge"
                          style={{ color: getRecommendationColor(stock.recommendation) }}
                        >
                          {stock.recommendation}
                        </span>
                      </td>
                      <td className="risk-cell">
                        <span 
                          className="risk-badge"
                          style={{ color: getRiskColor(stock.risk_level) }}
                        >
                          {stock.risk_level}
                        </span>
                      </td>
                      <td className="reliability-cell">
                        <span style={{ color: getScoreColor(stock.reliability_score) }}>
                          {stock.reliability_score}
                        </span>
                      </td>
                      <td className="growth-cell">
                        <span style={{ color: getScoreColor(stock.growth_score) }}>
                          {stock.growth_score}
                        </span>
                      </td>
                      <td className="valuation-cell">
                        <span style={{ color: getScoreColor(stock.valuation_score) }}>
                          {stock.valuation_score}
                        </span>
                      </td>
                      <td className="roe-cell">
                        {stock.roe !== null ? `${stock.roe}%` : 'N/A'}
                      </td>
                      <td className="profit-margin-cell">
                        {stock.profit_margin !== null ? `${stock.profit_margin}%` : 'N/A'}
                      </td>
                      <td className="current-ratio-cell">
                        {stock.current_ratio !== null ? stock.current_ratio : 'N/A'}
                      </td>
                      <td className="revenue-growth-cell">
                        {stock.revenue_growth !== null ? `${stock.revenue_growth}%` : 'N/A'}
                      </td>
                      <td className="pe-ratio-cell">
                        {stock.pe_ratio !== null ? stock.pe_ratio : 'N/A'}
                      </td>
                      <td className="pb-ratio-cell">
                        {stock.price_to_book !== null ? stock.price_to_book : 'N/A'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderSectoralView = () => (
    <div className="dashboard-section sector-view">
      <div className="section-header">
        <div className="header-content">
          <h2>📊 Sectoral Analysis</h2>
          <p>Comprehensive sector-wise market analysis and performance metrics</p>
        </div>
        <button 
          className={`add-button ${selectedStock && isInPortfolio(selectedStock) ? 'remove' : 'add'}`} 
          title={selectedStock && isInPortfolio(selectedStock) ? 'Remove from Portfolio' : 'Add to Portfolio'}
          onClick={() => selectedStock && isInPortfolio(selectedStock) ? removeFromPortfolio(selectedStock) : handleAddButtonClick('sectoral')}
        >
          <span>{selectedStock && isInPortfolio(selectedStock) ? '−' : '+'}</span>
        </button>
      </div>
      
      <div className="charts-section">
        {/* Market Sentiment Overview */}
        {/* <div className="chart-card gauge-board">
          <div className="chart-header">
            <h3>Market Sentiment Overview</h3>
            <div className="info-tooltip" title="Shows the overall mood of the entire stock market. Positive numbers mean investors are optimistic (bullish), negative numbers mean they're worried (bearish). The bar shows how strong this feeling is.">
              ℹ️
            </div>
          </div>
          <div className="sentiment-overview">
            <div className="sentiment-card overall">
              <h3>Overall Market Sentiment</h3>
              {sentimentData.length > 0 ? (
                (() => {
                  const overallSentiment = {
                    sentiment: Math.round(sentimentData.reduce((sum, item) => sum + item.sentiment, 0) / sentimentData.length * 10) / 10,
                    label: 'Market Average'
                  };
                  return (
                    <>
                      <div className="sentiment-score">
                        <span className={`score ${overallSentiment.sentiment > 0 ? 'positive' : 'negative'}`}>{overallSentiment.sentiment}</span>
                        <span className="label">{overallSentiment.label || (overallSentiment.sentiment > 0 ? 'Bullish' : 'Bearish')}</span>
                      </div>
                      <div className="sentiment-bar">
                        <div className={`bar-fill ${getSentimentClass(overallSentiment.sentiment)}`} style={{ width: `${(overallSentiment.sentiment / 10) * 100}%` }}></div>
                      </div>
                    </>
                  );
                })()
              ) : (
                <div className="sentiment-score">
                  <span className="label">No sentiment data available</span>
                </div>
              )}
            </div>
          </div>
        </div> */}

      <div className="chart-card gauge-board">
      <div className="chart-header">
        <h3>Market Sentiment Overview</h3>
        <div className="info-tooltip" title="Shows the overall mood of the entire stock market. Positive numbers mean investors are optimistic (bullish), negative numbers mean they're worried (bearish). The bar shows how strong this feeling is.">
          ℹ️
        </div>
      </div>
      <div className="sentiment-overview">
        <div className="sentiment-card overall">
          <h3>Overall Market Sentiment</h3>
          {sentimentData.length > 0 ? (() => {
           const min = -10, max = 10;
           const overallSentiment = Math.round(sentimentData.reduce((sum, item) => sum + item.sentiment, 0) / sentimentData.length * 10) / 10;
           const gaugePercent = (overallSentiment - min) / (max - min);
         
           // Section values
           const redRange = 0 - min;    // 10
           const yellowRange = 5 - 0;   // 5
           const greenRange = max - 5;  // 5
           const totalRange = max - min; // 20
         
           const sections = [
             { value: redRange / totalRange, color: "#EA4228" },    // 0.5
             { value: yellowRange / totalRange, color: "#F5CD19" }, // 0.25
             { value: greenRange / totalRange, color: "#5BE12C" },  // 0.25
           ];
         
           // Arc and needle center at the bottom of the SVG
           const centerX = 110;
           const centerY = 120; // BOTTOM of the SVG!
           const radius = 80;
           const angle = Math.PI - gaugePercent * Math.PI;
           const needleX = centerX + radius * Math.cos(angle);
           const needleY = centerY + radius * Math.sin(angle);
         
           return (
             <div style={{ marginTop:'50px', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
               <PieChart width={220} height={180}>
                  <Pie
                    data={sections}
                    startAngle={180}
                    endAngle={0}
                    innerRadius={60}
                    outerRadius={100}
                    cx={110}
                    cy={110}
                    dataKey="value"
                    stroke="none"
                  >
                    {sections.map((entry, idx) => (
                      <Cell key={`cell-${idx}`} fill={entry.color} />
                    ))}
                  </Pie>
                  {/* Needle */}
                  <g>
                    <line
                      x1={110}
                      y1={110}
                      x2={110 + 80 * Math.cos(Math.PI * (1 - gaugePercent))}
                      y2={110 - 80 * Math.sin(Math.PI * (1 - gaugePercent))}
                      stroke="#222"
                      strokeWidth="4"
                      strokeLinecap="round"
                    />
                    <circle cx={110} cy={110} r={7} fill="#222" />
                  </g>
                  {/* Value label */}
                  <text x={110} y={100} textAnchor="middle" fontSize={22} fill="#222" fontWeight="bold">
                    {overallSentiment}
                  </text>
                </PieChart>
               <div className="sentiment-score" style={{ textAlign: 'center' }}>
                 <span className={`score ${overallSentiment > 0 ? 'positive' : 'negative'}`}>{overallSentiment > 0 ? 'Bullish' : 'Bearish'}</span>
               </div>
             </div>
            );
            })() : (
              <div className="sentiment-score">
                <span className="label">No sentiment data available</span>
              </div>
            )}
          </div>
        </div>
      </div>

        {/* Top Stocks by Sentiment */}
        <div className="chart-card gauge-board">
          <div className="chart-header">
            <h3>Top Stocks by Sentiment</h3>
            <div className="info-tooltip" title="Shows the 10 stocks getting the most attention. Higher positive numbers mean people are very positive about the stock, lower negative numbers mean they're very negative. This helps you see which stocks are trending.">
              ℹ️
            </div>
          </div>
          <div className="stock-sentiment-list">
            {sentimentData && sentimentData.length > 0 ? (
              sentimentData.slice(0, 10).map((item, index) => (
                <div key={index} className="stock-sentiment-item">
                  <div className="stock-info">
                    <span className="stock-symbol">{item.stock}</span>
                    <span className="stock-name">{item.stock_name || item.stock}</span>
                  </div>
                  <div className="sentiment-indicator">
                    <span className={`sentiment-value ${item.sentiment > 0 ? 'positive' : 'negative'}`}>{item.sentiment}</span>
                  </div>
                  <div className="powered-by-ai">Powered by AI</div>
                </div>
              ))
            ) : (
              <div className="stock-sentiment-item">
                <span className="label">No sentiment data available</span>
              </div>
            )}
          </div>
        </div>

        {/* Sector Analysis Charts */}
        <div className="chart-card gauge-board">
          <div className="chart-header">
            <h3>Sector Bullseye</h3>
            <div className="info-tooltip" title="Shows how well different sectors (Technology, Healthcare, Finance, etc.) are performing. Higher scores mean that sector is doing well, lower scores mean it's struggling. Helps you see which business areas are hot right now.">
              ℹ️
            </div>
          </div>
          <div className="sector-bullseye-chart">
            <AdvancedCharts.SectorBullseyeChart
              data={sectorData.map(sector => ({
                name: sector.sector_name,
                performance_score: sector.performance_score || 0
              }))}
              title="Sector Bullseye"
            />
          </div>
        </div>
        
        <div className="chart-card gauge-board">
          <div className="chart-header">
            <h3>Risk Gauge Board</h3>
            <div className="info-tooltip" title="For each sector, shows Risk Score (how risky to invest), Return Potential (how much money you might make), and Market Cap (how big the companies are). High risk + high return = risky but could pay off big. Low risk + low return = safe but won't make you rich quickly.">
              ℹ️
            </div>
          </div>
          <div className='risk-return-gauge-chart'>
            <AdvancedCharts.RiskReturnGaugeChart
              data={sectorData.map(sector => ({
                symbol: sector.sector_name,
                risk_score: sector.risk_score || 0,
                return_potential: sector.return_potential || 0,
                market_cap: sector.market_cap || 0
              }))}
            />
          </div>
        </div>
        
        <div className="chart-card gauge-board">
          <div className="chart-header">
            <h3>Sector Comparison</h3>
            <div className="info-tooltip" title="Shows six measures for each sector: Profitability (how much money companies make), Valuation (if stocks are expensive/cheap), Growth (how fast sector is growing), Liquidity (how easy to buy/sell), Financial Health (how strong finances are), and Market Position (how well compared to others). Bigger shape = better scores.">
              ℹ️
            </div>
          </div>
          <div className='sector-radar-chart'>
            <AdvancedCharts.SectorRadarChart
              data={sectorData.map(sector => ({
                name: sector.sector_name,
                profitability: sector.profitability || 0,
                valuation: sector.valuation || 0,
                growth: sector.growth || 0,
                liquidity: sector.liquidity || 0,
                financial_health: sector.financial_health || 0,
                market_position: sector.market_position || 0
              }))}
              title="Sector Analysis"
            />
          </div>
        </div>
        
        <div className="chart-card gauge-board">
          <div className="chart-header">
            <h3>Financial Metrics Overview</h3>
            <div className="info-tooltip" title="Shows three important financial numbers: ROE (how efficiently companies use money - higher is better), P/E Ratio (how expensive stocks are - lower is cheaper), and Debt/Equity (how much debt companies have - lower is less risky). These help measure if stocks are good value.">
              ℹ️
            </div>
          </div>
          <div className='multiAxis-financial-chart'>
            <AdvancedCharts.MultiAxisFinancialChart
              data={sectorData.map(sector => ({
                symbol: sector.sector_name,
                roe: sector.roe || 0,
                pe_ratio: sector.pe_ratio || 0,
                debt_equity: sector.debt_equity || 0
              }))}
              title="Sector Financial Metrics"
            />
          </div>
        </div>
      </div>
    </div>
  );



  const renderStockNewsSection = () => {
    if (!selectedStock) {
      return (
        <div className="chart-card">
          <div className="chart-header">
            <h3>Latest Stock News</h3>
            <div className="info-tooltip" title="Latest news and updates about the selected stock from database">
              ℹ️
            </div>
          </div>
          <div className="no-stock-selected">
            <p>Select a stock to view latest news</p>
          </div>
        </div>
      );
    }

    if (newsLoading) {
      return (
        <div className="chart-card">
          <div className="chart-header">
            <h3>Latest Stock News - {selectedStock}</h3>
            <div className="info-tooltip" title="Latest news and updates about the selected stock from database">
              ℹ️
            </div>
          </div>
          <div className="loading-message">
            <div className="spinner"></div>
            <p>Loading latest news from database...</p>
          </div>
        </div>
      );
    }

    if (!newsData || !newsData.articles || newsData.articles.length === 0) {
      return (
        <div className="chart-card">
          <div className="chart-header">
            <h3>Latest Stock News - {selectedStock}</h3>
            <div className="info-tooltip" title="Latest news and updates about the selected stock from database">
              ℹ️
            </div>
          </div>
          <div className="no-news-message">
            <p>No news available for {selectedStock} in the database</p>
            {newsData?.database_info && (
              <p className="database-info">
                Database: {newsData.database_info.table_name} 
                (Total articles: {newsData.database_info.total_articles_found})
              </p>
            )}
          </div>
        </div>
      );
    }

    return (
      <div className="chart-card">
        <div className="chart-header">
          <h3>Latest Stock News - {selectedStock}</h3>
          <div className="info-tooltip" title="Latest news and updates about the selected stock from database">
            ℹ️
          </div>
        </div>
        
        <div className="news-container">
          {newsData.articles.map((article, index) => (
            <div key={index} className="news-item">
              <div className="news-header">
                <h4 className="news-title">
                  <a href={article.url} target="_blank" rel="noopener noreferrer">
                    {article.title}
                  </a>
                </h4>
                <div className="news-meta">
                  <span className="news-source">{article.source}</span>
                  <span className="news-time">
                    {formatDateDDMMYYYY(article.published_at)} at{' '}
                    {new Date(article.published_at).toLocaleTimeString()}
                  </span>
                </div>
              </div>
              <p className="news-description">{article.description}</p>
            </div>
          ))}
        </div>

        {/* News Pagination */}
        {newsData.pagination && newsData.pagination.total_pages > 1 && (
          <div className="news-pagination">
            <div className="pagination-info">
              <span>
                Page {newsData.pagination.current_page} of {newsData.pagination.total_pages} 
                ({newsData.pagination.total_articles} articles)
              </span>
            </div>
            <div className="pagination-controls">
              <button 
                className={`pagination-btn ${!newsData.pagination.has_prev ? 'disabled' : ''}`}
                onClick={() => fetchStockNews(selectedStock, newsData.pagination.current_page - 1)}
                disabled={!newsData.pagination.has_prev}
              >
                ← Previous
              </button>
              <div className="page-numbers">
                {Array.from({ length: newsData.pagination.total_pages }, (_, i) => i + 1).map(pageNum => (
                  <button
                    key={pageNum}
                    className={`page-btn ${newsData.pagination.current_page === pageNum ? 'active' : ''}`}
                    onClick={() => fetchStockNews(selectedStock, pageNum)}
                  >
                    {pageNum}
                  </button>
                ))}
              </div>
              <button 
                className={`pagination-btn ${!newsData.pagination.has_next ? 'disabled' : ''}`}
                onClick={() => fetchStockNews(selectedStock, newsData.pagination.current_page + 1)}
                disabled={!newsData.pagination.has_next}
              >
                Next →
              </button>
            </div>
          </div>
        )}

        {/* Database Info */}
        {newsData.database_info && (
          <div className="database-info">
            <p>Data from: {newsData.database_info.table_name}</p>
                            <p>Last updated: {formatToIST(newsData.last_updated)}</p>
          </div>
        )}
      </div>
    );
  };

  const renderMarketSentiment = () => {
    // Calculate overall market sentiment
    const overallSentiment = sentimentData.length > 0 ? {
      sentiment: Math.round(sentimentData.reduce((sum, item) => sum + item.sentiment, 0) / sentimentData.length * 10) / 10,
      label: 'Market Average'
    } : null;

    // Get sentiment for selected stock
    const selectedStockSentiment = selectedStock && sentimentData.length > 0 
      ? sentimentData.find(item => item.stock === selectedStock)
      : null;

    // Get last updated date from database timestamp
    const lastUpdated = lastFetchedTimestamp 
      ? formatToIST(lastFetchedTimestamp.last_modified)
      : (sentimentData.length > 0 
          ? formatToIST(sentimentData[0].datetime)
          : null);

    console.log('🕒 Last updated debug:', { 
      sentimentDataLength: sentimentData.length, 
      firstItem: sentimentData[0], 
      lastUpdated,
      timestampData: lastFetchedTimestamp
    });

    return (
      <div className="dashboard-section stock-sentiment-dashboard">
        <div className="charts-section">
          {/* Selected Stock Sentiment Card */}
          {selectedStock && (
            <div className="chart-card">
              <h3>Selected Stock Sentiment - {selectedStock}</h3>
              <div className="sentiment-overview">
                <div className="sentiment-card selected-stock">
                  {selectedStockSentiment ? (
                    <>
                      <div className="sentiment-score">
                        <span className={`score ${selectedStockSentiment.sentiment > 0 ? 'positive' : 'negative'}`}>
                          {selectedStockSentiment.sentiment}
                        </span>
                        <span className="label">
                          {selectedStockSentiment.sentiment > 0 ? 'Bullish' : 'Bearish'}
                        </span>
                      </div>
                      <div className="sentiment-bar">
                        <div 
                          className={`bar-fill ${getSentimentClass(selectedStockSentiment.sentiment)}`} 
                          style={{ width: `${(selectedStockSentiment.sentiment / 10) * 100}%` }}
                        ></div>
                      </div>
                      <div className="powered-by-ai">Powered by AI</div>
                      <div className="sentiment-details">
                        <span className="stock-name">{selectedStockSentiment.stock_name || selectedStock}</span>
                        <span className="update-time" style={{ color: 'white' }}>
                          Last updated: {formatToIST(selectedStockSentiment.datetime)}
                          {lastFetchedTimestamp && (
                            <> | Last fetched: {formatToIST(lastFetchedTimestamp.last_modified)}</>
                          )}
                        </span>
                      </div>
                    </>
                  ) : (
                    <div className="sentiment-score">
                      <span className="label">No sentiment data available for {selectedStock}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Price Chart */}
          <div className="chart-card">
            <StockPriceChart stockSymbol={selectedStock} />
          </div>

          {/* Latest Stock News Section */}
          {renderStockNewsSection()}

          {/* Market Sentiment Overview */}
          <div className="chart-card">
            <div className="chart-header">
              <h3>Market Sentiment Overview</h3>
              <div className="info-tooltip" title="Shows the overall mood of the entire stock market. Positive numbers mean investors are optimistic (bullish), negative numbers mean they're worried (bearish). The bar shows how strong this feeling is.">
                ℹ️
              </div>
            </div>
            <div className="sentiment-overview">
              <div className="sentiment-card overall">
                <h3>Overall Market Sentiment</h3>
                {sentimentData.length > 0 ? (
                  (() => {
                    const overallSentiment = {
                      sentiment: Math.round(sentimentData.reduce((sum, item) => sum + item.sentiment, 0) / sentimentData.length * 10) / 10,
                      label: 'Market Average'
                    };
                    return (
                      <>
                        <div className="sentiment-score">
                          <span className={`score ${overallSentiment.sentiment > 0 ? 'positive' : 'negative'}`}>{overallSentiment.sentiment}</span>
                          <span className="label">{overallSentiment.label || (overallSentiment.sentiment > 0 ? 'Bullish' : 'Bearish')}</span>
                        </div>
                        <div className="sentiment-bar">
                          <div className={`bar-fill ${getSentimentClass(overallSentiment.sentiment)}`} style={{ width: `${(overallSentiment.sentiment / 10) * 100}%` }}></div>
                        </div>
                      </>
                    );
                  })()
                ) : (
                  <div className="sentiment-score">
                    <span className="label">No sentiment data available</span>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Top Stocks by Sentiment */}
          <div className="chart-card">
            <div className="chart-header">
              <h3>Top Stocks by Sentiment</h3>
              <div className="info-tooltip" title="Shows the 10 stocks getting the most attention. Higher positive numbers mean people are very positive about the stock, lower negative numbers mean they're very negative. This helps you see which stocks are trending.">
                ℹ️
              </div>
            </div>
            <div className="stock-sentiment-list">
              {sentimentData && sentimentData.length > 0 ? (
                sentimentData.slice(0, 10).map((item, index) => (
                  <div key={index} className="stock-sentiment-item">
                    <div className="stock-info">
                      <span className="stock-symbol">{item.stock}</span>
                      <span className="stock-name">{item.stock_name || item.stock}</span>
                    </div>
                    <div className="sentiment-indicator">
                      <span className={`sentiment-value ${item.sentiment > 0 ? 'positive' : 'negative'}`}>{item.sentiment}</span>
                    </div>
                    <div className="powered-by-ai">Powered by AI</div>
                  </div>
                ))
              ) : (
                <div className="stock-sentiment-item">
                  <span className="label">No sentiment data available</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderFundamentalAnalysis = () => {
    if (selectedStock && fundamentalData) {
      return (
        <div className="dashboard-section fundamental-dashboard">
          <FundamentalDashboard selectedStock={selectedStock} />
        </div>
      );
    } else if (selectedStock) {
      return (
        <div className="dashboard-section">
          <div className="loading">
            <div className="spinner"></div>
            <p>Loading fundamental analysis...</p>
          </div>
        </div>
      );
    } else {
      return (
        <div className="dashboard-section">
          <div className="no-stock-selected">
            <p>Select a stock from the sidebar to view detailed fundamental analysis</p>
          </div>
        </div>
      );
    }
  };

  const renderUserSettings = () => (
    <div className="dashboard-section">
      <div className="section-header">
        <div className="header-content">
          <h2>⚙️ User Settings</h2>
          <p>Customize your dashboard and preferences</p>
        </div>
        <button className="add-button" title="Add new item">
          <span>+</span>
        </button>
      </div>
      
      <div className="settings-grid">
        <div className="settings-card">
          <h3>Profile Settings</h3>
          <div className="setting-item">
            <label>Display Name</label>
            <input type="text" placeholder="Enter your name" />
          </div>
          <div className="setting-item">
            <label>Email Notifications</label>
            <select>
              <option>Daily</option>
              <option>Weekly</option>
              <option>Monthly</option>
              <option>Never</option>
            </select>
          </div>
          <div className="setting-item">
            <label>Theme</label>
            <select>
              <option>Light</option>
              <option>Dark</option>
              <option>Auto</option>
            </select>
          </div>
        </div>
        
        <div className="settings-card">
          <h3>Dashboard Preferences</h3>
          <div className="setting-item">
            <label>Default Tab</label>
            <select>
              <option>Sectoral View</option>
              <option>Market Sentiment</option>
              <option>Fundamental Analysis</option>
            </select>
          </div>
          <div className="setting-item">
            <label>Refresh Interval</label>
            <select>
              <option>30 seconds</option>
              <option>1 minute</option>
              <option>5 minutes</option>
              <option>Manual</option>
            </select>
          </div>
          <div className="setting-item">
            <label>Show Alerts</label>
            <input type="checkbox" defaultChecked />
          </div>
        </div>
        
        <div className="settings-card">
          <h3>Data Sources</h3>
          <div className="setting-item">
            <label>Primary Data Source</label>
            <select>
              <option>Yahoo Finance</option>
              <option>Alpha Vantage</option>
              <option>Quandl</option>
            </select>
          </div>
          <div className="setting-item">
            <label>Backup Data Source</label>
            <select>
              <option>Alpha Vantage</option>
              <option>Yahoo Finance</option>
              <option>Quandl</option>
            </select>
          </div>
        </div>
      </div>
    </div>
  );

  // const renderOverallPortfolioSentiment = () => {
  //   if (portfolioLoading || portfolio.length === 0) {
  //     return null;
  //   }

  //   // Get sentiment data for portfolio stocks
  //   const portfolioSentiments = portfolio.map(item => {
  //     const sentiment = sentimentData.find(s => s.stock === item.stock_symbol);
  //     return {
  //       ...item,
  //       sentiment: sentiment ? sentiment.sentiment : 0,
  //       sentiment_data: sentiment
  //     };
  //   });

  //   // Calculate overall portfolio sentiment
  //   const overallPortfolioSentiment = portfolioSentiments.length > 0 
  //     ? Math.round(portfolioSentiments.reduce((sum, item) => sum + item.sentiment, 0) / portfolioSentiments.length * 10) / 10
  //     : 0;

  //   return (
  //     <div className="chart-card portfolio-overall-sentiment-section">
  //       <div className="chart-header">
  //         <h3>Overall Portfolio Sentiment</h3>
  //         <div className="info-tooltip" title="Shows the overall sentiment for your entire portfolio. This score tells you if your portfolio is generally performing well (positive) or poorly (negative). A higher positive score means your portfolio is doing well overall.">
  //           ℹ️
  //         </div>
  //       </div>
        
  //       <div className="sentiment-overview">
  //         <div className="sentiment-card portfolio-overall">
  //           <div className="sentiment-score">
  //             <span className={`score ${overallPortfolioSentiment > 0 ? 'positive' : 'negative'}`}>
  //               {overallPortfolioSentiment}
  //             </span>
  //             <span className="label">
  //               {overallPortfolioSentiment > 0 ? 'Bullish Portfolio' : 'Bearish Portfolio'}
  //             </span>
  //           </div>
  //           <div className="sentiment-bar">
  //             <div 
  //               className={`bar-fill ${getSentimentClass(overallPortfolioSentiment)}`} 
  //               style={{ width: `${(overallPortfolioSentiment / 10) * 100}%` }}
  //             ></div>
  //           </div>
  //           <div className="powered-by-ai">Powered by AI</div>
  //           <div className="portfolio-summary">
  //             <p>Portfolio contains {portfolio.length} stocks with an average sentiment of {overallPortfolioSentiment}</p>
  //           </div>
  //         </div>
  //       </div>
  //     </div>
  //   );
  // };


const renderOverallPortfolioSentiment = () => {
  if (portfolioLoading || portfolio.length === 0) {
    return null;
  }

  // Get sentiment data for portfolio stocks
  const portfolioSentiments = portfolio.map(item => {
    const sentiment = sentimentData.find(s => s.stock === item.stock_symbol);
    return {
      ...item,
      sentiment: sentiment ? sentiment.sentiment : 0,
      sentiment_data: sentiment
    };
  });

  // Calculate overall portfolio sentiment
  const overallPortfolioSentiment = portfolioSentiments.length > 0 
    ? Math.round(portfolioSentiments.reduce((sum, item) => sum + item.sentiment, 0) / portfolioSentiments.length * 10) / 10
    : 0;

  // Convert sentiment to a value between 0 and 1 for the gauge
  // Assuming -10 (very bearish) to +10 (very bullish)
  // const gaugePercent = (overallPortfolioSentiment + 10) / 20;

  const min = -10, max = 10;
  const gaugePercent = (overallPortfolioSentiment - min) / (max - min);

  const redRange = 0 - min;    // 10
  const yellowRange = 5 - 0;   // 5
  const greenRange = max - 5;  // 5
  const totalRange = max - min; // 20
         
  const sections = [
    { value: redRange / totalRange, color: "#EA4228" },    // 0.5
    { value: yellowRange / totalRange, color: "#F5CD19" }, // 0.25
    { value: greenRange / totalRange, color: "#5BE12C" },  // 0.25
  ];
  // Gauge data for PieChart
  // const data = [
  //   { value: gaugePercent, color: gaugePercent > 0.6 ? "#5BE12C" : gaugePercent > 0.4 ? "#F5CD19" : "#EA4228" },
  //   { value: 1 - gaugePercent, color: "#eee" }
  // ];
  

  return (
    <div className="chart-card portfolio-overall-sentiment-section">
      <div className="chart-header">
        <h3>Overall Portfolio Sentiment</h3>
        <div className="info-tooltip" title="Shows the overall sentiment for your entire portfolio. This score tells you if your portfolio is generally performing well (positive) or poorly (negative). A higher positive score means your portfolio is doing well overall.">
          ℹ️
        </div>
      </div>
      <div className="sentiment-overview" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <PieChart width={220} height={120}>
          <Pie
            data={sections}
            startAngle={180}
            endAngle={0}
            innerRadius={60}
            outerRadius={100}
            cx={110}
            cy={110}
            dataKey="value"
            stroke="none"
          >
            {sections.map((entry, idx) => (
              <Cell key={`cell-${idx}`} fill={entry.color} />
            ))}
          </Pie>
          {/* Needle */}
          <g>
            <line
              x1={110}
              y1={110}
              x2={110 + 80 * Math.cos(Math.PI * (1 - gaugePercent))}
              y2={110 - 80 * Math.sin(Math.PI * (1 - gaugePercent))}
              stroke="#222"
              strokeWidth="4"
              strokeLinecap="round"
            />
            <circle cx={110} cy={110} r={7} fill="#222" />
          </g>
          {/* Value label */}
          <text x={110} y={100} textAnchor="middle" fontSize={22} fill="#222" fontWeight="bold">
            {overallPortfolioSentiment}
          </text>
        </PieChart>
        <div className="sentiment-score" style={{ textAlign: 'center' }}>
          <span className={`score ${overallPortfolioSentiment > 0 ? 'positive' : 'negative'}`}>
            {overallPortfolioSentiment > 0 ? 'Bullish Portfolio' : 'Bearish Portfolio'}
          </span>
        </div>
        <div className="powered-by-ai">Powered by AI</div>
        <div className="portfolio-summary" style={{ fontSize: '0.95em', color: '#aaa' }}>
          Portfolio contains {portfolio.length} stocks with an average sentiment of {overallPortfolioSentiment}
        </div>
      </div>
    </div>
  );
};

  const renderIndividualStockSentiments = () => {
    if (portfolioLoading || portfolio.length === 0) {
      return null;
    }

    // Get sentiment data for portfolio stocks
    const portfolioSentiments = portfolio.map(item => {
      const sentiment = sentimentData.find(s => s.stock === item.stock_symbol);
      return {
        ...item,
        sentiment: sentiment ? sentiment.sentiment : 0,
        sentiment_data: sentiment
      };
    });

    return (
      <div className="chart-card portfolio-stock-sentiments-section">
        <div className="chart-header">
          <h3>Individual Stock Sentiments</h3>
          <div className="info-tooltip" title="Shows the sentiment for each individual stock in your portfolio. This helps you identify which stocks are performing well (positive sentiment) and which ones might need attention (negative sentiment).">
            ℹ️
          </div>
        </div>
        
        <div className="portfolio-sentiment-list">
          {portfolioSentiments.map((item, index) => (
            <div key={index} className="portfolio-sentiment-item">
              <div className="stock-info">
                <span className="stock-symbol">{item.stock_symbol}</span>
                <span className="stock-name">{item.stock_name}</span>
              </div>
              <div className="sentiment-indicator">
                <span className={`sentiment-value ${item.sentiment > 0 ? 'positive' : 'negative'}`}>
                  {item.sentiment}
                </span>
                <span className="sentiment-label">
                  {item.sentiment > 0 ? 'Bullish' : 'Bearish'}
                </span>
              </div>
              <div className="powered-by-ai">Powered by AI</div>
              <div className="stock-actions">
                <button 
                  className="remove-btn"
                  onClick={() => removeFromPortfolio(item.stock_symbol)}
                  title="Remove from Portfolio"
                >
                  ×
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderPortfolioSummary = () => {
    if (portfolioLoading || portfolio.length === 0) {
      return null;
    }

    return (
      <div className="chart-card portfolio-summary-card">
        <div className="chart-header">
          <h3>Portfolio Overview</h3>
          <div className="info-tooltip" title="Quick overview of your portfolio statistics and recent activity.">
            ℹ️
          </div>
        </div>
        
        <div className="portfolio-summary-section">
          <div className="summary-stats">
            <div className="stat-item">
              <span className="stat-label">Total Stocks</span>
              <span className="stat-value">{portfolio.length}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Added Today</span>
              <span className="stat-value">
                {portfolio.filter(item => {
                  const today = new Date().toDateString();
                  const addedDate = new Date(item.added_date).toDateString();
                  return today === addedDate;
                }).length}
              </span>
            </div>
            <div className="stat-item">
              <span className="stat-label">This Week</span>
              <span className="stat-value">
                {portfolio.filter(item => {
                  const weekAgo = new Date();
                  weekAgo.setDate(weekAgo.getDate() - 7);
                  return new Date(item.added_date) >= weekAgo;
                }).length}
              </span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Avg Days Held</span>
              <span className="stat-value">
                {Math.round(portfolio.reduce((sum, item) => {
                  return sum + Math.floor((new Date() - new Date(item.added_date)) / (1000 * 60 * 60 * 24));
                }, 0) / portfolio.length)}
              </span>
            </div>
          </div>
        </div>
      </div>
    );
  };


  const renderPortfolioSection = () => {
    if (portfolioLoading) {
      return (
        <div className="chart-card portfolio-section">
          <h3>My Portfolio</h3>
          <div className="loading-message">
            <div className="spinner"></div>
            <p>Loading your portfolio...</p>
          </div>
        </div>
      );
    }

    if (portfolio.length === 0) {
      return (
        <div className="chart-card portfolio-section">
          <h3>My Portfolio</h3>
          <div className="empty-portfolio">
            <p>📈 Your portfolio is empty</p>
            <p>Add stocks from the Market Sentiment or Fundamental Analysis tabs to get started!</p>
          </div>
        </div>
      );
    }

    return (
      <div className="chart-card portfolio-section">
        <div className="chart-header">
          <h3>Portfolio Details ({portfolio.length} assets)</h3>
          <div className="info-tooltip" title="Your complete portfolio list with sentiment scores. Each stock shows its current market sentiment to help you track performance.">
            ℹ️
          </div>
        </div>

        {/* Portfolio List Header */}
        <div className="portfolio-list-header">
          <div className="header-column stock-info-header">
            <span>Stock Information</span>
          </div>
          <div className="header-column sentiment-header">
            <span>Market Sentiment</span>
          </div>
          <div className="header-column actions-header">
            <span>Actions</span>
          </div>
        </div>

        {/* Portfolio Items */}
        <div className="portfolio-list">
          {(() => {
            // Calculate pagination
            const totalPages = Math.ceil(portfolio.length / itemsPerPage);
            const startIndex = (currentPage - 1) * itemsPerPage;
            const endIndex = startIndex + itemsPerPage;
            const currentPortfolioItems = portfolio.slice(startIndex, endIndex);

            return currentPortfolioItems.map((item, index) => {
              // Get sentiment data for this stock
              const sentiment = sentimentData.find(s => s.stock === item.stock_symbol);
              const sentimentScore = sentiment ? sentiment.sentiment : 0;
              console.log("sentiment score for test",sentimentScore);
              return (
                <div key={item.stock_symbol} className="portfolio-item">
                  <div className="stock-info">
                    <div className="stock-main-info">
                      <button className="stock-link" onClick={() => handlePortfolioStockClick(item.stock_symbol)}>
                        <span className="stock-symbol">{item.stock_symbol}</span>
                        <span className="stock-name">{item.stock_name}</span>
                      </button>
                    </div>
                    <div className="stock-meta-info">
                      <span className="added-date">
                        <span className="date-icon">📅</span>
                        {formatDateDDMMYYYY(item.added_date)}
                      </span>
                      <span className="days-held">
                        {Math.floor((new Date() - new Date(item.added_date)) / (1000 * 60 * 60 * 24))} days
                      </span>
                    </div>
                  </div>
                  <div className="sentiment-indicator">
                    <span className={`sentiment-value ${sentimentScore > 0 ? 'positive' : 'negative'}`}>
                      {sentimentScore}
                    </span>
                    <span className="sentiment-label">
                      {sentimentScore > 0 ? 'Bullish' : 'Bearish'}
                    </span>
                  </div>
                  <div className="powered-by-ai">Powered by AI</div>
                  <div className="stock-actions">
                    <button 
                      className="remove-btn"
                      onClick={() => removeFromPortfolio(item.stock_symbol)}
                      title="Remove from Portfolio"
                    >
                      ×
                    </button>
                  </div>
                </div>
              );
            });
          })()}
        </div>

        {/* Pagination Controls */}
        {(() => {
          const totalPages = Math.ceil(portfolio.length / itemsPerPage);
          if (totalPages <= 1) return null;

          return (
            <div className="portfolio-pagination">
              <div className="pagination-info">
                <span>
                  Showing {((currentPage - 1) * itemsPerPage) + 1} to {Math.min(currentPage * itemsPerPage, portfolio.length)} of {portfolio.length} stocks
                </span>
              </div>
              <div className="pagination-controls">
                <button 
                  className={`pagination-btn ${currentPage === 1 ? 'disabled' : ''}`}
                  onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                  disabled={currentPage === 1}
                >
                  ← Previous
                </button>
                <div className="page-numbers">
                  {Array.from({ length: totalPages }, (_, i) => i + 1).map(pageNum => (
                    <button
                      key={pageNum}
                      className={`page-btn ${currentPage === pageNum ? 'active' : ''}`}
                      onClick={() => setCurrentPage(pageNum)}
                    >
                      {pageNum}
                    </button>
                  ))}
                </div>
                <button 
                  className={`pagination-btn ${currentPage === totalPages ? 'disabled' : ''}`}
                  onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                  disabled={currentPage === totalPages}
                >
                  Next →
                </button>
              </div>
            </div>
          );
        })()}

        {/* Portfolio Footer */}
        <div className="portfolio-footer">
          <div className="footer-info">
            <span className="footer-text">Last updated: {formatToIST(new Date())}</span>
            <span className="footer-text">•</span>
            <span className="footer-text">Sentiment data refreshes automatically</span>
          </div>
        </div>
      </div>
    );
  };

  // Add a simple fallback display if nothing is loading
  if (!loading && !error && sentimentData.length === 0 && sectorData.length === 0) {
    console.log('⚠️ Dashboard has no data, showing fallback display');
    return (
      <div className="dashboard">
        <div className="dashboard-section">
          <div className="section-header">
            <h2>📊 Dashboard Loading</h2>
            <p>Setting up your market analysis dashboard...</p>
          </div>
          <div className="loading-message">
            <div className="spinner"></div>
            <p>Loading dashboard data...</p>
            <button onClick={() => window.location.reload()} className="retry-btn">
              Retry Loading
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="loading-spinner"></div>
        <p>Loading your dashboard...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-error">
        <div className="error-icon">⚠️</div>
        <h3>Oops! Something went wrong</h3>
        <p>{error}</p>
        <button onClick={() => window.location.reload()}>Try Again</button>
      </div>
    );
  }

  // Force activeTab for testing - default to portfolio if not set
  const currentTab = activeTab || 'portfolio';
  
  // Add fallback display for debugging
  if (!sentimentData.length && !sectorData.length && !loading) {
    return (
      <div className="dashboard">
        <div className="dashboard-section">
          <div className="section-header">
            <h2>🔍 Debug Mode - Dashboard</h2>
            <p>Component is rendering but no data loaded</p>
          </div>
          <div className="debug-info">
            <h3>Debug Information:</h3>
            <ul>
              <li>✅ Component is rendering</li>
              <li>❌ No sentiment data loaded ({sentimentData.length} items)</li>
              <li>❌ No sector data loaded ({sectorData.length} items)</li>
              <li>🔧 Active Tab: {currentTab}</li>
              <li>🔧 Selected Stock: {selectedStock || 'None'}</li>
              <li>🔧 Authenticated: {isAuthenticated ? 'Yes' : 'No'}</li>
              <li>🔧 Loading: {loading ? 'Yes' : 'No'}</li>
              <li>🔧 Error: {error || 'None'}</li>
            </ul>
            <button onClick={() => window.location.reload()}>Reload Page</button>
          </div>
        </div>
      </div>
    );
  }
  
  // Tab Navigation Section (now global for all 3 tabs)
  const renderTabNavigation = () => (
    <div className="portfolio-tab-navigation">
      <div className="tab-nav-container">
        {activeTab === 'portfolio' ? (
          <>
            <button 
              className={`portfolio-tab-btn ${activeTab === 'portfolio' ? 'active' : ''}`}
              onClick={() => onTabChange('portfolio')}
            >
              <span className="tab-icon">💼</span>
              <span className="tab-label">Portfolio Overview</span>
            </button>
          </>
        ):(
          <>
            <button 
              className={`portfolio-tab-btn ${activeTab === 'market' ? 'active' : ''}`}
              onClick={() => onTabChange('market')}
            >
              <span className="tab-icon">📈</span>
              <span className="tab-label">Market Sentiment</span>
            </button>
            <button 
              className={`portfolio-tab-btn ${activeTab === 'fundamental' ? 'active' : ''}`}
              onClick={() => onTabChange('fundamental')}
            >
              <span className="tab-icon">📋</span>
              <span className="tab-label">Fundamental Analysis</span>
            </button>
          </>
        )}
        {/* <button 
          className={`portfolio-tab-btn ${activeTab === 'portfolio' ? 'active' : ''}`}
          onClick={() => onTabChange('portfolio')}
        >
          <span className="tab-icon">💼</span>
          <span className="tab-label">Portfolio Overview</span>
        </button> */}
        {/* <button 
          className={`portfolio-tab-btn ${activeTab === 'market' ? 'active' : ''}`}
          onClick={() => onTabChange('market')}
        >
          <span className="tab-icon">📈</span>
          <span className="tab-label">Market Sentiment</span>
        </button>
        <button 
          className={`portfolio-tab-btn ${activeTab === 'fundamental' ? 'active' : ''}`}
          onClick={() => onTabChange('fundamental')}
        >
          <span className="tab-icon">📋</span>
          <span className="tab-label">Fundamental Analysis</span>
        </button> */}
      </div>
    </div>
  );

  // Section headers for each tab
  const renderTabHeader = () => {
    // Helper for add/remove button
    const renderAddRemoveButton = (tabName) => {
      if (!selectedStock) return null;
      return (
        <button
          className={`add-button ${selectedStock && isInPortfolio(selectedStock) ? 'remove' : 'add'}`}
          title={selectedStock && isInPortfolio(selectedStock) ? 'Remove from Portfolio' : 'Add to Portfolio'}
          onClick={() => selectedStock && isInPortfolio(selectedStock)
            ? removeFromPortfolio(selectedStock)
            : handleAddButtonClick(tabName)
          }
        >
          <span>{selectedStock && isInPortfolio(selectedStock) ? '−' : '+'}</span>
        </button>
      );
    };
    

    if (activeTab === 'portfolio') {
      return (
        <div className="section-header">
          <div className="header-content">
            <h2>💼 My Portfolio</h2>
            <p>Manage your stock portfolio and watchlist</p>
          </div>
          {renderAddRemoveButton('portfolio')}
        </div>
      );
    }
    if (activeTab === 'market') {
      return (
        <div className="section-header">
          <div className="header-content">
            <h2>📈 Market Sentiment</h2>
            <p>Real-time sentiment analysis and market mood indicators</p>
          </div>
          {renderAddRemoveButton('market')}
        </div>
      );
    }
    if (activeTab === 'fundamental') {
      return (
        <div className="section-header">
          <div className="header-content">
            <h2>📋 Fundamental Analysis</h2>
            <p>Deep dive into company fundamentals and financial metrics</p>
          </div>
          {renderAddRemoveButton('fundamental')}
        </div>
      );
    }
    return null;
  };

  // Main content for each tab
  const renderTabContent = () => {
    if (activeTab === 'portfolio') {
      return (
        <div className="charts-section">
          {renderPortfolioSummary()}
          {renderPortfolioSection()}
          {renderOverallPortfolioSentiment()}
        </div>
      );
    }
    if (activeTab === 'market') {
      return <div className="charts-section stock-chart">{renderMarketSentiment()}</div>;
    }
    if (activeTab === 'fundamental') {
      return <div className="charts-section fundamental-chart">{renderFundamentalAnalysis()}</div>;
    }
    return null;
  };



  // exchange-sentiment section
  // if (activeTab === 'exchange-sentiment') {
  //   return (
  //     <div className="dashboard">
  //       <h2>🌐 Exchange Sentiment Index</h2>
  //       {exchangeSentimentLoading ? (
  //         <div>Loading...</div>
  //       ) : (
  //         <table>
  //           <thead>
  //             <tr>
  //               <th>Ticker</th>
  //               <th>Index</th>
  //               <th>Date</th>
  //               <th>Open</th>
  //               <th>Close</th>
  //               <th>Volume</th>
  //               {/* Add more columns as needed */}
  //             </tr>
  //           </thead>
  //           <tbody>
  //             {exchangeSentimentData.map((row, idx) => (
  //               <tr key={idx}>
  //                 <td>{row.ticker}</td>
  //                 <td>{row.index_name}</td>
  //                 <td>{row.Date || row.date}</td>
  //                 <td>{row.Open}</td>
  //                 <td>{row.Close}</td>
  //                 <td>{row.Volume}</td>
  //                 {/* Add more cells as needed */}
  //               </tr>
  //             ))}
  //           </tbody>
  //         </table>
  //       )}
  //     </div>
  //   );
  // }

  if (activeTab === 'exchange-sentiment') {
    return (
      <div className="dashboard">
        <div className="exchange-sentiment-header">
            <span className="exchange-sentiment-icon" role="img" aria-label="globe">
              🌐
            </span>
            <span className="exchange-sentiment-title">Exchange Sentiment Index</span>
        </div>
        {exchangeSentimentLoading ? (
          <div>Loading...</div>
        ) : (
          <div className="exchange-sentiment-outer-card">
            <div className="exchange-sentiment-powered">Powered by AI</div>
            <div className="exchange-sentiment-scroll-container">
              <div className="exchange-sentiment-list">
                {(() => {
                  // Separate live and non-live indices
                  const live = exchangeSentimentData.filter(row => row.price_type === 'live');
                  const nonLive = exchangeSentimentData.filter(row => row.price_type !== 'live');
                  const sorted = [...live, ...nonLive];
                  return sorted.map((row, idx) => (
                    <div className="exchange-sentiment-row" key={idx}>
                      <div className="exchange-info">
                        <span className="exchange-symbol">{row.ticker}</span>
                        <span className="exchange-name">{row.index_name}</span>
                        {row.price_type === 'live' && (
                          <span className="live-label" style={{ color: 'red', fontWeight: 'bold', marginLeft: 8 }}>
                            ● Live
                          </span>
                        )}
                      </div>
                      <div className="sentiment-score-center">
                        <span className="sentiment-score">
                          {(row.price ?? row.Close)?.toFixed(2)}
                        </span>
                      </div>
                      <div className={`index-change-right ${row.change < 0 ? 'negative' : 'positive'}`}> 
                        {row.change > 0 ? '+' : ''}
                        {row.change?.toFixed(2)} {row.percent_change > 0 ? '+' : ''}
                        {row.percent_change?.toFixed(2)}%
                      </div>
                    </div>
                  ));
                })()}
              </div>
            </div>
          </div>
        )}
      </div>
    );
  }


  // Check if we're in sectoral view (separate from portfolio sub-tabs)
  if (activeTab === 'sectoral') {
    return (
      <div className="dashboard">
        {renderSectoralView()}
      </div>
    );
  }

  // Check if we're in top-stocks view
  if (activeTab === 'top-stocks') {
    return (
      <div className="dashboard">
        {renderTopStocksView()}
      </div>
    );
  }

  // Check if we're in sector-analysis view
  if (activeTab === 'sector-analysis') {
    return (
      <div className="dashboard">
        {renderSectorAnalysisView()}
      </div>
    );
  }

  // Portfolio view with sub-tabs
  return (
    <div className="dashboard">
      {renderTabNavigation()}
      {renderTabHeader()}
      {renderTabContent()}
    </div>
  );

};


export default Dashboard;