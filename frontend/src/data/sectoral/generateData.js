/**
 * Utility script to generate sectoral data from reports
 * This can be used to convert your report data into the required JSON format
 */

// Example function to convert report data to sectoral format
export const convertReportToSectoral = (reportData) => {
  const sectors = [];
  
  // Example structure - modify based on your actual report format
  reportData.forEach(sector => {
    const sectorData = {
      id: sector.id || sector.name.toLowerCase().replace(/\s+/g, '_'),
      name: sector.name,
      performance: parseFloat(sector.performance || 0),
      sentiment: parseFloat(sector.sentiment || 0),
      volume: parseInt(sector.volume || 0),
      market_cap: parseInt(sector.marketCap || 0),
      description: sector.description || `${sector.name} companies`,
      top_stocks: sector.stocks?.map(stock => ({
        symbol: stock.symbol,
        name: stock.name,
        price: parseFloat(stock.price || 0),
        change: parseFloat(stock.change || 0),
        sentiment: parseFloat(stock.sentiment || 0),
        volume: parseInt(stock.volume || 0),
        market_cap: parseInt(stock.marketCap || 0)
      })) || []
    };
    
    sectors.push(sectorData);
  });
  
  return {
    lastUpdated: new Date().toISOString(),
    timeframe: '1d', // Change as needed
    sectors,
    market_summary: {
      total_market_cap: sectors.reduce((sum, s) => sum + (s.market_cap || 0), 0),
      total_volume: sectors.reduce((sum, s) => sum + (s.volume || 0), 0),
      overall_sentiment: sectors.reduce((sum, s) => sum + (s.sentiment || 0), 0) / sectors.length,
      top_performer: sectors.sort((a, b) => (b.performance || 0) - (a.performance || 0))[0]?.name,
      worst_performer: sectors.sort((a, b) => (a.performance || 0) - (b.performance || 0))[0]?.name
    }
  };
};

// Example function to validate sectoral data
export const validateSectoralData = (data) => {
  const errors = [];
  
  if (!data.sectors || !Array.isArray(data.sectors)) {
    errors.push('Sectors must be an array');
  }
  
  if (!data.lastUpdated) {
    errors.push('lastUpdated is required');
  }
  
  if (!data.timeframe) {
    errors.push('timeframe is required');
  }
  
  data.sectors?.forEach((sector, index) => {
    if (!sector.id) errors.push(`Sector ${index}: id is required`);
    if (!sector.name) errors.push(`Sector ${index}: name is required`);
    if (typeof sector.performance !== 'number') errors.push(`Sector ${index}: performance must be a number`);
    if (typeof sector.sentiment !== 'number') errors.push(`Sector ${index}: sentiment must be a number`);
    
    sector.top_stocks?.forEach((stock, stockIndex) => {
      if (!stock.symbol) errors.push(`Sector ${index}, Stock ${stockIndex}: symbol is required`);
      if (!stock.name) errors.push(`Sector ${index}, Stock ${stockIndex}: name is required`);
    });
  });
  
  return {
    isValid: errors.length === 0,
    errors
  };
};

// Example function to generate sample data for testing
export const generateSampleData = () => {
  return {
    lastUpdated: new Date().toISOString(),
    timeframe: '1d',
    sectors: [
      {
        id: 'technology',
        name: 'Technology',
        performance: 2.45,
        sentiment: 0.72,
        volume: 1542000000,
        market_cap: 45000000000000,
        description: 'Software, hardware, and digital services companies',
        top_stocks: [
          {
            symbol: 'TCS',
            name: 'Tata Consultancy Services',
            price: 3850.50,
            change: 1.25,
            sentiment: 0.78,
            volume: 1250000,
            market_cap: 14500000000000
          }
        ]
      }
    ],
    market_summary: {
      total_market_cap: 45000000000000,
      total_volume: 1542000000,
      overall_sentiment: 0.72,
      top_performer: 'Technology',
      worst_performer: 'Technology'
    }
  };
};

// Usage example:
/*
import { convertReportToSectoral, validateSectoralData } from './generateData';

// Convert your report data
const reportData = [
  {
    name: 'Technology',
    performance: 2.45,
    sentiment: 0.72,
    volume: 1542000000,
    marketCap: 45000000000000,
    stocks: [
      {
        symbol: 'TCS',
        name: 'Tata Consultancy Services',
        price: 3850.50,
        change: 1.25,
        sentiment: 0.78,
        volume: 1250000,
        marketCap: 14500000000000
      }
    ]
  }
];

const sectoralData = convertReportToSectoral(reportData);
const validation = validateSectoralData(sectoralData);

if (validation.isValid) {
  console.log('Data is valid!');
  // Save to file or use in your app
} else {
  console.log('Validation errors:', validation.errors);
}
*/ 