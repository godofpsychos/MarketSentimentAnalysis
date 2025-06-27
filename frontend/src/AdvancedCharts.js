import React, { useRef, useEffect } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  RadialLinearScale,
  ArcElement,
  ScatterController,
  BubbleController
} from 'chart.js';
import { Chart } from 'react-chartjs-2';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  RadialLinearScale,
  ArcElement,
  ScatterController,
  BubbleController
);

// Color palette
const CHART_COLORS = {
  red: 'rgb(255, 99, 132)',
  orange: 'rgb(255, 159, 64)',
  yellow: 'rgb(255, 205, 86)',
  green: 'rgb(75, 192, 192)',
  blue: 'rgb(54, 162, 235)',
  purple: 'rgb(153, 102, 255)',
  grey: 'rgb(201, 203, 207)',
  primary: '#4F46E5',
  secondary: '#10B981',
  accent: '#F59E0B',
  danger: '#EF4444'
};

// Stock Performance Heatmap
export const StockHeatmap = ({ data, title = "Stock Performance Heatmap" }) => {
  const chartRef = useRef();

  const heatmapData = {
    labels: data?.map(d => d.symbol) || [],
    datasets: [{
      label: 'Performance Score',
      data: data?.map(d => ({
        x: d.symbol,
        y: d.performance_score || 0,
        v: d.market_cap || 0
      })) || [],
      backgroundColor: (ctx) => {
        const value = ctx.parsed.y;
        if (value > 80) return 'rgba(16, 185, 129, 0.8)'; // Excellent
        if (value > 60) return 'rgba(132, 204, 22, 0.8)'; // Good
        if (value > 40) return 'rgba(245, 158, 11, 0.8)'; // Average
        return 'rgba(239, 68, 68, 0.8)'; // Poor
      },
      borderColor: 'rgba(255, 255, 255, 0.8)',
      borderWidth: 2
    }]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      title: { display: true, text: title },
      legend: { display: false },
      tooltip: {
        callbacks: {
          title: (context) => `${context[0].label}`,
          label: (context) => [
            `Performance Score: ${context.parsed.y}`,
            `Market Cap: ₹${(context.raw.v / 1000000000).toFixed(2)}B`
          ]
        }
      }
    },
    scales: {
      x: { display: true, title: { display: true, text: 'Stocks' } },
      y: { 
        display: true, 
        title: { display: true, text: 'Performance Score' },
        min: 0,
        max: 100
      }
    }
  };

  return <Chart ref={chartRef} type="scatter" data={heatmapData} options={options} />;
};

// Bubble Chart for Risk vs Return
export const RiskReturnBubbleChart = ({ data, title = "Risk vs Return Analysis" }) => {
  const bubbleData = {
    datasets: [{
      label: 'Stocks',
      data: data?.map(d => ({
        x: d.risk_score || 0,
        y: d.return_potential || 0,
        r: Math.sqrt(d.market_cap / 1000000000) * 5 // Size based on market cap
      })) || [],
      backgroundColor: data?.map(d => {
        const score = (d.risk_score + d.return_potential) / 2;
        if (score > 75) return 'rgba(16, 185, 129, 0.6)';
        if (score > 50) return 'rgba(245, 158, 11, 0.6)';
        return 'rgba(239, 68, 68, 0.6)';
      }) || [],
      borderColor: data?.map(d => {
        const score = (d.risk_score + d.return_potential) / 2;
        if (score > 75) return 'rgb(16, 185, 129)';
        if (score > 50) return 'rgb(245, 158, 11)';
        return 'rgb(239, 68, 68)';
      }) || [],
      borderWidth: 2
    }]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      title: { display: true, text: title },
      legend: { display: false },
      tooltip: {
        callbacks: {
          title: (context) => data?.[context[0].dataIndex]?.symbol || '',
          label: (context) => [
            `Risk Score: ${context.parsed.x}`,
            `Return Potential: ${context.parsed.y}`,
            `Market Cap: ₹${(data?.[context.dataIndex]?.market_cap / 1000000000)?.toFixed(2) || 0}B`
          ]
        }
      }
    },
    scales: {
      x: { 
        display: true, 
        title: { display: true, text: 'Risk Score' },
        min: 0,
        max: 100
      },
      y: { 
        display: true, 
        title: { display: true, text: 'Return Potential' },
        min: 0,
        max: 100
      }
    }
  };

  return <Chart type="bubble" data={bubbleData} options={options} />;
};

