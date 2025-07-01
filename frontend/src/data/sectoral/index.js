// Export the main data service
export { default as sectoralDataService } from './sectoralDataService';

// Export data files for direct access if needed
export { default as sectorsData } from './sectors.json';
export { default as sectorsData1W } from './sectors-1w.json';

// Export utility functions
export const formatCurrency = (amount) => {
  if (amount >= 1e12) {
    return `₹${(amount / 1e12).toFixed(2)}T`;
  } else if (amount >= 1e9) {
    return `₹${(amount / 1e9).toFixed(2)}B`;
  } else if (amount >= 1e6) {
    return `₹${(amount / 1e6).toFixed(2)}M`;
  } else if (amount >= 1e3) {
    return `₹${(amount / 1e3).toFixed(2)}K`;
  }
  return `₹${amount.toFixed(2)}`;
};

export const formatVolume = (volume) => {
  if (volume >= 1e9) {
    return `${(volume / 1e9).toFixed(2)}B`;
  } else if (volume >= 1e6) {
    return `${(volume / 1e6).toFixed(2)}M`;
  } else if (volume >= 1e3) {
    return `${(volume / 1e3).toFixed(2)}K`;
  }
  return volume.toString();
};

export const getSentimentColor = (sentiment) => {
  if (sentiment >= 0.7) return '#10B981'; // Green for positive
  if (sentiment >= 0.5) return '#F59E0B'; // Yellow for neutral
  return '#EF4444'; // Red for negative
};

export const getPerformanceColor = (performance) => {
  if (performance > 0) return '#10B981'; // Green for positive
  if (performance < 0) return '#EF4444'; // Red for negative
  return '#6B7280'; // Gray for neutral
};

export const getSentimentLabel = (sentiment) => {
  if (sentiment >= 0.8) return 'Very Bullish';
  if (sentiment >= 0.6) return 'Bullish';
  if (sentiment >= 0.4) return 'Neutral';
  if (sentiment >= 0.2) return 'Bearish';
  return 'Very Bearish';
};

// Export data generation utilities
export { 
  convertReportToSectoral, 
  validateSectoralData, 
  generateSampleData 
} from './generateData'; 