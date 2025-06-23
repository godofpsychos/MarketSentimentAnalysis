# Corporate Actions Scraper

This system scrapes corporate actions (like dividends, bonuses, splits, etc.) for all stocks listed in your `stocksList.csv` file.

## What Was Done ✅

1. **Removed all testing files** from the corporate_announcements directory
2. **Created a new scraper** that reads stocks from `stocksList.csv`
3. **Scrapes corporate actions** for the last 7 days for all 51 stocks
4. **Saves results** in JSON format with timestamps

## How to Use

### Quick Start (Recommended)
```bash
# Make sure you're in the project directory and virtual environment is active
source .venv/bin/activate

# Run the scraper (simple way)
python run_corporate_scraper.py
```

### Advanced Usage
```bash
# Run from corporate_announcements directory
cd corporate_announcements
python scrape_stocks_from_csv.py
```

## Output Files

The scraper creates two files in the `corporate_announcements/` directory:

1. **Detailed Results**: `stock_corporate_actions_YYYYMMDD_HHMMSS.json`
   - Complete data for all stocks
   - Individual BSE and NSE announcements
   - Full corporate action details

2. **Summary**: `stock_corporate_actions_summary_YYYYMMDD_HHMMSS.json`
   - Quick overview of results
   - Stock count and announcement statistics
   - List of all processed stocks

## What It Scrapes

The system looks for these types of corporate actions:
- 📈 **Dividends** - Cash distributions to shareholders
- 🎁 **Bonus Issues** - Free shares given to existing shareholders
- ✂️ **Stock Splits** - Division of existing shares
- 💰 **Rights Issues** - New shares offered to existing shareholders
- 🔄 **Buybacks** - Company repurchasing its own shares
- 🤝 **Mergers & Demergers** - Company restructuring
- 🌟 **Spin-offs** - Creation of new independent companies
- 📋 **Allotments** - Assignment of new shares

## Stock Coverage

Currently processes **51 stocks** from your `stocksList.csv`:
- All major Nifty 50 companies
- Includes both BSE and NSE data where available
- Covers all major sectors (Banking, IT, Pharma, Auto, etc.)

## Data Sources

- **BSE (Bombay Stock Exchange)**: Direct company-specific scraping
- **NSE (National Stock Exchange)**: RSS feeds (currently experiencing 404 errors)

## Logs

Check the log file for detailed execution information:
- `corporate_announcements/stock_scraper.log`

## Customization

To change the scraping period, edit the `days_back` parameter:
```python
# In run_corporate_scraper.py or scrape_stocks_from_csv.py
results = scraper.run_scraping(days_back=14, save_results=True)  # 14 days instead of 7
```

## Notes

- The system is designed to handle RSS feed outages gracefully
- BSE scraping is more reliable than NSE RSS feeds
- All 51 stocks from your CSV are processed automatically
- Results are timestamped to avoid overwriting previous runs

## Example Output

```
🚀 Corporate Actions Scraper for Market Sentiment Analysis
============================================================
📅 Started at: 2025-06-23 02:46:58
📊 Reading stocks from: stocksList.csv
🔍 Scraping period: Last 7 days
============================================================

🎉 SCRAPING COMPLETED SUCCESSFULLY!
📁 Output files created in corporate_announcements/ directory:
   📄 Detailed: stock_corporate_actions_20250623_024659.json
   📋 Summary: stock_corporate_actions_summary_20250623_024659.json

📈 RESULTS SUMMARY:
   📊 Total stocks processed: 51
   🏢 Stocks with announcements: 0
   📢 Total announcements: 0
   🏦 BSE announcements: 0
   🏛️  NSE announcements: 0

🏁 Finished at: 2025-06-23 02:46:59
```

---

**Note**: If NSE RSS feeds return 404 errors, this is a temporary issue with their servers. The BSE scraper will continue to work normally. 