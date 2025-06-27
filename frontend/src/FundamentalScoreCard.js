import React, { useState, useEffect } from 'react';
import './FundamentalScoreCard.css';

const FundamentalScoreCard = ({ stockSymbol }) => {
  const [scores, setScores] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Mock data for demonstration purposes
  const getMockData = (symbol) => {
    // Normalize symbol for lookup (handle both with and without .NS suffix)
    const normalizedSymbol = symbol.includes('.') ? symbol : symbol + '.NS';
    const baseSymbol = symbol.replace('.NS', '');
    
    const mockDataMap = {
      'RELIANCE': {
        symbol: 'RELIANCE',
        reliability_score: 78,
        growth_scope: 65,
        valuation_score: 72,
        overall_score: 72.1,
        overall_grade: 'B+',
        recommendation: 'Buy',
        risk_level: 'Medium',
        key_highlights: [
          'Reliability: 78/100',
          'Growth Potential: 65/100',
          'Valuation: 72/100',
          'Risk: Medium'
        ]
      },
      'TCS': {
        symbol: 'TCS',
        reliability_score: 88,
        growth_scope: 75,
        valuation_score: 55,
        overall_score: 75.4,
        overall_grade: 'A',
        recommendation: 'Buy',
        risk_level: 'Low',
        key_highlights: [
          'Reliability: 88/100',
          'Growth Potential: 75/100',
          'Valuation: 55/100',
          'Risk: Low'
        ]
      },
      'HDFCBANK': {
        symbol: 'HDFCBANK',
        reliability_score: 82,
        growth_scope: 70,
        valuation_score: 68,
        overall_score: 74.2,
        overall_grade: 'B+',
        recommendation: 'Buy',
        risk_level: 'Medium',
        key_highlights: [
          'Reliability: 82/100',
          'Growth Potential: 70/100',
          'Valuation: 68/100',
          'Risk: Medium'
        ]
      },
      'INFY': {
        symbol: 'INFY',
        reliability_score: 85,
        growth_scope: 68,
        valuation_score: 62,
        overall_score: 72.8,
        overall_grade: 'B+',
        recommendation: 'Hold',
        risk_level: 'Low',
        key_highlights: [
          'Reliability: 85/100',
          'Growth Potential: 68/100',
          'Valuation: 62/100',
          'Risk: Low'
        ]
      },
      'ICICIBANK': {
        symbol: 'ICICIBANK',
        reliability_score: 76,
        growth_scope: 72,
        valuation_score: 65,
        overall_score: 71.3,
        overall_grade: 'B',
        recommendation: 'Hold',
        risk_level: 'Medium',
        key_highlights: [
          'Reliability: 76/100',
          'Growth Potential: 72/100',
          'Valuation: 65/100',
          'Risk: Medium'
        ]
      },
      'ADANIGREEN': {
        symbol: 'ADANIGREEN',
        reliability_score: 65,
        growth_scope: 85,
        valuation_score: 45,
        overall_score: 66.5,
        overall_grade: 'B',
        recommendation: 'Hold',
        risk_level: 'Medium',
        key_highlights: [
          'Reliability: 65/100',
          'Growth Potential: 85/100',
          'Valuation: 45/100',
          'Risk: Medium'
        ]
      },
      'ADANIPORTS': {
        symbol: 'ADANIPORTS',
        reliability_score: 70,
        growth_scope: 75,
        valuation_score: 60,
        overall_score: 69.0,
        overall_grade: 'B',
        recommendation: 'Hold',
        risk_level: 'Medium',
        key_highlights: [
          'Reliability: 70/100',
          'Growth Potential: 75/100',
          'Valuation: 60/100',
          'Risk: Medium'
        ]
      },
      'BHARTIARTL': {
        symbol: 'BHARTIARTL',
        reliability_score: 80,
        growth_scope: 70,
        valuation_score: 65,
        overall_score: 72.5,
        overall_grade: 'B+',
        recommendation: 'Buy',
        risk_level: 'Low',
        key_highlights: [
          'Reliability: 80/100',
          'Growth Potential: 70/100',
          'Valuation: 65/100',
          'Risk: Low'
        ]
      },
      'MARUTI': {
        symbol: 'MARUTI',
        reliability_score: 85,
        growth_scope: 60,
        valuation_score: 55,
        overall_score: 68.5,
        overall_grade: 'B',
        recommendation: 'Hold',
        risk_level: 'Low',
        key_highlights: [
          'Reliability: 85/100',
          'Growth Potential: 60/100',
          'Valuation: 55/100',
          'Risk: Low'
        ]
      },
      'ADANIPOWER': {
        symbol: 'ADANIPOWER',
        reliability_score: 55,
        growth_scope: 80,
        valuation_score: 50,
        overall_score: 62.5,
        overall_grade: 'C+',
        recommendation: 'Hold',
        risk_level: 'High',
        key_highlights: [
          'Reliability: 55/100',
          'Growth Potential: 80/100',
          'Valuation: 50/100',
          'Risk: High'
        ]
      },
      'APOLLOHOSP': {
        symbol: 'APOLLOHOSP',
        reliability_score: 82,
        growth_scope: 70,
        valuation_score: 58,
        overall_score: 71.2,
        overall_grade: 'B+',
        recommendation: 'Buy',
        risk_level: 'Low',
        key_highlights: [
          'Reliability: 82/100',
          'Growth Potential: 70/100',
          'Valuation: 58/100',
          'Risk: Low'
        ]
      },
      'ASIANPAINT': {
        symbol: 'ASIANPAINT',
        reliability_score: 88,
        growth_scope: 65,
        valuation_score: 52,
        overall_score: 70.1,
        overall_grade: 'B+',
        recommendation: 'Hold',
        risk_level: 'Low',
        key_highlights: [
          'Reliability: 88/100',
          'Growth Potential: 65/100',
          'Valuation: 52/100',
          'Risk: Low'
        ]
      },
      'AXISBANK': {
        symbol: 'AXISBANK',
        reliability_score: 75,
        growth_scope: 68,
        valuation_score: 70,
        overall_score: 70.9,
        overall_grade: 'B+',
        recommendation: 'Buy',
        risk_level: 'Medium',
        key_highlights: [
          'Reliability: 75/100',
          'Growth Potential: 68/100',
          'Valuation: 70/100',
          'Risk: Medium'
        ]
      }
    };

    // Try to find data using both the original symbol and base symbol
    return mockDataMap[baseSymbol] || mockDataMap[symbol] || {
      symbol: symbol,
      reliability_score: 60,
      growth_scope: 55,
      valuation_score: 50,
      overall_score: 55.5,
      overall_grade: 'C',
      recommendation: 'Hold',
      risk_level: 'Medium',
      key_highlights: [
        'Reliability: 60/100',
        'Growth Potential: 55/100',
        'Valuation: 50/100',
        'Risk: Medium'
      ]
    };
  };

  useEffect(() => {
    const fetchScores = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Try with .NS suffix for API call if not already present
        const apiSymbol = stockSymbol.includes('.') ? stockSymbol : stockSymbol + '.NS';
        console.log(`FundamentalScoreCard: Fetching scores for ${stockSymbol}, API call with ${apiSymbol}`);
        const response = await fetch(`http://localhost:5000/api/fundamental-scores/${apiSymbol}`);
        
        if (!response.ok) {
          throw new Error('Failed to fetch fundamental scores');
        }
        
        const data = await response.json();
        
        if (data.success && data.frontend_summary) {
          // Sanitize the API response to handle null/NaN values
          const sanitizedScores = {
            reliability_score: isNaN(data.frontend_summary.reliability_score) || data.frontend_summary.reliability_score === null ? 0 : Number(data.frontend_summary.reliability_score),
            growth_scope: isNaN(data.frontend_summary.growth_scope) || data.frontend_summary.growth_scope === null ? 0 : Number(data.frontend_summary.growth_scope),
            valuation_score: isNaN(data.frontend_summary.valuation_score) || data.frontend_summary.valuation_score === null ? 0 : Number(data.frontend_summary.valuation_score),
            overall_score: isNaN(data.frontend_summary.overall_score) || data.frontend_summary.overall_score === null ? 0 : Number(data.frontend_summary.overall_score),
            overall_grade: data.frontend_summary.overall_grade || 'N/A',
            recommendation: data.frontend_summary.recommendation || 'Data Unavailable',
            risk_level: data.frontend_summary.risk_level || 'Unknown'
          };
          
          setScores(sanitizedScores);
        } else {
          throw new Error(data.error || 'No data available');
        }
        
      } catch (err) {
        console.log(`Using mock data for ${stockSymbol} - API unavailable:`, err.message);
        // Fall back to mock data for demonstration
        const mockData = getMockData(stockSymbol);
        console.log(`Mock data for ${stockSymbol}:`, mockData);
        setScores(mockData);
      } finally {
        setLoading(false);
      }
    };

    if (stockSymbol) {
      fetchScores();
    }
  }, [stockSymbol]);

  const getScoreColor = (score) => {
    if (score >= 80) return '#10B981'; // Green - Excellent
    if (score >= 65) return '#84CC16'; // Light Green - Good
    if (score >= 50) return '#F59E0B'; // Yellow - Average
    if (score >= 35) return '#F97316'; // Orange - Below Average
    return '#EF4444'; // Red - Poor
  };

  const getGradeColor = (grade) => {
    if (grade.includes('A')) return '#10B981';
    if (grade.includes('B')) return '#84CC16';
    if (grade.includes('C')) return '#F59E0B';
    if (grade.includes('D')) return '#F97316';
    return '#EF4444';
  };

  const getRiskColor = (risk) => {
    switch (risk.toLowerCase()) {
      case 'low': return '#10B981';
      case 'medium': return '#F59E0B';
      case 'high': return '#EF4444';
      default: return '#6B7280';
    }
  };

  const getRecommendationColor = (recommendation) => {
    if (recommendation.includes('Buy')) return '#10B981';
    if (recommendation.includes('Hold')) return '#F59E0B';
    if (recommendation.includes('Sell')) return '#EF4444';
    return '#6B7280';
  };

  if (loading) {
    return (
      <div className="fundamental-score-card loading">
        <div className="score-header">
          <h4>📈 Fundamental Analysis</h4>
        </div>
        <div className="loading-content">
          <div className="mini-spinner"></div>
          <p>Calculating scores...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="fundamental-score-card error">
        <div className="score-header">
          <h4>📈 Fundamental Analysis</h4>
        </div>
        <div className="error-content">
          <p>Unable to load scores</p>
          <span className="error-detail">{error}</span>
        </div>
      </div>
    );
  }

  if (!scores) {
    return (
      <div className="fundamental-score-card no-data">
        <div className="score-header">
          <h4>📈 Fundamental Analysis</h4>
        </div>
        <div className="no-data-content">
          <p>No data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="fundamental-score-card">
      <div className="score-header">
        <h4>📈 Fundamental Analysis</h4>
        <div className="overall-grade" style={{ backgroundColor: getGradeColor(scores.overall_grade) }}>
          {scores.overall_grade}
        </div>
      </div>
      
      <div className="score-grid">
        <div className="score-item">
          <span className="score-label">Reliability</span>
          <div className="score-bar">
            <div 
              className="score-fill" 
              style={{ 
                width: `${scores.reliability_score}%`,
                backgroundColor: getScoreColor(scores.reliability_score)
              }}
            ></div>
          </div>
          <span className="score-value">{scores.reliability_score}/100</span>
        </div>
        
        <div className="score-item">
          <span className="score-label">Growth</span>
          <div className="score-bar">
            <div 
              className="score-fill" 
              style={{ 
                width: `${scores.growth_scope}%`,
                backgroundColor: getScoreColor(scores.growth_scope)
              }}
            ></div>
          </div>
          <span className="score-value">{scores.growth_scope}/100</span>
        </div>
        
        <div className="score-item">
          <span className="score-label">Valuation</span>
          <div className="score-bar">
            <div 
              className="score-fill" 
              style={{ 
                width: `${scores.valuation_score}%`,
                backgroundColor: getScoreColor(scores.valuation_score)
              }}
            ></div>
          </div>
          <span className="score-value">{scores.valuation_score}/100</span>
        </div>
      </div>
      
      <div className="score-summary">
        <div className="summary-row">
          <span className="summary-label">Overall Score:</span>
          <span 
            className="summary-value overall-score" 
            style={{ color: getScoreColor(scores.overall_score) }}
          >
            {scores.overall_score}/100
          </span>
        </div>
        
        <div className="summary-row">
          <span className="summary-label">Recommendation:</span>
          <span 
            className="summary-value recommendation"
            style={{ color: getRecommendationColor(scores.recommendation) }}
          >
            {scores.recommendation}
          </span>
        </div>
        
        <div className="summary-row">
          <span className="summary-label">Risk Level:</span>
          <span 
            className="summary-value risk-level"
            style={{ color: getRiskColor(scores.risk_level) }}
          >
            {scores.risk_level}
          </span>
        </div>
      </div>
    </div>
  );
};

export default FundamentalScoreCard; 