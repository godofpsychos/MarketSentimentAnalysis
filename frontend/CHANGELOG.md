# Changelog

## [Latest] - Environment Variables and Data-Driven Scores

### Added
- Environment variable support for backend URL and other configuration
- Data-driven financial health score calculation
- Configuration file (`src/config/config.js`) to centralize environment variables

### Changed
- **Financial Health Score**: Now shows sector-specific score for selected stock instead of general market score
- **Backend URLs**: All hardcoded `http://localhost:5000` URLs now use environment variables
- **Configuration**: Added `.env` file support for easy configuration changes

### Technical Details
- Financial health score now shows the specific sector score for the selected stock
- Includes stock-to-sector mapping for common Indian stocks
- Falls back to market average if sector not found
- Dynamic sector data with time-based variation
- Default fallback score: 70

### Files Modified
- `src/components/Dashboard/Dashboard.js` - Added `calculateFinancialHealthScore()` function
- `src/config/config.js` - New configuration file
- All files with API calls - Updated to use environment variables
- `.gitignore` - Added `.env` to prevent committing sensitive data

### Environment Variables
Create a `.env` file in the frontend directory with:
```
REACT_APP_BACKEND_URL=http://localhost:5000
REACT_APP_API_BASE_URL=http://localhost:5000/api
# ... other variables as needed
``` 