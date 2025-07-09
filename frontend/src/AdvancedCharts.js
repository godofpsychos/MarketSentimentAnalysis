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
  BubbleController,
  DoughnutController,
  RadarController,
  LineController,
  BarController,
  PolarAreaController,
  Filler
} from 'chart.js';
import { Chart } from 'react-chartjs-2';
import PlotlyChart from 'react-plotly.js';

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
  BubbleController,
  DoughnutController,
  RadarController,
  LineController,
  BarController,
  PolarAreaController,
  Filler
);

// Global chart cleanup function
const cleanupChart = (chartRef) => {
  if (chartRef.current && chartRef.current.chartInstance) {
    try {
      chartRef.current.chartInstance.destroy();
      chartRef.current.chartInstance = null;
    } catch (error) {
      console.warn('Error destroying chart:', error);
    }
  }
};

// Enhanced chart component wrapper
const ChartWrapper = ({ type, data, options, chartRef, title, height = 300, ...props }) => {
  const uniqueId = React.useMemo(() => `${type}-${title}-${Math.random().toString(36).substr(2, 9)}`, [type, title]);

  useEffect(() => {
    return () => {
      cleanupChart(chartRef);
    };
  }, [chartRef]);

  // Cleanup chart when data changes
  useEffect(() => {
    cleanupChart(chartRef);
  }, [data, type, chartRef]);

  return <Chart ref={chartRef} type={type} data={data} options={options} id={uniqueId} height={height} {...props} />;
};

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

  // Cleanup chart on unmount
  useEffect(() => {
    return () => {
      cleanupChart(chartRef);
    };
  }, []);

  // Cleanup chart when data changes
  useEffect(() => {
    cleanupChart(chartRef);
  }, [data]);

  // Safety check for data
  if (!data || !Array.isArray(data) || data.length === 0) {
    return (
      <div style={{ 
        height: '300px', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        backgroundColor: 'rgba(255,255,255,0.05)',
        borderRadius: '8px',
        border: '1px solid rgba(255,255,255,0.1)'
      }}>
        <p>No data available for heatmap</p>
      </div>
    );
  }

  const heatmapData = {
    labels: data.map(d => d.symbol || 'Unknown') || [],
    datasets: [{
      label: 'Performance Score',
      data: data.map(d => ({
        x: d.symbol || 'Unknown',
        y: d.performance_score || 0,
        v: d.market_cap || 0
      })) || [],
      backgroundColor: (ctx) => {
        const value = ctx.parsed?.y || 0;
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
          title: (context) => `${context[0]?.label || 'Unknown'}`,
          label: (context) => [
            `Performance Score: ${context.parsed?.y || 0}`,
            `Market Cap: ₹${((context.raw?.v || 0) / 1000000000).toFixed(2)}B`
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

  return <ChartWrapper type="scatter" data={heatmapData} options={options} chartRef={chartRef} title={title} />;
};

// Bubble Chart for Risk vs Return
export const RiskReturnBubbleChart = ({ data, title = "Risk vs Return Analysis" }) => {
  const chartRef = useRef();

  // Cleanup chart on unmount
  useEffect(() => {
    return () => {
      cleanupChart(chartRef);
    };
  }, []);

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

  return <ChartWrapper type="bubble" data={bubbleData} options={options} chartRef={chartRef} title={title} />;
};

// Multi-axis Financial Metrics Chart
export const MultiAxisFinancialChart = ({ data, title = "Financial Metrics Overview" }) => {
  const chartRef = useRef();

  // Cleanup chart on unmount
  useEffect(() => {
    return () => {
      cleanupChart(chartRef);
    };
  }, []);

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

  return <ChartWrapper type="bar" data={chartData} options={options} chartRef={chartRef} title={title} />;
};

// Sector Comparison Radar Chart
export const SectorRadarChart = ({ data, title = "Sector Analysis" }) => {
  const chartRef = useRef();

  // Cleanup chart on unmount
  useEffect(() => {
    return () => {
      cleanupChart(chartRef);
    };
  }, []);

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
      // Convert base RGB color to RGBA with 0.1 opacity for better transparency
      backgroundColor: Object.values(CHART_COLORS)[index % Object.keys(CHART_COLORS).length]
        .replace('rgb(', 'rgba(')
        .replace(')', ', 0.1)'),
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
      legend: { position: 'right' }
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

  return <ChartWrapper type="radar" data={radarData} options={options} chartRef={chartRef} title={title} />;
};

// Trend Analysis Line Chart with Annotations
export const TrendAnalysisChart = ({ data, title = "Performance Trends" }) => {
  const chartRef = useRef();

  // Cleanup chart on unmount
  useEffect(() => {
    return () => {
      cleanupChart(chartRef);
    };
  }, []);

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
        borderColor: 'rgb(16, 185, 129)',
        backgroundColor: 'rgba(16, 185, 129, 0.3)',
        borderWidth: 2,
        fill: false,
        tension: 0.4,
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
      legend: { position: 'top' }
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

  return <ChartWrapper type="line" data={trendData} options={options} chartRef={chartRef} title={title} />;
};

// Financial Health Score Gauge
export const FinancialHealthGauge = ({ score, title = "Financial Health Score" }) => {
  const chartRef = useRef();

  // Cleanup chart on unmount
  useEffect(() => {
    return () => {
      cleanupChart(chartRef);
    };
  }, []);

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
      <ChartWrapper type="doughnut" data={gaugeData} options={options} chartRef={chartRef} title={title} />
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

// Horizontal "thermometer" bar chart for sector scores
export const SectorThermometerBarChart = ({ data, title = "Sector Performance (Thermometer)" }) => {
  const chartRef = useRef();

  useEffect(() => () => cleanupChart(chartRef), []);
  useEffect(() => cleanupChart(chartRef), [data]);

  if (!Array.isArray(data) || data.length === 0) return <p>No data</p>;

  const labels = data.map(d => d.name);
  const scores = data.map(d => d.performance_score || d.score || d.value || 0);

  const datasetColors = scores.map(v => {
    if (v > 75) return 'rgba(16, 185, 129, 0.8)'; // green
    if (v > 50) return 'rgba(234, 179, 8, 0.8)'; // yellow
    if (v > 25) return 'rgba(245, 158, 11, 0.8)'; // orange
    return 'rgba(239, 68, 68, 0.8)'; // red
  });

  const barData = {
    labels,
    datasets: [{
      label: 'Score',
      data: scores,
      backgroundColor: datasetColors,
      borderRadius: 6,
      borderWidth: 1,
    }]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    indexAxis: 'y',
    plugins: {
      title: { display: true, text: title },
      legend: { display: false }
    },
    scales: {
      x: { suggestedMin: 0, suggestedMax: 100 },
      y: { ticks: { autoSkip: false } }
    }
  };

  return <ChartWrapper type="bar" data={barData} options={options} chartRef={chartRef} title={title} />;
};

// Bullseye / Polar Area chart showing sector scores
export const SectorBullseyeChart = ({ data, title = "Sector Bullseye" }) => {
  const chartRef = useRef();
  useEffect(() => () => cleanupChart(chartRef), []);
  useEffect(() => cleanupChart(chartRef), [data]);

  if (!Array.isArray(data) || data.length === 0) return <p>No data</p>;

  const labels = data.map(d => d.name);
  const scores = data.map(d => d.performance_score || d.score || d.value || 0);
  const bgColors = scores.map(v => {
    if (v > 75) return 'rgba(16, 185, 129, 0.6)';
    if (v > 50) return 'rgba(234, 179, 8, 0.6)';
    if (v > 25) return 'rgba(245, 158, 11, 0.6)';
    return 'rgba(239, 68, 68, 0.6)';
  });
  const borderColors = bgColors.map(c => c.replace(/0\.6\)/, '1)'));

  const polarData = {
    labels,
    datasets: [{
      data: scores,
      backgroundColor: bgColors,
      borderColor: borderColors,
      borderWidth: 1
    }]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      title: { display: true, text: title },
      legend: { position: 'right' }
    },
    scales: {
      r: { suggestedMin: 0, suggestedMax: 100 }
    }
  };

  return <ChartWrapper type="polarArea" data={polarData} options={options} chartRef={chartRef} title={title} />;
};

// Band Scatter (Traffic-Light Zones)
export const RiskReturnBandChart = ({ data, title = "Risk vs Return (Bands)" }) => {
  const chartRef = useRef();
  useEffect(() => () => cleanupChart(chartRef), []);
  useEffect(() => cleanupChart(chartRef), [data]);

  const scatterData = {
    datasets: [{
      label: 'Stocks',
      data: data?.map(d => ({ x: d.risk_score || 0, y: d.return_potential || 0 })) || [],
      pointBackgroundColor: 'rgba(59, 130, 246, 0.8)',
      pointRadius: 6,
    }]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      title: { display: true, text: title },
      legend: { display: false },
      // custom background bands
      beforeDraw: (chart) => {
        const { ctx, chartArea } = chart;
        if (!chartArea) return;
        const { left, top, width, height } = chartArea;
        const thirds = width / 3;
        const bands = [
          { x: left, width: thirds, color: 'rgba(16,185,129,0.05)' }, // good zone
          { x: left + thirds, width: thirds, color: 'rgba(252,211,77,0.05)' }, // mid
          { x: left + thirds * 2, width: thirds, color: 'rgba(239,68,68,0.05)' } // bad
        ];
        ctx.save();
        bands.forEach(b => {
          ctx.fillStyle = b.color;
          ctx.fillRect(b.x, top, b.width, height);
        });
        ctx.restore();
      }
    },
    scales: {
      x: { min: 0, max: 100, title: { display: true, text: 'Risk Score' } },
      y: { min: 0, max: 100, title: { display: true, text: 'Return Potential' } }
    }
  };

  return <ChartWrapper type="scatter" data={scatterData} options={options} chartRef={chartRef} title={title} height={300} />;
};

// Arrow Scatter (momentum)
export const RiskReturnArrowScatter = ({ data, title = "Risk vs Return (Arrows)" }) => {
  const chartRef = useRef();
  useEffect(() => () => cleanupChart(chartRef), []);
  useEffect(() => cleanupChart(chartRef), [data]);

  const scatterData = {
    datasets: [{
      label: 'Stocks',
      data: data?.map(d => ({ x: d.risk_score || 0, y: d.return_potential || 0 })) || [],
      pointStyle: 'triangle',
      rotation: 90,
      pointBackgroundColor: 'rgba(99,102,241,0.8)',
      pointRadius: 8,
    }]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      title: { display: true, text: title },
      legend: { display: false }
    },
    scales: {
      x: { min: 0, max: 100, title: { display: true, text: 'Risk' } },
      y: { min: 0, max: 100, title: { display: true, text: 'Return' } }
    }
  };

  return <ChartWrapper type="scatter" data={scatterData} options={options} chartRef={chartRef} title={title} height={300} />;
};

// Quadrant scatter chart
export const RiskReturnQuadrantChart = ({ data, title = "Risk vs Return (Quadrants)" }) => {
  const chartRef = useRef();
  useEffect(() => () => cleanupChart(chartRef), []);
  useEffect(() => cleanupChart(chartRef), [data]);

  const scatterData = {
    datasets: [{
      label: 'Stocks',
      data: data?.map(d => ({ x: d.risk_score || 0, y: d.return_potential || 0 })) || [],
      pointBackgroundColor: 'rgba(99,102,241,0.9)',
      pointRadius: 6,
    }]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      title: { display: true, text: title },
      legend: { display: false },
      beforeDraw: (chart) => {
        const { ctx, chartArea } = chart;
        if (!chartArea) return;
        const { left, top, width, height } = chartArea;
        const midX = left + width / 2;
        const midY = top + height / 2;
        const quadrants = [
          { x: left,   y: midY, w: width/2, h: height/2, color: 'rgba(16,185,129,0.06)' }, // top-left good
          { x: midX,   y: midY, w: width/2, h: height/2, color: 'rgba(245,158,11,0.06)' }, // top-right mid-high risk
          { x: left,   y: top,  w: width/2, h: height/2, color: 'rgba(234,179,8,0.06)' }, // bottom-left low everything
          { x: midX,   y: top,  w: width/2, h: height/2, color: 'rgba(239,68,68,0.06)' }  // bottom-right worst
        ];
        ctx.save();
        quadrants.forEach(q => {
          ctx.fillStyle = q.color;
          ctx.fillRect(q.x, q.y, q.w, q.h);
        });
        ctx.restore();
      }
    },
    scales: {
      x: { min: 0, max: 100, title: { display: true, text: 'Risk' } },
      y: { min: 0, max: 100, title: { display: true, text: 'Return' } }
    }
  };

  return <ChartWrapper type="scatter" data={scatterData} options={options} chartRef={chartRef} title={title} height={300} />;
};

