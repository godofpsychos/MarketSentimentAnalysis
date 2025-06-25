#!/usr/bin/env python3
"""
Historical Financial Data Fetcher
Fetches ALL available historical financial data from yfinance for stocks in CSV
Saves individual JSON files for each stock
"""

import os
import sys
import csv
import json
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('financial_reports/fetch_financial_data.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FinancialDataFetcher:
    def __init__(self, csv_file_path='stocksList.csv', output_dir='financial_reports/data'):
        """
        Initialize the financial data fetcher
        
        Args:
            csv_file_path (str): Path to CSV file with stock symbols
            output_dir (str): Directory to save JSON files
        """
        self.csv_file_path = csv_file_path
        self.output_dir = output_dir
        self.stocks = []
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        logger.info(f"Financial Data Fetcher initialized")
        logger.info(f"CSV file: {csv_file_path}")
        logger.info(f"Output directory: {output_dir}")
    
    def check_venv(self):
        """Check if we're in a virtual environment"""
        if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            logger.error("Not in a virtual environment!")
            logger.error("Please activate your virtual environment first: source .venv/bin/activate")
            return False
        return True
    
    def load_stocks_from_csv(self):
        """Load stock symbols from CSV file"""
        try:
            stocks = []
            with open(self.csv_file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    symbol = row['SYMBOL'].strip()
                    if symbol:
                        stocks.append(symbol)
            
            self.stocks = stocks
            logger.info(f"Successfully loaded {len(stocks)} stock symbols from CSV")
            return stocks
            
        except FileNotFoundError:
            logger.error(f"CSV file not found: {self.csv_file_path}")
            return []
        except Exception as e:
            logger.error(f"Error reading CSV file: {e}")
            return []
    
    def format_currency(self, value):
        """Format currency values in Indian format (Crores, Lakhs)"""
        if value is None or value == 0:
            return "₹0"
        
        try:
            value = float(value)
            if abs(value) >= 10000000:  # 1 Crore = 10 Million
                return f"₹{value/10000000:.2f} Cr"
            elif abs(value) >= 100000:  # 1 Lakh = 100 Thousand
                return f"₹{value/100000:.2f} L"
            else:
                return f"₹{value:,.2f}"
        except:
            return str(value)
    
    def clean_financial_dataframe(self, df, statement_name):
        """Clean and format financial dataframe"""
        if df is None or df.empty:
            return {}
        
        try:
            # Convert to dictionary with proper date formatting
            data = {}
            for column in df.columns:
                # Format date as string
                if hasattr(column, 'strftime'):
                    date_key = column.strftime('%Y-%m-%d')
                else:
                    date_key = str(column)
                
                period_data = {}
                for index, value in df[column].items():
                    # Clean the index name
                    field_name = str(index).replace('\n', ' ').strip()
                    
                    # Convert value
                    if value is not None:
                        try:
                            if isinstance(value, (int, float)):
                                period_data[field_name] = {
                                    'value': float(value),
                                    'formatted': self.format_currency(value)
                                }
                            else:
                                period_data[field_name] = {
                                    'value': str(value),
                                    'formatted': str(value)
                                }
                        except:
                            period_data[field_name] = {
                                'value': str(value),
                                'formatted': str(value)
                            }
                
                data[date_key] = period_data
            
            return data
            
        except Exception as e:
            logger.warning(f"Error cleaning {statement_name} dataframe: {e}")
            return {}
    
    def get_historical_stock_data(self, ticker, periods=['max', '5y', '2y', '1y']):
        """Get historical stock price data for multiple periods"""
        historical_data = {}
        
        for period in periods:
            try:
                hist = ticker.history(period=period)
                if not hist.empty:
                    period_data = {}
                    for date, row in hist.iterrows():
                        period_data[date.strftime('%Y-%m-%d')] = {
                            'open': float(row['Open']),
                            'high': float(row['High']),
                            'low': float(row['Low']),
                            'close': float(row['Close']),
                            'volume': int(row['Volume']) if not pd.isna(row['Volume']) else 0,
                            'formatted': {
                                'open': self.format_currency(row['Open']),
                                'high': self.format_currency(row['High']),
                                'low': self.format_currency(row['Low']),
                                'close': self.format_currency(row['Close']),
                                'volume': f"{int(row['Volume']):,}" if not pd.isna(row['Volume']) else "0"
                            }
                        }
                    historical_data[period] = period_data
                    logger.debug(f"Fetched {len(period_data)} price records for period {period}")
            except Exception as e:
                logger.warning(f"Could not fetch historical data for period {period}: {e}")
        
        return historical_data
    
    def get_complete_financial_data(self, symbol):
        """Get complete financial data for a single stock"""
        try:
            import yfinance as yf
            import pandas as pd
            
            logger.info(f"Fetching complete financial data for {symbol} ({symbol}.NS)")
            
            # Create ticker
            ticker_symbol = f"{symbol}.NS"
            ticker = yf.Ticker(ticker_symbol)
            
            # Get basic company info
            try:
                info = ticker.info
            except:
                info = {}
            
            # Prepare the complete data structure
            complete_data = {
                'symbol': symbol,
                'ticker_symbol': ticker_symbol,
                'fetch_date': datetime.now().isoformat(),
                'company_info': {
                    'name': info.get('longName', symbol),
                    'sector': info.get('sector', 'N/A'),
                    'industry': info.get('industry', 'N/A'),
                    'market_cap': info.get('marketCap'),
                    'market_cap_formatted': self.format_currency(info.get('marketCap')),
                    'employees': info.get('fullTimeEmployees'),
                    'business_summary': info.get('longBusinessSummary', ''),
                    'website': info.get('website', ''),
                    'city': info.get('city', ''),
                    'country': info.get('country', ''),
                    'currency': info.get('currency', 'INR')
                },
                'current_price_info': {
                    'current_price': info.get('currentPrice'),
                    'previous_close': info.get('previousClose'),
                    'day_high': info.get('dayHigh'),
                    'day_low': info.get('dayLow'),
                    'fifty_two_week_high': info.get('fiftyTwoWeekHigh'),
                    'fifty_two_week_low': info.get('fiftyTwoWeekLow'),
                    'volume': info.get('volume'),
                    'avg_volume': info.get('averageVolume')
                },
                'financial_statements': {},
                'historical_prices': {},
                'corporate_actions': {},
                'valuation_metrics': {},
                'financial_health': {},
                'earnings': {},
                'data_summary': {
                    'annual_financial_periods': 0,
                    'quarterly_financial_periods': 0,
                    'historical_price_periods': 0,
                    'dividend_records': 0,
                    'split_records': 0
                }
            }
            
            # Get financial statements
            try:
                # Annual statements
                annual_income = ticker.income_stmt
                annual_balance = ticker.balance_sheet
                annual_cashflow = ticker.cashflow
                
                # Quarterly statements  
                quarterly_income = ticker.quarterly_income_stmt
                quarterly_balance = ticker.quarterly_balance_sheet
                quarterly_cashflow = ticker.quarterly_cashflow
                
                complete_data['financial_statements'] = {
                    'annual': {
                        'income_statement': self.clean_financial_dataframe(annual_income, 'Annual Income Statement'),
                        'balance_sheet': self.clean_financial_dataframe(annual_balance, 'Annual Balance Sheet'),
                        'cash_flow': self.clean_financial_dataframe(annual_cashflow, 'Annual Cash Flow')
                    },
                    'quarterly': {
                        'income_statement': self.clean_financial_dataframe(quarterly_income, 'Quarterly Income Statement'),
                        'balance_sheet': self.clean_financial_dataframe(quarterly_balance, 'Quarterly Balance Sheet'),
                        'cash_flow': self.clean_financial_dataframe(quarterly_cashflow, 'Quarterly Cash Flow')
                    }
                }
                
                # Count periods
                annual_periods = len(complete_data['financial_statements']['annual']['income_statement'])
                quarterly_periods = len(complete_data['financial_statements']['quarterly']['income_statement'])
                complete_data['data_summary']['annual_financial_periods'] = annual_periods
                complete_data['data_summary']['quarterly_financial_periods'] = quarterly_periods
                
            except Exception as e:
                logger.warning(f"Could not fetch financial statements for {symbol}: {e}")
            
            # Get historical prices
            try:
                historical_prices = self.get_historical_stock_data(ticker)
                complete_data['historical_prices'] = historical_prices
                complete_data['data_summary']['historical_price_periods'] = len(historical_prices)
            except Exception as e:
                logger.warning(f"Could not fetch historical prices for {symbol}: {e}")
            
            # Get corporate actions (dividends and splits)
            try:
                # Dividends
                dividends = ticker.dividends
                if not dividends.empty:
                    div_data = {}
                    for date, amount in dividends.items():
                        div_data[date.strftime('%Y-%m-%d')] = {
                            'amount': float(amount),
                            'formatted': self.format_currency(amount)
                        }
                    complete_data['corporate_actions']['dividends'] = div_data
                    complete_data['data_summary']['dividend_records'] = len(div_data)
                
                # Stock splits
                splits = ticker.splits
                if not splits.empty:
                    split_data = {}
                    for date, ratio in splits.items():
                        split_data[date.strftime('%Y-%m-%d')] = {
                            'ratio': float(ratio),
                            'formatted': f"1:{ratio}"
                        }
                    complete_data['corporate_actions']['splits'] = split_data
                    complete_data['data_summary']['split_records'] = len(split_data)
                    
            except Exception as e:
                logger.warning(f"Could not fetch corporate actions for {symbol}: {e}")
            
            # Get valuation metrics
            try:
                complete_data['valuation_metrics'] = {
                    'pe_ratio': info.get('trailingPE'),
                    'forward_pe': info.get('forwardPE'),
                    'peg_ratio': info.get('pegRatio'),
                    'price_to_book': info.get('priceToBook'),
                    'price_to_sales': info.get('priceToSalesTrailing12Months'),
                    'enterprise_value': info.get('enterpriseValue'),
                    'enterprise_value_formatted': self.format_currency(info.get('enterpriseValue')),
                    'ev_to_revenue': info.get('enterpriseToRevenue'),
                    'ev_to_ebitda': info.get('enterpriseToEbitda')
                }
            except Exception as e:
                logger.warning(f"Could not fetch valuation metrics for {symbol}: {e}")
            
            # Get financial health metrics
            try:
                complete_data['financial_health'] = {
                    'return_on_equity': info.get('returnOnEquity'),
                    'return_on_assets': info.get('returnOnAssets'),
                    'debt_to_equity': info.get('debtToEquity'),
                    'current_ratio': info.get('currentRatio'),
                    'quick_ratio': info.get('quickRatio'),
                    'gross_margin': info.get('grossMargins'),
                    'operating_margin': info.get('operatingMargins'),
                    'profit_margin': info.get('profitMargins'),
                    'revenue_growth': info.get('revenueGrowth'),
                    'earnings_growth': info.get('earningsGrowth')
                }
            except Exception as e:
                logger.warning(f"Could not fetch financial health metrics for {symbol}: {e}")
            
            # Get earnings data
            try:
                earnings = ticker.earnings
                if earnings is not None and not earnings.empty:
                    earnings_data = {}
                    for year, row in earnings.iterrows():
                        earnings_data[str(year)] = {
                            'revenue': float(row['Revenue']) if 'Revenue' in row and not pd.isna(row['Revenue']) else None,
                            'earnings': float(row['Earnings']) if 'Earnings' in row and not pd.isna(row['Earnings']) else None,
                            'revenue_formatted': self.format_currency(row['Revenue']) if 'Revenue' in row else None,
                            'earnings_formatted': self.format_currency(row['Earnings']) if 'Earnings' in row else None
                        }
                    complete_data['earnings'] = earnings_data
            except Exception as e:
                logger.warning(f"Could not fetch earnings for {symbol}: {e}")
            
            logger.info(f"Successfully fetched complete financial data for {symbol}")
            return complete_data
            
        except Exception as e:
            logger.error(f"Error fetching financial data for {symbol}: {e}")
            return {
                'symbol': symbol,
                'error': str(e),
                'fetch_date': datetime.now().isoformat()
            }
    
    def save_stock_data(self, symbol, data):
        """Save individual stock data to JSON file"""
        try:
            filename = os.path.join(self.output_dir, f"{symbol}_financial_data.json")
            
            def json_serializer(obj):
                """Custom JSON serializer for handling datetime and other objects"""
                if hasattr(obj, 'isoformat'):  # datetime objects
                    return obj.isoformat()
                elif hasattr(obj, 'item'):  # numpy objects
                    return obj.item()
                elif hasattr(obj, 'tolist'):  # numpy arrays
                    return obj.tolist()
                else:
                    return str(obj)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=json_serializer)
            
            logger.info(f"Saved financial data for {symbol} to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error saving data for {symbol}: {e}")
            return None
    
    def fetch_all_financial_data(self, max_workers=3):
        """Fetch financial data for all stocks and save individual JSON files"""
        logger.info("=" * 80)
        logger.info("STARTING COMPLETE FINANCIAL DATA FETCHING")
        logger.info("=" * 80)
        
        if not self.check_venv():
            return False
        
        # Load stocks
        stocks = self.load_stocks_from_csv()
        if not stocks:
            logger.error("No stocks loaded from CSV. Exiting.")
            return False
        
        logger.info(f"Processing {len(stocks)} stocks with {max_workers} workers")
        
        successful = 0
        failed = 0
        
        # Use ThreadPoolExecutor for concurrent processing
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_symbol = {
                executor.submit(self.get_complete_financial_data, stock): stock 
                for stock in stocks
            }
            
            # Process completed tasks
            for future in as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                try:
                    data = future.result()
                    
                    # Save to individual JSON file
                    saved_file = self.save_stock_data(symbol, data)
                    
                    if saved_file and 'error' not in data:
                        successful += 1
                    else:
                        failed += 1
                    
                    # Small delay to avoid overwhelming the API
                    time.sleep(0.3)
                    
                except Exception as e:
                    logger.error(f"Error processing {symbol}: {e}")
                    failed += 1
        
        # Print summary
        logger.info("=" * 80)
        logger.info("FINANCIAL DATA FETCHING COMPLETED")
        logger.info("=" * 80)
        logger.info(f"Total stocks processed: {len(stocks)}")
        logger.info(f"Successful fetches: {successful}")
        logger.info(f"Failed fetches: {failed}")
        logger.info(f"Success rate: {(successful/len(stocks)*100):.1f}%")
        logger.info(f"Data saved to: {self.output_dir}")
        
        return successful > 0

def main():
    """Main execution function"""
    fetcher = FinancialDataFetcher()
    
    try:
        success = fetcher.fetch_all_financial_data()
        
        if success:
            print("\n" + "="*80)
            print("🎉 FINANCIAL DATA FETCHING SUCCESSFUL!")
            print("="*80)
            print(f"📁 Individual JSON files saved to: {fetcher.output_dir}")
            print(f"📋 Log file: financial_reports/fetch_financial_data.log")
            print("✅ Ready for database import!")
        else:
            print("\n" + "="*80)
            print("❌ FINANCIAL DATA FETCHING FAILED!")
            print("="*80)
            print("Check the log file for details")
            
    except KeyboardInterrupt:
        print("\n⏹️  Process interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    main() 