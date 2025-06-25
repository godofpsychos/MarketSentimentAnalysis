#!/usr/bin/env python3
"""
Test Script for Financial Data
Quick test to verify data for a specific company
"""

import sys
import json
import sqlite3
from pathlib import Path

def test_json_data(symbol):
    """Test JSON data for a symbol"""
    json_file = f"financial_reports/data/{symbol}_financial_data.json"
    
    if not Path(json_file).exists():
        print(f"❌ JSON file not found: {json_file}")
        return False
    
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        print(f"✅ JSON file loaded successfully")
        print(f"📊 Company: {data.get('company_info', {}).get('name', 'N/A')}")
        print(f"🏢 Sector: {data.get('company_info', {}).get('sector', 'N/A')}")
        
        # Check data summary
        summary = data.get('data_summary', {})
        print(f"📈 Annual periods: {summary.get('annual_financial_periods', 0)}")
        print(f"📈 Quarterly periods: {summary.get('quarterly_financial_periods', 0)}")
        print(f"💰 Dividend records: {summary.get('dividend_records', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading JSON: {e}")
        return False

def test_database_data(symbol):
    """Test database data for a symbol"""
    db_file = "financial_reports/financial_data.db"
    
    if not Path(db_file).exists():
        print(f"❌ Database not found: {db_file}")
        return False
    
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Check if company exists
        cursor.execute("SELECT * FROM companies WHERE symbol = ?", (symbol,))
        company = cursor.fetchone()
        
        if not company:
            print(f"❌ Company not found in database: {symbol}")
            return False
        
        print(f"✅ Company found in database")
        
        # Check financial statements
        cursor.execute("SELECT COUNT(*) FROM annual_income_statements WHERE symbol = ?", (symbol,))
        annual_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM quarterly_income_statements WHERE symbol = ?", (symbol,))
        quarterly_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM historical_prices WHERE symbol = ?", (symbol,))
        price_count = cursor.fetchone()[0]
        
        print(f"📈 Annual financial records: {annual_count}")
        print(f"📈 Quarterly financial records: {quarterly_count}")
        print(f"💰 Historical price records: {price_count}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error reading database: {e}")
        return False

def main():
    """Main test function"""
    if len(sys.argv) < 2:
        print("Usage: python test_data.py <SYMBOL>")
        print("Example: python test_data.py RELIANCE")
        sys.exit(1)
    
    symbol = sys.argv[1].upper()
    
    print(f"🧪 Testing Financial Data for {symbol}")
    print("=" * 50)
    
    print("\n📁 Testing JSON Data...")
    json_ok = test_json_data(symbol)
    
    print("\n💾 Testing Database Data...")
    db_ok = test_database_data(symbol)
    
    print("\n" + "=" * 50)
    if json_ok and db_ok:
        print(f"✅ All tests passed for {symbol}!")
    else:
        print(f"❌ Some tests failed for {symbol}")
        sys.exit(1)

if __name__ == "__main__":
    main() 