// Animated Risk-Return Bubble Chart (Story Mode)
export const RiskReturnAnimatedChart = ({ frames = [], title = "Risk vs Return Over Time" }) => {
  const chartRef = useRef();

  // Use Plotly for easier animation
  useEffect(() => {
    return () => cleanupChart(chartRef);
  }, []);

  if (!frames || frames.length === 0) {
    return <p>No data</p>;
  }

  // Build Plotly frame structure
  const firstFrame = frames[0];
  const trace0 = {
    x: firstFrame.map(p => p.risk),
    y: firstFrame.map(p => p.return),
    mode: 'markers',
    marker: {
      size: firstFrame.map(p => Math.sqrt(p.market_cap || 1e9) / 1e3 + 5),
      color: 'rgba(59,130,246,0.8)'
    },
    text: firstFrame.map(p => p.symbol)
  };

  const plotFrames = frames.map((frameData, idx) => ({
    name: `frame${idx}`,
    data: [{
      x: frameData.map(p => p.risk),
      y: frameData.map(p => p.return),
      marker: {
        size: frameData.map(p => Math.sqrt(p.market_cap || 1e9) / 1e3 + 5)
      },
      text: frameData.map(p => p.symbol)
    }]
  }));

  const layout = {
    title,
    xaxis: { title: 'Risk', range: [0, 100] },
    yaxis: { title: 'Return', range: [0, 100] },
    updatemenus: [{
      type: 'buttons',
      x: 0.05,
      y: 1.15,
      buttons: [{
        label: 'Play',
        method: 'animate',
        args: [null, { fromcurrent: true, frame: { duration: 600, redraw: false }, transition: { duration: 0 } }]
      }]
    }]
  };

  const config = { responsive: true };

  return (
    <div style={{ width: '100%', height: '300px' }}>
      <PlotlyChart data={[trace0]} layout={layout} frames={plotFrames} config={config} />
    </div>
  );
};

