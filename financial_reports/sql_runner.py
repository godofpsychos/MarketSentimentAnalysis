#!/usr/bin/env python3
"""
Simple SQL Runner for Financial Database
Executes a single query to fetch data from financial_data.db
"""

import sqlite3
import pandas as pd
from pathlib import Path

def fetch_financial_data():
    """Fetch financial data from the database"""
    
    # Database path
    db_path = 'financial_reports/financial_data.db'
    
    # Check if database exists
    if not Path(db_path).exists():
        print(f"❌ Database not found: {db_path}")
        print("Please run the financial reports pipeline first!")
        return None
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        print(f"✅ Connected to database: {db_path}")
        
        # Read stocksList.csv to get the exact stocks to include
        import pandas as pd
        stocks_df = pd.read_csv('stocksList.csv')
        stock_symbols = stocks_df['SYMBOL'].str.strip().tolist()
        
        # Handle SBI/SBIN duplicate - use SBIN as it has the financial data
        if 'SBI' in stock_symbols and 'SBIN' in stock_symbols:
            stock_symbols = [s for s in stock_symbols if s != 'SBI']  # Remove SBI, keep SBIN
            print("📋 Note: Using SBIN instead of SBI (same company, SBIN has financial data)")
        
        symbols_str = "', '".join(stock_symbols)
        print(f"📋 Processing {len(stock_symbols)} stocks from stocksList.csv")
        
        # SQL Query to fetch ALL revenue, expenditure, and net profit data for stocks in stocksList.csv
        query = f"""
        SELECT 
            ais.symbol,
            c.name as company_name,
            ais.period_date,
            MAX(CASE WHEN ais.field_name = 'Total Revenue' THEN ais.value END) as total_revenue,
            MAX(CASE WHEN ais.field_name = 'Operating Expense' THEN ais.value END) as total_expenditure,
            MAX(CASE WHEN ais.field_name = 'Net Income' THEN ais.value END) as net_profit
        FROM annual_income_statements ais
        JOIN companies c ON ais.symbol = c.symbol
        WHERE ais.field_name IN ('Total Revenue', 'Operating Expense', 'Net Income')
        AND ais.symbol IN ('{symbols_str}')
        GROUP BY ais.symbol, c.name, ais.period_date
        HAVING MAX(CASE WHEN ais.field_name = 'Total Revenue' THEN ais.value END) IS NOT NULL
        ORDER BY ais.symbol, ais.period_date DESC;
        """
        
        print(f"📊 Executing query: ALL Historical Data for {len(stock_symbols)} stocks from stocksList.csv")
        print("=" * 60)
        
        # Execute query and fetch results
        df = pd.read_sql_query(query, conn)
        
        # Display results
        if not df.empty:
            print(f"✅ Query successful! Found {len(df)} records")
            print("\n📋 Sample of first 10 results:")
            print("=" * 60)
            print(df.head(10).to_string(index=False))
            
            # Save to CSV
            output_file = 'report.csv'
            df.to_csv(output_file, index=False)
            print(f"\n💾 Complete dataset with {len(df)} records saved to: {output_file}")
            
        else:
            print("❌ No data found")
        
        # Close connection
        conn.close()
        print("\n🔌 Database connection closed")
        
        return df
        
    except Exception as e:
        print(f"❌ Error executing query: {e}")
        return None

def main():
    """Main function"""
    print("🗃️  Financial Database SQL Runner")
    print("=" * 50)
    
    # Fetch and display data
    results = fetch_financial_data()
    
    if results is not None:
        print(f"\n🎉 Query completed successfully!")
        print(f"📊 Retrieved {len(results)} company records")
    else:
        print(f"\n❌ Query failed!")

if __name__ == "__main__":
    main() 