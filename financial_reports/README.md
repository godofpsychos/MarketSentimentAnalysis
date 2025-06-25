# Financial Reports Pipeline

A complete pipeline to fetch, process, and store historical financial data for Indian stocks using yfinance.

## 🚀 Quick Start

1. **Activate your virtual environment:**
   ```bash
   source .venv/bin/activate
   ```

2. **Run the complete pipeline:**
   ```bash
   chmod +x financial_reports/run.sh
   ./financial_reports/run.sh
   ```

## 📁 Project Structure

```
financial_reports/
├── run.sh                    # Main pipeline script
├── fetch_financial_data.py   # Fetches data from yfinance
├── database.py              # Creates SQLite database and imports data
├── query_database.py        # Interactive query tool
├── test_data.py            # Test script for specific companies
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── data/                  # JSON files for each stock
│   ├── RELIANCE_financial_data.json
│   ├── TCS_financial_data.json
│   └── ...
├── financial_data.db      # SQLite database
└── *.log                 # Log files
```

## 🔧 Individual Components

### 1. Data Fetching (`fetch_financial_data.py`)
- Reads stock symbols from `stocksList.csv`
- Fetches ALL available historical data from yfinance:
  - Annual & Quarterly Financial Statements
  - Historical Stock Prices (multiple periods)
  - Dividend History
  - Stock Split History
  - Company Information
  - Valuation Metrics
  - Financial Health Indicators
- Saves individual JSON files for each stock
- Formats currency in Indian format (₹ Crores, Lakhs)

### 2. Database Import (`database.py`)
- Creates comprehensive SQLite database schema
- Imports all JSON files into structured tables
- Handles data type conversions and relationships
- Provides data integrity and fast querying

### 3. Query Tool (`query_database.py`)
- Interactive command-line tool to explore data
- Pre-built queries for common use cases
- Support for custom SQL queries
- Easy company analysis and comparisons

### 4. Testing (`test_data.py`)
- Verify data integrity for specific companies
- Check both JSON and database data
- Quick validation of pipeline results

## 🗃️ Database Schema

The database contains 13 tables:

### Core Tables:
- **companies** - Basic company information
- **annual_income_statements** - Annual income statement data
- **quarterly_income_statements** - Quarterly income statement data
- **annual_balance_sheets** - Annual balance sheet data
- **quarterly_balance_sheets** - Quarterly balance sheet data
- **annual_cash_flows** - Annual cash flow data
- **quarterly_cash_flows** - Quarterly cash flow data

### Market Data:
- **historical_prices** - Stock price history
- **dividends** - Dividend payment history
- **stock_splits** - Stock split history

### Analysis Tables:
- **valuation_metrics** - P/E ratios, P/B ratios, etc.
- **financial_health** - ROE, ROA, debt ratios, margins
- **earnings** - Annual earnings data

## 💡 Usage Examples

### Run Complete Pipeline:
```bash
./financial_reports/run.sh
```

### Fetch Data Only:
```bash
python3 financial_reports/fetch_financial_data.py
```

### Import to Database Only:
```bash
python3 financial_reports/database.py
```

### Query Database:
```bash
python3 financial_reports/query_database.py
```

### Test Specific Company:
```bash
python3 financial_reports/test_data.py RELIANCE
```

## 🔍 Query Examples

Using the interactive query tool:

```bash
python3 financial_reports/query_database.py
```

Available commands:
- `companies 10` - Show top 10 companies by market cap
- `details RELIANCE` - Show detailed info for Reliance
- `revenue RELIANCE 5` - Show revenue trends for last 5 periods
- `stats` - Show database statistics
- `sql SELECT * FROM companies LIMIT 5` - Custom SQL query

## 📊 Data Coverage

For each stock, the pipeline fetches:

- **Financial Statements**: 4-10+ years of annual data, 4-20+ quarters
- **Stock Prices**: Multiple time periods (max, 5y, 2y, 1y)
- **Dividends**: Complete dividend history
- **Corporate Actions**: Stock splits and other actions
- **Market Metrics**: Real-time valuation ratios
- **Company Info**: Sector, industry, employees, business summary

## 🛠️ Dependencies

- Python 3.8+
- yfinance >= 0.2.18
- pandas >= 2.0.0
- numpy >= 1.24.0
- requests >= 2.28.0

## 📋 Requirements

1. Virtual environment activated
2. `stocksList.csv` in project root with SYMBOL column
3. Internet connection for yfinance API
4. Sufficient disk space for JSON files and database

## 🔧 Configuration

The pipeline uses these default settings:
- **Concurrent workers**: 3 (to avoid API rate limits)
- **API delay**: 0.3 seconds between requests
- **Price periods**: max, 5y, 2y, 1y
- **Currency format**: Indian (₹ Crores, Lakhs)

## 📝 Logs

All operations are logged to:
- `financial_reports/fetch_financial_data.log`
- `financial_reports/database_import.log`

## 🚨 Troubleshooting

### Common Issues:

1. **Not in virtual environment**
   ```bash
   source .venv/bin/activate
   ```

2. **Missing stocksList.csv**
   - Ensure file exists in project root
   - Check SYMBOL column format

3. **API rate limits**
   - Pipeline includes delays to avoid rate limits
   - Reduce concurrent workers if needed

4. **Database locked**
   - Close any existing connections
   - Restart the import process

### Performance Tips:

- Run during off-peak hours for better API response
- Ensure stable internet connection
- Monitor disk space for large datasets

## 🎯 Output

After successful completion:
- ✅ Individual JSON files for each stock
- ✅ Complete SQLite database ready for analysis
- ✅ Interactive query tool available
- ✅ Comprehensive logs for debugging

## 🔄 Updating Data

To refresh data:
1. Delete old JSON files: `rm -rf financial_reports/data/*`
2. Delete database: `rm financial_reports/financial_data.db`
3. Run pipeline again: `./financial_reports/run.sh`

---

**Note**: This pipeline fetches data from Yahoo Finance and is subject to their terms of service and rate limits. Use responsibly for educational and research purposes. 