// Violin + Strip chart using Plotly
export const RiskReturnViolinStripChart = ({ data = [], title = "Risk / Return Distribution" }) => {
  if (!Array.isArray(data) || data.length === 0) return <p>No data</p>;

  const riskValues = data.map(d => d.risk_score || 0);
  const returnValues = data.map(d => d.return_potential || 0);

  const plotData = [
    {
      type: 'violin',
      y: riskValues,
      name: 'Risk',
      box: { visible: true },
      meanline: { visible: true },
      points: 'all',
      jitter: 0.3,
      scalemode: 'width',
      fillcolor: 'rgba(99,102,241,0.6)'
    },
    {
      type: 'violin',
      y: returnValues,
      name: 'Return',
      box: { visible: true },
      meanline: { visible: true },
      points: 'all',
      jitter: 0.3,
      scalemode: 'width',
      fillcolor: 'rgba(16,185,129,0.6)'
    }
  ];

  const layout = {
    title,
    yaxis: { range: [0, 100] },
    violingap: 0.3,
    violingroupgap: 0.2,
    violinmode: 'group',
    height: 300,
    paper_bgcolor: 'transparent',
    plot_bgcolor: 'transparent'
  };

  return (
    <div style={{ width: '100%', height: '300px' }}>
      <PlotlyChart data={plotData} layout={layout} config={{ responsive: true }} />
    </div>
  );
};

