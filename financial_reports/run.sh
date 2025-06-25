#!/bin/bash

# Financial Reports Pipeline
# This script runs the complete pipeline:
# 1. Fetch financial data from yfinance and save as JSON files
# 2. Import JSON files into SQLite database
# 3. Show summary and provide query tool access

set -e  # Exit on any error

echo "🚀 Financial Reports Pipeline"
echo "=============================================="

# Check if we're in virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  You're not in a virtual environment!"
    echo "Please activate your virtual environment first:"
    echo "source .venv/bin/activate"
    exit 1
fi

echo "✅ Virtual environment detected: $VIRTUAL_ENV"

# Change to the project root directory
cd "$(dirname "$0")/.."

# Check if stocksList.csv exists
if [[ ! -f "stocksList.csv" ]]; then
    echo "❌ stocksList.csv not found!"
    echo "Please ensure stocksList.csv is in the project root directory"
    exit 1
fi

echo "✅ Found stocksList.csv"

# Step 1: Fetch financial data
echo ""
echo "📊 Step 1: Fetching Financial Data from yfinance..."
echo "=================================================="
python3 financial_reports/fetch_financial_data.py

if [[ $? -ne 0 ]]; then
    echo "❌ Failed to fetch financial data"
    exit 1
fi

echo "✅ Financial data fetching completed"

# Step 2: Import to database
echo ""
echo "💾 Step 2: Importing Data to SQLite Database..."
echo "=============================================="
python3 financial_reports/database.py

if [[ $? -ne 0 ]]; then
    echo "❌ Failed to import data to database"
    exit 1
fi

echo "✅ Database import completed"

# Step 3: Show summary
echo ""
echo "🎉 PIPELINE COMPLETED SUCCESSFULLY!"
echo "=================================="
echo "📁 JSON files location: financial_reports/data/"
echo "💾 Database location: financial_reports/financial_data.db"
echo "📋 Log files: financial_reports/*.log"
echo ""
echo "🔍 To explore the data:"
echo "  python3 financial_reports/query_database.py"
echo ""
echo "🧪 Test specific company:"
echo "  python3 financial_reports/test_data.py RELIANCE"
echo ""

# Optional: Run quick test
read -p "🧪 Do you want to run a quick test? [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Running quick test..."
    python3 financial_reports/test_data.py RELIANCE
fi

echo "✨ Pipeline completed successfully! ✨" 