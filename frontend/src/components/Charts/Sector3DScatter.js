import React from 'react';
import Plot from 'react-plotly.js';

// 3-D scatter chart to compare sectors without overlap
// X-axis → Profitability, Y-axis → Growth, Z-axis → Valuation
// Bubble size → Market-cap, Colour → Financial-health score
const Sector3DScatter = ({ data = [], title = 'Sector 3-D Comparison' }) => {
  // Guard against empty data
  if (!Array.isArray(data) || data.length === 0) {
    return (
      <div style={{ height: '300px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <p>No sector data available</p>
      </div>
    );
  }

  const trace = {
    type: 'scatter3d',
    mode: 'markers',
    x: data.map((d) => d.profitability || 0),
    y: data.map((d) => d.growth || 0),
    z: data.map((d) => d.valuation || 0),
    text: data.map((d) => d.name),
    marker: {
      size: data.map((d) => Math.sqrt((d.market_cap || 1) / 1e12) * 5 + 5), // Scale size by market-cap
      color: data.map((d) => d.financial_health || 0),
      colorscale: 'Viridis',
      showscale: true,
      opacity: 0.9,
    },
  };

  const layout = {
    title,
    autosize: true,
    margin: { l: 0, r: 0, b: 0, t: 40 },
    scene: {
      xaxis: { title: 'Profitability' },
      yaxis: { title: 'Growth' },
      zaxis: { title: 'Valuation' },
    },
  };

  return (
    <div style={{ width: '100%', height: '100%', minHeight: '300px' }}>
      <Plot data={[trace]} layout={layout} style={{ width: '100%', height: '100%' }} />
    </div>
  );
};

export default Sector3DScatter; 