#!/usr/bin/env python3
"""
Financial Data SQLite Database System
Stores comprehensive financial data from yfinance reports into SQLite database
"""

import sqlite3
import json
import os
import sys
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('financial_db.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FinancialDataDB:
    def __init__(self, db_path='financial_data.db'):
        """
        Initialize the Financial Data Database
        
        Args:
            db_path (str): Path to the SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        logger.info(f"Financial Data DB initialized with path: {db_path}")
    
    def connect(self):
        """Connect to the SQLite database"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            logger.info(f"Connected to database: {self.db_path}")
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            raise
    
    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
    
    def create_tables(self):
        """Create all necessary tables for financial data"""
        logger.info("Creating financial data tables...")
        
        # Companies table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS companies (
            symbol TEXT PRIMARY KEY,
            company_name TEXT,
            sector TEXT,
            industry TEXT,
            country TEXT,
            exchange TEXT,
            currency TEXT,
            market_cap REAL,
            enterprise_value REAL,
            shares_outstanding REAL,
            employees INTEGER,
            website TEXT,
            business_summary TEXT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Annual Income Statements
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS annual_income_statements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            period_date TEXT,
            total_revenue REAL,
            cost_of_revenue REAL,
            gross_profit REAL,
            operating_expense REAL,
            operating_income REAL,
            interest_expense REAL,
            interest_income REAL,
            tax_provision REAL,
            net_income REAL,
            ebitda REAL,
            ebit REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (symbol) REFERENCES companies(symbol),
            UNIQUE(symbol, period_date)
        )
        ''')
        
        # Quarterly Income Statements
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS quarterly_income_statements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            period_date TEXT,
            total_revenue REAL,
            cost_of_revenue REAL,
            gross_profit REAL,
            operating_expense REAL,
            operating_income REAL,
            interest_expense REAL,
            interest_income REAL,
            tax_provision REAL,
            net_income REAL,
            ebitda REAL,
            ebit REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (symbol) REFERENCES companies(symbol),
            UNIQUE(symbol, period_date)
        )
        ''')
        
        # Annual Balance Sheets
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS annual_balance_sheets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            period_date TEXT,
            total_assets REAL,
            current_assets REAL,
            non_current_assets REAL,
            cash_and_equivalents REAL,
            inventory REAL,
            total_liabilities REAL,
            current_liabilities REAL,
            non_current_liabilities REAL,
            total_debt REAL,
            long_term_debt REAL,
            short_term_debt REAL,
            total_equity REAL,
            retained_earnings REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (symbol) REFERENCES companies(symbol),
            UNIQUE(symbol, period_date)
        )
        ''')
        
        # Quarterly Balance Sheets
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS quarterly_balance_sheets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            period_date TEXT,
            total_assets REAL,
            current_assets REAL,
            non_current_assets REAL,
            cash_and_equivalents REAL,
            inventory REAL,
            total_liabilities REAL,
            current_liabilities REAL,
            non_current_liabilities REAL,
            total_debt REAL,
            long_term_debt REAL,
            short_term_debt REAL,
            total_equity REAL,
            retained_earnings REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (symbol) REFERENCES companies(symbol),
            UNIQUE(symbol, period_date)
        )
        ''')
        
        # Annual Cash Flow Statements
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS annual_cash_flows (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            period_date TEXT,
            operating_cash_flow REAL,
            investing_cash_flow REAL,
            financing_cash_flow REAL,
            free_cash_flow REAL,
            capital_expenditures REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (symbol) REFERENCES companies(symbol),
            UNIQUE(symbol, period_date)
        )
        ''')
        
        # Quarterly Cash Flow Statements
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS quarterly_cash_flows (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            period_date TEXT,
            operating_cash_flow REAL,
            investing_cash_flow REAL,
            financing_cash_flow REAL,
            free_cash_flow REAL,
            capital_expenditures REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (symbol) REFERENCES companies(symbol),
            UNIQUE(symbol, period_date)
        )
        ''')
        
        # Historical Stock Prices
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS historical_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            period_type TEXT,
            records_count INTEGER,
            date_start TEXT,
            date_end TEXT,
            highest_price REAL,
            lowest_price REAL,
            avg_price REAL,
            latest_price REAL,
            price_change REAL,
            price_change_percent REAL,
            highest_volume INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (symbol) REFERENCES companies(symbol),
            UNIQUE(symbol, period_type)
        )
        ''')
        
        # Dividends
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS dividends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            dividend_date TEXT,
            dividend_amount REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (symbol) REFERENCES companies(symbol),
            UNIQUE(symbol, dividend_date)
        )
        ''')
        
        # Stock Splits
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock_splits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            split_date TEXT,
            split_ratio REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (symbol) REFERENCES companies(symbol),
            UNIQUE(symbol, split_date)
        )
        ''')
        
        # Valuation Metrics
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS valuation_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            pe_ratio REAL,
            forward_pe REAL,
            peg_ratio REAL,
            price_to_book REAL,
            price_to_sales REAL,
            enterprise_to_revenue REAL,
            enterprise_to_ebitda REAL,
            book_value REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (symbol) REFERENCES companies(symbol),
            UNIQUE(symbol)
        )
        ''')
        
        # Financial Health Metrics
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS financial_health (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            total_revenue REAL,
            revenue_per_share REAL,
            profit_margins REAL,
            operating_margins REAL,
            return_on_assets REAL,
            return_on_equity REAL,
            total_cash REAL,
            total_debt REAL,
            debt_to_equity REAL,
            current_ratio REAL,
            quick_ratio REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (symbol) REFERENCES companies(symbol),
            UNIQUE(symbol)
        )
        ''')
        
        # Earnings Data
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS earnings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            period_type TEXT,
            period_date TEXT,
            earnings REAL,
            revenue REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (symbol) REFERENCES companies(symbol),
            UNIQUE(symbol, period_type, period_date)
        )
        ''')
        
        self.conn.commit()
        logger.info("All financial data tables created successfully")
    
    def safe_float(self, value):
        """Safely convert value to float, return None if not possible"""
        if value is None or value == 'N/A':
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def safe_int(self, value):
        """Safely convert value to int, return None if not possible"""
        if value is None or value == 'N/A':
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
    
    def extract_financial_statement_data(self, statement_data, field_mappings):
        """
        Extract financial statement data using field mappings
        
        Args:
            statement_data (dict): Financial statement data
            field_mappings (dict): Mapping of database fields to statement fields
        
        Returns:
            dict: Extracted data
        """
        extracted = {}
        
        if not statement_data.get('available', False):
            return extracted
        
        data = statement_data.get('data', {})
        
        for period_date, period_data in data.items():
            period_extracted = {'period_date': period_date}
            
            for db_field, statement_fields in field_mappings.items():
                value = None
                for field in statement_fields:
                    if field in period_data:
                        value = period_data[field].get('value')
                        break
                period_extracted[db_field] = self.safe_float(value)
            
            extracted[period_date] = period_extracted
        
        return extracted
    
    def insert_company_data(self, symbol, report):
        """Insert company basic information"""
        try:
            company_info = report.get('company_info', {})
            
            self.cursor.execute('''
            INSERT OR REPLACE INTO companies (
                symbol, company_name, sector, industry, country, exchange, currency,
                market_cap, enterprise_value, shares_outstanding, employees, website, business_summary
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                symbol,
                report.get('company_name', 'N/A'),
                report.get('sector', 'N/A'),
                report.get('industry', 'N/A'),
                report.get('country', 'N/A'),
                report.get('exchange', 'N/A'),
                report.get('currency', 'N/A'),
                self.safe_float(company_info.get('market_cap')),
                self.safe_float(company_info.get('enterprise_value')),
                self.safe_float(company_info.get('shares_outstanding')),
                self.safe_int(company_info.get('employees')),
                company_info.get('website', 'N/A'),
                company_info.get('business_summary', 'N/A')
            ))
            
        except Exception as e:
            logger.error(f"Error inserting company data for {symbol}: {e}")
    
    def insert_income_statements(self, symbol, statements, table_name):
        """Insert income statement data"""
        try:
            field_mappings = {
                'total_revenue': ['Total Revenue', 'Revenue', 'Net Sales'],
                'cost_of_revenue': ['Cost Of Revenue', 'Cost of Goods Sold', 'Cost of Sales'],
                'gross_profit': ['Gross Profit'],
                'operating_expense': ['Operating Expense', 'Total Operating Expenses', 'Operating Expenses'],
                'operating_income': ['Operating Income', 'Operating Profit'],
                'interest_expense': ['Interest Expense'],
                'interest_income': ['Interest Income'],
                'tax_provision': ['Tax Provision', 'Income Tax Expense'],
                'net_income': ['Net Income', 'Net Profit', 'Profit After Tax'],
                'ebitda': ['EBITDA'],
                'ebit': ['EBIT']
            }
            
            extracted_data = self.extract_financial_statement_data(statements, field_mappings)
            
            for period_date, data in extracted_data.items():
                self.cursor.execute(f'''
                INSERT OR REPLACE INTO {table_name} (
                    symbol, period_date, total_revenue, cost_of_revenue, gross_profit,
                    operating_expense, operating_income, interest_expense, interest_income,
                    tax_provision, net_income, ebitda, ebit
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    symbol, data['period_date'], data.get('total_revenue'),
                    data.get('cost_of_revenue'), data.get('gross_profit'),
                    data.get('operating_expense'), data.get('operating_income'),
                    data.get('interest_expense'), data.get('interest_income'),
                    data.get('tax_provision'), data.get('net_income'),
                    data.get('ebitda'), data.get('ebit')
                ))
                
        except Exception as e:
            logger.error(f"Error inserting income statements for {symbol}: {e}")
    
    def insert_balance_sheets(self, symbol, statements, table_name):
        """Insert balance sheet data"""
        try:
            field_mappings = {
                'total_assets': ['Total Assets'],
                'current_assets': ['Current Assets'],
                'non_current_assets': ['Non Current Assets'],
                'cash_and_equivalents': ['Cash And Cash Equivalents'],
                'inventory': ['Inventory'],
                'total_liabilities': ['Total Liabilities'],
                'current_liabilities': ['Current Liabilities'],
                'non_current_liabilities': ['Non Current Liabilities'],
                'total_debt': ['Total Debt'],
                'long_term_debt': ['Long Term Debt'],
                'short_term_debt': ['Short Term Debt'],
                'total_equity': ['Total Equity', 'Stockholders Equity'],
                'retained_earnings': ['Retained Earnings']
            }
            
            extracted_data = self.extract_financial_statement_data(statements, field_mappings)
            
            for period_date, data in extracted_data.items():
                self.cursor.execute(f'''
                INSERT OR REPLACE INTO {table_name} (
                    symbol, period_date, total_assets, current_assets, non_current_assets,
                    cash_and_equivalents, inventory, total_liabilities, current_liabilities,
                    non_current_liabilities, total_debt, long_term_debt, short_term_debt,
                    total_equity, retained_earnings
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    symbol, data['period_date'], data.get('total_assets'),
                    data.get('current_assets'), data.get('non_current_assets'),
                    data.get('cash_and_equivalents'), data.get('inventory'),
                    data.get('total_liabilities'), data.get('current_liabilities'),
                    data.get('non_current_liabilities'), data.get('total_debt'),
                    data.get('long_term_debt'), data.get('short_term_debt'),
                    data.get('total_equity'), data.get('retained_earnings')
                ))
                
        except Exception as e:
            logger.error(f"Error inserting balance sheets for {symbol}: {e}")
    
    def insert_cash_flows(self, symbol, statements, table_name):
        """Insert cash flow data"""
        try:
            field_mappings = {
                'operating_cash_flow': ['Operating Cash Flow', 'Cash Flow From Operations'],
                'investing_cash_flow': ['Investing Cash Flow', 'Cash Flow From Investing'],
                'financing_cash_flow': ['Financing Cash Flow', 'Cash Flow From Financing'],
                'free_cash_flow': ['Free Cash Flow'],
                'capital_expenditures': ['Capital Expenditures']
            }
            
            extracted_data = self.extract_financial_statement_data(statements, field_mappings)
            
            for period_date, data in extracted_data.items():
                self.cursor.execute(f'''
                INSERT OR REPLACE INTO {table_name} (
                    symbol, period_date, operating_cash_flow, investing_cash_flow,
                    financing_cash_flow, free_cash_flow, capital_expenditures
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    symbol, data['period_date'], data.get('operating_cash_flow'),
                    data.get('investing_cash_flow'), data.get('financing_cash_flow'),
                    data.get('free_cash_flow'), data.get('capital_expenditures')
                ))
                
        except Exception as e:
            logger.error(f"Error inserting cash flows for {symbol}: {e}")
    
    def insert_historical_prices(self, symbol, historical_data):
        """Insert historical price data"""
        try:
            for period_type, data in historical_data.items():
                if data.get('available', False):
                    summary = data.get('summary', {})
                    date_range = data.get('date_range', {})
                    
                    self.cursor.execute('''
                    INSERT OR REPLACE INTO historical_prices (
                        symbol, period_type, records_count, date_start, date_end,
                        highest_price, lowest_price, avg_price, latest_price,
                        price_change, price_change_percent, highest_volume
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        symbol, period_type, data.get('records_count'),
                        date_range.get('start'), date_range.get('end'),
                        self.safe_float(summary.get('highest_price')),
                        self.safe_float(summary.get('lowest_price')),
                        self.safe_float(summary.get('avg_price')),
                        self.safe_float(summary.get('latest_price')),
                        self.safe_float(summary.get('price_change')),
                        self.safe_float(summary.get('price_change_percent')),
                        self.safe_int(summary.get('highest_volume'))
                    ))
                    
        except Exception as e:
            logger.error(f"Error inserting historical prices for {symbol}: {e}")
    
    def insert_dividends(self, symbol, dividend_data):
        """Insert dividend data"""
        try:
            if dividend_data.get('available', False):
                data = dividend_data.get('data', {})
                for date_str, amount in data.items():
                    self.cursor.execute('''
                    INSERT OR REPLACE INTO dividends (symbol, dividend_date, dividend_amount)
                    VALUES (?, ?, ?)
                    ''', (symbol, date_str, self.safe_float(amount)))
                    
        except Exception as e:
            logger.error(f"Error inserting dividends for {symbol}: {e}")
    
    def insert_stock_splits(self, symbol, splits_data):
        """Insert stock split data"""
        try:
            if splits_data.get('available', False):
                data = splits_data.get('data', {})
                for date_str, ratio in data.items():
                    self.cursor.execute('''
                    INSERT OR REPLACE INTO stock_splits (symbol, split_date, split_ratio)
                    VALUES (?, ?, ?)
                    ''', (symbol, date_str, self.safe_float(ratio)))
                    
        except Exception as e:
            logger.error(f"Error inserting stock splits for {symbol}: {e}")
    
    def insert_valuation_metrics(self, symbol, metrics):
        """Insert valuation metrics"""
        try:
            self.cursor.execute('''
            INSERT OR REPLACE INTO valuation_metrics (
                symbol, pe_ratio, forward_pe, peg_ratio, price_to_book,
                price_to_sales, enterprise_to_revenue, enterprise_to_ebitda, book_value
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                symbol,
                self.safe_float(metrics.get('pe_ratio')),
                self.safe_float(metrics.get('forward_pe')),
                self.safe_float(metrics.get('peg_ratio')),
                self.safe_float(metrics.get('price_to_book')),
                self.safe_float(metrics.get('price_to_sales')),
                self.safe_float(metrics.get('enterprise_to_revenue')),
                self.safe_float(metrics.get('enterprise_to_ebitda')),
                self.safe_float(metrics.get('book_value'))
            ))
            
        except Exception as e:
            logger.error(f"Error inserting valuation metrics for {symbol}: {e}")
    
    def insert_financial_health(self, symbol, health_data):
        """Insert financial health metrics"""
        try:
            self.cursor.execute('''
            INSERT OR REPLACE INTO financial_health (
                symbol, total_revenue, revenue_per_share, profit_margins, operating_margins,
                return_on_assets, return_on_equity, total_cash, total_debt,
                debt_to_equity, current_ratio, quick_ratio
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                symbol,
                self.safe_float(health_data.get('total_revenue')),
                self.safe_float(health_data.get('revenue_per_share')),
                self.safe_float(health_data.get('profit_margins')),
                self.safe_float(health_data.get('operating_margins')),
                self.safe_float(health_data.get('return_on_assets')),
                self.safe_float(health_data.get('return_on_equity')),
                self.safe_float(health_data.get('total_cash')),
                self.safe_float(health_data.get('total_debt')),
                self.safe_float(health_data.get('debt_to_equity')),
                self.safe_float(health_data.get('current_ratio')),
                self.safe_float(health_data.get('quick_ratio'))
            ))
            
        except Exception as e:
            logger.error(f"Error inserting financial health for {symbol}: {e}")
    
    def insert_earnings(self, symbol, earnings_data):
        """Insert earnings data"""
        try:
            if earnings_data.get('available', False):
                # Annual earnings
                annual_earnings = earnings_data.get('annual_earnings', {})
                if annual_earnings.get('available', False):
                    data = annual_earnings.get('data', {})
                    for year, values in data.items():
                        if isinstance(values, dict):
                            self.cursor.execute('''
                            INSERT OR REPLACE INTO earnings (symbol, period_type, period_date, earnings, revenue)
                            VALUES (?, ?, ?, ?, ?)
                            ''', (
                                symbol, 'annual', str(year),
                                self.safe_float(values.get('Earnings')),
                                self.safe_float(values.get('Revenue'))
                            ))
                
                # Quarterly earnings
                quarterly_earnings = earnings_data.get('quarterly_earnings', {})
                if quarterly_earnings.get('available', False):
                    data = quarterly_earnings.get('data', {})
                    for quarter, values in data.items():
                        if isinstance(values, dict):
                            self.cursor.execute('''
                            INSERT OR REPLACE INTO earnings (symbol, period_type, period_date, earnings, revenue)
                            VALUES (?, ?, ?, ?, ?)
                            ''', (
                                symbol, 'quarterly', str(quarter),
                                self.safe_float(values.get('Earnings')),
                                self.safe_float(values.get('Revenue'))
                            ))
                            
        except Exception as e:
            logger.error(f"Error inserting earnings for {symbol}: {e}")
    
    def import_financial_report(self, symbol, report):
        """Import a complete financial report for a symbol"""
        try:
            logger.info(f"Importing financial data for {symbol}")
            
            # Insert company data
            self.insert_company_data(symbol, report)
            
            # Insert financial statements
            financial_statements = report.get('financial_statements', {})
            
            # Annual statements
            annual = financial_statements.get('annual', {})
            if annual:
                self.insert_income_statements(symbol, annual.get('income_statement', {}), 'annual_income_statements')
                self.insert_balance_sheets(symbol, annual.get('balance_sheet', {}), 'annual_balance_sheets')
                self.insert_cash_flows(symbol, annual.get('cash_flow', {}), 'annual_cash_flows')
            
            # Quarterly statements
            quarterly = financial_statements.get('quarterly', {})
            if quarterly:
                self.insert_income_statements(symbol, quarterly.get('income_statement', {}), 'quarterly_income_statements')
                self.insert_balance_sheets(symbol, quarterly.get('balance_sheet', {}), 'quarterly_balance_sheets')
                self.insert_cash_flows(symbol, quarterly.get('cash_flow', {}), 'quarterly_cash_flows')
            
            # Historical prices
            historical_prices = report.get('historical_prices', {})
            if historical_prices:
                self.insert_historical_prices(symbol, historical_prices)
            
            # Corporate actions
            corporate_actions = report.get('corporate_actions', {})
            if corporate_actions:
                self.insert_dividends(symbol, corporate_actions.get('dividends', {}))
                self.insert_stock_splits(symbol, corporate_actions.get('splits', {}))
            
            # Valuation metrics
            valuation_metrics = report.get('valuation_metrics', {})
            if valuation_metrics:
                self.insert_valuation_metrics(symbol, valuation_metrics)
            
            # Financial health
            financial_health = report.get('financial_health', {})
            if financial_health:
                self.insert_financial_health(symbol, financial_health)
            
            # Earnings
            earnings = report.get('earnings', {})
            if earnings:
                self.insert_earnings(symbol, earnings)
            
            self.conn.commit()
            logger.info(f"Successfully imported financial data for {symbol}")
            
        except Exception as e:
            logger.error(f"Error importing financial report for {symbol}: {e}")
            self.conn.rollback()
    
    def import_from_json_file(self, json_file_path):
        """Import financial data from a JSON file"""
        try:
            logger.info(f"Starting import from JSON file: {json_file_path}")
            
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            total_companies = len(data)
            successful_imports = 0
            failed_imports = 0
            
            for symbol, report in data.items():
                try:
                    if 'error' not in report:
                        self.import_financial_report(symbol, report)
                        successful_imports += 1
                    else:
                        logger.warning(f"Skipping {symbol} due to error in report: {report.get('error')}")
                        failed_imports += 1
                except Exception as e:
                    logger.error(f"Failed to import {symbol}: {e}")
                    failed_imports += 1
            
            logger.info(f"Import completed: {successful_imports} successful, {failed_imports} failed out of {total_companies} total")
            return successful_imports, failed_imports
            
        except Exception as e:
            logger.error(f"Error importing from JSON file: {e}")
            return 0, 0
    
    def get_database_stats(self):
        """Get statistics about the database"""
        try:
            stats = {}
            
            # Count records in each table
            tables = [
                'companies', 'annual_income_statements', 'quarterly_income_statements',
                'annual_balance_sheets', 'quarterly_balance_sheets', 'annual_cash_flows',
                'quarterly_cash_flows', 'historical_prices', 'dividends', 'stock_splits',
                'valuation_metrics', 'financial_health', 'earnings'
            ]
            
            for table in tables:
                self.cursor.execute(f'SELECT COUNT(*) FROM {table}')
                count = self.cursor.fetchone()[0]
                stats[table] = count
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {}

# Main execution functions
def import_financial_data_to_db(json_file_path, db_path='financial_data.db'):
    """
    Import financial data from JSON file to SQLite database
    
    Args:
        json_file_path (str): Path to the JSON file with financial data
        db_path (str): Path to the SQLite database
    
    Returns:
        tuple: (successful_imports, failed_imports)
    """
    db = FinancialDataDB(db_path)
    
    try:
        db.connect()
        db.create_tables()
        successful, failed = db.import_from_json_file(json_file_path)
        
        # Print statistics
        stats = db.get_database_stats()
        print("\n" + "="*60)
        print("DATABASE IMPORT COMPLETED")
        print("="*60)
        print(f"Successful imports: {successful}")
        print(f"Failed imports: {failed}")
        print("\nDatabase Statistics:")
        for table, count in stats.items():
            print(f"  {table}: {count} records")
        
        return successful, failed
        
    finally:
        db.close()

if __name__ == "__main__":
    # Example usage
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    else:
        # Look for the most recent financial reports file
        import glob
        files = glob.glob('*financial_statements_all_*.json') + glob.glob('*complete_historical_financials_all_*.json')
        if files:
            json_file = max(files, key=os.path.getctime)
            print(f"Using most recent financial data file: {json_file}")
        else:
            print("No financial data JSON files found!")
            print("Please run the financial reports generator first or specify a JSON file path.")
            sys.exit(1)
    
    # Import the data
    import_financial_data_to_db(json_file)