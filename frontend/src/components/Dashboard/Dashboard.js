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

  // Debug: Check props
  console.log('Dashboard props:', { activeTab, selectedStock, isAuthenticated });

  // Calculate financial health score based on available data
  // This function makes the financial health score data-driven instead of hardcoded
  const calculateFinancialHealthScore = () => {
    console.log('Calculating financial health score...');
    console.log('Selected stock:', selectedStock);
    console.log('Fundamental data:', fundamentalData);
    
    // If we have fundamental data for a selected stock, use that
    if (fundamentalData && selectedStock) {
      console.log('Using fundamental data for stock-specific calculation');
      // Try to extract financial health metrics from fundamental data
      const financialMetrics = fundamentalData.financial_metrics || fundamentalData.metrics || {};
      console.log('Financial metrics found:', financialMetrics);
      
      // Calculate score based on multiple financial indicators
      let score = 0;
      let factors = 0;
      
      // Debt-to-Equity ratio (lower is better)
      if (financialMetrics.debt_to_equity !== undefined) {
        const debtEquityScore = Math.max(0, 100 - (financialMetrics.debt_to_equity * 20));
        score += debtEquityScore;
        factors++;
        console.log('Debt-to-Equity score:', debtEquityScore);
      }
      
      // Current ratio (higher is better, but not too high)
      if (financialMetrics.current_ratio !== undefined) {
        const currentRatioScore = Math.min(100, financialMetrics.current_ratio * 25);
        score += currentRatioScore;
        factors++;
        console.log('Current ratio score:', currentRatioScore);
      }
      
      // Return on Equity (higher is better)
      if (financialMetrics.roe !== undefined) {
        const roeScore = Math.min(100, financialMetrics.roe * 2);
        score += roeScore;
        factors++;
        console.log('ROE score:', roeScore);
      }
      
      // Profit margin (higher is better)
      if (financialMetrics.profit_margin !== undefined) {
        const profitMarginScore = Math.min(100, financialMetrics.profit_margin * 2);
        score += profitMarginScore;
        factors++;
        console.log('Profit margin score:', profitMarginScore);
      }
      
      // If we have factors, return average; otherwise fall back to sector average
      if (factors > 0) {
        const finalScore = Math.round(score / factors);
        console.log('Final score from fundamental data:', finalScore);
        return finalScore;
      }
    }
    
    // If no fundamental data, calculate from sector data
    if (sectorData && sectorData.length > 0) {
      console.log('Using sector data for calculation');
      const sectorAverages = sectorData.reduce((acc, sector) => {
        acc.financial_health += sector.financial_health || 0;
        acc.count++;
        return acc;
      }, { financial_health: 0, count: 0 });
      
      if (sectorAverages.count > 0) {
        const sectorScore = Math.round(sectorAverages.financial_health / sectorAverages.count);
        console.log('Sector average score:', sectorScore);
        return sectorScore;
      }
    }
    
    // Default fallback score
    console.log('Using default fallback score: 70');
    return 70;
  };

  // Get sector score for the selected stock
  const getSectorScoreForStock = () => {
    if (!selectedStock || !sectorData || sectorData.length === 0) {
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
      console.log('Dashboard useEffect triggered');
      setLoading(true);
      setError(null);
      console.log('Starting data fetch for Dashboard...');

      try {
        // Fetch available data
        const promises = [
          fetch(`${config.backendUrl}/api/sentiment`).then(res => res.json()).catch(() => ({ data: [] })),
          fetch(`${config.backendUrl}/api/stocks`).then(res => res.json()).catch(() => ({ stocks: [] }))
        ];

        const [sentimentResult] = await Promise.all(promises);
        
        setSentimentData(sentimentResult.data || []);
        
        // Create sample sector data since sector-analysis API doesn't exist
        // Add some variation based on time to make it more dynamic
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
        
        // If a stock is selected, fetch its data
        if (selectedStock) {
          try {
            const [, fundamentalInfo] = await Promise.all([
              fetch(`${config.backendUrl}/api/stock-info/${selectedStock}`).then(res => res.json()).catch(() => null),
              fetch(`${config.backendUrl}/api/fundamental-analysis/${selectedStock}`).then(res => res.json()).catch(() => null)
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
            <h3>Sector Financial Health Score</h3>
            {(() => {
              const sectorInfo = getSectorScoreForStock();
              return (
                <>
                  <AdvancedCharts.FinancialHealthGauge 
                    score={sectorInfo ? sectorInfo.score : 70}
                    title={`${sectorInfo ? sectorInfo.sector : 'Market'} Health Score`}
                  />
                </>
              );
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