import React from 'react';
import './SectorTileMap.css';

const defaultIconMap = {
  Technology: '💻',
  Healthcare: '🏥',
  Finance: '🏦',
  Energy: '⚡',
  'Consumer Goods': '🛍️',
  'Real Estate': '🏘️',
  default: '📊'
};

const getColor = (value) => {
  if (value > 75) return 'rgba(16, 185, 129, 0.8)'; // green
  if (value > 50) return 'rgba(234, 179, 8, 0.8)'; // yellow
  if (value > 25) return 'rgba(245, 158, 11, 0.8)'; // orange
  return 'rgba(239, 68, 68, 0.8)'; // red
};

const SectorTileMap = ({ data = [], iconMap = defaultIconMap, title = 'Sector Tiles' }) => {
  if (!Array.isArray(data) || data.length === 0) {
    return <p>No data available</p>;
  }

  return (
    <div className="sector-tile-map-wrapper">
      <h4 className="tile-map-title">{title}</h4>
      <div className="sector-tile-grid">
        {data.map((sector, idx) => {
          const score = sector.performance_score || sector.score || 0;
          const bg = getColor(score);
          const icon = iconMap[sector.name] || iconMap.default;
          return (
            <div key={idx} className="sector-tile" style={{ background: bg }}>
              <span className="tile-icon" role="img" aria-label={sector.name}>{icon}</span>
              <span className="tile-name">{sector.name}</span>
              <span className="tile-score">{score.toFixed(0)}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default SectorTileMap; 