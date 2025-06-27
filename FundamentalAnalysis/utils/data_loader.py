#!/usr/bin/env python3
"""
Data Loader Utility for Fundamental Analysis
Common functions to load and parse financial data from JSON files
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
import os
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class FinancialDataLoader:
    """Utility class to load and parse financial data"""
    
    def __init__(self, data_directory="../financial_reports/data"):
        self.data_dir = Path(data_directory)
        self.companies_data = {}
        self.companies_list = []
        
    def load_all_companies(self):
        """Load financial data for all companies"""
        print("📊 Loading financial data for all companies...")
        
        json_files = list(self.data_dir.glob("*.json"))
        print(f"Found {len(json_files)} companies")
        
        for json_file in json_files:
            try:
                symbol = json_file.stem.replace("_financial_data", "")
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.companies_data[symbol] = data
                    self.companies_list.append(symbol)
            except Exception as e:
                print(f"⚠️  Error loading {json_file}: {e}")
        
        print(f"✅ Successfully loaded {len(self.companies_data)} companies")
        return self.companies_data
    
    def get_company_info(self, symbol):
        """Get basic company information"""
        if symbol not in self.companies_data:
            return None
        
        data = self.companies_data[symbol]
        company_info = data.get('company_info', {})
        current_price = data.get('current_price_info', {})
        
        return {
            'symbol': symbol,
            'name': company_info.get('name', 'N/A'),
            'sector': company_info.get('sector', 'N/A'),
            'industry': company_info.get('industry', 'N/A'),
            'market_cap': company_info.get('market_cap', 0),
            'market_cap_formatted': company_info.get('market_cap_formatted', 'N/A'),
            'current_price': current_price.get('current_price', 0),
            'employees': company_info.get('employees', 0),
            'website': company_info.get('website', 'N/A'),
            'fetch_date': data.get('fetch_date', 'N/A')
        }
    
    def get_annual_income_statement(self, symbol, field_name=None):
        """Extract annual income statement data"""
        if symbol not in self.companies_data:
            return pd.DataFrame()
        
        data = self.companies_data[symbol]
        annual_data = data.get('financial_statements', {}).get('annual', {}).get('income_statement', {})
        
        if not annual_data:
            return pd.DataFrame()
        
        rows = []
        for period, fields in annual_data.items():
            if field_name:
                if field_name in fields:
                    rows.append({
                        'symbol': symbol,
                        'period': period,
                        'field': field_name,
                        'value': fields[field_name].get('value', np.nan),
                        'formatted': fields[field_name].get('formatted', 'N/A')
                    })
            else:
                for field, field_data in fields.items():
                    rows.append({
                        'symbol': symbol,
                        'period': period,
                        'field': field,
                        'value': field_data.get('value', np.nan),
                        'formatted': field_data.get('formatted', 'N/A')
                    })
        
        return pd.DataFrame(rows)
    
    def get_annual_balance_sheet(self, symbol, field_name=None):
        """Extract annual balance sheet data"""
        if symbol not in self.companies_data:
            return pd.DataFrame()
        
        data = self.companies_data[symbol]
        annual_data = data.get('financial_statements', {}).get('annual', {}).get('balance_sheet', {})
        
        if not annual_data:
            return pd.DataFrame()
        
        rows = []
        for period, fields in annual_data.items():
            if field_name:
                if field_name in fields:
                    rows.append({
                        'symbol': symbol,
                        'period': period,
                        'field': field_name,
                        'value': fields[field_name].get('value', np.nan),
                        'formatted': fields[field_name].get('formatted', 'N/A')
                    })
            else:
                for field, field_data in fields.items():
                    rows.append({
                        'symbol': symbol,
                        'period': period,
                        'field': field,
                        'value': field_data.get('value', np.nan),
                        'formatted': field_data.get('formatted', 'N/A')
                    })
        
        return pd.DataFrame(rows)
    
    def get_annual_cash_flow(self, symbol, field_name=None):
        """Extract annual cash flow statement data"""
        if symbol not in self.companies_data:
            return pd.DataFrame()
        
        data = self.companies_data[symbol]
        annual_data = data.get('financial_statements', {}).get('annual', {}).get('cash_flow', {})
        
        if not annual_data:
            return pd.DataFrame()
        
        rows = []
        for period, fields in annual_data.items():
            if field_name:
                if field_name in fields:
                    rows.append({
                        'symbol': symbol,
                        'period': period,
                        'field': field_name,
                        'value': fields[field_name].get('value', np.nan),
                        'formatted': fields[field_name].get('formatted', 'N/A')
                    })
            else:
                for field, field_data in fields.items():
                    rows.append({
                        'symbol': symbol,
                        'period': period,
                        'field': field,
                        'value': field_data.get('value', np.nan),
                        'formatted': field_data.get('formatted', 'N/A')
                    })
        
        return pd.DataFrame(rows)
    
    def get_valuation_metrics(self, symbol):
        """Get valuation metrics"""
        if symbol not in self.companies_data:
            return {}
        
        return self.companies_data[symbol].get('valuation_metrics', {})
    
    def get_financial_health(self, symbol):
        """Get financial health metrics"""
        if symbol not in self.companies_data:
            return {}
        
        return self.companies_data[symbol].get('financial_health', {})
    
    def get_dividends(self, symbol):
        """Get dividend history"""
        if symbol not in self.companies_data:
            return {}
        
        return self.companies_data[symbol].get('corporate_actions', {}).get('dividends', {})
    
    def get_specific_financial_item(self, symbol, statement_type, field_name, period_type='annual'):
        """Get specific financial statement item"""
        if symbol not in self.companies_data:
            return pd.DataFrame()
        
        data = self.companies_data[symbol]
        financial_data = data.get('financial_statements', {}).get(period_type, {}).get(statement_type, {})
        
        if not financial_data:
            return pd.DataFrame()
        
        rows = []
        for period, fields in financial_data.items():
            if field_name in fields:
                rows.append({
                    'symbol': symbol,
                    'period': period,
                    'value': fields[field_name].get('value', np.nan)
                })
        
        df = pd.DataFrame(rows)
        if not df.empty:
            df['period'] = pd.to_datetime(df['period'])
            df = df.sort_values('period')
        
        return df
    
    def get_financial_summary(self, symbol):
        """Get financial summary for a company"""
        if symbol not in self.companies_data:
            return None
        
        company_info = self.get_company_info(symbol)
        valuation = self.get_valuation_metrics(symbol)
        health = self.get_financial_health(symbol)
        
        # Get key financial figures
        revenue = self.get_specific_financial_item(symbol, 'income_statement', 'Total Revenue')
        net_income = self.get_specific_financial_item(symbol, 'income_statement', 'Net Income')
        total_assets = self.get_specific_financial_item(symbol, 'balance_sheet', 'Total Assets')
        shareholders_equity = self.get_specific_financial_item(symbol, 'balance_sheet', 'Stockholders Equity')
        
        return {
            'company_info': company_info,
            'valuation_metrics': valuation,
            'financial_health': health,
            'latest_revenue': revenue['value'].iloc[-1] if not revenue.empty else np.nan,
            'latest_net_income': net_income['value'].iloc[-1] if not net_income.empty else np.nan,
            'latest_total_assets': total_assets['value'].iloc[-1] if not total_assets.empty else np.nan,
            'latest_equity': shareholders_equity['value'].iloc[-1] if not shareholders_equity.empty else np.nan
        }
    
    def create_output_directory(self, output_dir):
        """Create output directory if it doesn't exist"""
        Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    def save_results(self, data, filename, output_dir, file_type='csv'):
        """Save results to file"""
        self.create_output_directory(output_dir)
        
        if file_type == 'csv' and isinstance(data, pd.DataFrame):
            filepath = Path(output_dir) / f"{filename}.csv"
            data.to_csv(filepath, index=False)
        elif file_type == 'json':
            filepath = Path(output_dir) / f"{filename}.json"
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        else:
            filepath = Path(output_dir) / f"{filename}.txt"
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(str(data))
        
        print(f"✅ Saved {file_type.upper()} output: {filepath}")
    
    def get_companies_by_sector(self, sector_name):
        """Get companies filtered by sector"""
        companies = []
        for symbol in self.companies_list:
            company_info = self.get_company_info(symbol)
            if company_info and sector_name.lower() in company_info['sector'].lower():
                companies.append(symbol)
        return companies
    
    def get_all_sectors(self):
        """Get list of all sectors"""
        sectors = set()
        for symbol in self.companies_list:
            company_info = self.get_company_info(symbol)
            if company_info:
                sectors.add(company_info['sector'])
        return list(sectors)