// Gauge dials for each stock (risk needle, return band)
export const RiskReturnGaugeChart = ({ data = [], title = 'Risk Gauge Board' }) => {
  if (!Array.isArray(data) || data.length === 0) return <p>No data</p>;
  const colsBase=3;
  const rows=Math.ceil(data.length/colsBase);
  const width=1/colsBase;
  const traces=data.map((d,i)=>{
    const row=Math.floor(i/colsBase);
    const gaugesInRow = row===rows-1 ? data.length - row*colsBase : colsBase;
    const offset=(colsBase-gaugesInRow)*width/2;
    const colIndex=i%colsBase;
    const xStart=offset+colIndex*width;
    const xEnd = xStart+width;
    const yStart = 1 - (row+1)/rows;
    const yEnd = yStart + 1/rows;
    return {
      type:'indicator',mode:'gauge+number',value:d.risk_score||0,
      title:{text:d.symbol||`S${i+1}`,font:{color:'#e0e7ff'}},
      gauge:{axis:{range:[0,100],tickcolor:'#6b7280'},bar:{color:'rgba(99,102,241,1)'},steps:[{range:[0,100],color:'rgba(255,255,255,0.06)'}]},
      domain:{x:[xStart,xEnd],y:[yStart,yEnd]}
    };});
  const layout={title,height:rows*350,margin:{t:40},paper_bgcolor:'transparent',plot_bgcolor:'transparent',font:{color:'#e0e7ff'}};
  return <PlotlyChart data={traces} layout={layout} config={{responsive:true}} />;
};

