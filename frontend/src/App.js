import React, { useEffect, useState } from 'react';
import './App.css';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { format, parseISO } from 'date-fns';

// Component for showing loading state
const Loading = () => (
  <div className="loading">
    <div className="spinner"></div>
    <p>Loading market data...</p>
  </div>
);

// Component for showing error state
const ErrorMessage = ({ message }) => (
  <div className="error-container">
    <h3>Error Loading Data</h3>
    <p>{message}</p>
    <button onClick={() => window.location.reload()}>Try Again</button>
  </div>
);

// Component for displaying sentiment score with color
const SentimentScore = ({ score }) => {
  // Determine color based on sentiment score
  let color = "#888"; // neutral (gray)
  if (score > 0.2) color = "#2e7d32"; // positive (green)
  if (score > 0.5) color = "#1b5e20"; // very positive (dark green)
  if (score < -0.2) color = "#c62828"; // negative (red)
  if (score < -0.5) color = "#b71c1c"; // very negative (dark red)
  
  return (
    <div className="sentiment-score" style={{ backgroundColor: color }}>
      <span>{score.toFixed(2)}</span>
    </div>
  );
};

// New component for sentiment meter (1-10 scale)
const SentimentMeter = ({ value }) => {
  // Convert value to a 0-100% scale for the meter
  const percentage = ((11 - value) / 10) * 100;
  
  // Determine color based on sentiment value
  // 1-3: Green (Thriving Business)
  // 4-6: Yellow (Stable Business)
  // 7-10: Red (Struggling Business)
  let color = "#FFC107"; // Default: Yellow (Stable)
  let label = "Stable Business";
  
  if (value <= 3) {
    color = "#4CAF50"; // Green (Thriving)
    label = "Thriving Business";
  } else if (value >= 7) {
    color = "#F44336"; // Red (Struggling)
    label = "Struggling Business";
  } else if (value < 5) {
    label = "Growing Business";
  } else if (value > 5) {
    label = "Declining Business";
  }
  
  return (
    <div className="sentiment-meter-container">
      <div className="main-stream-header">
        <h4>Main Stream Business Indicator</h4>
      </div>
      <div className="sentiment-meter">
        <div className="sentiment-meter-fill" style={{ width: `${percentage}%`, backgroundColor: color }}></div>
      </div>
      <div className="sentiment-label" style={{ color }}>
        {label} ({value.toFixed(1)}/10)
      </div>
      <div className="sentiment-scale">
        <span className="buy">Thriving</span>
        <span className="neutral">Stable</span>
        <span className="sell">Struggling</span>
      </div>
    </div>
  );
};

