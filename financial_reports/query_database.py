#!/usr/bin/env python3
"""
Financial Database Query Tool
Simple tool to query and explore the financial database
"""

import sqlite3
import pandas as pd
from pathlib import Path

class FinancialQueryTool:
    def __init__(self, db_path='financial_reports/financial_data.db'):
        self.db_path = db_path
        self.conn = None
        self.connect()
    
    def connect(self):
        """Connect to database"""
        if not Path(self.db_path).exists():
            print(f"❌ Database not found: {self.db_path}")
            print("Please run the data fetch and import pipeline first!")
            return False
        
        self.conn = sqlite3.connect(self.db_path)
        print(f"✅ Connected to database: {self.db_path}")
        return True
    
    def show_companies(self, limit=10):
        """Show all companies in database"""
        try:
            df = pd.read_sql_query(f"""
                SELECT symbol, name, sector, industry, market_cap_formatted, current_price
                FROM companies 
                ORDER BY market_cap DESC
                LIMIT {limit}
            """, self.conn)
            
            print(f"\n📊 Top {limit} Companies by Market Cap:")
            print("=" * 80)
            print(df.to_string(index=False))
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def show_company_details(self, symbol):
        """Show detailed information for a specific company"""
        try:
            # Company basic info
            df = pd.read_sql_query("""
                SELECT * FROM companies WHERE symbol = ?
            """, self.conn, params=[symbol])
            
            if df.empty:
                print(f"❌ No data found for symbol: {symbol}")
                return
            
            print(f"\n🏢 Company Details: {symbol}")
            print("=" * 60)
            company = df.iloc[0]
            print(f"Name: {company['name']}")
            print(f"Sector: {company['sector']}")
            print(f"Industry: {company['industry']}")
            print(f"Market Cap: {company['market_cap_formatted']}")
            print(f"Current Price: ₹{company['current_price']}")
            print(f"Employees: {company['employees']:,}" if company['employees'] else "Employees: N/A")
            
            # Financial statements summary
            annual_income = pd.read_sql_query("""
                SELECT COUNT(DISTINCT period_date) as periods 
                FROM annual_income_statements 
                WHERE symbol = ?
            """, self.conn, params=[symbol])
            
            quarterly_income = pd.read_sql_query("""
                SELECT COUNT(DISTINCT period_date) as periods 
                FROM quarterly_income_statements 
                WHERE symbol = ?
            """, self.conn, params=[symbol])
            
            print(f"\n📊 Financial Data Available:")
            print(f"Annual periods: {annual_income.iloc[0]['periods']}")
            print(f"Quarterly periods: {quarterly_income.iloc[0]['periods']}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def show_revenue_trends(self, symbol, limit=5):
        """Show revenue trends for a company"""
        try:
            df = pd.read_sql_query("""
                SELECT period_date, value, formatted_value
                FROM annual_income_statements 
                WHERE symbol = ? AND field_name LIKE '%Revenue%' OR field_name LIKE '%Total Revenue%'
                ORDER BY period_date DESC
                LIMIT ?
            """, self.conn, params=[symbol, limit])
            
            if df.empty:
                print(f"❌ No revenue data found for {symbol}")
                return
            
            print(f"\n📈 Revenue Trends for {symbol}:")
            print("=" * 50)
            print(df.to_string(index=False))
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def show_database_stats(self):
        """Show database statistics"""
        try:
            tables = [
                'companies', 'annual_income_statements', 'quarterly_income_statements',
                'annual_balance_sheets', 'quarterly_balance_sheets', 'annual_cash_flows',
                'quarterly_cash_flows', 'historical_prices', 'dividends', 'stock_splits',
                'valuation_metrics', 'financial_health', 'earnings'
            ]
            
            print(f"\n💾 Database Statistics:")
            print("=" * 50)
            
            for table in tables:
                try:
                    cursor = self.conn.cursor()
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    print(f"{table}: {count:,} records")
                except:
                    print(f"{table}: Error getting count")
                    
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def run_custom_query(self, query):
        """Run a custom SQL query"""
        try:
            df = pd.read_sql_query(query, self.conn)
            print(f"\n📋 Query Results:")
            print("=" * 60)
            print(df.to_string(index=False))
            
        except Exception as e:
            print(f"❌ Error executing query: {e}")
    
    def interactive_mode(self):
        """Interactive query mode"""
        print("\n🔍 Interactive Query Mode")
        print("=" * 50)
        print("Available commands:")
        print("  companies [limit] - Show companies")
        print("  details <symbol> - Show company details")
        print("  revenue <symbol> [limit] - Show revenue trends") 
        print("  stats - Show database statistics")
        print("  sql <query> - Run custom SQL query")
        print("  quit - Exit")
        print("=" * 50)
        
        while True:
            try:
                command = input("\n💡 Enter command: ").strip().split()
                
                if not command:
                    continue
                
                cmd = command[0].lower()
                
                if cmd == 'quit':
                    break
                elif cmd == 'companies':
                    limit = int(command[1]) if len(command) > 1 else 10
                    self.show_companies(limit)
                elif cmd == 'details':
                    if len(command) > 1:
                        self.show_company_details(command[1].upper())
                    else:
                        print("❌ Please provide a symbol: details RELIANCE")
                elif cmd == 'revenue':
                    if len(command) > 1:
                        symbol = command[1].upper()
                        limit = int(command[2]) if len(command) > 2 else 5
                        self.show_revenue_trends(symbol, limit)
                    else:
                        print("❌ Please provide a symbol: revenue RELIANCE")
                elif cmd == 'stats':
                    self.show_database_stats()
                elif cmd == 'sql':
                    if len(command) > 1:
                        query = ' '.join(command[1:])
                        self.run_custom_query(query)
                    else:
                        print("❌ Please provide a SQL query")
                else:
                    print("❌ Unknown command. Type 'quit' to exit.")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

def main():
    """Main function"""
    print("🗃️  Financial Database Query Tool")
    
    query_tool = FinancialQueryTool()
    
    if not query_tool.conn:
        return
    
    try:
        # Show basic stats first
        query_tool.show_database_stats()
        query_tool.show_companies(5)
        
        # Start interactive mode
        query_tool.interactive_mode()
        
    finally:
        query_tool.close()
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    main() 