// Waffle matrix 10x10
export const RiskReturnWaffleChart = ({ percentageGood=25,title='Risk Waffle' }) => {
  const total=100;const good=Math.round(total*percentageGood/100);
  const arr=[...Array(total)].map((_,i)=>({x:i%10,y:9-Math.floor(i/10),good:i<good}));
  const data=[{x:arr.map(a=>a.x),y:arr.map(a=>a.y),mode:'markers',marker:{symbol:'square',size:20,color:arr.map(a=>a.good?'rgba(16,185,129,0.8)':'rgba(239,68,68,0.3)')},hoverinfo:'skip'}];
  const layout={title,height:300,xaxis:{visible:false},yaxis:{visible:false},paper_bgcolor:'transparent',plot_bgcolor:'transparent'};
  return <PlotlyChart data={data} layout={layout} config={{responsive:true}} />;
};

// Parallel coordinates
export const RiskReturnParallelChart = ({ data=[], title='Risk vs Return Parallel' }) => {
  if(data.length===0) return <p>No data</p>;
  const trace={type:'parcoords',dimensions:[{label:'Risk',values:data.map(d=>d.risk_score||0)},{label:'Return',values:data.map(d=>d.return_potential||0)}],line:{color:'rgba(59,130,246,0.6)'}};
  const layout={title,height:300,paper_bgcolor:'transparent',plot_bgcolor:'transparent'};
  return <PlotlyChart data={[trace]} layout={layout} config={{responsive:true}} />;
};

// Swarm plot horizontally
export const RiskReturnSwarmChart = ({ data=[], title='Risk Swarm' }) => {
  if(data.length===0) return <p>No data</p>;
  const jittered=data.map(d=>({x:d.risk_score||0,y:(Math.random()-0.5)*0.5}));
  const trace={type:'scatter',mode:'markers',x:jittered.map(p=>p.x),y:jittered.map(p=>p.y),marker:{size:8,color:'rgba(99,102,241,0.8)'},hoverinfo:'x'};
  const layout={title,height:200,yaxis:{visible:false},xaxis:{range:[0,100],title:'Risk'},paper_bgcolor:'transparent',plot_bgcolor:'transparent'};
  return <PlotlyChart data={[trace]} layout={layout} config={{responsive:true}} />;
};

// Create a default export object with all chart components
const AdvancedCharts = {
  StockHeatmap,
  RiskReturnBubbleChart,
  MultiAxisFinancialChart,
  SectorRadarChart,
  TrendAnalysisChart,
  FinancialHealthGauge,
  SectorThermometerBarChart,
  SectorBullseyeChart,
  RiskReturnBandChart,
  RiskReturnArrowScatter,
  RiskReturnQuadrantChart,
  RiskReturnAnimatedChart,
  RiskReturnViolinStripChart,
  RiskReturnGaugeChart,
  RiskReturnWaffleChart,
  RiskReturnParallelChart,
  RiskReturnSwarmChart
};

export default AdvancedCharts; 