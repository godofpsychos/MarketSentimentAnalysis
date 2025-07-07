# Market Sentiment Analysis - Setup Guide

Complete setup guide for the Market Sentiment Analysis project with all dependencies and configuration.

## 🚀 Quick Start

### 1. Clone and Setup
```bash
# Clone the repository
git clone <your-repo-url>
cd MarketSentimentAnalysis

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 2. Install Dependencies

#### Option A: Full Installation (Recommended)
```bash
pip install -r requirements.txt
```

#### Option B: Minimal Installation (Production)
```bash
pip install -r requirements-minimal.txt
```

#### Option C: Development Installation
```bash
pip install -r requirements-dev.txt
```

### 3. Environment Setup
```bash
# Copy environment templates
cp backend.env .env
cp frontend/.env.example frontend/.env

# Edit environment files
nano .env
nano frontend/.env
```

### 4. Start the Application
```bash
# Start backend
python wsgi.py

# In another terminal, start frontend
cd frontend
npm start
```

## 📦 Requirements Files

### `requirements.txt` - Full Production
Complete dependencies for all features:
- **Web Framework**: Flask, Gunicorn
- **Data Processing**: Pandas, NumPy, yfinance
- **Authentication**: PyJWT, bcrypt
- **Web Scraping**: BeautifulSoup, feedparser, bsescraper
- **Visualization**: Matplotlib, Seaborn
- **News & Content**: gnews, newspaper3k
- **Testing**: pytest, pytest-cov

### `requirements-minimal.txt` - Minimal Production
Essential dependencies only:
- Core web framework
- Data processing
- Authentication
- Basic web scraping
- Utilities

### `requirements-dev.txt` - Development
Includes all production dependencies plus:
- **Code Quality**: black, flake8, isort, mypy
- **Testing**: pytest with additional plugins
- **Documentation**: Sphinx
- **Security**: bandit, safety
- **Jupyter**: For data analysis notebooks
- **Debugging**: ipdb

## 🔧 Environment Configuration

### Backend Environment (`.env`)
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
VALUATION_FILE=/home/tarun/MarketSentimentAnalysis/FundamentalAnalysis/outputs/valuation/basic_valuation_ratios.json
GROWTH_FILE=/home/tarun/MarketSentimentAnalysis/FundamentalAnalysis/outputs/growth/revenue_growth.json
LIQUIDITY_FILE=/home/tarun/MarketSentimentAnalysis/FundamentalAnalysis/outputs/liquidity/basic_liquidity_ratios.json
CCC_FILE=/home/tarun/MarketSentimentAnalysis/FundamentalAnalysis/outputs/liquidity/cash_conversion_cycle.json

# Report and data files
REPORT_CSV_PATH=/home/tarun/MarketSentimentAnalysis/report.csv
STOCKS_LIST_PATH=/home/tarun/MarketSentimentAnalysis/stocksList.csv

# News and sentiment files
NEWS_JSON_PATH=/home/tarun/MarketSentimentAnalysis/news.json
RECENT_NEWS_PATH=/home/tarun/MarketSentimentAnalysis/insightGen/recent_news.json
SENTIMENT_RESULTS_PATH=/home/tarun/MarketSentimentAnalysis/Sentiment_Analysis/sentiment_analysis_results.json

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Google OAuth Configuration
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:3000/auth/google/callback

# Server Configuration
HOST=0.0.0.0
PORT=5000
DEBUG=False

# Logging
LOG_LEVEL=info
LOG_FILE=logs/backend.log
ACCESS_LOG_FILE=logs/access.log
ERROR_LOG_FILE=logs/error.log
```

### Frontend Environment (`frontend/.env`)
```bash
# Backend API Configuration
REACT_APP_BACKEND_URL=http://localhost:5000
REACT_APP_API_BASE_URL=http://localhost:5000/api

# Application Configuration
REACT_APP_APP_NAME=Market Sentiment Analysis
REACT_APP_VERSION=1.0.0

# Feature Flags
REACT_APP_ENABLE_ANALYTICS=true
REACT_APP_ENABLE_MOCK_DATA=false

# Chart Configuration
REACT_APP_CHART_ANIMATION_DURATION=1000
REACT_APP_CHART_UPDATE_INTERVAL=30000

# Authentication Configuration
REACT_APP_GOOGLE_CLIENT_ID=your_google_client_id_here
REACT_APP_AUTH_REDIRECT_URL=http://localhost:3000/auth/callback
```

## 🏃‍♂️ Running the Application

### Development Mode
```bash
# Terminal 1: Backend
python wsgi.py

# Terminal 2: Frontend
cd frontend
npm start
```

### Production Mode
```bash
# Backend with Gunicorn
./start_backend.sh

# Frontend build
cd frontend
npm run build
```

### Systemd Service (Production)
```bash
# Install systemd service
sudo cp systemd/market-sentiment-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable market-sentiment-api
sudo systemctl start market-sentiment-api
```

## 🧪 Testing

### Backend Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest test_setup.py
```

### Frontend Tests
```bash
cd frontend
npm test
```

### API Testing
```bash
# Test backend API
curl http://localhost:5000/api/stocks
curl http://localhost:5000/api/sentiment
curl http://localhost:5000/api/fundamental-scores/TCS
```

## 🔍 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Reinstall requirements
   pip install -r requirements.txt --force-reinstall
   ```

2. **Permission Errors**
   ```bash
   # Fix permissions
   chmod +x start_backend.sh
   chmod 755 logs/
   ```

3. **Port Already in Use**
   ```bash
   # Find and kill process
   sudo lsof -i :5000
   sudo kill -9 <PID>
   ```

4. **Database Errors**
   ```bash
   # Check database paths in .env
   # Ensure directories exist
   mkdir -p db Sentiment_Analysis
   ```

### Validation Script
```bash
# Test environment setup
python -c "
import os
from dotenv import load_dotenv
load_dotenv()

print('✅ Environment loaded')
print('BASE_DIR:', os.getenv('BASE_DIR'))
print('Flask version:', __import__('flask').__version__)
print('Pandas version:', __import__('pandas').__version__)
"
```

## 📊 Dependencies Overview

### Core Dependencies
- **Flask 3.1.1** - Web framework
- **Pandas 2.3.0** - Data manipulation
- **NumPy 2.3.0** - Numerical computing
- **yfinance 0.2.63** - Stock data
- **PyJWT 2.10.1** - Authentication
- **bcrypt 4.3.0** - Password hashing

### Web Scraping
- **BeautifulSoup 4.13.4** - HTML parsing
- **feedparser 6.0.11** - RSS feeds
- **bsescraper 1.0.6** - BSE data

### Data Visualization
- **Matplotlib 3.10.3** - Plotting
- **Seaborn 0.13.2** - Statistical plots

### Development Tools
- **pytest 8.0.0** - Testing
- **black 24.1.1** - Code formatting
- **flake8 7.0.0** - Linting
- **mypy 1.8.0** - Type checking

## 🔒 Security Notes

1. **Environment Files**: Never commit `.env` files
2. **Secrets**: Change default JWT secrets
3. **Dependencies**: Regular security updates
4. **Permissions**: Restrict file access

## 📈 Performance Tips

1. **Use minimal requirements** for production
2. **Enable caching** for API responses
3. **Optimize database queries**
4. **Use CDN** for static assets
5. **Monitor memory usage**

## 🆘 Support

- Check `ENVIRONMENT_SETUP.md` for detailed environment configuration
- Check `README_BACKEND.md` for backend deployment
- Check `CHANGELOG.md` for recent changes 