import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { format, subDays, subMonths, subYears, isAfter } from 'date-fns';

// Shared fetch logic
const useStockFinancialData = (stockSymbol) => {
  const [financialData, setFinancialData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchFinancialData = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await fetch('http://localhost:5000/api/financial-data');
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const result = await response.json();
        if (result.error) {
          throw new Error(result.error);
        }
        // Filter data for this specific stock and process it
        const stockData = result.data
          .filter(row => row.symbol === stockSymbol)
          .map(row => ({
            period_date: row.period_date,
            total_revenue: row.total_revenue / 1000000000, // Convert to billions
            total_expenditure: row.total_expenditure / 1000000000, // Convert to billions
            net_profit: row.net_profit / 1000000000, // Convert to billions
            price: row.price, // If available
            year: format(new Date(row.period_date), 'yyyy')
          }))
          .sort((a, b) => new Date(a.period_date) - new Date(b.period_date));
        setFinancialData(stockData);
      } catch (err) {
        setError(err.message);
        console.error('Error fetching financial data for', stockSymbol, ':', err);
      } finally {
        setLoading(false);
      }
    };
    if (stockSymbol) {
      fetchFinancialData();
    }
  }, [stockSymbol]);
  return { financialData, loading, error };
};

const formatXAxisLabel = (tickItem) => {
  try {
    return format(new Date(tickItem), 'yyyy-MM-dd');
  } catch {
    return tickItem;
  }
};

const TIMEFRAMES = [
  { label: '1D', value: '1d' },
  { label: '5D', value: '5d' },
  { label: '1MO', value: '1mo' },
  { label: '3MO', value: '3mo' },
  { label: '6MO', value: '6mo' },
  { label: '1Y', value: '1y' },
  { label: '2Y', value: '2y' },
  { label: '5Y', value: '5y' },
  { label: 'MAX', value: 'max' }
];

function filterByTimeframe(data, timeframe) {
  if (!data || data.length === 0) return [];
  const lastDate = new Date(data[data.length - 1].period_date);
  let fromDate;
  switch (timeframe) {
    case '1D':
      fromDate = subDays(lastDate, 1); break;
    case '5D':
      fromDate = subDays(lastDate, 5); break;
    case '1MO':
      fromDate = subMonths(lastDate, 1); break;
    case '3MO':
      fromDate = subMonths(lastDate, 3); break;
    case '6MO':
      fromDate = subMonths(lastDate, 6); break;
    case '1Y':
      fromDate = subYears(lastDate, 1); break;
    default:
      return data;
  }
  return data.filter(row => isAfter(new Date(row.period_date), fromDate));
}

