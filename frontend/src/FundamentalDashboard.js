import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
  ResponsiveContainer, ComposedChart
} from 'recharts';
import './FundamentalDashboard.css';

// Color palette for different metrics
const COLORS = {
  profitability: '#4F46E5',
  valuation: '#10B981',
  growth: '#F59E0B',
  liquidity: '#06B6D4',
  leverage: '#EF4444',
  excellent: '#10B981',
  good: '#84CC16',
  average: '#F59E0B',
  poor: '#EF4444',
  danger: '#DC2626'
};

const FundamentalDashboard = ({ selectedStock }) => {
  const [fundamentalData, setFundamentalData] = useState(null);
  const [sectorData, setSectorData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');

  // Debug log to check if selectedStock is being passed correctly
  console.log('FundamentalDashboard rendered with selectedStock:', selectedStock);

  useEffect(() => {
    const fetchFundamentalData = async () => {
      if (!selectedStock) return;
      
      console.log('Fetching fundamental data for:', selectedStock);
      setLoading(true);
      try {
        const response = await fetch(`http://localhost:5000/api/fundamental-analysis/${selectedStock}`);
        if (!response.ok) throw new Error('Failed to fetch fundamental data');
        
        const data = await response.json();
        console.log('Fundamental data received:', data);
        setFundamentalData(data);
        
        // Fetch sector data for comparison
        if (data.company_info?.sector) {
          const sectorResponse = await fetch(`http://localhost:5000/api/sector-analysis/${data.company_info.sector}`);
          if (sectorResponse.ok) {
            const sectorData = await sectorResponse.json();
            setSectorData(sectorData);
          }
        }
      } catch (err) {
        console.error('Error fetching fundamental data:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchFundamentalData();
  }, [selectedStock]);

  if (!selectedStock) {
    return (
      <div className="fundamental-dashboard">
        <div className="dashboard-header">
          <h2 style={{ 
            color: '#ffffff', 
            fontSize: '3rem', 
            fontWeight: '800',
            textAlign: 'center',
            marginBottom: '30px',
            padding: '20px 0',
            borderBottom: '3px solid #fbbf24',
            background: 'linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
            textShadow: '2px 2px 4px rgba(0, 0, 0, 0.3)',
            letterSpacing: '-0.025em',
            lineHeight: '1.2'
          }}>
            Fundamental Analysis
          </h2>
        </div>
        <div className="no-selection">
          <h3>Select a stock to view fundamental analysis</h3>
          <p>Choose a stock from the dropdown above to see detailed financial metrics and visualizations.</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="fundamental-dashboard">
        <div className="dashboard-header">
          <h2 style={{ 
            color: '#ffffff', 
            fontSize: '3rem', 
            fontWeight: '800',
            textAlign: 'center',
            marginBottom: '30px',
            padding: '20px 0',
            borderBottom: '3px solid #fbbf24',
            background: 'linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
            textShadow: '2px 2px 4px rgba(0, 0, 0, 0.3)',
            letterSpacing: '-0.025em',
            lineHeight: '1.2'
          }}>
            Fundamental Analysis - {selectedStock}
          </h2>
        </div>
        <div className="loading-container">
          <motion.div 
            className="loading-spinner"
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          />
          <p>Loading fundamental analysis...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="fundamental-dashboard">
        <div className="dashboard-header">
          <h2 style={{ 
            color: '#ffffff', 
            fontSize: '3rem', 
            fontWeight: '800',
            textAlign: 'center',
            marginBottom: '30px',
            padding: '20px 0',
            borderBottom: '3px solid #fbbf24',
            background: 'linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
            textShadow: '2px 2px 4px rgba(0, 0, 0, 0.3)',
            letterSpacing: '-0.025em',
            lineHeight: '1.2'
          }}>
            Fundamental Analysis - {selectedStock}
          </h2>
        </div>
        <div className="error-container">
          <h3>Error loading fundamental data</h3>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  return (
    <motion.div 
      className="fundamental-dashboard"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="dashboard-header">
        <h2 style={{ 
          color: '#ffffff', 
          fontSize: '3rem', 
          fontWeight: '800',
          textAlign: 'center',
          marginBottom: '30px',
          padding: '20px 0',
          borderBottom: '3px solid #fbbf24',
          background: 'linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text',
          textShadow: '2px 2px 4px rgba(0, 0, 0, 0.3)',
          letterSpacing: '-0.025em',
          lineHeight: '1.2'
        }}>
          Fundamental Analysis - {selectedStock}
        </h2>
        <div className="tab-navigation">
          {['overview', 'profitability', 'valuation', 'growth', 'liquidity', 'leverage'].map(tab => (
            <button
              key={tab}
              className={`tab-btn ${activeTab === tab ? 'active' : ''}`}
              onClick={() => setActiveTab(tab)}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>
      </div>

      <AnimatePresence mode="wait">
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          transition={{ duration: 0.3 }}
          className="tab-content"
        >
          {activeTab === 'overview' && <OverviewTab data={fundamentalData} sectorData={sectorData} />}
          {activeTab === 'profitability' && <ProfitabilityTab data={fundamentalData} sectorData={sectorData} />}
          {activeTab === 'valuation' && <ValuationTab data={fundamentalData} sectorData={sectorData} />}
          {activeTab === 'growth' && <GrowthTab data={fundamentalData} sectorData={sectorData} />}
          {activeTab === 'liquidity' && <LiquidityTab data={fundamentalData} sectorData={sectorData} />}
          {activeTab === 'leverage' && <LeverageTab data={fundamentalData} sectorData={sectorData} />}
        </motion.div>
      </AnimatePresence>
    </motion.div>
  );
};

// Overview Tab Component
const OverviewTab = ({ data, sectorData }) => {
  if (!data) return null;

  // Helper function to safely get numeric values and handle NaN
  const safeValue = (value) => {
    if (value === null || value === undefined || isNaN(value) || !isFinite(value)) {
      return 0;
    }
    return Number(value);
  };

  // Extract data from the new API structure
  const profitability = data.profitability || {};
  const valuation = data.valuation || {};
  const growth = data.growth || {};
  const liquidity = data.liquidity || {};

  const keyMetrics = [
    { 
      name: 'ROE', 
      value: safeValue(profitability.roe_percent), 
      unit: '%', 
      color: COLORS.profitability,
      description: 'Return on Equity'
    },
    { 
      name: 'P/E Ratio', 
      value: safeValue(valuation.pe_ratio), 
      unit: 'x', 
      color: COLORS.valuation,
      description: 'Price to Earnings Ratio'
    },
    { 
      name: 'Revenue Growth', 
      value: safeValue(growth.revenue_growth_percent), 
      unit: '%', 
      color: COLORS.growth,
      description: 'Annual Revenue Growth'
    },
    { 
      name: 'Current Ratio', 
      value: safeValue(liquidity.current_ratio), 
      unit: 'x', 
      color: COLORS.liquidity,
      description: 'Current Assets / Current Liabilities'
    },
    { 
      name: 'Net Margin', 
      value: safeValue(profitability.net_margin_percent), 
      unit: '%', 
      color: COLORS.profitability,
      description: 'Net Profit Margin'
    },
    { 
      name: 'Operating Margin', 
      value: safeValue(profitability.operating_margin_percent), 
      unit: '%', 
      color: COLORS.profitability,
      description: 'Operating Profit Margin'
    }
  ];

  const radarData = keyMetrics.map(metric => ({
    metric: metric.name,
    value: Math.min(Math.abs(safeValue(metric.value)), 100), // Normalize for radar chart and handle NaN
    fullMark: 100
  }));

  return (
    <div className="overview-tab">
      <div className="company-info-section">
        <h3>{data.company_info?.company_name || 'Company Information'}</h3>
        <p className="sector-info">Sector: {data.company_info?.sector || 'Unknown'}</p>
      </div>

      <div className="metrics-grid">
        {keyMetrics.map((metric, index) => (
          <motion.div
            key={metric.name}
            className="metric-card"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
            style={{ borderColor: metric.color }}
          >
            <div className="metric-header">
              <h4>{metric.name}</h4>
              <div className="metric-value" style={{ color: metric.color }}>
                {metric.value.toFixed(2)}{metric.unit}
              </div>
            </div>
            <div className="metric-description">
              {metric.description}
            </div>
            <div className="metric-bar">
              <motion.div
                className="metric-fill"
                style={{ backgroundColor: metric.color }}
                initial={{ width: 0 }}
                animate={{ width: `${Math.min(Math.abs(metric.value) / 5, 100)}%` }}
                transition={{ duration: 1, delay: index * 0.1 }}
              />
            </div>
          </motion.div>
        ))}
      </div>

      <div className="charts-row">
        <div className="chart-container">
          <h4>Key Metrics Overview</h4>
          <ResponsiveContainer width="100%" height={300}>
            <RadarChart data={radarData}>
              <PolarGrid />
              <PolarAngleAxis dataKey="metric" />
              <PolarRadiusAxis angle={90} domain={[0, 100]} />
              <Radar
                name="Metrics"
                dataKey="value"
                stroke={COLORS.profitability}
                fill={COLORS.profitability}
                fillOpacity={0.3}
              />
            </RadarChart>
          </ResponsiveContainer>
        </div>

        <div className="summary-section">
          <h4>Financial Summary</h4>
          <div className="summary-grid">
            <div className="summary-item">
              <span className="summary-label">Total Revenue:</span>
              <span className="summary-value">
                ₹{(profitability.revenue / 1000000000).toFixed(2)}B
              </span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Net Income:</span>
              <span className="summary-value">
                ₹{(profitability.net_income / 1000000000).toFixed(2)}B
              </span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Total Assets:</span>
              <span className="summary-value">
                ₹{(profitability.total_assets / 1000000000).toFixed(2)}B
              </span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Shareholders Equity:</span>
              <span className="summary-value">
                ₹{(profitability.shareholders_equity / 1000000000).toFixed(2)}B
              </span>
            </div>
          </div>
        </div>
      </div>

      {sectorData && (
        <div className="sector-comparison">
          <h4>Sector Comparison</h4>
          <div className="sector-metrics">
            <div className="sector-metric">
              <span>Avg P/E: {sectorData.avg_pe}</span>
            </div>
            <div className="sector-metric">
              <span>Avg ROE: {sectorData.avg_roe}%</span>
            </div>
            <div className="sector-metric">
              <span>Avg Debt/Equity: {sectorData.avg_debt_equity}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Profitability Tab Component
const ProfitabilityTab = ({ data, sectorData }) => {
  if (!data || !data.profitability) {
    return (
      <div className="profitability-tab">
        <div className="no-data">
          <h3>No profitability data available</h3>
          <p>Please select a different stock or check back later.</p>
        </div>
      </div>
    );
  }

  const profitability = data.profitability;
  
  // Helper function to safely get numeric values
  const safeValue = (value) => {
    if (value === null || value === undefined || isNaN(value) || !isFinite(value)) {
      return 0;
    }
    return Number(value);
  };

  // Create margins data from real data
  const margins = [
    { name: 'Gross Margin', value: safeValue(profitability.gross_margin_percent) },
    { name: 'Operating Margin', value: safeValue(profitability.operating_margin_percent) },
    { name: 'Net Margin', value: safeValue(profitability.net_margin_percent) },
    { name: 'EBITDA Margin', value: safeValue(profitability.ebitda_margin_percent) }
  ];

  // Create key metrics for comparison
  const keyMetrics = [
    { name: 'ROE', value: safeValue(profitability.roe_percent), unit: '%' },
    { name: 'ROA', value: safeValue(profitability.roa_percent), unit: '%' },
    { name: 'Net Margin', value: safeValue(profitability.net_margin_percent), unit: '%' }
  ];

  return (
    <div className="profitability-tab">
      <div className="metrics-overview">
        <h3>Profitability Overview</h3>
        <div className="metrics-grid">
          {keyMetrics.map((metric, index) => (
            <motion.div
              key={metric.name}
              className="metric-card"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
              style={{ borderColor: COLORS.profitability }}
            >
              <div className="metric-header">
                <h4>{metric.name}</h4>
                <div className="metric-value" style={{ color: COLORS.profitability }}>
                  {metric.value.toFixed(2)}{metric.unit}
                </div>
              </div>
              <div className="metric-bar">
                <motion.div
                  className="metric-fill"
                  style={{ backgroundColor: COLORS.profitability }}
                  initial={{ width: 0 }}
                  animate={{ width: `${Math.min(Math.abs(metric.value) / 2, 100)}%` }}
                  transition={{ duration: 1, delay: index * 0.1 }}
                />
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      <div className="charts-grid">
        <div className="chart-container">
          <h3>Profit Margins Breakdown</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={margins}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip formatter={(value) => `${value}%`} />
              <Bar dataKey="value" fill={COLORS.profitability} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-container">
          <h3>Financial Performance</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={[
                  { name: 'Net Income', value: safeValue(profitability.net_income) / 1000000000, color: COLORS.profitability },
                  { name: 'Total Revenue', value: safeValue(profitability.revenue) / 1000000000, color: COLORS.growth }
                ]}
                cx="50%"
                cy="50%"
                outerRadius={80}
                dataKey="value"
                label={({ name, value }) => `${name}: ₹${value.toFixed(2)}B`}
              >
                {[
                  { color: COLORS.profitability },
                  { color: COLORS.growth }
                ].map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => `₹${value.toFixed(2)}B`} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-container">
          <h3>Efficiency Metrics</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={[
              { metric: 'ROE', value: safeValue(profitability.roe_percent) },
              { metric: 'ROA', value: safeValue(profitability.roa_percent) },
              { metric: 'Asset Turnover', value: safeValue(profitability.revenue) / safeValue(profitability.total_assets) }
            ]}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="metric" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill={COLORS.liquidity} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-container">
          <h3>Financial Summary</h3>
          <div className="financial-summary">
            <div className="summary-item">
              <span className="summary-label">Total Revenue:</span>
              <span className="summary-value">
                ₹{(safeValue(profitability.revenue) / 1000000000).toFixed(2)}B
              </span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Net Income:</span>
              <span className="summary-value">
                ₹{(safeValue(profitability.net_income) / 1000000000).toFixed(2)}B
              </span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Total Assets:</span>
              <span className="summary-value">
                ₹{(safeValue(profitability.total_assets) / 1000000000).toFixed(2)}B
              </span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Shareholders Equity:</span>
              <span className="summary-value">
                ₹{(safeValue(profitability.shareholders_equity) / 1000000000).toFixed(2)}B
              </span>
            </div>
          </div>
        </div>
      </div>

      {sectorData && (
        <div className="sector-comparison">
          <h3>Sector Comparison</h3>
          <div className="sector-metrics">
            <div className="sector-metric">
              <span>Company ROE: {safeValue(profitability.roe_percent).toFixed(2)}%</span>
              <span>Sector Avg: {sectorData.avg_roe}%</span>
            </div>
            <div className="sector-metric">
              <span>Company Net Margin: {safeValue(profitability.net_margin_percent).toFixed(2)}%</span>
              <span>Sector Avg: {sectorData.avg_net_margin || 'N/A'}%</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Valuation Tab Component
const ValuationTab = ({ data, sectorData }) => {
  if (!data || !data.valuation) {
    return (
      <div className="valuation-tab">
        <div className="no-data">
          <h3>No valuation data available</h3>
          <p>Please select a different stock or check back later.</p>
        </div>
      </div>
    );
  }

  const valuation = data.valuation;
  
  // Helper function to safely get numeric values
  const safeValue = (value) => {
    if (value === null || value === undefined || isNaN(value) || !isFinite(value)) {
      return 0;
    }
    return Number(value);
  };

  // Create valuation metrics from real data
  const valuationMetrics = [
    { name: 'P/E Ratio', value: safeValue(valuation.pe_ratio), unit: 'x' },
    { name: 'P/B Ratio', value: safeValue(valuation.pb_ratio), unit: 'x' },
    { name: 'P/S Ratio', value: safeValue(valuation.ps_ratio), unit: 'x' },
    { name: 'EV/EBITDA', value: safeValue(valuation.ev_ebitda), unit: 'x' }
  ];

  // Create key metrics for comparison
  const keyMetrics = [
    { name: 'P/E Ratio', value: safeValue(valuation.pe_ratio), unit: 'x' },
    { name: 'P/B Ratio', value: safeValue(valuation.pb_ratio), unit: 'x' },
    { name: 'P/S Ratio', value: safeValue(valuation.ps_ratio), unit: 'x' },
    { name: 'EV/EBITDA', value: safeValue(valuation.ev_ebitda), unit: 'x' }
  ];

  return (
    <div className="valuation-tab">
      <div className="metrics-overview">
        <h3>Valuation Overview</h3>
        <div className="metrics-grid">
          {keyMetrics.map((metric, index) => (
            <motion.div
              key={metric.name}
              className="metric-card"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
              style={{ borderColor: COLORS.valuation }}
            >
              <div className="metric-header">
                <h4>{metric.name}</h4>
                <div className="metric-value" style={{ color: COLORS.valuation }}>
                  {metric.value.toFixed(2)}{metric.unit}
                </div>
              </div>
              <div className="metric-bar">
                <motion.div
                  className="metric-fill"
                  style={{ backgroundColor: COLORS.valuation }}
                  initial={{ width: 0 }}
                  animate={{ width: `${Math.min(Math.abs(metric.value) / 10, 100)}%` }}
                  transition={{ duration: 1, delay: index * 0.1 }}
                />
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      <div className="charts-grid">
        <div className="chart-container">
          <h3>Valuation Ratios</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={valuationMetrics}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip formatter={(value) => `${value.toFixed(2)}x`} />
              <Bar dataKey="value" fill={COLORS.valuation} />
            </BarChart>
          </ResponsiveContainer>
        </div>
        
        <div className="chart-container">
          <h3>Price Analysis</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={[
                  { name: 'Current Price', value: safeValue(valuation.current_price), color: COLORS.valuation },
                  { name: 'Book Value', value: safeValue(valuation.book_value_per_share), color: COLORS.growth },
                  { name: 'EPS', value: safeValue(valuation.eps), color: COLORS.profitability }
                ]}
                cx="50%"
                cy="50%"
                outerRadius={80}
                dataKey="value"
                label={({ name, value }) => `${name}: ₹${value.toFixed(2)}`}
              >
                {[
                  { color: COLORS.valuation },
                  { color: COLORS.growth },
                  { color: COLORS.profitability }
                ].map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => `₹${value.toFixed(2)}`} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-container">
          <h3>Enterprise Value Analysis</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={[
              { metric: 'Enterprise Value', value: safeValue(valuation.enterprise_value) / 1000000000 },
              { metric: 'Market Cap', value: safeValue(valuation.market_cap) / 1000000000 },
              { metric: 'EV/Revenue', value: safeValue(valuation.ev_revenue) }
            ]}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="metric" />
              <YAxis />
              <Tooltip formatter={(value, name) => name === 'EV/Revenue' ? `${value.toFixed(2)}x` : `₹${value.toFixed(2)}B`} />
              <Bar dataKey="value" fill={COLORS.liquidity} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-container">
          <h3>Valuation Summary</h3>
          <div className="financial-summary">
            <div className="summary-item">
              <span className="summary-label">Current Price:</span>
              <span className="summary-value">
                ₹{safeValue(valuation.current_price).toFixed(2)}
              </span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Book Value per Share:</span>
              <span className="summary-value">
                ₹{safeValue(valuation.book_value_per_share).toFixed(2)}
              </span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Earnings per Share:</span>
              <span className="summary-value">
                ₹{safeValue(valuation.eps).toFixed(2)}
              </span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Enterprise Value:</span>
              <span className="summary-value">
                ₹{(safeValue(valuation.enterprise_value) / 1000000000).toFixed(2)}B
              </span>
            </div>
          </div>
        </div>
      </div>

      {sectorData && (
        <div className="sector-comparison">
          <h3>Sector Comparison</h3>
          <div className="sector-metrics">
            <div className="sector-metric">
              <span>Company P/E: {safeValue(valuation.pe_ratio).toFixed(2)}x</span>
              <span>Sector Avg: {sectorData.avg_pe}x</span>
            </div>
            <div className="sector-metric">
              <span>Company P/B: {safeValue(valuation.pb_ratio).toFixed(2)}x</span>
              <span>Sector Avg: {sectorData.avg_pb}x</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Growth Tab Component
const GrowthTab = ({ data, sectorData }) => {
  if (!data || !data.growth) {
    return (
      <div className="growth-tab">
        <div className="no-data">
          <h3>No growth data available</h3>
          <p>Please select a different stock or check back later.</p>
        </div>
      </div>
    );
  }

  const growth = data.growth;
  
  // Helper function to safely get numeric values
  const safeValue = (value) => {
    if (value === null || value === undefined || isNaN(value) || !isFinite(value)) {
      return 0;
    }
    return Number(value);
  };

  // Helper function to calculate growth quality score
  const calculateGrowthQuality = (growthRate, volatility) => {
    if (growthRate <= 0) return 0;
    
    // Base score from growth rate (0-60 points)
    let baseScore = Math.min(growthRate * 3, 60);
    
    // Volatility penalty (0-40 points deduction)
    let volatilityPenalty = Math.min(volatility * 2, 40);
    
    // Calculate final score
    let finalScore = Math.max(baseScore - volatilityPenalty, 0);
    
    return Math.min(finalScore, 100);
  };

  // Create growth metrics from real data
  const growthMetrics = [
    { name: 'Revenue Growth', value: safeValue(growth.revenue_growth_percent), unit: '%' },
    { name: 'Earnings Growth', value: safeValue(growth.earnings_growth_percent), unit: '%' },
    { name: 'Asset Growth', value: safeValue(growth.asset_growth_percent), unit: '%' },
    { name: 'Equity Growth', value: safeValue(growth.equity_growth_percent), unit: '%' }
  ];

  // Create key metrics for comparison
  const keyMetrics = [
    { name: 'Revenue Growth', value: safeValue(growth.revenue_growth_percent), unit: '%' },
    { name: 'Earnings Growth', value: safeValue(growth.earnings_growth_percent), unit: '%' },
    { name: 'Asset Growth', value: safeValue(growth.asset_growth_percent), unit: '%' }
  ];

  // Create growth trends data (simplified for now)
  const growthTrends = [
    { year: '2021', revenue_growth: safeValue(growth.revenue_growth_percent) * 0.8, earnings_growth: safeValue(growth.earnings_growth_percent) * 0.8 },
    { year: '2022', revenue_growth: safeValue(growth.revenue_growth_percent) * 0.9, earnings_growth: safeValue(growth.earnings_growth_percent) * 0.9 },
    { year: '2023', revenue_growth: safeValue(growth.revenue_growth_percent), earnings_growth: safeValue(growth.earnings_growth_percent) }
  ];

  return (
    <div className="growth-tab">
      <div className="metrics-overview">
        <h3>Growth Overview</h3>
        <div className="metrics-grid">
          {keyMetrics.map((metric, index) => (
            <motion.div
              key={metric.name}
              className="metric-card"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
              style={{ borderColor: COLORS.growth }}
            >
              <div className="metric-header">
                <h4>{metric.name}</h4>
                <div className="metric-value" style={{ color: COLORS.growth }}>
                  {metric.value.toFixed(2)}{metric.unit}
                </div>
              </div>
              <div className="metric-bar">
                <motion.div
                  className="metric-fill"
                  style={{ backgroundColor: COLORS.growth }}
                  initial={{ width: 0 }}
                  animate={{ width: `${Math.min(Math.abs(metric.value) / 2, 100)}%` }}
                  transition={{ duration: 1, delay: index * 0.1 }}
                />
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      <div className="charts-grid">
        <div className="chart-container">
          <h3>Revenue & Earnings Growth</h3>
          <ResponsiveContainer width="100%" height={300}>
            <ComposedChart data={growthTrends}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="year" />
              <YAxis />
              <Tooltip formatter={(value) => `${value.toFixed(2)}%`} />
              <Legend />
              <Bar dataKey="revenue_growth" fill={COLORS.growth} name="Revenue Growth %" />
              <Line type="monotone" dataKey="earnings_growth" stroke={COLORS.profitability} strokeWidth={3} name="Earnings Growth %" />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
        
        <div className="chart-container">
          <h3>Growth Metrics</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={growthMetrics}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip formatter={(value) => `${value.toFixed(2)}%`} />
              <Bar dataKey="value" fill={COLORS.growth} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-container">
          <h3>Growth Quality Analysis</h3>
          <ResponsiveContainer width="100%" height={300}>
            <RadarChart data={[
              { 
                metric: 'Revenue Quality', 
                value: calculateGrowthQuality(safeValue(growth.revenue_growth_percent), safeValue(growth.revenue_volatility)), 
                fullMark: 100 
              },
              { 
                metric: 'Earnings Quality', 
                value: calculateGrowthQuality(safeValue(growth.earnings_growth_percent), 5), // Using default volatility
                fullMark: 100 
              },
              { 
                metric: 'Asset Growth', 
                value: calculateGrowthQuality(safeValue(growth.asset_growth_percent), 8), // Using default volatility
                fullMark: 100 
              },
              { 
                metric: 'Equity Growth', 
                value: calculateGrowthQuality(safeValue(growth.equity_growth_percent), 6), // Using default volatility
                fullMark: 100 
              }
            ]}>
              <PolarGrid />
              <PolarAngleAxis dataKey="metric" />
              <PolarRadiusAxis domain={[0, 100]} />
              <Radar dataKey="value" stroke={COLORS.growth} fill={COLORS.growth} fillOpacity={0.3} />
            </RadarChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-container">
          <h3>Growth Summary</h3>
          <div className="financial-summary">
            <div className="summary-item">
              <span className="summary-label">Revenue Growth:</span>
              <span className="summary-value">
                {safeValue(growth.revenue_growth_percent).toFixed(2)}%
              </span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Earnings Growth:</span>
              <span className="summary-value">
                {safeValue(growth.earnings_growth_percent).toFixed(2)}%
              </span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Asset Growth:</span>
              <span className="summary-value">
                {safeValue(growth.asset_growth_percent).toFixed(2)}%
              </span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Equity Growth:</span>
              <span className="summary-value">
                {safeValue(growth.equity_growth_percent).toFixed(2)}%
              </span>
            </div>
          </div>
        </div>
      </div>

      {sectorData && (
        <div className="sector-comparison">
          <h3>Sector Comparison</h3>
          <div className="sector-metrics">
            <div className="sector-metric">
              <span>Company Revenue Growth: {safeValue(growth.revenue_growth_percent).toFixed(2)}%</span>
              <span>Sector Avg: {sectorData.sector_growth}%</span>
            </div>
            <div className="sector-metric">
              <span>Company Earnings Growth: {safeValue(growth.earnings_growth_percent).toFixed(2)}%</span>
              <span>Sector Avg: {sectorData.avg_earnings_growth || 'N/A'}%</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Liquidity Tab Component
const LiquidityTab = ({ data, sectorData }) => {
  if (!data || !data.liquidity) {
    return (
      <div className="liquidity-tab">
        <div className="no-data">
          <h3>No liquidity data available</h3>
          <p>Please select a different stock or check back later.</p>
        </div>
      </div>
    );
  }

  const liquidity = data.liquidity;
  
  // Helper function to safely get numeric values
  const safeValue = (value) => {
    if (value === null || value === undefined || isNaN(value) || !isFinite(value)) {
      return 0;
    }
    return Number(value);
  };

  // Create liquidity metrics from real data
  const liquidityRatios = [
    { name: 'Current Ratio', value: safeValue(liquidity.current_ratio), benchmark: 2.0 },
    { name: 'Quick Ratio', value: safeValue(liquidity.quick_ratio), benchmark: 1.0 },
    { name: 'Cash Ratio', value: safeValue(liquidity.cash_ratio), benchmark: 0.5 },
    { name: 'Working Capital', value: safeValue(liquidity.working_capital) / 1000000000, benchmark: 0, unit: 'B' }
  ];

  // Create key metrics for comparison
  const keyMetrics = [
    { name: 'Current Ratio', value: safeValue(liquidity.current_ratio), unit: 'x' },
    { name: 'Quick Ratio', value: safeValue(liquidity.quick_ratio), unit: 'x' },
    { name: 'Cash Ratio', value: safeValue(liquidity.cash_ratio), unit: 'x' }
  ];

  return (
    <div className="liquidity-tab">
      <div className="metrics-overview">
        <h3>Liquidity Overview</h3>
        <div className="metrics-grid">
          {keyMetrics.map((metric, index) => (
            <motion.div
              key={metric.name}
              className="metric-card"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
              style={{ borderColor: COLORS.liquidity }}
            >
              <div className="metric-header">
                <h4>{metric.name}</h4>
                <div className="metric-value" style={{ color: COLORS.liquidity }}>
                  {metric.value.toFixed(2)}{metric.unit}
                </div>
              </div>
              <div className="metric-bar">
                <motion.div
                  className="metric-fill"
                  style={{ backgroundColor: COLORS.liquidity }}
                  initial={{ width: 0 }}
                  animate={{ width: `${Math.min(Math.abs(metric.value) / 3, 100)}%` }}
                  transition={{ duration: 1, delay: index * 0.1 }}
                />
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      <div className="charts-grid">
        <div className="chart-container">
          <h3>Liquidity Ratios vs Benchmarks</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={liquidityRatios}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip formatter={(value, name) => name === 'Working Capital' ? `₹${value.toFixed(2)}B` : `${value.toFixed(2)}x`} />
              <Legend />
              <Bar dataKey="value" fill={COLORS.liquidity} name="Current" />
              <Bar dataKey="benchmark" fill={COLORS.average} name="Benchmark" />
            </BarChart>
          </ResponsiveContainer>
        </div>
        
        <div className="chart-container">
          <h3>Working Capital Analysis</h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={[
              { year: '2021', working_capital: safeValue(liquidity.working_capital) * 0.8 / 1000000000 },
              { year: '2022', working_capital: safeValue(liquidity.working_capital) * 0.9 / 1000000000 },
              { year: '2023', working_capital: safeValue(liquidity.working_capital) / 1000000000 }
            ]}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="year" />
              <YAxis />
              <Tooltip formatter={(value) => `₹${value.toFixed(2)}B`} />
              <Area type="monotone" dataKey="working_capital" stroke={COLORS.liquidity} fill={COLORS.liquidity} fillOpacity={0.3} />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-container">
          <h3>Cash Conversion Cycle Analysis</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={[
              { metric: 'Days Sales Outstanding', value: safeValue(liquidity.days_sales_outstanding) },
              { metric: 'Days Inventory Outstanding', value: safeValue(liquidity.days_inventory_outstanding) },
              { metric: 'Days Payable Outstanding', value: safeValue(liquidity.days_payable_outstanding) },
              { metric: 'Cash Conversion Cycle', value: safeValue(liquidity.cash_conversion_cycle) }
            ]}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="metric" />
              <YAxis />
              <Tooltip formatter={(value) => `${value.toFixed(1)} days`} />
              <Bar dataKey="value" fill={COLORS.profitability} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-container">
          <h3>Liquidity Summary</h3>
          <div className="financial-summary">
            <div className="summary-item">
              <span className="summary-label">Current Assets:</span>
              <span className="summary-value">
                ₹{(safeValue(liquidity.current_assets) / 1000000000).toFixed(2)}B
              </span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Current Liabilities:</span>
              <span className="summary-value">
                ₹{(safeValue(liquidity.current_liabilities) / 1000000000).toFixed(2)}B
              </span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Working Capital:</span>
              <span className="summary-value">
                ₹{(safeValue(liquidity.working_capital) / 1000000000).toFixed(2)}B
              </span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Cash & Equivalents:</span>
              <span className="summary-value">
                ₹{(safeValue(liquidity.cash_and_equivalents) / 1000000000).toFixed(2)}B
              </span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Cash Conversion Cycle:</span>
              <span className="summary-value">
                {safeValue(liquidity.cash_conversion_cycle).toFixed(1)} days
              </span>
            </div>
            <div className="summary-item">
              <span className="summary-label">CCC Interpretation:</span>
              <span className="summary-value">
                {liquidity.ccc_interpretation || 'N/A'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {sectorData && (
        <div className="sector-comparison">
          <h3>Sector Comparison</h3>
          <div className="sector-metrics">
            <div className="sector-metric">
              <span>Company Current Ratio: {safeValue(liquidity.current_ratio).toFixed(2)}x</span>
              <span>Sector Avg: {sectorData.avg_current_ratio}x</span>
            </div>
            <div className="sector-metric">
              <span>Company Quick Ratio: {safeValue(liquidity.quick_ratio).toFixed(2)}x</span>
              <span>Sector Avg: {sectorData.avg_quick_ratio || 'N/A'}x</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Leverage Tab Component
const LeverageTab = ({ data, sectorData }) => {
  if (!data) {
    return (
      <div className="leverage-tab">
        <div className="no-data">
          <h3>No leverage data available</h3>
          <p>Please select a different stock or check back later.</p>
        </div>
      </div>
    );
  }

  const profitability = data.profitability || {};
  const liquidity = data.liquidity || {};
  
  // Helper function to safely get numeric values
  const safeValue = (value) => {
    if (value === null || value === undefined || isNaN(value) || !isFinite(value)) {
      return 0;
    }
    return Number(value);
  };

  // Calculate leverage metrics from available data
  const totalAssets = safeValue(profitability.total_assets);
  const totalEquity = safeValue(profitability.shareholders_equity);
  const totalDebt = totalAssets - totalEquity; // Simplified calculation
  const debtEquityRatio = totalEquity > 0 ? totalDebt / totalEquity : 0;
  const debtAssetsRatio = totalAssets > 0 ? totalDebt / totalAssets : 0;
  
  // Create leverage metrics from calculated data
  const leverageMetrics = [
    { name: 'Debt/Equity', value: debtEquityRatio, unit: 'x' },
    { name: 'Debt/Assets', value: debtAssetsRatio, unit: 'x' },
    { name: 'Equity Ratio', value: totalEquity / totalAssets, unit: 'x' },
    { name: 'Asset Turnover', value: safeValue(profitability.revenue) / totalAssets, unit: 'x' }
  ];

  // Create key metrics for comparison
  const keyMetrics = [
    { name: 'Debt/Equity', value: debtEquityRatio, unit: 'x' },
    { name: 'Debt/Assets', value: debtAssetsRatio, unit: 'x' },
    { name: 'Equity Ratio', value: totalEquity / totalAssets, unit: 'x' }
  ];

  return (
    <div className="leverage-tab">
      <div className="metrics-overview">
        <h3>Leverage Overview</h3>
        <div className="metrics-grid">
          {keyMetrics.map((metric, index) => (
            <motion.div
              key={metric.name}
              className="metric-card"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
              style={{ borderColor: COLORS.leverage }}
            >
              <div className="metric-header">
                <h4>{metric.name}</h4>
                <div className="metric-value" style={{ color: COLORS.leverage }}>
                  {metric.value.toFixed(2)}{metric.unit}
                </div>
              </div>
              <div className="metric-bar">
                <motion.div
                  className="metric-fill"
                  style={{ backgroundColor: COLORS.leverage }}
                  initial={{ width: 0 }}
                  animate={{ width: `${Math.min(Math.abs(metric.value) * 20, 100)}%` }}
                  transition={{ duration: 1, delay: index * 0.1 }}
                />
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      <div className="charts-grid">
        <div className="chart-container">
          <h3>Leverage Ratios</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={leverageMetrics}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip formatter={(value) => `${value.toFixed(2)}x`} />
              <Bar dataKey="value" fill={COLORS.leverage} />
            </BarChart>
          </ResponsiveContainer>
        </div>
        
        <div className="chart-container">
          <h3>Capital Structure</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={[
                  { name: 'Total Debt', value: totalDebt / 1000000000, color: COLORS.danger },
                  { name: 'Shareholders Equity', value: totalEquity / 1000000000, color: COLORS.excellent }
                ]}
                cx="50%"
                cy="50%"
                outerRadius={80}
                dataKey="value"
                label={({ name, value }) => `${name}: ₹${value.toFixed(2)}B`}
              >
                {[
                  { color: COLORS.danger },
                  { color: COLORS.excellent }
                ].map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => `₹${value.toFixed(2)}B`} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-container">
          <h3>Financial Efficiency</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={[
              { metric: 'Asset Turnover', value: safeValue(profitability.revenue) / totalAssets },
              { metric: 'ROE', value: safeValue(profitability.roe_percent) / 100 },
              { metric: 'ROA', value: safeValue(profitability.roa_percent) / 100 }
            ]}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="metric" />
              <YAxis />
              <Tooltip formatter={(value) => `${(value * 100).toFixed(2)}%`} />
              <Bar dataKey="value" fill={COLORS.profitability} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-container">
          <h3>Leverage Summary</h3>
          <div className="financial-summary">
            <div className="summary-item">
              <span className="summary-label">Total Assets:</span>
              <span className="summary-value">
                ₹{(totalAssets / 1000000000).toFixed(2)}B
              </span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Total Debt:</span>
              <span className="summary-value">
                ₹{(totalDebt / 1000000000).toFixed(2)}B
              </span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Shareholders Equity:</span>
              <span className="summary-value">
                ₹{(totalEquity / 1000000000).toFixed(2)}B
              </span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Debt/Equity Ratio:</span>
              <span className="summary-value">
                {debtEquityRatio.toFixed(2)}x
              </span>
            </div>
          </div>
        </div>
      </div>

      {sectorData && (
        <div className="sector-comparison">
          <h3>Sector Comparison</h3>
          <div className="sector-metrics">
            <div className="sector-metric">
              <span>Company Debt/Equity: {debtEquityRatio.toFixed(2)}x</span>
              <span>Sector Avg: {sectorData.avg_debt_equity || 'N/A'}x</span>
            </div>
            <div className="sector-metric">
              <span>Company ROE: {safeValue(profitability.roe_percent).toFixed(2)}%</span>
              <span>Sector Avg: {sectorData.avg_roe}%</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FundamentalDashboard; 