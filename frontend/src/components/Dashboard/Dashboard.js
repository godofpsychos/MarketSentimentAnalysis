import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import FundamentalDashboard from '../../FundamentalDashboard';
import AdvancedCharts from '../../AdvancedCharts';
import { StockPriceChart } from '../../StockFinancialChart';
import './Dashboard.css';

const Dashboard = ({ activeTab, selectedStock, isAuthenticated }) => {
  const [sentimentData, setSentimentData] = useState([]);
  const [sectorData, setSectorData] = useState([]);
  const [fundamentalData, setFundamentalData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  // Debug: Check props
  console.log('Dashboard props:', { activeTab, selectedStock, isAuthenticated });

  useEffect(() => {
    const fetchData = async () => {
      console.log('Dashboard useEffect triggered');
      setLoading(true);
      setError(null);
      console.log('Starting data fetch for Dashboard...');

      try {
        // Fetch available data
        const promises = [
          fetch('http://localhost:5000/api/sentiment').then(res => res.json()).catch(() => ({ data: [] })),
          fetch('http://localhost:5000/api/stocks').then(res => res.json()).catch(() => ({ stocks: [] }))
        ];

        const [sentimentResult] = await Promise.all(promises);
        
        setSentimentData(sentimentResult.data || []);
        
        // Create sample sector data since sector-analysis API doesn't exist
        const sampleSectorData = [
          { sector_name: 'Technology', performance_score: 85, market_cap: 5000000000000, risk_score: 65, return_potential: 80, profitability: 75, valuation: 70, growth: 85, liquidity: 80, financial_health: 85, market_position: 90 },
          { sector_name: 'Healthcare', performance_score: 78, market_cap: 3000000000000, risk_score: 55, return_potential: 75, profitability: 80, valuation: 65, growth: 70, liquidity: 85, financial_health: 90, market_position: 75 },
          { sector_name: 'Finance', performance_score: 72, market_cap: 8000000000000, risk_score: 70, return_potential: 70, profitability: 85, valuation: 60, growth: 65, liquidity: 90, financial_health: 80, market_position: 85 },
          { sector_name: 'Energy', performance_score: 65, market_cap: 4000000000000, risk_score: 80, return_potential: 60, profitability: 70, valuation: 55, growth: 55, liquidity: 75, financial_health: 70, market_position: 65 },
          { sector_name: 'Consumer Goods', performance_score: 80, market_cap: 6000000000000, risk_score: 60, return_potential: 85, profitability: 75, valuation: 75, growth: 80, liquidity: 85, financial_health: 85, market_position: 80 },
          { sector_name: 'Real Estate', performance_score: 58, market_cap: 2000000000000, risk_score: 85, return_potential: 55, profitability: 60, valuation: 50, growth: 50, liquidity: 65, financial_health: 60, market_position: 55 }
        ];
        setSectorData(sampleSectorData);
        
        // If a stock is selected, fetch its data
        if (selectedStock) {
          try {
            const [, fundamentalInfo] = await Promise.all([
              fetch(`http://localhost:5000/api/stock-info/${selectedStock}`).then(res => res.json()).catch(() => null),
              fetch(`http://localhost:5000/api/fundamental-analysis/${selectedStock}`).then(res => res.json()).catch(() => null)
            ]);
            setFundamentalData(fundamentalInfo);
          } catch (stockError) {
            console.error('Error fetching stock data:', stockError);
          }
        }

        setLoading(false);
        console.log('Dashboard data loaded successfully!');
      } catch (error) {
        console.error('Error fetching data:', error);
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
        <div className="chart-card">
          <h3>Sector Performance Heatmap</h3>
          <AdvancedCharts.StockHeatmap 
            data={sectorData.map(sector => ({
              symbol: sector.sector_name,
              performance_score: sector.performance_score || Math.random() * 100,
              market_cap: sector.market_cap || Math.random() * 1000000000000
            }))}
            title="Sector Performance Overview"
          />
        </div>
        
        <div className="chart-card">
          <h3>Risk vs Return Analysis</h3>
          <AdvancedCharts.RiskReturnBubbleChart 
            data={sectorData.map(sector => ({
              symbol: sector.sector_name,
              risk_score: sector.risk_score || Math.random() * 100,
              return_potential: sector.return_potential || Math.random() * 100,
              market_cap: sector.market_cap || Math.random() * 1000000000000
            }))}
            title="Sector Risk-Return Profile"
          />
        </div>
        
        <div className="chart-card">
          <h3>Sector Comparison</h3>
          <AdvancedCharts.SectorRadarChart 
            data={sectorData.map(sector => ({
              name: sector.sector_name,
              profitability: sector.profitability || Math.random() * 100,
              valuation: sector.valuation || Math.random() * 100,
              growth: sector.growth || Math.random() * 100,
              liquidity: sector.liquidity || Math.random() * 100,
              financial_health: sector.financial_health || Math.random() * 100,
              market_position: sector.market_position || Math.random() * 100
            }))}
            title="Sector Analysis"
          />
        </div>
        
        <div className="chart-card">
          <h3>Financial Metrics Overview</h3>
          <AdvancedCharts.MultiAxisFinancialChart 
            data={sectorData.map(sector => ({
              symbol: sector.sector_name,
              roe: sector.roe || Math.random() * 30,
              pe_ratio: sector.pe_ratio || Math.random() * 50,
              debt_equity: sector.debt_equity || Math.random() * 2
            }))}
            title="Sector Financial Metrics"
          />
        </div>
      </div>
    </div>
  );

  const renderMarketSentiment = () => {
    // Get overall sentiment from sentimentData (example: average or first item)
    let overallSentiment = null;
    if (sentimentData && sentimentData.length > 0) {
      // Example: use the first item as overall, or calculate average
      overallSentiment = sentimentData[0];
    }

    return (
      <div className="dashboard-section">
        <div className="section-header">
          <h2>📈 Market Sentiment</h2>
          <p>Real-time sentiment analysis and market mood indicators</p>
        </div>
        <div className="charts-section">
          <div className="chart-card">
            <h3>Market Sentiment Overview</h3>
            <div className="sentiment-overview">
              <div className="sentiment-card overall">
                <h3>Overall Market Sentiment</h3>
                {overallSentiment ? (
                  <>
                    <div className="sentiment-score">
                      <span className={`score ${overallSentiment.sentiment > 0 ? 'positive' : 'negative'}`}>{overallSentiment.sentiment}</span>
                      <span className="label">{overallSentiment.label || (overallSentiment.sentiment > 0 ? 'Bullish' : 'Bearish')}</span>
                    </div>
                    <div className="sentiment-bar">
                      <div className={`bar-fill ${overallSentiment.sentiment > 0 ? 'positive' : 'negative'}`} style={{ width: `${Math.abs(overallSentiment.sentiment) * 10}%` }}></div>
                    </div>
                  </>
                ) : (
                  <div className="sentiment-score">
                    <span className="label">No sentiment data available</span>
                  </div>
                )}
              </div>
            </div>
          </div>
          {/* Price Chart moved here */}
          <div className="chart-card">
            <StockPriceChart stockSymbol={selectedStock} />
          </div>
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
            <h3>Financial Health Score</h3>
            <AdvancedCharts.FinancialHealthGauge 
              score={75}
              title="Market Health Score"
            />
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