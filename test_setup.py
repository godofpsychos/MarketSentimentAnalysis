#!/usr/bin/env python3
"""
Test script to verify the Market Sentiment Analysis application setup
with advanced fundamental analysis visualizations.
"""

import os
import json
import requests
import sys
from pathlib import Path

def test_file_structure():
    """Test if all required files are in place"""
    print("🔍 Testing file structure...")
    
    required_files = [
        'frontend/src/FundamentalDashboard.js',
        'frontend/src/FundamentalDashboard.css',
        'frontend/src/AdvancedCharts.js',
        'backend_api.py',
        'FundamentalAnalysis/run_all_indicators.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    else:
        print("✅ All required files are present")
        return True

def test_financial_data():
    """Test if financial data files are available"""
    print("\n📊 Testing financial data availability...")
    
    data_dir = Path("financial_reports/data")
    if not data_dir.exists():
        print("❌ Financial data directory not found")
        return False
    
    json_files = list(data_dir.glob("*_financial_data.json"))
    if len(json_files) == 0:
        print("❌ No financial data files found")
        return False
    
    # Test loading a sample file
    try:
        sample_file = json_files[0]
        with open(sample_file, 'r') as f:
            data = json.load(f)
        
        required_keys = ['companyInfo', 'valuationMetrics', 'annualIncomeStatement', 'annualBalanceSheet']
        missing_keys = [key for key in required_keys if key not in data]
        
        if missing_keys:
            print(f"❌ Sample file missing keys: {missing_keys}")
            return False
        
        print(f"✅ Found {len(json_files)} financial data files")
        print(f"✅ Sample file structure is valid: {sample_file.name}")
        return True
        
    except Exception as e:
        print(f"❌ Error reading financial data: {e}")
        return False

def test_npm_dependencies():
    """Test if npm dependencies are installed"""
    print("\n📦 Testing npm dependencies...")
    
    package_json_path = Path("frontend/package.json")
    if not package_json_path.exists():
        print("❌ package.json not found")
        return False
    
    with open(package_json_path, 'r') as f:
        package_data = json.load(f)
    
    required_deps = [
        'react-chartjs-2',
        'chart.js',
        'framer-motion',
        'recharts'
    ]
    
    installed_deps = list(package_data.get('dependencies', {}).keys())
    missing_deps = [dep for dep in required_deps if dep not in installed_deps]
    
    if missing_deps:
        print(f"❌ Missing npm dependencies: {missing_deps}")
        print("Run: cd frontend && npm install --save " + " ".join(missing_deps))
        return False
    else:
        print("✅ All required npm dependencies are installed")
        return True

def test_api_endpoints():
    """Test if API endpoints are working"""
    print("\n🌐 Testing API endpoints...")
    
    base_url = os.getenv('BACKEND_URL', "http://localhost:5000")
    endpoints = [
        "/api/stocks",
        "/api/available-sectors",
        "/api/fundamental-summary"
    ]
    
    working_endpoints = []
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                working_endpoints.append(endpoint)
                print(f"✅ {endpoint} - Working")
            else:
                print(f"❌ {endpoint} - Status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ {endpoint} - Connection failed: {e}")
    
    if len(working_endpoints) == len(endpoints):
        print("✅ All API endpoints are working")
        return True
    else:
        print(f"⚠️  {len(working_endpoints)}/{len(endpoints)} endpoints working")
        print("Make sure the backend server is running: python backend_api.py")
        return False

def print_usage_instructions():
    """Print usage instructions"""
    print("\n" + "="*60)
    print("🚀 MARKET SENTIMENT ANALYSIS WITH ADVANCED VISUALIZATIONS")
    print("="*60)
    print("\n📋 To start the application:")
    print("1. Backend: python backend_api.py")
    print("2. Frontend: cd frontend && npm start")
    print("\n🎯 Features:")
    print("• 📊 Sentiment Analysis Dashboard")
    print("• 📈 Advanced Fundamental Analysis")
    print("• 🎨 Interactive Visualizations (Recharts + Chart.js)")
    print("• 📱 Responsive Design with Animations")
    print("• 🔄 Real-time Data Updates")
    print("\n🎪 Visualization Types:")
    print("• 📈 Line & Area Charts (Trends)")
    print("• 📊 Bar & Column Charts (Comparisons)")
    print("• 🥧 Pie & Doughnut Charts (Compositions)")
    print("• 🕸️  Radar Charts (Multi-metric Analysis)")
    print("• 🎯 Bubble Charts (Risk vs Return)")
    print("• 🌡️  Heatmaps (Performance)")
    print("• ⚡ Multi-axis Charts (Complex Metrics)")
    print("• 🎚️  Gauge Charts (Health Scores)")
    print("\n📊 Analysis Categories:")
    print("• 💰 Profitability (ROE, ROA, Margins)")
    print("• 💎 Valuation (P/E, P/B, DCF)")
    print("• 📈 Growth (Revenue, Earnings)")
    print("• 💧 Liquidity (Current, Quick Ratios)")
    print("• ⚖️  Leverage (Debt Ratios)")
    print("• 🏆 Sector Comparisons")

def main():
    """Main test function"""
    print("🧪 Testing Market Sentiment Analysis Setup\n")
    
    tests = [
        test_file_structure,
        test_financial_data,
        test_npm_dependencies,
        test_api_endpoints
    ]
    
    passed_tests = 0
    for test in tests:
        if test():
            passed_tests += 1
    
    print(f"\n📊 Test Results: {passed_tests}/{len(tests)} tests passed")
    
    if passed_tests == len(tests):
        print("🎉 All tests passed! The application is ready to use.")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
    
    print_usage_instructions()

if __name__ == "__main__":
    main() 