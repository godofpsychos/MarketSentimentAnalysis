# Corporate Announcements Scraper

This module provides comprehensive corporate announcements data from both BSE (Bombay Stock Exchange) and NSE (National Stock Exchange) in India.

## Features

- **BSE Announcements**: Uses `bsescraper` library to fetch detailed corporate announcements
- **NSE Announcements**: Uses RSS feeds and API calls to get real-time announcements
- **Combined Data**: Merges data from both exchanges for comprehensive coverage
- **Keyword Filtering**: Search announcements by specific keywords
- **Corporate Actions**: Track dividends, bonuses, splits, and other corporate actions
- **Multiple Formats**: Save data as JSON, CSV, and generate summary reports

## Installation

1. Install required packages:
```bash
pip install -r requirements.txt
```

2. Or install individually:
```bash
pip install bsescraper feedparser requests pandas beautifulsoup4 lxml
```

## Quick Start

```python
from combined_announcements import CombinedAnnouncements

# Initialize scraper
scraper = CombinedAnnouncements()

# Get TCS announcements from both exchanges
tcs_data = scraper.get_company_announcements(
    bse_code=532540,
    nse_symbol='TCS',
    company_name='TCS',
    days_back=30
)

print(f"Total announcements: {tcs_data['combined_count']}")

# Save data
scraper.save_combined_data(tcs_data, 'tcs_announcements')
scraper.close()
```

## Testing Setup

Run the test script to verify installation:
```bash
python test_setup.py
```

## Available Scripts

- `bse_announcements.py` - BSE only scraper
- `nse_announcements.py` - NSE only scraper  
- `combined_announcements.py` - Combined scraper (recommended)
- `test_setup.py` - Setup verification

## Common Company Codes

| Company | BSE Code | NSE Symbol |
|---------|----------|------------|
| TCS | 532540 | TCS |
| HDFC Bank | 500180 | HDFCBANK |
| Reliance | 500325 | RELIANCE |
| Infosys | 500209 | INFY |
| ICICI Bank | 532174 | ICICIBANK |

## Legal Notice

This tool is for educational and research purposes only. Respect the terms of service of BSE and NSE websites. 