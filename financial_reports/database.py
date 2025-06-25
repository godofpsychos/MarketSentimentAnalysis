#!/usr/bin/env python3
"""
Financial Data Database Module
Creates and manages SQLite database for financial data
Imports data from JSON files created by fetch_financial_data.py
"""

import os
import json
import sqlite3
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class FinancialDatabase:
    def __init__(self, db_path='financial_reports/financial_data.db'):
        """Initialize database connection and create tables"""
        self.db_path = db_path
        self.conn = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        """Connect to SQLite database"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            self.conn = sqlite3.connect(self.db_path)
            self.conn.execute("PRAGMA foreign_keys = ON")
            logger.info(f"Connected to database: {self.db_path}")
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            raise
    
    def create_tables(self):
        """Create all necessary tables"""
        try:
            cursor = self.conn.cursor()
            
            # Companies table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS companies (
                    symbol TEXT PRIMARY KEY,
                    name TEXT,
                    sector TEXT,
                    industry TEXT,
                    market_cap INTEGER,
                    market_cap_formatted TEXT,
                    employees INTEGER,
                    business_summary TEXT,
                    website TEXT,
                    city TEXT,
                    country TEXT,
                    currency TEXT,
                    current_price REAL,
                    previous_close REAL,
                    day_high REAL,
                    day_low REAL,
                    fifty_two_week_high REAL,
                    fifty_two_week_low REAL,
                    volume INTEGER,
                    avg_volume INTEGER,
                    fetch_date TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Annual income statements
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS annual_income_statements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT,
                    period_date TEXT,
                    field_name TEXT,
                    value REAL,
                    formatted_value TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (symbol) REFERENCES companies (symbol)
                )
            ''')
            
            # Quarterly income statements  
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS quarterly_income_statements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT,
                    period_date TEXT,
                    field_name TEXT,
                    value REAL,
                    formatted_value TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (symbol) REFERENCES companies (symbol)
                )
            ''')
            
            # Annual balance sheets
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS annual_balance_sheets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT,
                    period_date TEXT,
                    field_name TEXT,
                    value REAL,
                    formatted_value TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (symbol) REFERENCES companies (symbol)
                )
            ''')
            
            # Quarterly balance sheets
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS quarterly_balance_sheets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT,
                    period_date TEXT,
                    field_name TEXT,
                    value REAL,
                    formatted_value TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (symbol) REFERENCES companies (symbol)
                )
            ''')
            
            # Annual cash flows
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS annual_cash_flows (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT,
                    period_date TEXT,
                    field_name TEXT,
                    value REAL,
                    formatted_value TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (symbol) REFERENCES companies (symbol)
                )
            ''')
            
            # Quarterly cash flows
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS quarterly_cash_flows (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT,
                    period_date TEXT,
                    field_name TEXT,
                    value REAL,
                    formatted_value TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (symbol) REFERENCES companies (symbol)
                )
            ''')
            
            # Historical prices
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS historical_prices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT,
                    date TEXT,
                    period_type TEXT,
                    open_price REAL,
                    high_price REAL,
                    low_price REAL,
                    close_price REAL,
                    volume INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (symbol) REFERENCES companies (symbol)
                )
            ''')
            
            # Dividends
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS dividends (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT,
                    date TEXT,
                    amount REAL,
                    formatted_amount TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (symbol) REFERENCES companies (symbol)
                )
            ''')
            
            # Stock splits
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stock_splits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT,
                    date TEXT,
                    ratio REAL,
                    formatted_ratio TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (symbol) REFERENCES companies (symbol)
                )
            ''')
            
            # Valuation metrics
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS valuation_metrics (
                    symbol TEXT PRIMARY KEY,
                    pe_ratio REAL,
                    forward_pe REAL,
                    peg_ratio REAL,
                    price_to_book REAL,
                    price_to_sales REAL,
                    enterprise_value INTEGER,
                    enterprise_value_formatted TEXT,
                    ev_to_revenue REAL,
                    ev_to_ebitda REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (symbol) REFERENCES companies (symbol)
                )
            ''')
            
            # Financial health
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS financial_health (
                    symbol TEXT PRIMARY KEY,
                    return_on_equity REAL,
                    return_on_assets REAL,
                    debt_to_equity REAL,
                    current_ratio REAL,
                    quick_ratio REAL,
                    gross_margin REAL,
                    operating_margin REAL,
                    profit_margin REAL,
                    revenue_growth REAL,
                    earnings_growth REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (symbol) REFERENCES companies (symbol)
                )
            ''')
            
            # Earnings
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS earnings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT,
                    year INTEGER,
                    revenue REAL,
                    earnings REAL,
                    revenue_formatted TEXT,
                    earnings_formatted TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (symbol) REFERENCES companies (symbol)
                )
            ''')
            
            self.conn.commit()
            logger.info("All database tables created successfully")
            
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            raise
    
    def import_company_data(self, data):
        """Import company basic information"""
        try:
            symbol = data['symbol']
            company_info = data.get('company_info', {})
            price_info = data.get('current_price_info', {})
            
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO companies 
                (symbol, name, sector, industry, market_cap, market_cap_formatted, employees, 
                 business_summary, website, city, country, currency, current_price, 
                 previous_close, day_high, day_low, fifty_two_week_high, fifty_two_week_low, 
                 volume, avg_volume, fetch_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                symbol,
                company_info.get('name'),
                company_info.get('sector'),
                company_info.get('industry'),
                company_info.get('market_cap'),
                company_info.get('market_cap_formatted'),
                company_info.get('employees'),
                company_info.get('business_summary'),
                company_info.get('website'),
                company_info.get('city'),
                company_info.get('country'),
                company_info.get('currency'),
                price_info.get('current_price'),
                price_info.get('previous_close'),
                price_info.get('day_high'),
                price_info.get('day_low'),
                price_info.get('fifty_two_week_high'),
                price_info.get('fifty_two_week_low'),
                price_info.get('volume'),
                price_info.get('avg_volume'),
                data.get('fetch_date')
            ))
            
        except Exception as e:
            logger.error(f"Error importing company data for {data.get('symbol', 'unknown')}: {e}")
    
    def import_financial_statements(self, symbol, statements, statement_type):
        """Import financial statements (income, balance, cashflow)"""
        try:
            cursor = self.conn.cursor()
            
            for period_date, period_data in statements.items():
                for field_name, field_data in period_data.items():
                    if isinstance(field_data, dict):
                        value = field_data.get('value')
                        formatted_value = field_data.get('formatted')
                        
                        # Convert string values to float if possible
                        if isinstance(value, str):
                            try:
                                value = float(value)
                            except:
                                value = None
                        
                        cursor.execute(f'''
                            INSERT INTO {statement_type}
                            (symbol, period_date, field_name, value, formatted_value)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (symbol, period_date, field_name, value, formatted_value))
                        
        except Exception as e:
            logger.error(f"Error importing {statement_type} for {symbol}: {e}")
    
    def import_historical_prices(self, symbol, price_data):
        """Import historical price data"""
        try:
            cursor = self.conn.cursor()
            
            for period_type, period_data in price_data.items():
                for date, daily_data in period_data.items():
                    cursor.execute('''
                        INSERT INTO historical_prices
                        (symbol, date, period_type, open_price, high_price, low_price, close_price, volume)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        symbol, date, period_type,
                        daily_data.get('open'),
                        daily_data.get('high'),
                        daily_data.get('low'),
                        daily_data.get('close'),
                        daily_data.get('volume')
                    ))
                    
        except Exception as e:
            logger.error(f"Error importing historical prices for {symbol}: {e}")
    
    def import_dividends(self, symbol, dividend_data):
        """Import dividend data"""
        try:
            cursor = self.conn.cursor()
            
            for date, div_info in dividend_data.items():
                if isinstance(div_info, dict):
                    amount = div_info.get('amount')
                    formatted = div_info.get('formatted')
                else:
                    amount = div_info
                    formatted = str(div_info)
                
                cursor.execute('''
                    INSERT INTO dividends (symbol, date, amount, formatted_amount)
                    VALUES (?, ?, ?, ?)
                ''', (symbol, date, amount, formatted))
                
        except Exception as e:
            logger.error(f"Error importing dividends for {symbol}: {e}")
    
    def import_stock_splits(self, symbol, split_data):
        """Import stock split data"""
        try:
            cursor = self.conn.cursor()
            
            for date, split_info in split_data.items():
                if isinstance(split_info, dict):
                    ratio = split_info.get('ratio')
                    formatted = split_info.get('formatted')
                else:
                    ratio = split_info
                    formatted = str(split_info)
                
                cursor.execute('''
                    INSERT INTO stock_splits (symbol, date, ratio, formatted_ratio)
                    VALUES (?, ?, ?, ?)
                ''', (symbol, date, ratio, formatted))
                
        except Exception as e:
            logger.error(f"Error importing stock splits for {symbol}: {e}")
    
    def import_valuation_metrics(self, symbol, metrics):
        """Import valuation metrics"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO valuation_metrics
                (symbol, pe_ratio, forward_pe, peg_ratio, price_to_book, price_to_sales,
                 enterprise_value, enterprise_value_formatted, ev_to_revenue, ev_to_ebitda)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                symbol,
                metrics.get('pe_ratio'),
                metrics.get('forward_pe'),
                metrics.get('peg_ratio'),
                metrics.get('price_to_book'),
                metrics.get('price_to_sales'),
                metrics.get('enterprise_value'),
                metrics.get('enterprise_value_formatted'),
                metrics.get('ev_to_revenue'),
                metrics.get('ev_to_ebitda')
            ))
            
        except Exception as e:
            logger.error(f"Error importing valuation metrics for {symbol}: {e}")
    
    def import_financial_health(self, symbol, health):
        """Import financial health metrics"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO financial_health
                (symbol, return_on_equity, return_on_assets, debt_to_equity, current_ratio,
                 quick_ratio, gross_margin, operating_margin, profit_margin, revenue_growth, earnings_growth)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                symbol,
                health.get('return_on_equity'),
                health.get('return_on_assets'),
                health.get('debt_to_equity'),
                health.get('current_ratio'),
                health.get('quick_ratio'),
                health.get('gross_margin'),
                health.get('operating_margin'),
                health.get('profit_margin'),
                health.get('revenue_growth'),
                health.get('earnings_growth')
            ))
            
        except Exception as e:
            logger.error(f"Error importing financial health for {symbol}: {e}")
    
    def import_earnings(self, symbol, earnings_data):
        """Import earnings data"""
        try:
            cursor = self.conn.cursor()
            
            for year, earnings_info in earnings_data.items():
                cursor.execute('''
                    INSERT INTO earnings
                    (symbol, year, revenue, earnings, revenue_formatted, earnings_formatted)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    symbol, int(year),
                    earnings_info.get('revenue'),
                    earnings_info.get('earnings'),
                    earnings_info.get('revenue_formatted'),
                    earnings_info.get('earnings_formatted')
                ))
                
        except Exception as e:
            logger.error(f"Error importing earnings for {symbol}: {e}")
    
    def import_json_file(self, json_file_path):
        """Import data from a single JSON file"""
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            symbol = data.get('symbol')
            if not symbol:
                logger.warning(f"No symbol found in {json_file_path}")
                return False
            
            if 'error' in data:
                logger.warning(f"Error data found for {symbol}: {data['error']}")
                return False
            
            logger.info(f"Importing data for {symbol}")
            
            # Import company data
            self.import_company_data(data)
            
            # Import financial statements
            financial_statements = data.get('financial_statements', {})
            if 'annual' in financial_statements:
                annual = financial_statements['annual']
                self.import_financial_statements(symbol, annual.get('income_statement', {}), 'annual_income_statements')
                self.import_financial_statements(symbol, annual.get('balance_sheet', {}), 'annual_balance_sheets')
                self.import_financial_statements(symbol, annual.get('cash_flow', {}), 'annual_cash_flows')
            
            if 'quarterly' in financial_statements:
                quarterly = financial_statements['quarterly']
                self.import_financial_statements(symbol, quarterly.get('income_statement', {}), 'quarterly_income_statements')
                self.import_financial_statements(symbol, quarterly.get('balance_sheet', {}), 'quarterly_balance_sheets')
                self.import_financial_statements(symbol, quarterly.get('cash_flow', {}), 'quarterly_cash_flows')
            
            # Import historical prices
            historical_prices = data.get('historical_prices', {})
            if historical_prices:
                self.import_historical_prices(symbol, historical_prices)
            
            # Import corporate actions
            corporate_actions = data.get('corporate_actions', {})
            if 'dividends' in corporate_actions:
                self.import_dividends(symbol, corporate_actions['dividends'])
            if 'splits' in corporate_actions:
                self.import_stock_splits(symbol, corporate_actions['splits'])
            
            # Import valuation metrics
            valuation_metrics = data.get('valuation_metrics', {})
            if valuation_metrics:
                self.import_valuation_metrics(symbol, valuation_metrics)
            
            # Import financial health
            financial_health = data.get('financial_health', {})
            if financial_health:
                self.import_financial_health(symbol, financial_health)
            
            # Import earnings
            earnings = data.get('earnings', {})
            if earnings:
                self.import_earnings(symbol, earnings)
            
            self.conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error importing JSON file {json_file_path}: {e}")
            return False
    
    def import_all_json_files(self, data_dir='financial_reports/data'):
        """Import all JSON files from data directory"""
        try:
            data_path = Path(data_dir)
            if not data_path.exists():
                logger.error(f"Data directory not found: {data_dir}")
                return 0, 0
            
            json_files = list(data_path.glob("*_financial_data.json"))
            if not json_files:
                logger.warning(f"No JSON files found in {data_dir}")
                return 0, 0
            
            logger.info(f"Found {len(json_files)} JSON files to import")
            
            successful = 0
            failed = 0
            
            for json_file in json_files:
                if self.import_json_file(json_file):
                    successful += 1
                else:
                    failed += 1
            
            logger.info(f"Import completed: {successful} successful, {failed} failed")
            return successful, failed
            
        except Exception as e:
            logger.error(f"Error importing JSON files: {e}")
            return 0, 0
    
    def get_database_stats(self):
        """Get database statistics"""
        try:
            cursor = self.conn.cursor()
            
            tables = [
                'companies', 'annual_income_statements', 'quarterly_income_statements',
                'annual_balance_sheets', 'quarterly_balance_sheets', 'annual_cash_flows',
                'quarterly_cash_flows', 'historical_prices', 'dividends', 'stock_splits',
                'valuation_metrics', 'financial_health', 'earnings'
            ]
            
            stats = {}
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                stats[table] = cursor.fetchone()[0]
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {}
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")

def main():
    """Main function to import all JSON files to database"""
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('financial_reports/database_import.log'),
            logging.StreamHandler()
        ]
    )
    
    logger.info("=" * 80)
    logger.info("STARTING DATABASE IMPORT")
    logger.info("=" * 80)
    
    try:
        # Initialize database
        db = FinancialDatabase()
        
        # Import all JSON files
        successful, failed = db.import_all_json_files()
        
        # Show statistics
        stats = db.get_database_stats()
        
        print("\n" + "=" * 80)
        print("🎉 DATABASE IMPORT COMPLETED!")
        print("=" * 80)
        print(f"✅ Successful imports: {successful}")
        print(f"❌ Failed imports: {failed}")
        if successful + failed > 0:
            print(f"📈 Success rate: {(successful/(successful+failed)*100):.1f}%")
        
        print(f"\n💾 Database Statistics:")
        for table, count in stats.items():
            print(f"  • {table}: {count:,} records")
        
        print(f"\n📁 Database location: {db.db_path}")
        print(f"📋 Log file: financial_reports/database_import.log")
        
        # Close database
        db.close()
        
        return successful > 0
        
    except Exception as e:
        logger.error(f"Error in main process: {e}")
        return False

if __name__ == "__main__":
    main() 