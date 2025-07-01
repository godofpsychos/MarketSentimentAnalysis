# Sectoral Analysis Data

This folder contains all the data and services for sectoral analysis functionality.

## Structure

```
sectoral/
├── sectors.json          # Main sectoral data (1-day timeframe)
├── sectors-1w.json       # 1-week timeframe data
├── sectoralDataService.js # Data service for managing sectoral data
├── index.js              # Exports and utility functions
└── README.md             # This file
```

## Data Format

### Sector Object
```json
{
  "id": "technology",
  "name": "Technology",
  "performance": 2.45,
  "sentiment": 0.72,
  "volume": 1542000000,
  "market_cap": 45000000000000,
  "description": "Software, hardware, and digital services companies",
  "top_stocks": [...]
}
```

### Stock Object
```json
{
  "symbol": "TCS",
  "name": "Tata Consultancy Services",
  "price": 3850.50,
  "change": 1.25,
  "sentiment": 0.78,
  "volume": 1250000,
  "market_cap": 14500000000000
}
```

## Usage

### Basic Usage
```javascript
import { sectoralDataService } from '../../data/sectoral';

// Load data
const data = await sectoralDataService.loadSectoralData('1d');

// Get all sectors
const sectors = sectoralDataService.getSectors();

// Get specific sector
const techSector = sectoralDataService.getSectorById('technology');

// Get top performers
const topPerformers = sectoralDataService.getTopPerformers(3);
```

### Utility Functions
```javascript
import { 
  formatCurrency, 
  formatVolume, 
  getSentimentColor, 
  getPerformanceColor,
  getSentimentLabel 
} from '../../data/sectoral';

// Format large numbers
formatCurrency(45000000000000); // "₹45.00T"
formatVolume(1542000000); // "1.54B"

// Get colors for sentiment/performance
getSentimentColor(0.75); // "#10B981" (green)
getPerformanceColor(-1.25); // "#EF4444" (red)

// Get sentiment labels
getSentimentLabel(0.75); // "Bullish"
```

## Adding New Data

1. **Create new timeframe data**: Copy an existing JSON file and modify the data
2. **Update the service**: Add the new timeframe to the `loadSectoralData` method
3. **Export in index.js**: Add the new data file to the exports

### Example: Adding 1-month data
```javascript
// In sectoralDataService.js
async loadSectoralData(timeframe = '1d') {
  let dataFile;
  switch(timeframe) {
    case '1d':
      dataFile = sectorsData;
      break;
    case '1w':
      dataFile = sectorsData1W;
      break;
    case '1m':
      dataFile = sectorsData1M; // New data file
      break;
    default:
      dataFile = sectorsData;
  }
  // ... rest of the method
}
```

## Data Sources

Currently, the data is static JSON files. In a production environment, you would:

1. **Connect to real APIs**: Update the `updateData()` method to fetch from your backend
2. **Real-time updates**: Implement WebSocket connections for live data
3. **Data validation**: Add schema validation for incoming data
4. **Caching**: Implement caching strategies for better performance

## Performance Considerations

- The data service uses a singleton pattern to avoid multiple data loads
- Data is loaded once and cached in memory
- Utility functions are optimized for large number formatting
- Consider implementing data pagination for large datasets

## Future Enhancements

- [ ] Add more timeframes (1m, 3m, 6m, 1y)
- [ ] Implement real-time data fetching
- [ ] Add data validation schemas
- [ ] Create data visualization helpers
- [ ] Add sector comparison tools
- [ ] Implement data export functionality 