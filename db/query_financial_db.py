#!/usr/bin/env python3
"""
Financial Database Query Tool
Simple tool to query financial data from SQLite database
"""

import sqlite3
import sys
import os
from datetime import datetime
import pandas as pd

class FinancialDBQuery:
    def __init__(self, db_path='financial_data.db'):
        """Initialize the query tool"""
        self.db_path = db_path
        self.conn = None
    
    def connect(self):
        """Connect to the database"""
        try:
            if not os.path.exists(self.db_path):
                print(f"❌ Database not found: {self.db_path}")
                print("Please run the database import first: python run_financial_db_import.py")
                return False
            
            self.conn = sqlite3.connect(self.db_path)
            return True
        except Exception as e:
            print(f"❌ Error connecting to database: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def execute_query(self, query, description=""):
        """Execute a query and return results"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            
            if description:
                print(f"\n📊 {description}")
                print("-" * 50)
            
            if not results:
                print("No data found.")
                return
            
            # Create a simple table display
            df = pd.DataFrame(results, columns=columns)
            print(df.to_string(index=False))
            print(f"\nTotal records: {len(results)}")
            
        except Exception as e:
            print(f"❌ Error executing query: {e}")
    
    def show_database_overview(self):
        """Show overview of the database"""
        print("🗄️  DATABASE OVERVIEW")
        print("=" * 60)
        
        # Count records in each table
        tables = [
            'companies', 'annual_income_statements', 'quarterly_income_statements',
            'annual_balance_sheets', 'quarterly_balance_sheets', 'annual_cash_flows',
            'quarterly_cash_flows', 'historical_prices', 'dividends', 'stock_splits',
            'valuation_metrics', 'financial_health', 'earnings'
        ]
        
        for table in tables:
            try:
                cursor = self.conn.cursor()
                cursor.execute(f'SELECT COUNT(*) FROM {table}')
                count = cursor.fetchone()[0]
                print(f"  {table}: {count} records")
            except:
                print(f"  {table}: Table not found")
    
    def show_top_companies_by_market_cap(self, limit=10):
        """Show top companies by market cap"""
        query = f"""
        SELECT symbol, company_name, sector, 
               ROUND(market_cap/10000000, 2) as market_cap_crores
        FROM companies 
        WHERE market_cap IS NOT NULL 
        ORDER BY market_cap DESC 
        LIMIT {limit}
        """
        self.execute_query(query, f"Top {limit} Companies by Market Cap (₹ Crores)")
    
    def show_latest_revenue_data(self, limit=10):
        """Show latest revenue data"""
        query = f"""
        SELECT c.symbol, c.company_name, a.period_date, 
               ROUND(a.total_revenue/10000000, 2) as revenue_crores,
               ROUND(a.net_income/10000000, 2) as profit_crores
        FROM annual_income_statements a
        JOIN companies c ON a.symbol = c.symbol
        WHERE a.total_revenue IS NOT NULL
        ORDER BY a.period_date DESC, a.total_revenue DESC
        LIMIT {limit}
        """
        self.execute_query(query, f"Latest Revenue Data (₹ Crores)")
    
    def show_quarterly_performance(self, symbol, limit=8):
        """Show quarterly performance for a specific company"""
        query = f"""
        SELECT period_date, 
               ROUND(total_revenue/10000000, 2) as revenue_crores,
               ROUND(net_income/10000000, 2) as profit_crores,
               ROUND(gross_profit/10000000, 2) as gross_profit_crores
        FROM quarterly_income_statements
        WHERE symbol = '{symbol}' AND total_revenue IS NOT NULL
        ORDER BY period_date DESC
        LIMIT {limit}
        """
        self.execute_query(query, f"Quarterly Performance for {symbol} (₹ Crores)")
    
    def show_financial_health_metrics(self, limit=10):
        """Show financial health metrics"""
        query = f"""
        SELECT c.symbol, c.company_name,
               ROUND(f.profit_margins * 100, 2) as profit_margin_percent,
               ROUND(f.return_on_equity * 100, 2) as roe_percent,
               ROUND(f.debt_to_equity, 2) as debt_to_equity_ratio,
               ROUND(f.current_ratio, 2) as current_ratio
        FROM financial_health f
        JOIN companies c ON f.symbol = c.symbol
        WHERE f.profit_margins IS NOT NULL
        ORDER BY f.return_on_equity DESC
        LIMIT {limit}
        """
        self.execute_query(query, f"Financial Health Metrics (Top {limit} by ROE)")
    
    def show_dividend_history(self, symbol):
        """Show dividend history for a company"""
        query = f"""
        SELECT dividend_date, dividend_amount
        FROM dividends
        WHERE symbol = '{symbol}'
        ORDER BY dividend_date DESC
        """
        self.execute_query(query, f"Dividend History for {symbol}")
    
    def show_sector_analysis(self):
        """Show sector-wise analysis"""
        query = """
        SELECT sector, 
               COUNT(*) as companies_count,
               ROUND(AVG(market_cap)/10000000, 2) as avg_market_cap_crores,
               ROUND(AVG(profit_margins) * 100, 2) as avg_profit_margin_percent
        FROM companies c
        LEFT JOIN financial_health f ON c.symbol = f.symbol
        WHERE sector != 'N/A' AND sector IS NOT NULL
        GROUP BY sector
        ORDER BY avg_market_cap_crores DESC
        """
        self.execute_query(query, "Sector-wise Analysis")
    
    def show_price_performance(self, limit=10):
        """Show price performance"""
        query = f"""
        SELECT c.symbol, c.company_name, h.period_type,
               ROUND(h.price_change_percent, 2) as price_change_percent,
               ROUND(h.latest_price, 2) as latest_price
        FROM historical_prices h
        JOIN companies c ON h.symbol = c.symbol
        WHERE h.period_type = '1y' AND h.price_change_percent IS NOT NULL
        ORDER BY h.price_change_percent DESC
        LIMIT {limit}
        """
        self.execute_query(query, f"Top {limit} Price Performers (1 Year)")
    
    def custom_query(self, query):
        """Execute a custom query"""
        self.execute_query(query, "Custom Query Results")

def main():
    """Main function with interactive menu"""
    print("💰 FINANCIAL DATABASE QUERY TOOL")
    print("=" * 60)
    
    # Initialize query tool
    query_tool = FinancialDBQuery('db/financial_data.db')
    
    if not query_tool.connect():
        sys.exit(1)
    
    try:
        while True:
            print("\n📋 AVAILABLE QUERIES:")
            print("1. Database Overview")
            print("2. Top Companies by Market Cap")
            print("3. Latest Revenue Data")
            print("4. Quarterly Performance (specific company)")
            print("5. Financial Health Metrics")
            print("6. Dividend History (specific company)")
            print("7. Sector Analysis")
            print("8. Price Performance")
            print("9. Custom SQL Query")
            print("0. Exit")
            
            choice = input("\nEnter your choice (0-9): ").strip()
            
            if choice == '0':
                break
            elif choice == '1':
                query_tool.show_database_overview()
            elif choice == '2':
                limit = input("Number of companies to show (default 10): ").strip()
                limit = int(limit) if limit.isdigit() else 10
                query_tool.show_top_companies_by_market_cap(limit)
            elif choice == '3':
                limit = input("Number of records to show (default 10): ").strip()
                limit = int(limit) if limit.isdigit() else 10
                query_tool.show_latest_revenue_data(limit)
            elif choice == '4':
                symbol = input("Enter company symbol (e.g., RELIANCE): ").strip().upper()
                if symbol:
                    query_tool.show_quarterly_performance(symbol)
            elif choice == '5':
                limit = input("Number of companies to show (default 10): ").strip()
                limit = int(limit) if limit.isdigit() else 10
                query_tool.show_financial_health_metrics(limit)
            elif choice == '6':
                symbol = input("Enter company symbol (e.g., RELIANCE): ").strip().upper()
                if symbol:
                    query_tool.show_dividend_history(symbol)
            elif choice == '7':
                query_tool.show_sector_analysis()
            elif choice == '8':
                limit = input("Number of companies to show (default 10): ").strip()
                limit = int(limit) if limit.isdigit() else 10
                query_tool.show_price_performance(limit)
            elif choice == '9':
                print("\nEnter your SQL query (press Enter twice to execute):")
                lines = []
                while True:
                    line = input()
                    if line.strip() == "" and lines:
                        break
                    lines.append(line)
                
                custom_query = '\n'.join(lines)
                if custom_query.strip():
                    query_tool.custom_query(custom_query)
            else:
                print("❌ Invalid choice. Please try again.")
    
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    finally:
        query_tool.close()

if __name__ == "__main__":
    # Check if pandas is available
    try:
        import pandas as pd
    except ImportError:
        print("❌ pandas is required for this tool.")
        print("Install it with: pip install pandas")
        sys.exit(1)
    
    main() 