// Chart 1: Price only
export const StockPriceChart = ({ stockSymbol }) => {
  const [period, setPeriod] = useState('1mo');
  const [priceData, setPriceData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentPrice, setCurrentPrice] = useState(null);

  useEffect(() => {
    if (!stockSymbol) return;
    setLoading(true);
    setError(null);
    fetch(`http://localhost:5000/api/stock-data/${stockSymbol}?period=${period}`)
      .then(res => res.json())
      .then(result => {
        if (result.error) throw new Error(result.error);
        setPriceData(result.data || []);
        setCurrentPrice(result.current_price || null);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, [stockSymbol, period]);

  if (loading) return <div className="stock-financial-loading"><div className="mini-spinner"></div><p>Loading price data...</p></div>;
  if (error) return <div className="stock-financial-error"><p>Unable to load price data</p></div>;
  if (!priceData || priceData.length === 0) return <div className="stock-financial-no-data"><p>No price data available for {stockSymbol}</p></div>;

  const minPrice = Math.min(...priceData.map(d => d.close));
  const maxPrice = Math.max(...priceData.map(d => d.close));
  const latestPrice = priceData[priceData.length - 1]?.close;

  return (
    <div className="stock-financial-chart" style={{ background: 'white', borderRadius: '16px', padding: '24px', boxShadow: '0 2px 16px rgba(80,80,160,0.07)' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
        <div style={{ fontWeight: 700, fontSize: 22, color: '#673ab7' }}>{stockSymbol}</div>
        {latestPrice !== null && <div style={{ fontWeight: 700, fontSize: 28, color: '#10B981' }}>₹{latestPrice}</div>}
        <div style={{ color: '#888', fontSize: 14 }}>Day: ₹{minPrice} - ₹{maxPrice}</div>
      </div>
      <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
        {TIMEFRAMES.map(tf => (
          <button
            key={tf.value}
            onClick={() => setPeriod(tf.value)}
            style={{
              background: period === tf.value ? 'linear-gradient(90deg,#7b61ff,#5a4fff)' : '#f3f4f6',
              color: period === tf.value ? '#fff' : '#333',
              border: 'none',
              borderRadius: 8,
              padding: '4px 16px',
              fontWeight: 600,
              fontSize: 14,
              cursor: 'pointer',
              boxShadow: period === tf.value ? '0 2px 8px rgba(80,80,160,0.07)' : 'none',
              outline: 'none',
              transition: 'all 0.2s'
            }}
          >
            {tf.label}
          </button>
        ))}
      </div>
      <ResponsiveContainer width="100%" height={250}>
        <AreaChart data={priceData} margin={{ top: 10, right: 20, left: 10, bottom: 10 }}>
          <defs>
            <linearGradient id="priceWhiteArea" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#fff" stopOpacity={0.8} />
              <stop offset="100%" stopColor="#fff" stopOpacity={0.2} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
          <XAxis dataKey="date" tickFormatter={formatXAxisLabel} tick={{ fontSize: 10 }} stroke="#666" />
          <YAxis tick={{ fontSize: 10 }} stroke="#666" domain={[minPrice, maxPrice]} />
          <Tooltip formatter={(value) => `₹${value}`} labelStyle={{ color: '#333' }} contentStyle={{ backgroundColor: 'rgba(255,255,255,0.95)', border: '1px solid #ccc', borderRadius: '4px' }} />
          <Area type="monotone" dataKey="close" stroke="#7b61ff" strokeWidth={3} fill="url(#priceWhiteArea)" dot={false} name="Price" />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};

// Chart 2: Revenue, Expense, Net Profit
export const RevenueExpenseProfitChart = ({ stockSymbol }) => {
  const { financialData, loading, error } = useStockFinancialData(stockSymbol);
  if (loading) return <div className="stock-financial-loading"><div className="mini-spinner"></div><p>Loading financial data...</p></div>;
  if (error) return <div className="stock-financial-error"><p>Unable to load financial data</p></div>;
  if (financialData.length === 0) return <div className="stock-financial-no-data"><p>No financial data available for {stockSymbol}</p></div>;
  return (
    <div className="stock-financial-chart">
      <h4>Revenue, Expense & Net Profit - {stockSymbol}</h4>
      <ResponsiveContainer width="100%" height={250}>
        <LineChart data={financialData} margin={{ top: 10, right: 20, left: 10, bottom: 10 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey="period_date" tickFormatter={formatXAxisLabel} tick={{ fontSize: 10 }} stroke="#666" />
          <YAxis tick={{ fontSize: 10 }} stroke="#666" />
          <Tooltip formatter={(value) => `₹${value}B`} labelStyle={{ color: '#333' }} contentStyle={{ backgroundColor: 'rgba(255,255,255,0.95)', border: '1px solid #ccc', borderRadius: '4px' }} />
          <Legend wrapperStyle={{ fontSize: '12px' }} />
          <Line type="monotone" dataKey="total_revenue" stroke="#2196F3" strokeWidth={2} dot={{ fill: '#2196F3', strokeWidth: 1, r: 3 }} name="Revenue" />
          <Line type="monotone" dataKey="total_expenditure" stroke="#FF5722" strokeWidth={2} dot={{ fill: '#FF5722', strokeWidth: 1, r: 3 }} name="Expenditure" />
          <Line type="monotone" dataKey="net_profit" stroke="#4CAF50" strokeWidth={2} dot={{ fill: '#4CAF50', strokeWidth: 1, r: 3 }} name="Net Profit" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}; 