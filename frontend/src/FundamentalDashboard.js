import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  BarChart, Bar, Line, PieChart, Pie, Cell,
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
  ResponsiveContainer, ComposedChart
} from 'recharts';
import './FundamentalDashboard.css';
import { StockPriceChart, RevenueExpenseProfitChart } from './StockFinancialChart';
import config from './config/config';

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
  const [aiData, setAiData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    const fetchData = async () => {
      if (!selectedStock) return;
      setLoading(true);
      setError(null);
      try {
        // Fetch both original and AI-powered data in parallel
        const [fundamentalRes, aiRes] = await Promise.all([
          fetch(`${config.backendUrl}/api/fundamental-analysis/${selectedStock}`),
          fetch(`${config.backendUrl}/api/ai-fundamental-analysis/${selectedStock}`)
        ]);
        if (!fundamentalRes.ok) throw new Error('Failed to fetch fundamental analysis');
        if (!aiRes.ok) throw new Error('Failed to fetch AI fundamental analysis');
        const fundamentalJson = await fundamentalRes.json();
        const aiJson = await aiRes.json();
        setFundamentalData(fundamentalJson);
        setAiData(aiJson);
      } catch (err) {
        setError(err.message);
        setFundamentalData(null);
        setAiData(null);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [selectedStock]);

  if (!selectedStock) {
    return <div className="fundamental-dashboard"><h3>Select a stock to view fundamental analysis</h3></div>;
  }
  if (loading) {
    return <div className="fundamental-dashboard"><p>Loading fundamental analysis...</p></div>;
  }
  if (error) {
    return <div className="fundamental-dashboard"><p>Error: {error}</p></div>;
  }
  if (!fundamentalData) {
    return <div className="fundamental-dashboard"><p>No fundamental data available.</p></div>;
  }

  return (
    <motion.div className="fundamental-dashboard">
      <div className="dashboard-header">
        <h2>Fundamental Analysis - {selectedStock}</h2>
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
        <motion.div key={activeTab} className="tab-content">
          {activeTab === 'overview' && <OverviewTab fundamentalData={fundamentalData} aiData={aiData} />}
          {activeTab === 'profitability' && <ProfitabilityTab fundamentalData={fundamentalData} aiData={aiData} />}
          {activeTab === 'valuation' && <ValuationTab fundamentalData={fundamentalData} aiData={aiData} />}
          {activeTab === 'growth' && <GrowthTab fundamentalData={fundamentalData} aiData={aiData} />}
          {activeTab === 'liquidity' && <LiquidityTab fundamentalData={fundamentalData} aiData={aiData} />}
          {activeTab === 'leverage' && <LeverageTab fundamentalData={fundamentalData} aiData={aiData} />}
        </motion.div>
      </AnimatePresence>
    </motion.div>
  );
};

// Overview Tab
const OverviewTab = ({ fundamentalData, aiData }) => {
  const profitability = fundamentalData.profitability || {};
  const valuation = fundamentalData.valuation || {};
  const growth = fundamentalData.growth || {};
  const liquidity = fundamentalData.liquidity || {};

  const keyMetrics = [
    { name: 'ROE', value: profitability.roe_percent, unit: '%', color: '#4F46E5', description: 'Return on Equity' },
    { name: 'P/E Ratio', value: valuation.pe_ratio, unit: 'x', color: '#10B981', description: 'Price to Earnings Ratio' },
    { name: 'Revenue Growth', value: growth.revenue_growth_percent, unit: '%', color: '#F59E0B', description: 'Annual Revenue Growth' },
    { name: 'Current Ratio', value: liquidity.current_ratio, unit: 'x', color: '#06B6D4', description: 'Current Assets / Current Liabilities' },
    { name: 'Net Margin', value: profitability.net_margin_percent, unit: '%', color: '#4F46E5', description: 'Net Profit Margin' },
    { name: 'Operating Margin', value: profitability.operating_margin_percent, unit: '%', color: '#4F46E5', description: 'Operating Profit Margin' }
  ];

  const radarData = keyMetrics.map(metric => ({
    metric: metric.name,
    value: Math.min(Math.abs(Number(metric.value) || 0), 100),
    fullMark: 100
  }));

  return (
    <div className="overview-tab">
      <div className="company-info-section">
        <h3>{fundamentalData.company_info?.company_name || 'Company Information'}</h3>
        <p className="sector-info">Sector: {fundamentalData.company_info?.sector || 'Unknown'}</p>
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
                {Number(metric.value).toFixed(2)}{metric.unit}
              </div>
            </div>
            <div className="metric-description">{metric.description}</div>
            <div className="metric-bar">
              <motion.div
                className="metric-fill"
                style={{ backgroundColor: metric.color }}
                initial={{ width: 0 }}
                animate={{ width: `${Math.min(Math.abs(Number(metric.value) || 0) / 5, 100)}%` }}
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
              <Radar name="Metrics" dataKey="value" stroke="#4F46E5" fill="#4F46E5" fillOpacity={0.3} />
            </RadarChart>
          </ResponsiveContainer>
        </div>
        <div className="summary-section">
          <h4>Financial Summary</h4>
          <div className="summary-grid">
            <div className="summary-item">
              <span className="summary-label">Total Revenue:</span>
              <span className="summary-value">₹{(profitability.revenue / 1000000000).toFixed(2)}B</span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Net Income:</span>
              <span className="summary-value">₹{(profitability.net_income / 1000000000).toFixed(2)}B</span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Total Assets:</span>
              <span className="summary-value">₹{(profitability.total_assets / 1000000000).toFixed(2)}B</span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Shareholders Equity:</span>
              <span className="summary-value">₹{(profitability.shareholders_equity / 1000000000).toFixed(2)}B</span>
            </div>
          </div>
        </div>
      </div>
      <div className="chart-row">
        <StockPriceChart stockSymbol={fundamentalData.company_info?.symbol} />
      </div>
      <div className="chart-row">
        <RevenueExpenseProfitChart stockSymbol={fundamentalData.company_info?.symbol} />
      </div>
      {/* AI-powered add-on */}
      {aiData && (
        <div className="ai-indicator-card">
          <h3>AI-Powered Indicator</h3>
          <div className="ai-indicator-content">
            <p><strong>Composite Score:</strong> {aiData.overview_score || 'N/A'}/100</p>
            <p><strong>Health Grade:</strong> {aiData.overview_grade || 'N/A'}</p>
            <p>{aiData.overview_summary || 'No summary available.'}</p>
          </div>
        </div>
      )}
    </div>
  );
};

// Profitability Tab
const ProfitabilityTab = ({ fundamentalData, aiData }) => {
  const profitability = fundamentalData.profitability || {};
  const growth = fundamentalData.growth || {};
  const liquidity = fundamentalData.liquidity || {};
  const leverage = fundamentalData.leverage || {};

  const keyMetrics = [
    { name: 'ROE', value: profitability.roe_percent, unit: '%', color: '#4F46E5', description: 'Return on Equity' },
    { name: 'Net Margin', value: profitability.net_margin_percent, unit: '%', color: '#4F46E5', description: 'Net Profit Margin' },
    { name: 'Operating Margin', value: profitability.operating_margin_percent, unit: '%', color: '#4F46E5', description: 'Operating Profit Margin' },
    { name: 'Revenue Growth', value: growth.revenue_growth_percent, unit: '%', color: '#F59E0B', description: 'Annual Revenue Growth' },
    { name: 'Earnings Growth', value: growth.earnings_growth_percent, unit: '%', color: '#F59E0B', description: 'Annual Earnings Growth' },
    { name: 'Current Ratio', value: liquidity.current_ratio, unit: 'x', color: '#06B6D4', description: 'Current Assets / Current Liabilities' },
    { name: 'Debt to Equity', value: leverage.debt_to_equity, unit: 'x', color: '#EF4444', description: 'Total Debt / Shareholders Equity' },
    { name: 'Quick Ratio', value: liquidity.quick_ratio, unit: 'x', color: '#06B6D4', description: 'Cash + Marketable Securities / Current Liabilities' }
  ];

  const radarData = keyMetrics.map(metric => ({
    metric: metric.name,
    value: Math.min(Math.abs(Number(metric.value) || 0), 100),
    fullMark: 100
  }));

  return (
    <div className="profitability-tab">
      <h3>Traditional Metrics</h3>
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
                {Number(metric.value).toFixed(2)}{metric.unit}
              </div>
            </div>
            <div className="metric-description">{metric.description}</div>
            <div className="metric-bar">
              <motion.div
                className="metric-fill"
                style={{ backgroundColor: metric.color }}
                initial={{ width: 0 }}
                animate={{ width: `${Math.min(Math.abs(Number(metric.value) || 0) / 5, 100)}%` }}
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
              <Radar name="Metrics" dataKey="value" stroke="#4F46E5" fill="#4F46E5" fillOpacity={0.3} />
            </RadarChart>
          </ResponsiveContainer>
        </div>
        <div className="summary-section">
          <h4>Financial Summary</h4>
          <div className="summary-grid">
            <div className="summary-item">
              <span className="summary-label">Total Revenue:</span>
              <span className="summary-value">₹{(profitability.revenue / 1000000000).toFixed(2)}B</span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Net Income:</span>
              <span className="summary-value">₹{(profitability.net_income / 1000000000).toFixed(2)}B</span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Total Assets:</span>
              <span className="summary-value">₹{(profitability.total_assets / 1000000000).toFixed(2)}B</span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Shareholders Equity:</span>
              <span className="summary-value">₹{(profitability.shareholders_equity / 1000000000).toFixed(2)}B</span>
            </div>
          </div>
        </div>
      </div>
      <div className="chart-row">
        <StockPriceChart stockSymbol={fundamentalData.company_info?.symbol} />
      </div>
      <div className="chart-row">
        <RevenueExpenseProfitChart stockSymbol={fundamentalData.company_info?.symbol} />
      </div>
      {/* AI-powered add-on */}
      {aiData && (
        <div className="ai-indicator-card">
          <h3>AI-Powered Indicator</h3>
          <div className="ai-indicator-content">
            <p><strong>Profitability Score:</strong> {aiData.profitability_score || 'N/A'}/100</p>
            <p>{aiData.profitability_summary || 'No summary available.'}</p>
          </div>
        </div>
      )}
    </div>
  );
};

// Growth Tab
const GrowthTab = ({ fundamentalData, aiData }) => {
  const growth = fundamentalData.growth || {};
  const profitability = fundamentalData.profitability || {};
  const liquidity = fundamentalData.liquidity || {};
  const leverage = fundamentalData.leverage || {};

  const keyMetrics = [
    { name: 'Revenue Growth', value: growth.revenue_growth_percent, unit: '%', color: '#F59E0B', description: 'Annual Revenue Growth' },
    { name: 'Earnings Growth', value: growth.earnings_growth_percent, unit: '%', color: '#F59E0B', description: 'Annual Earnings Growth' },
    { name: 'Operating Margin', value: profitability.operating_margin_percent, unit: '%', color: '#4F46E5', description: 'Operating Profit Margin' },
    { name: 'Net Margin', value: profitability.net_margin_percent, unit: '%', color: '#4F46E5', description: 'Net Profit Margin' },
    { name: 'Current Ratio', value: liquidity.current_ratio, unit: 'x', color: '#06B6D4', description: 'Current Assets / Current Liabilities' },
    { name: 'Debt to Equity', value: leverage.debt_to_equity, unit: 'x', color: '#EF4444', description: 'Total Debt / Shareholders Equity' }
  ];

  const radarData = keyMetrics.map(metric => ({
    metric: metric.name,
    value: Math.min(Math.abs(Number(metric.value) || 0), 100),
    fullMark: 100
  }));

  return (
    <div className="growth-tab">
      <h3>Growth Score: {aiData?.growth_score || 'N/A'}/100</h3>
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
                {Number(metric.value).toFixed(2)}{metric.unit}
              </div>
            </div>
            <div className="metric-description">{metric.description}</div>
            <div className="metric-bar">
              <motion.div
                className="metric-fill"
                style={{ backgroundColor: metric.color }}
                initial={{ width: 0 }}
                animate={{ width: `${Math.min(Math.abs(Number(metric.value) || 0) / 5, 100)}%` }}
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
              <Radar name="Metrics" dataKey="value" stroke="#4F46E5" fill="#4F46E5" fillOpacity={0.3} />
            </RadarChart>
          </ResponsiveContainer>
        </div>
        <div className="summary-section">
          <h4>Financial Summary</h4>
          <div className="summary-grid">
            <div className="summary-item">
              <span className="summary-label">Total Revenue:</span>
              <span className="summary-value">₹{(growth.revenue / 1000000000).toFixed(2)}B</span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Net Income:</span>
              <span className="summary-value">₹{(growth.net_income / 1000000000).toFixed(2)}B</span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Total Assets:</span>
              <span className="summary-value">₹{(growth.total_assets / 1000000000).toFixed(2)}B</span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Shareholders Equity:</span>
              <span className="summary-value">₹{(growth.shareholders_equity / 1000000000).toFixed(2)}B</span>
            </div>
          </div>
        </div>
      </div>
      <div className="chart-row">
        <StockPriceChart stockSymbol={fundamentalData.company_info?.symbol} />
      </div>
      <div className="chart-row">
        <RevenueExpenseProfitChart stockSymbol={fundamentalData.company_info?.symbol} />
      </div>
      {/* AI-powered add-on */}
      {aiData && (
        <div className="ai-indicator-card">
          <h3>AI-Powered Indicator</h3>
          <div className="ai-indicator-content">
            <p><strong>Growth Score:</strong> {aiData.growth_score || 'N/A'}/100</p>
            <p>Revenue Growth: {aiData.growth_revenue_growth || 'N/A'}%</p>
            <p>Earnings Growth: {aiData.growth_earnings_growth || 'N/A'}%</p>
            <p>{aiData.growth_summary || 'No summary available.'}</p>
          </div>
        </div>
      )}
    </div>
  );
};

// Liquidity Tab
const LiquidityTab = ({ fundamentalData, aiData }) => {
  const liquidity = fundamentalData.liquidity || {};
  const profitability = fundamentalData.profitability || {};
  const leverage = fundamentalData.leverage || {};

  const keyMetrics = [
    { name: 'Current Ratio', value: liquidity.current_ratio, unit: 'x', color: '#06B6D4', description: 'Current Assets / Current Liabilities' },
    { name: 'Quick Ratio', value: liquidity.quick_ratio, unit: 'x', color: '#06B6D4', description: 'Cash + Marketable Securities / Current Liabilities' },
    { name: 'Operating Margin', value: profitability.operating_margin_percent, unit: '%', color: '#4F46E5', description: 'Operating Profit Margin' },
    { name: 'Net Margin', value: profitability.net_margin_percent, unit: '%', color: '#4F46E5', description: 'Net Profit Margin' },
    { name: 'Debt to Equity', value: leverage.debt_to_equity, unit: 'x', color: '#EF4444', description: 'Total Debt / Shareholders Equity' }
  ];

  const radarData = keyMetrics.map(metric => ({
    metric: metric.name,
    value: Math.min(Math.abs(Number(metric.value) || 0), 100),
    fullMark: 100
  }));

  return (
    <div className="liquidity-tab">
      <h3>Liquidity Score: {aiData?.liquidity_score || 'N/A'}/100</h3>
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
                {Number(metric.value).toFixed(2)}{metric.unit}
              </div>
            </div>
            <div className="metric-description">{metric.description}</div>
            <div className="metric-bar">
              <motion.div
                className="metric-fill"
                style={{ backgroundColor: metric.color }}
                initial={{ width: 0 }}
                animate={{ width: `${Math.min(Math.abs(Number(metric.value) || 0) / 5, 100)}%` }}
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
              <Radar name="Metrics" dataKey="value" stroke="#4F46E5" fill="#4F46E5" fillOpacity={0.3} />
            </RadarChart>
          </ResponsiveContainer>
        </div>
        <div className="summary-section">
          <h4>Financial Summary</h4>
          <div className="summary-grid">
            <div className="summary-item">
              <span className="summary-label">Total Revenue:</span>
              <span className="summary-value">₹{(liquidity.revenue / 1000000000).toFixed(2)}B</span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Net Income:</span>
              <span className="summary-value">₹{(liquidity.net_income / 1000000000).toFixed(2)}B</span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Total Assets:</span>
              <span className="summary-value">₹{(liquidity.total_assets / 1000000000).toFixed(2)}B</span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Shareholders Equity:</span>
              <span className="summary-value">₹{(liquidity.shareholders_equity / 1000000000).toFixed(2)}B</span>
            </div>
          </div>
        </div>
      </div>
      <div className="chart-row">
        <StockPriceChart stockSymbol={fundamentalData.company_info?.symbol} />
      </div>
      <div className="chart-row">
        <RevenueExpenseProfitChart stockSymbol={fundamentalData.company_info?.symbol} />
      </div>
      {/* AI-powered add-on */}
      {aiData && (
        <div className="ai-indicator-card">
          <h3>AI-Powered Indicator</h3>
          <div className="ai-indicator-content">
            <p><strong>Liquidity Score:</strong> {aiData.liquidity_score || 'N/A'}/100</p>
            <p>Current Ratio: {fundamentalData.liquidity?.current_ratio || 'N/A'}</p>
            <p>{aiData.liquidity_summary || 'No summary available.'}</p>
          </div>
        </div>
      )}
    </div>
  );
};

// Leverage Tab
const LeverageTab = ({ fundamentalData, aiData }) => {
  const leverage = fundamentalData.leverage || {};
  const profitability = fundamentalData.profitability || {};
  const liquidity = fundamentalData.liquidity || {};

  const keyMetrics = [
    { name: 'Debt to Equity', value: leverage.debt_to_equity, unit: 'x', color: '#EF4444', description: 'Total Debt / Shareholders Equity' },
    { name: 'Interest Coverage Ratio', value: leverage.interest_coverage_ratio, unit: 'x', color: '#EF4444', description: 'EBIT / Interest Expense' },
    { name: 'Operating Margin', value: profitability.operating_margin_percent, unit: '%', color: '#4F46E5', description: 'Operating Profit Margin' },
    { name: 'Net Margin', value: profitability.net_margin_percent, unit: '%', color: '#4F46E5', description: 'Net Profit Margin' },
    { name: 'Current Ratio', value: liquidity.current_ratio, unit: 'x', color: '#06B6D4', description: 'Current Assets / Current Liabilities' }
  ];

  const radarData = keyMetrics.map(metric => ({
    metric: metric.name,
    value: Math.min(Math.abs(Number(metric.value) || 0), 100),
    fullMark: 100
  }));

  return (
    <div className="leverage-tab">
      <h3>Leverage Score: {aiData?.leverage_score || 'N/A'}/100</h3>
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
                {Number(metric.value).toFixed(2)}{metric.unit}
              </div>
            </div>
            <div className="metric-description">{metric.description}</div>
            <div className="metric-bar">
              <motion.div
                className="metric-fill"
                style={{ backgroundColor: metric.color }}
                initial={{ width: 0 }}
                animate={{ width: `${Math.min(Math.abs(Number(metric.value) || 0) / 5, 100)}%` }}
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
              <Radar name="Metrics" dataKey="value" stroke="#4F46E5" fill="#4F46E5" fillOpacity={0.3} />
            </RadarChart>
          </ResponsiveContainer>
        </div>
        <div className="summary-section">
          <h4>Financial Summary</h4>
          <div className="summary-grid">
            <div className="summary-item">
              <span className="summary-label">Total Revenue:</span>
              <span className="summary-value">₹{(leverage.revenue / 1000000000).toFixed(2)}B</span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Net Income:</span>
              <span className="summary-value">₹{(leverage.net_income / 1000000000).toFixed(2)}B</span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Total Assets:</span>
              <span className="summary-value">₹{(leverage.total_assets / 1000000000).toFixed(2)}B</span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Shareholders Equity:</span>
              <span className="summary-value">₹{(leverage.shareholders_equity / 1000000000).toFixed(2)}B</span>
            </div>
          </div>
        </div>
      </div>
      <div className="chart-row">
        <StockPriceChart stockSymbol={fundamentalData.company_info?.symbol} />
      </div>
      <div className="chart-row">
        <RevenueExpenseProfitChart stockSymbol={fundamentalData.company_info?.symbol} />
      </div>
      {/* AI-powered add-on */}
      {aiData && (
        <div className="ai-indicator-card">
          <h3>AI-Powered Indicator</h3>
          <div className="ai-indicator-content">
            <p><strong>Leverage Score:</strong> {aiData.leverage_score || 'N/A'}/100</p>
            <p>Debt to Equity: {fundamentalData.leverage?.debt_to_equity || 'N/A'}</p>
            <p>{aiData.leverage_summary || 'No summary available.'}</p>
          </div>
        </div>
      )}
    </div>
  );
};

// Valuation Tab
const ValuationTab = ({ fundamentalData, aiData }) => {
  const valuation = fundamentalData.valuation || {};
  const profitability = fundamentalData.profitability || {};
  const growth = fundamentalData.growth || {};

  const keyMetrics = [
    { name: 'P/E Ratio', value: valuation.pe_ratio, unit: 'x', color: '#10B981', description: 'Price to Earnings Ratio' },
    { name: 'Price to Book Ratio', value: valuation.price_to_book_ratio, unit: 'x', color: '#10B981', description: 'Price to Book Ratio' },
    { name: 'EV/EBITDA', value: valuation.ev_ebitda, unit: 'x', color: '#10B981', description: 'Enterprise Value to EBITDA' },
    { name: 'Operating Margin', value: profitability.operating_margin_percent, unit: '%', color: '#4F46E5', description: 'Operating Profit Margin' },
    { name: 'Net Margin', value: profitability.net_margin_percent, unit: '%', color: '#4F46E5', description: 'Net Profit Margin' },
    { name: 'Revenue Growth', value: growth.revenue_growth_percent, unit: '%', color: '#F59E0B', description: 'Annual Revenue Growth' }
  ];

  const radarData = keyMetrics.map(metric => ({
    metric: metric.name,
    value: Math.min(Math.abs(Number(metric.value) || 0), 100),
    fullMark: 100
  }));

  return (
    <div className="valuation-tab">
      <h3>Valuation Score: {aiData?.valuation_score || 'N/A'}/100</h3>
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
                {Number(metric.value).toFixed(2)}{metric.unit}
              </div>
            </div>
            <div className="metric-description">{metric.description}</div>
            <div className="metric-bar">
              <motion.div
                className="metric-fill"
                style={{ backgroundColor: metric.color }}
                initial={{ width: 0 }}
                animate={{ width: `${Math.min(Math.abs(Number(metric.value) || 0) / 5, 100)}%` }}
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
              <Radar name="Metrics" dataKey="value" stroke="#4F46E5" fill="#4F46E5" fillOpacity={0.3} />
            </RadarChart>
          </ResponsiveContainer>
        </div>
        <div className="summary-section">
          <h4>Financial Summary</h4>
          <div className="summary-grid">
            <div className="summary-item">
              <span className="summary-label">Total Revenue:</span>
              <span className="summary-value">₹{(valuation.revenue / 1000000000).toFixed(2)}B</span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Net Income:</span>
              <span className="summary-value">₹{(valuation.net_income / 1000000000).toFixed(2)}B</span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Total Assets:</span>
              <span className="summary-value">₹{(valuation.total_assets / 1000000000).toFixed(2)}B</span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Shareholders Equity:</span>
              <span className="summary-value">₹{(valuation.shareholders_equity / 1000000000).toFixed(2)}B</span>
            </div>
          </div>
        </div>
      </div>
      <div className="chart-row">
        <StockPriceChart stockSymbol={fundamentalData.company_info?.symbol} />
      </div>
      <div className="chart-row">
        <RevenueExpenseProfitChart stockSymbol={fundamentalData.company_info?.symbol} />
      </div>
      {/* AI-powered add-on */}
      {aiData && (
        <div className="ai-indicator-card">
          <h3>AI-Powered Indicator</h3>
          <div className="ai-indicator-content">
            <p><strong>Valuation Score:</strong> {aiData.valuation_score || 'N/A'}/100</p>
            <p>P/E Ratio: {fundamentalData.valuation?.pe_ratio || 'N/A'}</p>
            <p>{aiData.valuation_summary || 'No summary available.'}</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default FundamentalDashboard; 
// export default FundamentalDashboard; 