// Yahoo Finance Chart Component using Recharts
const YahooFinanceChart = ({ symbol }) => {
  const [chartData, setChartData] = useState([]);
  const [stockInfo, setStockInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [period, setPeriod] = useState('1d');

  useEffect(() => {
    const fetchStockData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Fetch both stock data and basic info
        const [dataResponse, infoResponse] = await Promise.all([
          fetch(`http://localhost:5000/api/stock-data/${symbol}?period=${period}`),
          fetch(`http://localhost:5000/api/stock-info/${symbol}`)
        ]);
        
        if (!dataResponse.ok || !infoResponse.ok) {
          throw new Error('Failed to fetch stock data');
        }
        
        const stockData = await dataResponse.json();
        const stockInfoData = await infoResponse.json();
        
        setChartData(stockData.data || []);
        setStockInfo(stockInfoData);
        
      } catch (err) {
        setError(err.message);
        console.error('Error fetching stock data:', err);
      } finally {
        setLoading(false);
      }
    };

    if (symbol) {
      fetchStockData();
    }
  }, [symbol, period]);

  const formatTooltipValue = (value, name) => {
    if (name === 'volume') {
      return [value.toLocaleString(), 'Volume'];
    }
    return [`₹${value.toFixed(2)}`, name.charAt(0).toUpperCase() + name.slice(1)];
  };

  const formatXAxisLabel = (tickItem) => {
    try {
      return format(parseISO(tickItem), 'MMM dd');
    } catch {
      return tickItem;
    }
  };

  if (loading) {
    return (
      <div className="chart-loading">
        <div className="spinner"></div>
        <p>Loading chart data...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="chart-error">
        <p>Error loading chart: {error}</p>
        <button onClick={() => window.location.reload()}>Retry</button>
      </div>
    );
  }

  return (
    <div className="yahoo-finance-chart">
      {stockInfo && (
        <div className="stock-info-header">
          <h3>{stockInfo.name} ({stockInfo.symbol})</h3>
          <div className="price-info">
            <span className="current-price">₹{stockInfo.current_price}</span>
            <span className="price-range">
              Day: ₹{stockInfo.day_low} - ₹{stockInfo.day_high}
            </span>
          </div>
        </div>
      )}
      
      <div className="chart-controls">
        <div className="period-selector">
          {['1d', '5d', '1mo', '3mo', '6mo', '1y'].map((p) => (
            <button
              key={p}
              className={`period-btn ${period === p ? 'active' : ''}`}
              onClick={() => setPeriod(p)}
            >
              {p.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      <div className="chart-container">
        <ResponsiveContainer width="100%" height={400}>
          <AreaChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#8884d8" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="#8884d8" stopOpacity={0.1}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="date" 
              tickFormatter={formatXAxisLabel}
              tick={{ fontSize: 12 }}
            />
            <YAxis 
              domain={['dataMin - 10', 'dataMax + 10']}
              tickFormatter={(value) => `₹${value}`}
              tick={{ fontSize: 12 }}
            />
            <Tooltip 
              formatter={formatTooltipValue}
              labelFormatter={(label) => `Date: ${format(parseISO(label), 'MMM dd, yyyy')}`}
              contentStyle={{
                backgroundColor: '#f8f9fa',
                border: '1px solid #dee2e6',
                borderRadius: '4px'
              }}
            />
            <Area 
              type="monotone" 
              dataKey="close" 
              stroke="#8884d8" 
              fillOpacity={1} 
              fill="url(#colorPrice)" 
              strokeWidth={2}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

// Component for displaying stock sentiment
const StockSentiment = ({ data }) => (
  <div className="stock-sentiment">
    <div className="stock-header">
      <div className="stock-info">
        <h3>{data.stock}</h3>
        <p className="updated-date">Last updated: {new Date(data.datetime).toLocaleString()}</p>
      </div>
    </div>
    <div className="stock-content">
      <div className="sentiment-info">
        <SentimentMeter value={data.sentiment} />
      </div>
      <div className="chart-section">
        <YahooFinanceChart symbol={data.stock} />
      </div>
    </div>
  </div>
);

// Component for displaying news entries
const NewsItem = ({ news }) => (
  <div className="news-item">
    <h3>{news.title}</h3>
    <p className="news-date">{new Date(news.date).toLocaleDateString()}</p>
    <p>{news.summary}</p>
    <div className="news-sentiment">
      <span>Sentiment: </span>
      <SentimentScore score={news.sentiment} />
    </div>
    {news.url && <a href={news.url} target="_blank" rel="noopener noreferrer" className="news-link">Read More</a>}
  </div>
);

function App() {
  // State variables
  const [stocksData, setStocksData] = useState([]);
  const [stocksList, setStocksList] = useState([]);
  const [selectedStock, setSelectedStock] = useState('');
  const [newsData, setNewsData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [overallSentiment, setOverallSentiment] = useState(0);

  // Fetch stocks list when component mounts
  useEffect(() => {
    const fetchStocks = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/stocks');
        
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        const data = await response.json();
        setStocksList(data.stocks || []);
        
        // Set default selected stock if available
        if (data.stocks && data.stocks.length > 0) {
          setSelectedStock('');  // Empty means show all
        }
        
      } catch (err) {
        setError(err.message);
        console.error("Error fetching stocks list:", err);
      }
    };

    fetchStocks();
  }, []);
  
  // Fetch sentiment data when component mounts or selectedStock changes
  useEffect(() => {
    const fetchSentimentData = async () => {
      try {
        // Build URL with optional stock parameter
        let url = 'http://localhost:5000/api/sentiment';
        if (selectedStock) {
          url += `?stock=${selectedStock}`;
        }
        
        const response = await fetch(url);
        
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        const data = await response.json();
        setStocksData(data.data || []);
        
      } catch (err) {
        console.error("Error fetching sentiment data:", err);
        // Don't set global error - we still want to try loading news
      }
    };

    // Fetch news data when component mounts
    const fetchNewsData = async () => {
      try {
        // Try to fetch news if the API endpoint exists
        const response = await fetch('http://localhost:5000/api/recent-news');
        
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        const data = await response.json();
        setNewsData(data);
        
        // Calculate overall sentiment if data has sentiment values
        if (data.length > 0 && data[0].sentiment !== undefined) {
          const avgSentiment = data.reduce((sum, item) => sum + item.sentiment, 0) / data.length;
          setOverallSentiment(avgSentiment);
        }
        
      } catch (err) {
        console.error("Error fetching news data:", err);
        // Don't set error state if only news fails
      }
    };

    const fetchAllData = async () => {
      setLoading(true);
      try {
        await Promise.all([
          fetchSentimentData(),
          fetchNewsData()
        ]);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchAllData();
  }, [selectedStock]);

  if (loading) return <Loading />;
  if (error) return <ErrorMessage message={error} />;

  return (
    <div className="App">
      <header className="App-header">
        <div className="header-content">
          <h1>Market Sentiment Analysis</h1>
          <div className="stock-selector">
            <label htmlFor="stock-select">Select Stock: </label>
            <select 
              id="stock-select"
              value={selectedStock}
              onChange={(e) => setSelectedStock(e.target.value)}
            >
              <option value="">All Stocks</option>
              {stocksList.map((stock) => (
                <option key={stock} value={stock}>{stock}</option>
              ))}
            </select>
          </div>
        </div>
      </header>
      
      <main className="content">
        <div className="dashboard-grid">
          <section className="sentiment-section">
            <h2>{selectedStock ? `${selectedStock} Sentiment` : 'Stock Sentiments'}</h2>
            <div className="sentiment-container">
              {stocksData.length > 0 ? (
                stocksData.map((data, index) => (
                  <StockSentiment key={index} data={data} />
                ))
              ) : (
                <p className="no-data">No sentiment data available</p>
              )}
            </div>
          </section>
          
          {/* Keep the news section if it exists in the API */}
          {newsData.length > 0 && (
            <section className="news-section">
              <h2>Recent Market News</h2>
              <div className="news-container">
                {newsData.map((news, index) => (
                  <NewsItem key={index} news={news} />
                ))}
              </div>
            </section>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