# Utility functions for common calculations
def safe_divide(numerator, denominator):
    """Safe division handling zero denominators"""
    if pd.isna(numerator) or pd.isna(denominator) or denominator == 0:
        return np.nan
    return numerator / denominator

def calculate_percentage_change(current, previous):
    """Calculate percentage change"""
    if pd.isna(current) or pd.isna(previous) or previous == 0:
        return np.nan
    return ((current - previous) / previous) * 100

def format_number(number, decimals=2):
    """Format number for display"""
    if pd.isna(number):
        return "N/A"
    return f"{number:,.{decimals}f}"

def format_percentage(number, decimals=2):
    """Format percentage for display"""
    if pd.isna(number):
        return "N/A"
    return f"{number:.{decimals}f}%"

def format_currency_inr(amount):
    """Format currency in INR crores"""
    if pd.isna(amount) or amount == 0:
        return "₹0 Cr"
    
    crores = amount / 1e7  # Convert to crores
    if crores >= 1000:
        return f"₹{crores/100:,.1f} L Cr"  # Lakh crores
    else:
        return f"₹{crores:,.1f} Cr"

def sanitize_numeric_value(value):
    """Convert numpy types and NaN values to JSON-serializable types"""
    if pd.isna(value) or value is None:
        return None
    elif isinstance(value, (np.integer, np.floating)):
        if np.isnan(value) or np.isinf(value):
            return None
        return float(value)
    elif isinstance(value, np.ndarray):
        return value.tolist()
    elif isinstance(value, (int, float)):
        if pd.isna(value) or np.isnan(value) or np.isinf(value):
            return None
        return float(value)
    return value

def sanitize_dict_values(data_dict):
    """Recursively sanitize all values in a dictionary"""
    if isinstance(data_dict, dict):
        return {k: sanitize_dict_values(v) for k, v in data_dict.items()}
    elif isinstance(data_dict, list):
        return [sanitize_dict_values(item) for item in data_dict]
    else:
        return sanitize_numeric_value(data_dict)

if __name__ == "__main__":
    # Test the data loader
    loader = FinancialDataLoader()
    companies = loader.load_all_companies()
    
    print(f"\n📊 Testing data loader with {len(companies)} companies")
    
    # Test with a sample company
    if companies:
        sample_symbol = list(companies.keys())[0]
        print(f"\n🔍 Testing with {sample_symbol}:")
        
        company_info = loader.get_company_info(sample_symbol)
        print(f"Company: {company_info['name']}")
        print(f"Sector: {company_info['sector']}")
        
        valuation = loader.get_valuation_metrics(sample_symbol)
        print(f"P/E Ratio: {valuation.get('pe_ratio', 'N/A')}")
        
        summary = loader.get_financial_summary(sample_symbol)
        print(f"Latest Revenue: {format_currency_inr(summary['latest_revenue'])}") 