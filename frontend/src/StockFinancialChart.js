import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { format } from 'date-fns';

const StockFinancialChart = ({ stockSymbol }) => {
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

  const formatTooltipValue = (value, name) => {
    return [`₹${value.toFixed(2)}B`, name];
  };

  const formatXAxisLabel = (tickItem) => {
    try {
      return format(new Date(tickItem), 'yyyy');
    } catch {
      return tickItem;
    }
  };

  if (loading) {
    return (
      <div className="stock-financial-loading">
        <div className="mini-spinner"></div>
        <p>Loading financial data...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="stock-financial-error">
        <p>Unable to load financial data</p>
      </div>
    );
  }

  if (financialData.length === 0) {
    return (
      <div className="stock-financial-no-data">
        <p>No financial data available for {stockSymbol}</p>
      </div>
    );
  }

  return (
    <div className="stock-financial-chart">
      <h4>Financial Performance - {stockSymbol}</h4>
      <ResponsiveContainer width="100%" height={250}>
        <LineChart data={financialData} margin={{ top: 10, right: 20, left: 10, bottom: 10 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis 
            dataKey="period_date" 
            tickFormatter={formatXAxisLabel}
            tick={{ fontSize: 10 }}
            stroke="#666"
          />
          <YAxis 
            tick={{ fontSize: 10 }}
            stroke="#666"
          />
          <Tooltip 
            formatter={formatTooltipValue}
            labelStyle={{ color: '#333' }}
            contentStyle={{ 
              backgroundColor: 'rgba(255, 255, 255, 0.95)',
              border: '1px solid #ccc',
              borderRadius: '4px'
            }}
          />
          <Legend 
            wrapperStyle={{ fontSize: '12px' }}
          />
          <Line 
            type="monotone" 
            dataKey="total_revenue" 
            stroke="#2196F3" 
            strokeWidth={2}
            dot={{ fill: '#2196F3', strokeWidth: 1, r: 3 }}
            name="Revenue"
          />
          <Line 
            type="monotone" 
            dataKey="total_expenditure" 
            stroke="#FF5722" 
            strokeWidth={2}
            dot={{ fill: '#FF5722', strokeWidth: 1, r: 3 }}
            name="Expenditure"
          />
          <Line 
            type="monotone" 
            dataKey="net_profit" 
            stroke="#4CAF50" 
            strokeWidth={2}
            dot={{ fill: '#4CAF50', strokeWidth: 1, r: 3 }}
            name="Net Profit"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default StockFinancialChart; 