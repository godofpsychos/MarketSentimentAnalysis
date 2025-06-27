# Fundamental Analysis Tools

This directory contains individual Python scripts for calculating various fundamental analysis indicators.

## Directory Structure

```
FundamentalAnalysis/
├── README.md
├── indicators/
│   ├── profitability_indicators.py     # ROE, ROA, Profit Margins, DuPont Analysis
│   ├── valuation_indicators.py         # P/E, P/B, P/S, EV/EBITDA, DCF
│   ├── efficiency_indicators.py        # Asset Turnover, Working Capital ratios
│   ├── growth_indicators.py            # Revenue/Earnings growth, SGR
│   ├── liquidity_indicators.py         # Current, Quick, Cash ratios
│   ├── leverage_indicators.py          # Debt ratios, Interest coverage
│   ├── quality_indicators.py           # Earnings quality, Cash flow analysis
│   ├── momentum_indicators.py          # Growth acceleration, Trend analysis
│   ├── risk_indicators.py              # Financial stress, Volatility metrics
│   └── sector_specific_indicators.py   # Banking, Tech, Energy specific metrics
├── outputs/
│   ├── profitability/
│   ├── valuation/
│   ├── efficiency/
│   ├── growth/
│   ├── liquidity/
│   ├── leverage/
│   ├── quality/
│   ├── momentum/
│   ├── risk/
│   └── sector_specific/
├── utils/
│   ├── data_loader.py                  # Common data loading utilities
│   └── report_generator.py             # Generate comprehensive reports
└── run_all_indicators.py               # Script to run all indicators

## Usage

### Run Individual Indicators
```bash
cd FundamentalAnalysis
python indicators/profitability_indicators.py
python indicators/valuation_indicators.py
# ... etc
```

### Run All Indicators
```bash
cd FundamentalAnalysis
python run_all_indicators.py
```

### Generate Company Report
```bash
cd FundamentalAnalysis
python utils/report_generator.py RELIANCE
```

## Output Files

Each indicator script generates:
- CSV files with calculated metrics for all companies
- JSON files with detailed analysis
- Summary reports in text format
- Visualization plots (PNG files)

## Indicators Calculated

### Profitability Indicators
- Return on Equity (ROE)
- Return on Assets (ROA)
- Gross Profit Margin
- Operating Profit Margin
- Net Profit Margin
- DuPont Analysis breakdown

### Valuation Indicators
- Price-to-Earnings (P/E) ratio
- Price-to-Book (P/B) ratio
- Price-to-Sales (P/S) ratio
- Enterprise Value to EBITDA
- Discounted Cash Flow (DCF) analysis
- PEG ratio

### Efficiency Indicators
- Asset Turnover ratio
- Inventory Turnover ratio
- Receivables Turnover ratio
- Working Capital Turnover
- Days Sales Outstanding (DSO)
- Days Inventory Outstanding (DIO)

### Growth Indicators
- Revenue Growth (YoY, QoQ)
- Earnings Growth (YoY, QoQ)
- Sustainable Growth Rate
- EBITDA Growth
- Book Value Growth

### Liquidity Indicators
- Current Ratio
- Quick Ratio (Acid Test)
- Cash Ratio
- Working Capital
- Cash Conversion Cycle

### Leverage Indicators
- Debt-to-Equity ratio
- Debt-to-Assets ratio
- Interest Coverage ratio
- EBITDA Coverage ratio
- Debt Service Coverage ratio

### Quality Indicators
- Operating Cash Flow to Net Income
- Free Cash Flow yield
- Earnings Quality Score
- Accruals ratio
- Revenue Quality metrics

### Momentum Indicators
- Revenue Growth Acceleration
- Earnings Growth Acceleration
- Margin Expansion trends
- ROE trend analysis

### Risk Indicators
- Financial Leverage
- Business Risk metrics
- Earnings Volatility
- Beta calculation
- Z-Score (Altman)

### Sector-Specific Indicators
- Banking: NIM, Cost-to-Income, CASA ratio
- Technology: Revenue per employee, R&D intensity
- Energy: Capacity utilization, Reserve ratios
- Retail: Same-store sales growth, Inventory days

## Requirements

- Python 3.8+
- pandas
- numpy
- matplotlib
- seaborn
- json
- pathlib 