import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { 
  sectoralDataService, 
  formatCurrency, 
  formatVolume, 
  getSentimentColor
} from '../../data/sectoral';
import './SectoralAnalysis.css';

const SectoralAnalysis = () => {
  const [sectorData, setSectorData] = useState([]);
  const [selectedSector, setSelectedSector] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timeframe, setTimeframe] = useState('1d');
  const [dataInfo, setDataInfo] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const loadSectorData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Load data from the service
        const data = await sectoralDataService.loadSectoralData(timeframe);
        
        if (data && data.sectors) {
          setSectorData(data.sectors);
          setDataInfo(sectoralDataService.getDataInfo());
        } else {
          throw new Error('Invalid data format received');
        }
        
      } catch (err) {
        setError(err.message);
        console.error('Error loading sector data:', err);
      } finally {
        setLoading(false);
      }
    };

    loadSectorData();
  }, [timeframe]);

  const formatTooltipValue = (value, name) => {
    if (name === 'performance') {
      return [`${value > 0 ? '+' : ''}${(value || 0).toFixed(2)}%`, 'Performance'];
    }
    if (name === 'sentiment') {
      return [(value || 0).toFixed(2), 'Sentiment'];
    }
    if (name === 'volume') {
      return [formatVolume(value || 0), 'Volume'];
    }
    if (name === 'market_cap') {
      return [formatCurrency(value || 0), 'Market Cap'];
    }
    return [value, name];
  };

  const handleTimeframeChange = (newTimeframe) => {
    setTimeframe(newTimeframe);
  };

  const handleRefresh = async () => {
    try {
      setLoading(true);
      const data = await sectoralDataService.updateData();
      if (data && data.sectors) {
        setSectorData(data.sectors);
        setDataInfo(sectoralDataService.getDataInfo());
      }
    } catch (err) {
      console.error('Error refreshing data:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="sectoral-loading">
        <div className="spinner"></div>
        <p>Loading sectoral analysis...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="sectoral-error">
        <h3>Error Loading Data</h3>
        <p>{error}</p>
        <button onClick={handleRefresh}>Try Again</button>
      </div>
    );
  }

  // Safety check for data
  if (!sectorData || !Array.isArray(sectorData) || sectorData.length === 0) {
    return (
      <div className="sectoral-error">
        <h3>No Data Available</h3>
        <p>No sector data is currently available. Please try again later.</p>
        <button onClick={handleRefresh}>Refresh</button>
      </div>
    );
  }

  const performanceData = sectorData.map(sector => ({
    name: sector.name || 'Unknown',
    performance: sector.performance || 0,
    sentiment: sector.sentiment || 0
  }));

  const sentimentData = sectorData.map(sector => ({
    name: sector.name || 'Unknown',
    value: sector.sentiment || 0,
    color: getSentimentColor(sector.sentiment || 0)
  }));

  const marketCapData = sectorData.map(sector => ({
    name: sector.name || 'Unknown',
    market_cap: (sector.market_cap || 0) / 1000000000 // Convert to billions
  }));

  return (
    <div className="sectoral-analysis">
      <div className="sectoral-header">
        <div className="header-top">
          <button 
            className="back-button"
            onClick={() => navigate('/')}
          >
            ← Back to Home
          </button>
          <div className="header-nav">
            <button 
              className="nav-button"
              onClick={() => navigate('/signin')}
            >
              Sign In
            </button>
            <button 
              className="nav-button primary"
              onClick={() => navigate('/signup')}
            >
              Sign Up
            </button>
          </div>
        </div>
        <h1>Sectoral Analysis</h1>
        <p>Comprehensive analysis of market sectors and their performance</p>
        
        <div className="timeframe-selector">
          <button 
            className={`timeframe-btn ${timeframe === '1d' ? 'active' : ''}`}
            onClick={() => handleTimeframeChange('1d')}
          >
            1D
          </button>
          <button 
            className={`timeframe-btn ${timeframe === '1w' ? 'active' : ''}`}
            onClick={() => handleTimeframeChange('1w')}
          >
            1W
          </button>
          <button 
            className={`timeframe-btn ${timeframe === '1m' ? 'active' : ''}`}
            onClick={() => handleTimeframeChange('1m')}
          >
            1M
          </button>
          <button 
            className={`timeframe-btn ${timeframe === '3m' ? 'active' : ''}`}
            onClick={() => handleTimeframeChange('3m')}
          >
            3M
          </button>
        </div>

        {dataInfo && (
          <div className="data-info">
            <span>Last updated: {dataInfo.lastUpdated?.toLocaleString()}</span>
            <span>• {dataInfo.totalSectors} sectors</span>
            <span>• {dataInfo.totalStocks} stocks</span>
            <button className="refresh-btn" onClick={handleRefresh}>
              🔄 Refresh
            </button>
          </div>
        )}
      </div>

      <div className="sectoral-grid">
        {/* Performance Overview */}
        <div className="sector-card performance-overview">
          <h2>Sector Performance</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={performanceData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis 
                dataKey="name" 
                stroke="rgba(255,255,255,0.7)"
                fontSize={12}
                angle={-45}
                textAnchor="end"
                height={80}
              />
              <YAxis stroke="rgba(255,255,255,0.7)" fontSize={12} />
              <Tooltip 
                contentStyle={{
                  backgroundColor: 'rgba(0,0,0,0.9)',
                  border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: '8px',
                  color: '#fff'
                }}
                formatter={formatTooltipValue}
              />
              <Bar 
                dataKey="performance" 
                fill="url(#performanceGradient)"
                radius={[4, 4, 0, 0]}
              />
              <defs>
                <linearGradient id="performanceGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#667eea" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#764ba2" stopOpacity={0.6}/>
                </linearGradient>
              </defs>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Sentiment Distribution */}
        <div className="sector-card sentiment-distribution">
          <h2>Sentiment Distribution</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={sentimentData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {sentimentData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{
                  backgroundColor: 'rgba(0,0,0,0.9)',
                  border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: '8px',
                  color: '#fff'
                }}
                formatter={(value) => [value.toFixed(2), 'Sentiment']}
              />
            </PieChart>
          </ResponsiveContainer>
          
          <div className="sentiment-legend">
            <div className="legend-item">
              <div className="legend-color" style={{ backgroundColor: '#10B981' }}></div>
              <span>Positive (&gt;0.6)</span>
            </div>
            <div className="legend-item">
              <div className="legend-color" style={{ backgroundColor: '#F59E0B' }}></div>
              <span>Neutral (0.4-0.6)</span>
            </div>
            <div className="legend-item">
              <div className="legend-color" style={{ backgroundColor: '#EF4444' }}></div>
              <span>Negative (&lt;0.4)</span>
            </div>
          </div>
        </div>

        {/* Sector Details Table */}
        <div className="sector-card sector-details">
          <h2>Sector Details</h2>
          <div className="sector-table">
            <div className="table-header">
              <span>Sector</span>
              <span>Performance</span>
              <span>Sentiment</span>
              <span>Volume</span>
              <span>Market Cap</span>
            </div>
            {sectorData.map((sector, index) => (
              <div 
                key={index} 
                className={`table-row ${selectedSector === sector.name ? 'selected' : ''}`}
                onClick={() => setSelectedSector(selectedSector === sector.name ? '' : sector.name)}
              >
                <span className="sector-name">{sector.name}</span>
                <span className="performance" style={{ color: (sector.performance || 0) >= 0 ? '#10B981' : '#EF4444' }}>
                  {(sector.performance || 0) > 0 ? '+' : ''}{(sector.performance || 0).toFixed(2)}%
                </span>
                <span className="sentiment">
                  <div 
                    className="sentiment-bar" 
                    style={{ 
                      width: `${(sector.sentiment || 0) * 100}%`,
                      backgroundColor: getSentimentColor(sector.sentiment || 0)
                    }}
                  ></div>
                  {(sector.sentiment || 0).toFixed(2)}
                </span>
                <span className="volume">{formatVolume(sector.volume || 0)}</span>
                <span className="market-cap">{formatCurrency(sector.market_cap || 0)}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Top Stocks */}
        <div className="sector-card top-stocks">
          <h2>Top Stocks by Sector</h2>
          <div className="stocks-grid">
            {sectorData.map((sector, index) => (
              <div key={index} className="stock-sector-group">
                <h3 className="sector-title">{sector.name}</h3>
                <div className="sector-stocks-list">
                  {(sector.top_stocks || []).map((stock, stockIndex) => {
                    // Determine color and arrow for price change
                    const isUp = typeof stock.change === 'number' && stock.change >= 0;
                    const changeColor = isUp ? '#10B981' : '#EF4444';
                    const arrow = isUp ? '▲' : '▼';
                    // Sentiment dot color
                    let sentimentColor = '#F59E0B';
                    const sentiment = typeof stock.sentiment === 'number' ? stock.sentiment : null;
                    if (sentiment !== null && sentiment > 0.6) sentimentColor = '#10B981';
                    else if (sentiment !== null && sentiment < 0.4) sentimentColor = '#EF4444';
                    return (
                      <div key={stockIndex} className="stock-card">
                        <div className="stock-card-header">
                          <span className="stock-symbol">{stock.symbol || 'N/A'}</span>
                          <span className="stock-name">{stock.name || 'Unknown'}</span>
                        </div>
                        <div className="stock-card-body">
                          <span className="stock-price">
                            {typeof stock.price === 'number' ? `₹${stock.price.toLocaleString()}` : 'N/A'}
                          </span>
                          <span className="stock-change" style={{ color: changeColor }}>
                            {typeof stock.change === 'number' ? `${arrow} ${stock.change > 0 ? '+' : ''}${stock.change.toFixed(2)}%` : 'N/A'}
                          </span>
                        </div>
                        <div className="stock-card-footer">
                          <span className="sentiment-dot" style={{ backgroundColor: sentimentColor }}></span>
                          <span className="sentiment-label">
                            Sentiment: {sentiment !== null ? sentiment.toFixed(2) : 'N/A'}
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Market Cap Distribution */}
        <div className="sector-card market-cap-distribution">
          <h2>Market Cap Distribution</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={marketCapData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis 
                dataKey="name" 
                stroke="rgba(255,255,255,0.7)"
                fontSize={12}
                angle={-45}
                textAnchor="end"
                height={80}
              />
              <YAxis stroke="rgba(255,255,255,0.7)" fontSize={12} />
              <Tooltip 
                contentStyle={{
                  backgroundColor: 'rgba(0,0,0,0.9)',
                  border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: '8px',
                  color: '#fff'
                }}
                formatter={(value) => [`₹${value.toFixed(1)}B`, 'Market Cap']}
              />
              <Bar 
                dataKey="market_cap" 
                fill="url(#marketCapGradient)"
                radius={[4, 4, 0, 0]}
              />
              <defs>
                <linearGradient id="marketCapGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10B981" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#059669" stopOpacity={0.6}/>
                </linearGradient>
              </defs>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default SectoralAnalysis; 