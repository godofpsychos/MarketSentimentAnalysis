# Changelog

## [Latest] - Environment Variables and Data-Driven Scores

### Added
- Environment variable support for backend URL and other configuration
- Data-driven financial health score calculation
- Configuration file (`src/config/config.js`) to centralize environment variables
- **Complete environment variable setup for all backend paths and configuration**
- **WSGI production deployment with Gunicorn**
- **Comprehensive environment documentation**
- **Complete requirements management with multiple requirement files**
- **Development and production dependency separation**

### Changed
- **Financial Health Score**: Now shows sector-specific score for selected stock instead of general market score
- **Backend URLs**: All hardcoded `http://localhost:5000` URLs now use environment variables
- **Configuration**: Added `.env` file support for easy configuration changes
- **All hardcoded paths**: Moved to environment variables for flexibility and portability
- **JWT and OAuth configuration**: Now configurable via environment variables

### Technical Details
- Financial health score now shows the specific sector score for the selected stock
- Includes stock-to-sector mapping for common Indian stocks
- Falls back to market average if sector not found
- Dynamic sector data with time-based variation
- Default fallback score: 70
- **All backend paths now configurable via environment variables:**
  - Base directory
  - Database paths
  - Fundamental analysis paths
  - Report and data files
  - News and sentiment files
  - JWT configuration
  - Google OAuth settings
  - Server configuration
  - Logging settings

### Files Modified
- `src/components/Dashboard/Dashboard.js` - Added `calculateFinancialHealthScore()` function
- `src/config/config.js` - New configuration file
- All files with API calls - Updated to use environment variables
- `.gitignore` - Added `.env` to prevent committing sensitive data
- **`backend_api.py` - Complete environment variable integration**
- **`wsgi.py` - WSGI entry point**
- **`gunicorn.conf.py` - Production server configuration**
- **`start_backend.sh` - Automated startup script**
- **`backend.env` - Environment variables template**
- **`systemd/market-sentiment-api.service` - Systemd service file**

### New Files Created
- **`ENVIRONMENT_SETUP.md` - Comprehensive environment setup guide**
- **`README_BACKEND.md` - Backend deployment documentation**
- **`SETUP_GUIDE.md` - Complete project setup guide**
- **`requirements.txt` - Full production dependencies**
- **`requirements-minimal.txt` - Minimal production dependencies**
- **`requirements-dev.txt` - Development dependencies**

### Environment Variables
Create a `.env` file in the frontend directory with:
```
REACT_APP_BACKEND_URL=http://localhost:5000
REACT_APP_API_BASE_URL=http://localhost:5000/api
# ... other variables as needed
```

**Backend environment variables (copy from `backend.env`):**
```bash
# Base Directory Configuration
BASE_DIR=/home/tarun/MarketSentimentAnalysis
DEVELOPMENT_MODE=True

# Database paths
SENTIMENT_DB_PATH=/home/tarun/MarketSentimentAnalysis/Sentiment_Analysis/sentiment_analysis.db
AUTH_DB_PATH=/home/tarun/MarketSentimentAnalysis/db/auth.db

# Fundamental Analysis paths
FUNDAMENTAL_BASE_DIR=/home/tarun/MarketSentimentAnalysis/FundamentalAnalysis
PROFITABILITY_FILE=/home/tarun/MarketSentimentAnalysis/FundamentalAnalysis/outputs/profitability/profitability_ratios.json
# ... and many more configurable paths
```

### Production Deployment
- **WSGI server**: Gunicorn with optimized configuration
- **Systemd service**: Automatic startup and restart
- **Environment-based configuration**: Easy deployment across environments
- **Logging**: Separate access and error logs
- **Security**: Configurable JWT secrets and OAuth settings

### Dependencies Management
- **`requirements.txt`**: Complete production dependencies (Flask, Pandas, yfinance, etc.)
- **`requirements-minimal.txt`**: Essential dependencies for lightweight deployment
- **`requirements-dev.txt`**: Development tools (testing, linting, documentation)
- **Version pinning**: All dependencies have specific versions for reproducibility
- **Categorized dependencies**: Organized by functionality (web, data, auth, etc.) 