import sectorsData from './sectors.json';
import sectorsData1W from './sectors-1w.json';

class SectoralDataService {
  constructor() {
    this.data = null;
    this.lastUpdated = null;
    this.currentTimeframe = '1d';
  }

  // Load sectoral data from JSON file
  async loadSectoralData(timeframe = '1d') {
    try {
      this.currentTimeframe = timeframe;
      
      // Select appropriate data file based on timeframe
      let dataFile;
      switch(timeframe) {
        case '1d':
          dataFile = sectorsData;
          break;
        case '1w':
          dataFile = sectorsData1W;
          break;
        case '1m':
        case '3m':
          // For now, use 1d data for other timeframes
          // In the future, you can add more JSON files
          dataFile = sectorsData;
          console.log(`Using 1d data for ${timeframe} timeframe`);
          break;
        default:
          dataFile = sectorsData;
      }
      
      this.data = dataFile;
      this.lastUpdated = new Date(this.data.lastUpdated);
      
      return this.data;
    } catch (error) {
      console.error('Error loading sectoral data:', error);
      throw error;
    }
  }

  // Get all sectors
  getSectors() {
    return this.data?.sectors || [];
  }

  // Get a specific sector by ID
  getSectorById(sectorId) {
    return this.data?.sectors?.find(sector => sector.id === sectorId) || null;
  }

  // Get top performing sectors
  getTopPerformers(limit = 3) {
    if (!this.data?.sectors) return [];
    
    return this.data.sectors
      .sort((a, b) => (b.performance || 0) - (a.performance || 0))
      .slice(0, limit);
  }

  // Get worst performing sectors
  getWorstPerformers(limit = 3) {
    if (!this.data?.sectors) return [];
    
    return this.data.sectors
      .sort((a, b) => (a.performance || 0) - (b.performance || 0))
      .slice(0, limit);
  }

  // Get sectors by sentiment range
  getSectorsBySentiment(minSentiment = 0, maxSentiment = 1) {
    if (!this.data?.sectors) return [];
    
    return this.data.sectors.filter(sector => {
      const sentiment = sector.sentiment || 0;
      return sentiment >= minSentiment && sentiment <= maxSentiment;
    });
  }

  // Get market summary
  getMarketSummary() {
    return this.data?.market_summary || null;
  }

  // Get all stocks across all sectors
  getAllStocks() {
    if (!this.data?.sectors) return [];
    
    return this.data.sectors.flatMap(sector => 
      (sector.top_stocks || []).map(stock => ({
        ...stock,
        sector: sector.name,
        sectorId: sector.id
      }))
    );
  }

  // Get top stocks across all sectors
  getTopStocks(limit = 10) {
    const allStocks = this.getAllStocks();
    
    return allStocks
      .sort((a, b) => (b.change || 0) - (a.change || 0))
      .slice(0, limit);
  }

  // Get stocks by sector
  getStocksBySector(sectorId) {
    const sector = this.getSectorById(sectorId);
    return sector?.top_stocks || [];
  }

  // Get data freshness info
  getDataInfo() {
    return {
      lastUpdated: this.lastUpdated,
      timeframe: this.currentTimeframe,
      totalSectors: this.data?.sectors?.length || 0,
      totalStocks: this.getAllStocks().length
    };
  }

  // Get current timeframe
  getCurrentTimeframe() {
    return this.currentTimeframe;
  }

  // Update data (for future use when connecting to real API)
  async updateData() {
    try {
      // This would fetch fresh data from your API
      const response = await fetch('http://localhost:5000/api/sectoral-analysis');
      if (response.ok) {
        const freshData = await response.json();
        this.data = freshData;
        this.lastUpdated = new Date();
        return this.data;
      }
    } catch (error) {
      console.error('Error updating sectoral data:', error);
      // Fallback to local data
      return this.data;
    }
  }

  // Get available timeframes
  getAvailableTimeframes() {
    return [
      { value: '1d', label: '1 Day' },
      { value: '1w', label: '1 Week' },
      { value: '1m', label: '1 Month' },
      { value: '3m', label: '3 Months' }
    ];
  }
}

// Create a singleton instance
const sectoralDataService = new SectoralDataService();

export default sectoralDataService; 