#!/usr/bin/env python3
"""
Profitability Indicators Calculator
Calculates various profitability metrics for fundamental analysis
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))

from data_loader import FinancialDataLoader, safe_divide, format_percentage, format_number, sanitize_dict_values
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

class ProfitabilityIndicators:
    """Calculate profitability indicators for companies"""
    
    def __init__(self, data_loader):
        self.loader = data_loader
        self.output_dir = "outputs/profitability"
        
    def calculate_basic_profitability_ratios(self, symbol):
        """Calculate basic profitability ratios"""
        try:
            # Get financial health data (contains pre-calculated ratios)
            health = self.loader.get_financial_health(symbol)
            
            # Get additional data for calculations
            revenue = self.loader.get_specific_financial_item(symbol, 'income_statement', 'Total Revenue')
            net_income = self.loader.get_specific_financial_item(symbol, 'income_statement', 'Net Income')
            gross_profit = self.loader.get_specific_financial_item(symbol, 'income_statement', 'Gross Profit')
            operating_income = self.loader.get_specific_financial_item(symbol, 'income_statement', 'Operating Income')
            ebitda = self.loader.get_specific_financial_item(symbol, 'income_statement', 'EBITDA')
            total_assets = self.loader.get_specific_financial_item(symbol, 'balance_sheet', 'Total Assets')
            shareholders_equity = self.loader.get_specific_financial_item(symbol, 'balance_sheet', 'Stockholders Equity')
            
            if revenue.empty or net_income.empty:
                return None
            
            # Get latest year data
            latest_period = revenue['period'].max()
            latest_revenue = revenue[revenue['period'] == latest_period]['value'].iloc[0] if not revenue.empty else np.nan
            latest_net_income = net_income[net_income['period'] == latest_period]['value'].iloc[0] if not net_income.empty else np.nan
            latest_gross_profit = gross_profit[gross_profit['period'] == latest_period]['value'].iloc[0] if not gross_profit.empty else np.nan
            latest_operating_income = operating_income[operating_income['period'] == latest_period]['value'].iloc[0] if not operating_income.empty else np.nan
            latest_ebitda = ebitda[ebitda['period'] == latest_period]['value'].iloc[0] if not ebitda.empty else np.nan
            latest_assets = total_assets[total_assets['period'] == latest_period]['value'].iloc[0] if not total_assets.empty else np.nan
            latest_equity = shareholders_equity[shareholders_equity['period'] == latest_period]['value'].iloc[0] if not shareholders_equity.empty else np.nan
            
            # Calculate profitability ratios
            roe = safe_divide(latest_net_income, latest_equity) * 100
            roa = safe_divide(latest_net_income, latest_assets) * 100
            gross_margin = safe_divide(latest_gross_profit, latest_revenue) * 100
            operating_margin = safe_divide(latest_operating_income, latest_revenue) * 100
            net_margin = safe_divide(latest_net_income, latest_revenue) * 100
            ebitda_margin = safe_divide(latest_ebitda, latest_revenue) * 100
            
            # Use pre-calculated values if available
            if health:
                roe = health.get('return_on_equity', roe/100) * 100 if health.get('return_on_equity') else roe
                roa = health.get('return_on_assets', roa/100) * 100 if health.get('return_on_assets') else roa
                gross_margin = health.get('gross_margin', gross_margin/100) * 100 if health.get('gross_margin') else gross_margin
                operating_margin = health.get('operating_margin', operating_margin/100) * 100 if health.get('operating_margin') else operating_margin
                net_margin = health.get('profit_margin', net_margin/100) * 100 if health.get('profit_margin') else net_margin
            
            result = {
                'symbol': symbol,
                'period': str(latest_period.date()) if pd.notna(latest_period) else 'N/A',
                'roe_percent': round(roe, 2) if pd.notna(roe) else np.nan,
                'roa_percent': round(roa, 2) if pd.notna(roa) else np.nan,
                'gross_margin_percent': round(gross_margin, 2) if pd.notna(gross_margin) else np.nan,
                'operating_margin_percent': round(operating_margin, 2) if pd.notna(operating_margin) else np.nan,
                'net_margin_percent': round(net_margin, 2) if pd.notna(net_margin) else np.nan,
                'ebitda_margin_percent': round(ebitda_margin, 2) if pd.notna(ebitda_margin) else np.nan,
                'revenue': latest_revenue,
                'net_income': latest_net_income,
                'total_assets': latest_assets,
                'shareholders_equity': latest_equity
            }
            
            return sanitize_dict_values(result)
            
        except Exception as e:
            print(f"Error calculating profitability ratios for {symbol}: {e}")
            return None
    
    def calculate_dupont_analysis(self, symbol):
        """Calculate DuPont analysis: ROE = Net Margin × Asset Turnover × Equity Multiplier"""
        try:
            # Get latest 3 years of data
            revenue = self.loader.get_specific_financial_item(symbol, 'income_statement', 'Total Revenue')
            net_income = self.loader.get_specific_financial_item(symbol, 'income_statement', 'Net Income')
            total_assets = self.loader.get_specific_financial_item(symbol, 'balance_sheet', 'Total Assets')
            shareholders_equity = self.loader.get_specific_financial_item(symbol, 'balance_sheet', 'Stockholders Equity')
            
            if any([df.empty for df in [revenue, net_income, total_assets, shareholders_equity]]):
                return None
            
            # Merge data on period
            merged = revenue.merge(net_income, on=['symbol', 'period'], suffixes=('_revenue', '_net_income'))
            merged = merged.merge(total_assets, on=['symbol', 'period']).rename(columns={'value': 'total_assets'})
            merged = merged.merge(shareholders_equity, on=['symbol', 'period']).rename(columns={'value': 'shareholders_equity'})
            
            if merged.empty:
                return None
            
            # Calculate DuPont components for each year
            merged['net_margin'] = safe_divide(merged['value_net_income'], merged['value_revenue']) * 100
            merged['asset_turnover'] = safe_divide(merged['value_revenue'], merged['total_assets'])
            merged['equity_multiplier'] = safe_divide(merged['total_assets'], merged['shareholders_equity'])
            merged['calculated_roe'] = (merged['net_margin'] / 100) * merged['asset_turnover'] * merged['equity_multiplier'] * 100
            
            # Get latest 3 years
            merged = merged.sort_values('period', ascending=False).head(3)
            
            results = []
            for _, row in merged.iterrows():
                results.append({
                    'symbol': symbol,
                    'period': str(row['period'].date()),
                    'net_margin_percent': round(row['net_margin'], 2) if pd.notna(row['net_margin']) else np.nan,
                    'asset_turnover': round(row['asset_turnover'], 2) if pd.notna(row['asset_turnover']) else np.nan,
                    'equity_multiplier': round(row['equity_multiplier'], 2) if pd.notna(row['equity_multiplier']) else np.nan,
                    'calculated_roe_percent': round(row['calculated_roe'], 2) if pd.notna(row['calculated_roe']) else np.nan
                })
            
            return results
            
        except Exception as e:
            print(f"Error calculating DuPont analysis for {symbol}: {e}")
            return None
    
    def calculate_profit_growth_trends(self, symbol):
        """Calculate profit growth trends over time"""
        try:
            # Get historical data
            revenue = self.loader.get_specific_financial_item(symbol, 'income_statement', 'Total Revenue')
            net_income = self.loader.get_specific_financial_item(symbol, 'income_statement', 'Net Income')
            operating_income = self.loader.get_specific_financial_item(symbol, 'income_statement', 'Operating Income')
            
            if any([df.empty for df in [revenue, net_income]]):
                return None
            
            # Merge and calculate growth rates
            merged = revenue.merge(net_income, on=['symbol', 'period'], suffixes=('_revenue', '_net_income'))
            if not operating_income.empty:
                merged = merged.merge(operating_income, on=['symbol', 'period']).rename(columns={'value': 'operating_income'})
            
            merged = merged.sort_values('period')
            
            # Calculate year-over-year growth
            merged['revenue_growth'] = merged['value_revenue'].pct_change() * 100
            merged['net_income_growth'] = merged['value_net_income'].pct_change() * 100
            if 'operating_income' in merged.columns:
                merged['operating_income_growth'] = merged['operating_income'].pct_change() * 100
            
            # Calculate margins
            merged['net_margin'] = safe_divide(merged['value_net_income'], merged['value_revenue']) * 100
            if 'operating_income' in merged.columns:
                merged['operating_margin'] = safe_divide(merged['operating_income'], merged['value_revenue']) * 100
            
            results = []
            for _, row in merged.iterrows():
                result = {
                    'symbol': symbol,
                    'period': str(row['period'].date()),
                    'revenue': row['value_revenue'],
                    'net_income': row['value_net_income'],
                    'revenue_growth_percent': round(row['revenue_growth'], 2) if pd.notna(row['revenue_growth']) else np.nan,
                    'net_income_growth_percent': round(row['net_income_growth'], 2) if pd.notna(row['net_income_growth']) else np.nan,
                    'net_margin_percent': round(row['net_margin'], 2) if pd.notna(row['net_margin']) else np.nan
                }
                
                if 'operating_income' in merged.columns:
                    result.update({
                        'operating_income': row['operating_income'],
                        'operating_income_growth_percent': round(row['operating_income_growth'], 2) if pd.notna(row['operating_income_growth']) else np.nan,
                        'operating_margin_percent': round(row['operating_margin'], 2) if pd.notna(row['operating_margin']) else np.nan
                    })
                
                results.append(result)
            
            return results
            
        except Exception as e:
            print(f"Error calculating profit growth trends for {symbol}: {e}")
            return None
    
    def run_analysis_for_all_companies(self):
        """Run profitability analysis for all companies"""
        print("🎯 CALCULATING PROFITABILITY INDICATORS")
        print("=" * 60)
        
        all_profitability = []
        all_dupont = []
        all_growth_trends = []
        
        for symbol in self.loader.companies_list:
            print(f"Processing {symbol}...")
            
            # Basic profitability ratios
            profitability = self.calculate_basic_profitability_ratios(symbol)
            if profitability:
                company_info = self.loader.get_company_info(symbol)
                profitability.update({
                    'company_name': company_info['name'],
                    'sector': company_info['sector'],
                    'industry': company_info['industry']
                })
                all_profitability.append(profitability)
            
            # DuPont analysis
            dupont = self.calculate_dupont_analysis(symbol)
            if dupont:
                company_info = self.loader.get_company_info(symbol)
                for period_data in dupont:
                    period_data.update({
                        'company_name': company_info['name'],
                        'sector': company_info['sector']
                    })
                all_dupont.extend(dupont)
            
            # Growth trends
            growth = self.calculate_profit_growth_trends(symbol)
            if growth:
                company_info = self.loader.get_company_info(symbol)
                for period_data in growth:
                    period_data.update({
                        'company_name': company_info['name'],
                        'sector': company_info['sector']
                    })
                all_growth_trends.extend(growth)
        
        # Convert to DataFrames
        profitability_df = pd.DataFrame(all_profitability)
        dupont_df = pd.DataFrame(all_dupont)
        growth_df = pd.DataFrame(all_growth_trends)
        
        # Save results
        if not profitability_df.empty:
            self.loader.save_results(profitability_df, "profitability_ratios", self.output_dir)
            self.loader.save_results(all_profitability, "profitability_ratios", self.output_dir, 'json')
        
        if not dupont_df.empty:
            self.loader.save_results(dupont_df, "dupont_analysis", self.output_dir)
            self.loader.save_results(all_dupont, "dupont_analysis", self.output_dir, 'json')
        
        if not growth_df.empty:
            self.loader.save_results(growth_df, "profit_growth_trends", self.output_dir)
            self.loader.save_results(all_growth_trends, "profit_growth_trends", self.output_dir, 'json')
        
        # Generate summary analysis
        self.generate_profitability_summary(profitability_df)
        
        return profitability_df, dupont_df, growth_df
    
    def generate_profitability_summary(self, df):
        """Generate profitability summary analysis"""
        if df.empty:
            return
        
        summary = []
        summary.append("📊 PROFITABILITY ANALYSIS SUMMARY")
        summary.append("=" * 50)
        summary.append(f"Total companies analyzed: {len(df)}")
        summary.append("")
        
        # Top performers by ROE
        top_roe = df.nlargest(10, 'roe_percent')[['symbol', 'company_name', 'sector', 'roe_percent']]
        summary.append("🏆 TOP 10 COMPANIES BY ROE:")
        summary.append("-" * 30)
        for _, row in top_roe.iterrows():
            summary.append(f"{row['symbol']}: {format_percentage(row['roe_percent'])} ({row['sector']})")
        summary.append("")
        
        # Top performers by Net Margin
        top_margin = df.nlargest(10, 'net_margin_percent')[['symbol', 'company_name', 'sector', 'net_margin_percent']]
        summary.append("💰 TOP 10 COMPANIES BY NET MARGIN:")
        summary.append("-" * 35)
        for _, row in top_margin.iterrows():
            summary.append(f"{row['symbol']}: {format_percentage(row['net_margin_percent'])} ({row['sector']})")
        summary.append("")
        
        # Sector averages
        sector_avg = df.groupby('sector')[['roe_percent', 'roa_percent', 'net_margin_percent', 'operating_margin_percent']].mean()
        summary.append("📈 SECTOR AVERAGES:")
        summary.append("-" * 20)
        for sector, metrics in sector_avg.iterrows():
            summary.append(f"{sector}:")
            summary.append(f"  ROE: {format_percentage(metrics['roe_percent'])}")
            summary.append(f"  ROA: {format_percentage(metrics['roa_percent'])}")
            summary.append(f"  Net Margin: {format_percentage(metrics['net_margin_percent'])}")
            summary.append("")
        
        # Poor performers (negative ROE)
        poor_performers = df[df['roe_percent'] < 0]
        if not poor_performers.empty:
            summary.append("⚠️  COMPANIES WITH NEGATIVE ROE:")
            summary.append("-" * 30)
            for _, row in poor_performers.iterrows():
                summary.append(f"{row['symbol']}: {format_percentage(row['roe_percent'])} ({row['sector']})")
            summary.append("")
        
        summary_text = "\n".join(summary)
        self.loader.save_results(summary_text, "profitability_summary", self.output_dir, 'txt')
        print(summary_text)

def main():
    """Main function to run profitability analysis"""
    try:
        # Initialize data loader
        loader = FinancialDataLoader()
        companies = loader.load_all_companies()
        
        if not companies:
            print("❌ No financial data found!")
            return
        
        # Initialize profitability calculator
        profitability_calc = ProfitabilityIndicators(loader)
        
        # Run analysis
        profitability_df, dupont_df, growth_df = profitability_calc.run_analysis_for_all_companies()
        
        print(f"\n✅ Profitability analysis completed!")
        print(f"📊 Results saved in: {profitability_calc.output_dir}")
        print(f"💾 Profitability ratios: {len(profitability_df)} companies")
        print(f"📈 DuPont analysis: {len(dupont_df)} records")
        print(f"📉 Growth trends: {len(growth_df)} records")
        
    except Exception as e:
        print(f"❌ Error in profitability analysis: {e}")

if __name__ == "__main__":
    main() 