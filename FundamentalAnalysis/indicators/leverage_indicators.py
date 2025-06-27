#!/usr/bin/env python3
"""
Leverage Indicators Calculator
Calculates various leverage and debt metrics for fundamental analysis
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))

from data_loader import FinancialDataLoader, safe_divide, format_percentage, format_number, sanitize_dict_values
import pandas as pd
import numpy as np

class LeverageIndicators:
    """Calculate leverage indicators for companies"""
    
    def __init__(self, data_loader):
        self.loader = data_loader
        self.output_dir = "outputs/leverage"
        
    def calculate_basic_leverage_ratios(self, symbol):
        """Calculate basic leverage and debt ratios"""
        try:
            # Get financial health data (contains pre-calculated ratios)
            health = self.loader.get_financial_health(symbol)
            
            # Get balance sheet data
            total_debt = self.loader.get_specific_financial_item(symbol, 'balance_sheet', 'Total Debt')
            total_assets = self.loader.get_specific_financial_item(symbol, 'balance_sheet', 'Total Assets')
            shareholders_equity = self.loader.get_specific_financial_item(symbol, 'balance_sheet', 'Stockholders Equity')
            long_term_debt = self.loader.get_specific_financial_item(symbol, 'balance_sheet', 'Long Term Debt')
            short_term_debt = self.loader.get_specific_financial_item(symbol, 'balance_sheet', 'Current Debt')
            
            # Get income statement data
            ebitda = self.loader.get_specific_financial_item(symbol, 'income_statement', 'EBITDA')
            interest_expense = self.loader.get_specific_financial_item(symbol, 'income_statement', 'Interest Expense')
            operating_income = self.loader.get_specific_financial_item(symbol, 'income_statement', 'Operating Income')
            
            if total_assets.empty or shareholders_equity.empty:
                return None
            
            # Get latest values
            latest_total_debt = total_debt['value'].iloc[-1] if not total_debt.empty else 0
            latest_assets = total_assets['value'].iloc[-1]
            latest_equity = shareholders_equity['value'].iloc[-1]
            latest_lt_debt = long_term_debt['value'].iloc[-1] if not long_term_debt.empty else 0
            latest_st_debt = short_term_debt['value'].iloc[-1] if not short_term_debt.empty else 0
            latest_ebitda = ebitda['value'].iloc[-1] if not ebitda.empty else np.nan
            latest_interest = abs(interest_expense['value'].iloc[-1]) if not interest_expense.empty else 0
            latest_oi = operating_income['value'].iloc[-1] if not operating_income.empty else np.nan
            
            # Calculate debt ratios
            debt_to_equity = safe_divide(latest_total_debt, latest_equity)
            debt_to_assets = safe_divide(latest_total_debt, latest_assets)
            equity_ratio = safe_divide(latest_equity, latest_assets)
            
            # Coverage ratios
            interest_coverage = safe_divide(latest_oi, latest_interest) if latest_interest > 0 else np.inf
            debt_to_ebitda = safe_divide(latest_total_debt, latest_ebitda)
            ebitda_coverage = safe_divide(latest_ebitda, latest_interest) if latest_interest > 0 else np.inf
            
            # Use pre-calculated values if available
            if health:
                debt_to_equity = health.get('debt_to_equity', debt_to_equity)
            
            # Interpret leverage
            def interpret_debt_to_equity(ratio):
                if pd.isna(ratio):
                    return "N/A"
                elif ratio < 0.3:
                    return "Conservative - Low debt"
                elif ratio < 0.6:
                    return "Moderate debt levels"
                elif ratio < 1.0:
                    return "Higher debt levels"
                elif ratio < 2.0:
                    return "High leverage"
                else:
                    return "Very high leverage - Risky"
            
            def interpret_interest_coverage(ratio):
                if pd.isna(ratio) or ratio == np.inf:
                    return "No interest expense"
                elif ratio > 10:
                    return "Excellent"
                elif ratio > 5:
                    return "Good"
                elif ratio > 2.5:
                    return "Adequate"
                elif ratio > 1.5:
                    return "Weak"
                else:
                    return "Poor - High risk"
            
            return {
                'symbol': symbol,
                'total_debt': latest_total_debt,
                'long_term_debt': latest_lt_debt,
                'short_term_debt': latest_st_debt,
                'total_assets': latest_assets,
                'shareholders_equity': latest_equity,
                'debt_to_equity': round(debt_to_equity, 2) if pd.notna(debt_to_equity) else np.nan,
                'debt_to_assets': round(debt_to_assets, 2) if pd.notna(debt_to_assets) else np.nan,
                'equity_ratio': round(equity_ratio, 2) if pd.notna(equity_ratio) else np.nan,
                'interest_coverage': round(interest_coverage, 2) if pd.notna(interest_coverage) and interest_coverage != np.inf else interest_coverage,
                'debt_to_ebitda': round(debt_to_ebitda, 2) if pd.notna(debt_to_ebitda) else np.nan,
                'ebitda_coverage': round(ebitda_coverage, 2) if pd.notna(ebitda_coverage) and ebitda_coverage != np.inf else ebitda_coverage,
                'debt_interpretation': interpret_debt_to_equity(debt_to_equity),
                'interest_coverage_interpretation': interpret_interest_coverage(interest_coverage)
            }
            
        except Exception as e:
            print(f"Error calculating leverage ratios for {symbol}: {e}")
            return None
    
    def calculate_debt_structure_analysis(self, symbol):
        """Analyze debt maturity structure"""
        try:
            # Get debt components
            total_debt = self.loader.get_specific_financial_item(symbol, 'balance_sheet', 'Total Debt')
            long_term_debt = self.loader.get_specific_financial_item(symbol, 'balance_sheet', 'Long Term Debt')
            short_term_debt = self.loader.get_specific_financial_item(symbol, 'balance_sheet', 'Current Debt')
            
            if total_debt.empty:
                return None
            
            latest_total_debt = total_debt['value'].iloc[-1]
            latest_lt_debt = long_term_debt['value'].iloc[-1] if not long_term_debt.empty else 0
            latest_st_debt = short_term_debt['value'].iloc[-1] if not short_term_debt.empty else 0
            
            if latest_total_debt == 0:
                return {
                    'symbol': symbol,
                    'total_debt': 0,
                    'long_term_debt': 0,
                    'short_term_debt': 0,
                    'lt_debt_percentage': 0,
                    'st_debt_percentage': 0,
                    'debt_structure': "No debt"
                }
            
            # Calculate percentages
            lt_debt_pct = (latest_lt_debt / latest_total_debt) * 100
            st_debt_pct = (latest_st_debt / latest_total_debt) * 100
            
            # Analyze structure
            if lt_debt_pct > 75:
                structure = "Long-term focused - Good"
            elif lt_debt_pct > 50:
                structure = "Balanced structure"
            elif st_debt_pct > 60:
                structure = "Short-term heavy - Risky"
            else:
                structure = "Mixed structure"
            
            return {
                'symbol': symbol,
                'total_debt': latest_total_debt,
                'long_term_debt': latest_lt_debt,
                'short_term_debt': latest_st_debt,
                'lt_debt_percentage': round(lt_debt_pct, 1),
                'st_debt_percentage': round(st_debt_pct, 1),
                'debt_structure': structure
            }
            
        except Exception as e:
            print(f"Error analyzing debt structure for {symbol}: {e}")
            return None
    
    def calculate_leverage_trends(self, symbol):
        """Calculate leverage trends over time"""
        try:
            # Get historical data
            total_debt = self.loader.get_specific_financial_item(symbol, 'balance_sheet', 'Total Debt')
            shareholders_equity = self.loader.get_specific_financial_item(symbol, 'balance_sheet', 'Stockholders Equity')
            total_assets = self.loader.get_specific_financial_item(symbol, 'balance_sheet', 'Total Assets')
            
            if any([df.empty for df in [total_debt, shareholders_equity, total_assets]]) or len(total_debt) < 2:
                return None
            
            # Merge data
            merged = total_debt.merge(shareholders_equity, on=['symbol', 'period'], suffixes=('_debt', '_equity'))
            merged = merged.merge(total_assets, on=['symbol', 'period']).rename(columns={'value': 'total_assets'})
            
            merged = merged.sort_values('period')
            
            # Calculate ratios for each period
            merged['debt_to_equity'] = safe_divide(merged['value_debt'], merged['value_equity'])
            merged['debt_to_assets'] = safe_divide(merged['value_debt'], merged['total_assets'])
            
            # Calculate trends
            de_trend = merged['debt_to_equity'].pct_change().mean() * 100
            da_trend = merged['debt_to_assets'].pct_change().mean() * 100
            
            # Latest vs first period
            latest_de = merged['debt_to_equity'].iloc[-1]
            first_de = merged['debt_to_equity'].iloc[0]
            de_change = ((latest_de - first_de) / first_de) * 100 if first_de != 0 else np.nan
            
            return {
                'symbol': symbol,
                'periods_analyzed': len(merged),
                'debt_to_equity_trend_percent': round(de_trend, 2) if pd.notna(de_trend) else np.nan,
                'debt_to_assets_trend_percent': round(da_trend, 2) if pd.notna(da_trend) else np.nan,
                'debt_to_equity_change_percent': round(de_change, 2) if pd.notna(de_change) else np.nan,
                'latest_debt_to_equity': round(latest_de, 2) if pd.notna(latest_de) else np.nan,
                'trend_direction': "Increasing leverage" if de_trend > 5 else "Decreasing leverage" if de_trend < -5 else "Stable leverage"
            }
            
        except Exception as e:
            print(f"Error calculating leverage trends for {symbol}: {e}")
            return None
    
    def run_analysis_for_all_companies(self):
        """Run leverage analysis for all companies"""
        print("⚖️  CALCULATING LEVERAGE INDICATORS")
        print("=" * 60)
        
        all_basic_leverage = []
        all_debt_structure = []
        all_leverage_trends = []
        
        for symbol in self.loader.companies_list:
            print(f"Processing {symbol}...")
            
            company_info = self.loader.get_company_info(symbol)
            
            # Basic leverage ratios
            basic_leverage = self.calculate_basic_leverage_ratios(symbol)
            if basic_leverage:
                basic_leverage.update({
                    'company_name': company_info['name'],
                    'sector': company_info['sector']
                })
                all_basic_leverage.append(basic_leverage)
            
            # Debt structure analysis
            debt_structure = self.calculate_debt_structure_analysis(symbol)
            if debt_structure:
                debt_structure.update({
                    'company_name': company_info['name'],
                    'sector': company_info['sector']
                })
                all_debt_structure.append(debt_structure)
            
            # Leverage trends
            trends = self.calculate_leverage_trends(symbol)
            if trends:
                trends.update({
                    'company_name': company_info['name'],
                    'sector': company_info['sector']
                })
                all_leverage_trends.append(trends)
        
        # Convert to DataFrames
        basic_df = pd.DataFrame(all_basic_leverage)
        structure_df = pd.DataFrame(all_debt_structure)
        trends_df = pd.DataFrame(all_leverage_trends)
        
        # Save results
        if not basic_df.empty:
            self.loader.save_results(basic_df, "basic_leverage_ratios", self.output_dir)
            self.loader.save_results(all_basic_leverage, "basic_leverage_ratios", self.output_dir, 'json')
        
        if not structure_df.empty:
            self.loader.save_results(structure_df, "debt_structure_analysis", self.output_dir)
            self.loader.save_results(all_debt_structure, "debt_structure_analysis", self.output_dir, 'json')
        
        if not trends_df.empty:
            self.loader.save_results(trends_df, "leverage_trends", self.output_dir)
            self.loader.save_results(all_leverage_trends, "leverage_trends", self.output_dir, 'json')
        
        # Generate summary
        self.generate_leverage_summary(basic_df, structure_df)
        
        return basic_df, structure_df, trends_df
    
    def generate_leverage_summary(self, basic_df, structure_df):
        """Generate leverage analysis summary"""
        summary = []
        summary.append("⚖️  LEVERAGE ANALYSIS SUMMARY")
        summary.append("=" * 50)
        
        if not basic_df.empty:
            summary.append(f"Companies analyzed: {len(basic_df)}")
            summary.append("")
            
            # Conservative companies (low debt)
            conservative = basic_df[basic_df['debt_to_equity'] < 0.3]
            summary.append("🟢 CONSERVATIVE COMPANIES (Low Debt):")
            summary.append("-" * 40)
            for _, row in conservative.head(10).iterrows():
                summary.append(f"{row['symbol']}: D/E {format_number(row['debt_to_equity'])} - {row['debt_interpretation']}")
            summary.append("")
            
            # High leverage companies
            high_leverage = basic_df[basic_df['debt_to_equity'] > 1.5].nlargest(10, 'debt_to_equity')
            if not high_leverage.empty:
                summary.append("🔴 HIGH LEVERAGE COMPANIES:")
                summary.append("-" * 30)
                for _, row in high_leverage.iterrows():
                    summary.append(f"{row['symbol']}: D/E {format_number(row['debt_to_equity'])} - {row['debt_interpretation']}")
                summary.append("")
            
            # Best interest coverage
            best_coverage = basic_df[basic_df['interest_coverage'] != np.inf].nlargest(10, 'interest_coverage')
            if not best_coverage.empty:
                summary.append("💰 BEST INTEREST COVERAGE:")
                summary.append("-" * 30)
                for _, row in best_coverage.iterrows():
                    summary.append(f"{row['symbol']}: {format_number(row['interest_coverage'])}x - {row['interest_coverage_interpretation']}")
                summary.append("")
            
            # Poor interest coverage
            poor_coverage = basic_df[(basic_df['interest_coverage'] < 2.5) & (basic_df['interest_coverage'] != np.inf)]
            if not poor_coverage.empty:
                summary.append("⚠️  POOR INTEREST COVERAGE:")
                summary.append("-" * 30)
                for _, row in poor_coverage.iterrows():
                    summary.append(f"{row['symbol']}: {format_number(row['interest_coverage'])}x - {row['interest_coverage_interpretation']}")
                summary.append("")
        
        # Sector averages
        if not basic_df.empty:
            sector_avg = basic_df.groupby('sector')[['debt_to_equity', 'debt_to_assets']].mean()
            summary.append("📊 SECTOR AVERAGE LEVERAGE:")
            summary.append("-" * 30)
            for sector, metrics in sector_avg.iterrows():
                summary.append(f"{sector}:")
                summary.append(f"  Debt/Equity: {format_number(metrics['debt_to_equity'])}")
                summary.append(f"  Debt/Assets: {format_percentage(metrics['debt_to_assets'] * 100)}")
                summary.append("")
        
        summary_text = "\n".join(summary)
        self.loader.save_results(summary_text, "leverage_summary", self.output_dir, 'txt')
        print(summary_text)

def main():
    """Main function to run leverage analysis"""
    try:
        # Initialize data loader
        loader = FinancialDataLoader()
        companies = loader.load_all_companies()
        
        if not companies:
            print("❌ No financial data found!")
            return
        
        # Initialize leverage calculator
        leverage_calc = LeverageIndicators(loader)
        
        # Run analysis
        basic_df, structure_df, trends_df = leverage_calc.run_analysis_for_all_companies()
        
        print(f"\n✅ Leverage analysis completed!")
        print(f"📊 Results saved in: {leverage_calc.output_dir}")
        print(f"⚖️  Basic leverage: {len(basic_df)} companies")
        print(f"🏗️  Debt structure: {len(structure_df)} companies")
        print(f"📈 Leverage trends: {len(trends_df)} companies")
        
    except Exception as e:
        print(f"❌ Error in leverage analysis: {e}")

if __name__ == "__main__":
    main() 