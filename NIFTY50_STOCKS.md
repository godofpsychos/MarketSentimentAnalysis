# Complete Nifty 50+ Stock Ticker Mapping

This document lists all 55 stocks (50 Nifty 50 stocks + 5 additional popular stocks) with their corresponding Yahoo Finance ticker symbols used in our Market Sentiment Analysis application.

## Banking & Financial Services (19 stocks)

| Stock Name | Symbol | Yahoo Finance Ticker | Sector |
|------------|--------|---------------------|---------|
| HDFC Bank | HDFCBANK | HDFCBANK.NS | Private Bank |
| ICICI Bank | ICICIBANK | ICICIBANK.NS | Private Bank |
| State Bank of India | SBIN | SBIN.NS | Public Bank |
| Kotak Mahindra Bank | KOTAKBANK | KOTAKBANK.NS | Private Bank |
| Axis Bank | AXISBANK | AXISBANK.NS | Private Bank |
| IndusInd Bank | INDUSINDBK | INDUSINDBK.NS | Private Bank |
| Bajaj Finance | BAJFINANCE | BAJFINANCE.NS | NBFC |
| Bajaj Finserv | BAJAJFINSV | BAJAJFINSV.NS | Financial Services |
| HDFC Life Insurance | HDFCLIFE | HDFCLIFE.NS | Insurance |
| SBI Life Insurance | SBILIFE | SBILIFE.NS | Insurance |
| Shriram Finance | SHRIRAMFIN | SHRIRAMFIN.NS | NBFC |
| Jio Financial Services | JIOFINANCE | JIOFINANCE.NS | Financial Services |

## Information Technology (4 stocks)

| Stock Name | Symbol | Yahoo Finance Ticker | Sector |
|------------|--------|---------------------|---------|
| Tata Consultancy Services | TCS | TCS.NS | IT Services |
| Infosys | INFY | INFY.NS | IT Services |
| HCL Technologies | HCLTECH | HCLTECH.NS | IT Services |
| Wipro | WIPRO | WIPRO.NS | IT Services |
| Tech Mahindra | TECHM | TECHM.NS | IT Services |

## Oil, Gas & Energy (6 stocks)

| Stock Name | Symbol | Yahoo Finance Ticker | Sector |
|------------|--------|---------------------|---------|
| Reliance Industries | RELIANCE | RELIANCE.NS | Oil & Gas |
| Oil & Natural Gas Corporation | ONGC | ONGC.NS | Oil & Gas |
| NTPC | NTPC | NTPC.NS | Power |
| Power Grid Corporation | POWERGRID | POWERGRID.NS | Power |
| Coal India | COALINDIA | COALINDIA.NS | Mining |
| Indian Oil Corporation | IOC | IOC.NS | Oil & Gas |
| Bharat Petroleum Corporation | BPCL | BPCL.NS | Oil & Gas |

## Automobiles (6 stocks)

| Stock Name | Symbol | Yahoo Finance Ticker | Sector |
|------------|--------|---------------------|---------|
| Maruti Suzuki | MARUTI | MARUTI.NS | Passenger Cars |
| Tata Motors | TATAMOTORS | TATAMOTORS.NS | Commercial Vehicles |
| Mahindra & Mahindra | M&M | M&M.NS | Passenger Cars |
| Bajaj Auto | BAJAJ-AUTO | BAJAJ-AUTO.NS | Two Wheelers |
| Eicher Motors | EICHERMOT | EICHERMOT.NS | Two Wheelers |
| Hero MotoCorp | HEROMOTOCO | HEROMOTOCO.NS | Two Wheelers |

## Pharmaceuticals & Healthcare (5 stocks)

| Stock Name | Symbol | Yahoo Finance Ticker | Sector |
|------------|--------|---------------------|---------|
| Sun Pharmaceutical | SUNPHARMA | SUNPHARMA.NS | Pharmaceuticals |
| Dr. Reddy's Laboratories | DRREDDY | DRREDDY.NS | Pharmaceuticals |
| Cipla | CIPLA | CIPLA.NS | Pharmaceuticals |
| Apollo Hospitals | APOLLOHOSP | APOLLOHOSP.NS | Healthcare Services |
| Divi's Laboratories | DIVISLAB | DIVISLAB.NS | Pharmaceuticals |