// Multi-axis Financial Metrics Chart
export const MultiAxisFinancialChart = ({ data, title = "Financial Metrics Overview" }) => {
  const chartData = {
    labels: data?.map(d => d.symbol) || [],
    datasets: [
      {
        type: 'bar',
        label: 'ROE (%)',
        data: data?.map(d => d.roe) || [],
        backgroundColor: 'rgba(79, 70, 229, 0.7)',
        borderColor: 'rgb(79, 70, 229)',
        borderWidth: 2,
        yAxisID: 'y'
      },
      {
        type: 'line',
        label: 'P/E Ratio',
        data: data?.map(d => d.pe_ratio) || [],
        borderColor: 'rgb(16, 185, 129)',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        borderWidth: 3,
        fill: false,
        tension: 0.4,
        yAxisID: 'y1'
      },
      {
        type: 'line',
        label: 'Debt/Equity',
        data: data?.map(d => d.debt_equity) || [],
        borderColor: 'rgb(239, 68, 68)',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        borderWidth: 3,
        fill: false,
        tension: 0.4,
        yAxisID: 'y2'
      }
    ]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index',
      intersect: false,
    },
    plugins: {
      title: { display: true, text: title },
      legend: { position: 'top' }
    },
    scales: {
      x: { display: true, title: { display: true, text: 'Stocks' } },
      y: {
        type: 'linear',
        display: true,
        position: 'left',
        title: { display: true, text: 'ROE (%)' },
        grid: { drawOnChartArea: false }
      },
      y1: {
        type: 'linear',
        display: true,
        position: 'right',
        title: { display: true, text: 'P/E Ratio' },
        grid: { drawOnChartArea: false }
      },
      y2: {
        type: 'linear',
        display: false,
        position: 'right'
      }
    }
  };

  return <Chart data={chartData} options={options} />;
};

// Sector Comparison Radar Chart
export const SectorRadarChart = ({ data, title = "Sector Analysis" }) => {
  const radarData = {
    labels: [
      'Profitability',
      'Valuation',
      'Growth',
      'Liquidity',
      'Financial Health',
      'Market Position'
    ],
    datasets: data?.map((sector, index) => ({
      label: sector.name,
      data: [
        sector.profitability || 0,
        sector.valuation || 0,
        sector.growth || 0,
        sector.liquidity || 0,
        sector.financial_health || 0,
        sector.market_position || 0
      ],
      backgroundColor: `${Object.values(CHART_COLORS)[index % Object.keys(CHART_COLORS).length]}20`,
      borderColor: Object.values(CHART_COLORS)[index % Object.keys(CHART_COLORS).length],
      borderWidth: 2,
      pointBackgroundColor: Object.values(CHART_COLORS)[index % Object.keys(CHART_COLORS).length],
      pointBorderColor: '#fff',
      pointHoverBackgroundColor: '#fff',
      pointHoverBorderColor: Object.values(CHART_COLORS)[index % Object.keys(CHART_COLORS).length]
    })) || []
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      title: { display: true, text: title },
      legend: { position: 'top' }
    },
    scales: {
      r: {
        angleLines: { display: true },
        suggestedMin: 0,
        suggestedMax: 100,
        ticks: { stepSize: 20 }
      }
    }
  };

  return <Chart type="radar" data={radarData} options={options} />;
};

