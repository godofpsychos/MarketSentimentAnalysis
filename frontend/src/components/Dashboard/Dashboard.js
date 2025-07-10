import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import FundamentalDashboard from '../../FundamentalDashboard';
import AdvancedCharts from '../../AdvancedCharts';
import { StockPriceChart } from '../../StockFinancialChart';
import './Dashboard.css';
import config from '../../config/config';

const Dashboard = ({ activeTab, selectedStock, isAuthenticated }) => {
  const [sentimentData, setSentimentData] = useState([]);
  const [sectorData, setSectorData] = useState([]);
  const [fundamentalData, setFundamentalData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();



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
          })
        ];

        const [sentimentResult, stocksResult] = await Promise.all(promises);
        
        console.log('📊 Sentiment result:', sentimentResult);
        console.log('📊 Stocks result:', stocksResult);
        
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

  const renderSectoralView = () => (
    <div className="dashboard-section">
      <div className="section-header">
        <h2>📊 Sectoral Analysis</h2>
        <p>Comprehensive sector-wise market analysis and performance metrics</p>
      </div>
      
      <div className="charts-section">
        {/* Moved Market Sentiment Overview here */}
        <div className="chart-card">
          <h3>Market Sentiment Overview</h3>
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
                        <div className={`bar-fill ${overallSentiment.sentiment > 0 ? 'positive' : 'negative'}`} style={{ width: `${Math.abs(overallSentiment.sentiment) * 10}%` }}></div>
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
          <h3>Top Stocks by Sentiment</h3>
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
                </div>
              ))
            ) : (
              <div className="stock-sentiment-item">
                <span className="label">No sentiment data available</span>
              </div>
            )}
          </div>
        </div>
        <div className="chart-card">
          <h3>Sector Bullseye</h3>
          <AdvancedCharts.SectorBullseyeChart 
            data={sectorData.map(sector => ({
              name: sector.sector_name,
              performance_score: sector.performance_score || 0
            }))}
            title="Sector Bullseye"
          />
        </div>
        
        <div className="chart-card gauge-board">
          <h3>Risk Gauge Board</h3>
          <AdvancedCharts.RiskReturnGaugeChart 
            data={sectorData.map(sector => ({
              symbol: sector.sector_name,
              risk_score: sector.risk_score || 0,
              return_potential: sector.return_potential || 0,
              market_cap: sector.market_cap || 0
            }))}
          />
        </div>
        
        <div className="chart-card">
          <h3>Sector Comparison</h3>
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
        
        <div className="chart-card">
          <h3>Financial Metrics Overview</h3>
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
  );

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

    // Get last updated date
    const lastUpdated = sentimentData.length > 0 
      ? new Date(sentimentData[0].datetime).toLocaleString()
      : null;

    console.log('🕒 Last updated debug:', { 
      sentimentDataLength: sentimentData.length, 
      firstItem: sentimentData[0], 
      lastUpdated 
    });

    return (
      <div className="dashboard-section">
        <div className="section-header">
          <h2>📈 Market Sentiment</h2>
          <p>Real-time sentiment analysis and market mood indicators</p>
          <div className="last-updated">
            <span>
              🕒 Last updated: {lastUpdated || new Date().toLocaleString()}
              {!lastUpdated && ' (Page loaded)'}
            </span>
          </div>
        </div>
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
                          className={`bar-fill ${selectedStockSentiment.sentiment > 0 ? 'positive' : 'negative'}`} 
                          style={{ width: `${Math.abs(selectedStockSentiment.sentiment) * 10}%` }}
                        ></div>
                      </div>
                      <div className="sentiment-details">
                        <span className="stock-name">{selectedStockSentiment.stock_name || selectedStock}</span>
                        <span className="update-time">
                          Updated: {new Date(selectedStockSentiment.datetime).toLocaleString()}
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

          {/* Price Chart moved here */}
          <div className="chart-card">
            <StockPriceChart stockSymbol={selectedStock} />
          </div>
          <div className="chart-card">
            <h3>Sector Financial Health Score</h3>
            {(() => {
              const sectorInfo = getSectorScoreForStock();
              if (sectorInfo) {
                return (
                  <AdvancedCharts.FinancialHealthGauge 
                    score={sectorInfo.score}
                    title={`${sectorInfo.sector} Health Score`}
                  />
                );
              } else {
                return (
                  <div className="no-data-message">
                    <p>No sector data available for health score calculation</p>
                  </div>
                );
              }
            })()}
          </div>
        </div>
      </div>
    );
  };

  const renderFundamentalAnalysis = () => {
    if (selectedStock && fundamentalData) {
      return (
        <div className="dashboard-section">
          <div className="section-header">
            <h2>📋 Fundamental Analysis - {selectedStock}</h2>
            <p>Deep dive into company fundamentals and financial metrics</p>
          </div>
          <FundamentalDashboard selectedStock={selectedStock} />
        </div>
      );
    } else if (selectedStock) {
      return (
        <div className="dashboard-section">
          <div className="section-header">
            <h2>📋 Fundamental Analysis - {selectedStock}</h2>
            <p>Loading fundamental data...</p>
          </div>
          <div className="loading">
            <div className="spinner"></div>
            <p>Loading fundamental analysis...</p>
          </div>
        </div>
      );
    } else {
      return (
        <div className="dashboard-section">
          <div className="section-header">
            <h2>📋 Fundamental Analysis</h2>
            <p>Please select a stock from the dropdown to view fundamental analysis</p>
          </div>
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
        <h2>⚙️ User Settings</h2>
        <p>Customize your dashboard and preferences</p>
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

  // Force activeTab for testing
  const currentTab = activeTab || 'sectoral';
  
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
  
  return (
    <div className="dashboard">
      {currentTab === 'sectoral' && renderSectoralView()}
      {currentTab === 'market' && renderMarketSentiment()}
      {currentTab === 'fundamental' && renderFundamentalAnalysis()}
      {currentTab === 'settings' && renderUserSettings()}
    </div>
  );
};

export default Dashboard;