## Consumer Goods & FMCG (5 stocks)

| Stock Name | Symbol | Yahoo Finance Ticker | Sector |
|------------|--------|---------------------|---------|
| Hindustan Unilever | HINDUNILVR | HINDUNILVR.NS | FMCG |
| ITC | ITC | ITC.NS | FMCG |
| Nestlé India | NESTLEIND | NESTLEIND.NS | FMCG |
| Asian Paints | ASIANPAINT | ASIANPAINT.NS | Paints |
| Tata Consumer Products | TATACONSUMR | TATACONSUMR.NS | FMCG |
| Britannia Industries | BRITANNIA | BRITANNIA.NS | FMCG |

## Metals & Mining (3 stocks)

| Stock Name | Symbol | Yahoo Finance Ticker | Sector |
|------------|--------|---------------------|---------|
| JSW Steel | JSWSTEEL | JSWSTEEL.NS | Steel |
| Tata Steel | TATASTEEL | TATASTEEL.NS | Steel |
| Hindalco Industries | HINDALCO | HINDALCO.NS | Aluminium |

## Retail & Consumer Services (2 stocks)

| Stock Name | Symbol | Yahoo Finance Ticker | Sector |
|------------|--------|---------------------|---------|
| Titan Company | TITAN | TITAN.NS | Jewelry & Watches |
| Trent | TRENT | TRENT.NS | Retail |

## Cement & Construction (3 stocks)

| Stock Name | Symbol | Yahoo Finance Ticker | Sector |
|------------|--------|---------------------|---------|
| UltraTech Cement | ULTRACEMCO | ULTRACEMCO.NS | Cement |
| Grasim Industries | GRASIM | GRASIM.NS | Diversified |
| Larsen & Toubro | LT | LT.NS | Engineering & Construction |

## Telecommunications (1 stock)

| Stock Name | Symbol | Yahoo Finance Ticker | Sector |
|------------|--------|---------------------|---------|
| Bharti Airtel | BHARTIARTL | BHARTIARTL.NS | Telecommunications |

## Defence (1 stock)

| Stock Name | Symbol | Yahoo Finance Ticker | Sector |
|------------|--------|---------------------|---------|
| Bharat Electronics | BEL | BEL.NS | Defence |

## Miscellaneous (4 stocks)

| Stock Name | Symbol | Yahoo Finance Ticker | Sector |
|------------|--------|---------------------|---------|
| Adani Enterprises | ADANIENT | ADANIENT.NS | Diversified |
| Adani Ports & SEZ | ADANIPORTS | ADANIPORTS.NS | Ports |
| Adani Green Energy | ADANIGREEN | ADANIGREEN.NS | Renewable Energy |
| Adani Power | ADANIPOWER | ADANIPOWER.NS | Power Generation |

## Usage in the Application

All these stocks are now available in your Market Sentiment Analysis application. You can:

1. **View Charts**: Get real-time price charts for any of these 50 stocks
2. **Analyze Sentiment**: Compare stock price movements with market sentiment data
3. **Track Performance**: Monitor historical performance across different time periods (1d, 5d, 1mo, 3mo, 6mo, 1y)

## API Endpoints

- **Stock Info**: `GET /api/stock-info/{SYMBOL}` - Get basic stock information
- **Stock Data**: `GET /api/stock-data/{SYMBOL}?period={PERIOD}` - Get historical price data
- **Sentiment Data**: `GET /api/sentiment?stock={SYMBOL}` - Get sentiment analysis data

## Example Usage

```bash
# Get Reliance stock info
curl "http://localhost:5000/api/stock-info/RELIANCE"

# Get TCS 1-month chart data
curl "http://localhost:5000/api/stock-data/TCS?period=1mo"

# Get HDFC Bank sentiment
curl "http://localhost:5000/api/sentiment?stock=HDFCBANK"
```

## Notes

- All Yahoo Finance tickers end with `.NS` (National Stock Exchange of India)
- Stock symbols should be used exactly as shown in the Symbol column
- The application automatically maps your stock symbols to Yahoo Finance tickers
- Data is fetched in real-time from Yahoo Finance API 