// Trend Analysis Line Chart with Annotations
export const TrendAnalysisChart = ({ data, title = "Performance Trends" }) => {
  const trendData = {
    labels: data?.periods || [],
    datasets: [
      {
        label: 'Stock Price',
        data: data?.price_trend || [],
        borderColor: 'rgb(79, 70, 229)',
        backgroundColor: 'rgba(79, 70, 229, 0.1)',
        borderWidth: 3,
        fill: true,
        tension: 0.4,
        yAxisID: 'y'
      },
      {
        label: 'Volume (M)',
        data: data?.volume_trend?.map(v => v / 1000000) || [],
        type: 'bar',
        backgroundColor: 'rgba(16, 185, 129, 0.5)',
        borderColor: 'rgb(16, 185, 129)',
        borderWidth: 1,
        yAxisID: 'y1'
      },
      {
        label: 'RSI',
        data: data?.rsi_trend || [],
        borderColor: 'rgb(245, 158, 11)',
        backgroundColor: 'rgba(245, 158, 11, 0.1)',
        borderWidth: 2,
        fill: false,
        tension: 0.4,
        yAxisID: 'y2'
      }
    ]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index',
      intersect: false,
    },
    plugins: {
      title: { display: true, text: title },
      legend: { position: 'top' },
      annotation: {
        annotations: {
          line1: {
            type: 'line',
            yMin: 70,
            yMax: 70,
            yScaleID: 'y2',
            borderColor: 'rgb(239, 68, 68)',
            borderWidth: 2,
            borderDash: [5, 5],
            label: {
              content: 'Overbought',
              enabled: true,
              position: 'end'
            }
          },
          line2: {
            type: 'line',
            yMin: 30,
            yMax: 30,
            yScaleID: 'y2',
            borderColor: 'rgb(16, 185, 129)',
            borderWidth: 2,
            borderDash: [5, 5],
            label: {
              content: 'Oversold',
              enabled: true,
              position: 'end'
            }
          }
        }
      }
    },
    scales: {
      x: { display: true, title: { display: true, text: 'Time Period' } },
      y: {
        type: 'linear',
        display: true,
        position: 'left',
        title: { display: true, text: 'Price (₹)' }
      },
      y1: {
        type: 'linear',
        display: true,
        position: 'right',
        title: { display: true, text: 'Volume (M)' },
        grid: { drawOnChartArea: false }
      },
      y2: {
        type: 'linear',
        display: false,
        min: 0,
        max: 100
      }
    }
  };

  return <Chart data={trendData} options={options} />;
};

// Financial Health Score Gauge
export const FinancialHealthGauge = ({ score, title = "Financial Health Score" }) => {
  const gaugeData = {
    datasets: [{
      data: [score, 100 - score],
      backgroundColor: [
        score > 80 ? CHART_COLORS.green :
        score > 60 ? CHART_COLORS.yellow :
        score > 40 ? CHART_COLORS.orange :
        CHART_COLORS.red,
        'rgba(229, 231, 235, 0.3)'
      ],
      borderWidth: 0,
      cutout: '80%',
      circumference: 180,
      rotation: 270
    }]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      title: { display: true, text: title },
      legend: { display: false },
      tooltip: { enabled: false }
    }
  };

  return (
    <div style={{ position: 'relative', height: '200px' }}>
      <Chart type="doughnut" data={gaugeData} options={options} />
      <div style={{
        position: 'absolute',
        top: '60%',
        left: '50%',
        transform: 'translateX(-50%)',
        textAlign: 'center',
        fontSize: '2rem',
        fontWeight: 'bold',
        color: score > 60 ? CHART_COLORS.green : CHART_COLORS.red
      }}>
        {score}%
      </div>
    </div>
  );
};

export default {
  StockHeatmap,
  RiskReturnBubbleChart,
  MultiAxisFinancialChart,
  SectorRadarChart,
  TrendAnalysisChart,
  FinancialHealthGauge
}; 