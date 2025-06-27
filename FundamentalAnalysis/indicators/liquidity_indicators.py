#!/usr/bin/env python3
"""
Liquidity Indicators Calculator
Calculates various liquidity metrics for fundamental analysis
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))

from data_loader import FinancialDataLoader, safe_divide, format_percentage, format_number, calculate_percentage_change, sanitize_dict_values
import pandas as pd
import numpy as np

class LiquidityIndicators:
    """Calculate liquidity indicators for companies"""
    
    def __init__(self, data_loader):
        self.loader = data_loader
        self.output_dir = "outputs/liquidity"
        
    def calculate_basic_liquidity_ratios(self, symbol):
        """Calculate basic liquidity ratios"""
        try:
            # Get pre-calculated ratios from financial health
            health = self.loader.get_financial_health(symbol)
            
            # Get balance sheet data
            current_assets = self.loader.get_specific_financial_item(symbol, 'balance_sheet', 'Current Assets')
            current_liabilities = self.loader.get_specific_financial_item(symbol, 'balance_sheet', 'Current Liabilities')
            cash = self.loader.get_specific_financial_item(symbol, 'balance_sheet', 'Cash And Cash Equivalents')
            inventory = self.loader.get_specific_financial_item(symbol, 'balance_sheet', 'Inventory')
            receivables = self.loader.get_specific_financial_item(symbol, 'balance_sheet', 'Accounts Receivable')
            
            if current_assets.empty or current_liabilities.empty:
                return None
            
            # Get latest values
            latest_ca = current_assets['value'].iloc[-1] if not current_assets.empty else np.nan
            latest_cl = current_liabilities['value'].iloc[-1] if not current_liabilities.empty else np.nan
            latest_cash = cash['value'].iloc[-1] if not cash.empty else np.nan
            latest_inventory = inventory['value'].iloc[-1] if not inventory.empty else np.nan
            latest_receivables = receivables['value'].iloc[-1] if not receivables.empty else np.nan
            
            # Calculate ratios
            current_ratio = safe_divide(latest_ca, latest_cl)
            
            # Quick ratio = (Current Assets - Inventory) / Current Liabilities
            quick_assets = latest_ca - (latest_inventory if pd.notna(latest_inventory) else 0)
            quick_ratio = safe_divide(quick_assets, latest_cl)
            
            # Cash ratio = Cash / Current Liabilities
            cash_ratio = safe_divide(latest_cash, latest_cl)
            
            # Working capital
            working_capital = latest_ca - latest_cl if pd.notna(latest_ca) and pd.notna(latest_cl) else np.nan
            
            # Use pre-calculated values if available
            if health:
                current_ratio = health.get('current_ratio', current_ratio)
                quick_ratio = health.get('quick_ratio', quick_ratio)
            
            # Interpret liquidity
            def interpret_current_ratio(ratio):
                if pd.isna(ratio):
                    return "N/A"
                elif ratio >= 2.0:
                    return "Excellent"
                elif ratio >= 1.5:
                    return "Good"
                elif ratio >= 1.0:
                    return "Adequate"
                else:
                    return "Poor"
            
            def interpret_quick_ratio(ratio):
                if pd.isna(ratio):
                    return "N/A"
                elif ratio >= 1.5:
                    return "Excellent"
                elif ratio >= 1.0:
                    return "Good"
                elif ratio >= 0.8:
                    return "Adequate"
                else:
                    return "Poor"
            
            return {
                'symbol': symbol,
                'current_assets': latest_ca,
                'current_liabilities': latest_cl,
                'cash_and_equivalents': latest_cash,
                'inventory': latest_inventory,
                'accounts_receivable': latest_receivables,
                'current_ratio': round(current_ratio, 2) if pd.notna(current_ratio) else np.nan,
                'quick_ratio': round(quick_ratio, 2) if pd.notna(quick_ratio) else np.nan,
                'cash_ratio': round(cash_ratio, 2) if pd.notna(cash_ratio) else np.nan,
                'working_capital': working_capital,
                'current_ratio_interpretation': interpret_current_ratio(current_ratio),
                'quick_ratio_interpretation': interpret_quick_ratio(quick_ratio)
            }
            
        except Exception as e:
            print(f"Error calculating liquidity ratios for {symbol}: {e}")
            return None
    
    def calculate_cash_conversion_cycle(self, symbol):
        """Calculate cash conversion cycle"""
        try:
            # Get required data
            revenue = self.loader.get_specific_financial_item(symbol, 'income_statement', 'Total Revenue')
            cost_of_goods = self.loader.get_specific_financial_item(symbol, 'income_statement', 'Cost Of Revenue')
            inventory = self.loader.get_specific_financial_item(symbol, 'balance_sheet', 'Inventory')
            receivables = self.loader.get_specific_financial_item(symbol, 'balance_sheet', 'Accounts Receivable')
            payables = self.loader.get_specific_financial_item(symbol, 'balance_sheet', 'Accounts Payable')
            
            if revenue.empty:
                return None
            
            # Get latest values
            latest_revenue = revenue['value'].iloc[-1]
            latest_cogs = cost_of_goods['value'].iloc[-1] if not cost_of_goods.empty else latest_revenue * 0.7  # Estimate
            latest_inventory = inventory['value'].iloc[-1] if not inventory.empty else 0
            latest_receivables = receivables['value'].iloc[-1] if not receivables.empty else 0
            latest_payables = payables['value'].iloc[-1] if not payables.empty else 0
            
            # Calculate days
            days_in_year = 365
            
            # Days Sales Outstanding (DSO)
            dso = safe_divide(latest_receivables * days_in_year, latest_revenue)
            
            # Days Inventory Outstanding (DIO)
            dio = safe_divide(latest_inventory * days_in_year, latest_cogs)
            
            # Days Payable Outstanding (DPO)
            dpo = safe_divide(latest_payables * days_in_year, latest_cogs)
            
            # Cash Conversion Cycle = DSO + DIO - DPO
            ccc = (dso if pd.notna(dso) else 0) + (dio if pd.notna(dio) else 0) - (dpo if pd.notna(dpo) else 0)
            
            def interpret_ccc(cycle):
                if pd.isna(cycle):
                    return "N/A"
                elif cycle < 30:
                    return "Excellent - Very efficient"
                elif cycle < 60:
                    return "Good - Efficient"
                elif cycle < 90:
                    return "Average"
                elif cycle < 120:
                    return "Below Average"
                else:
                    return "Poor - Inefficient"
            
            return {
                'symbol': symbol,
                'days_sales_outstanding': round(dso, 1) if pd.notna(dso) else np.nan,
                'days_inventory_outstanding': round(dio, 1) if pd.notna(dio) else np.nan,
                'days_payable_outstanding': round(dpo, 1) if pd.notna(dpo) else np.nan,
                'cash_conversion_cycle': round(ccc, 1) if pd.notna(ccc) else np.nan,
                'ccc_interpretation': interpret_ccc(ccc)
            }
            
        except Exception as e:
            print(f"Error calculating cash conversion cycle for {symbol}: {e}")
            return None
    
    def calculate_liquidity_trend(self, symbol):
        """Calculate liquidity trends over time"""
        try:
            # Get historical current and quick ratios
            current_assets = self.loader.get_specific_financial_item(symbol, 'balance_sheet', 'Current Assets')
            current_liabilities = self.loader.get_specific_financial_item(symbol, 'balance_sheet', 'Current Liabilities')
            inventory = self.loader.get_specific_financial_item(symbol, 'balance_sheet', 'Inventory')
            
            if current_assets.empty or current_liabilities.empty or len(current_assets) < 2:
                return None
            
            # Merge data
            merged = current_assets.merge(current_liabilities, on=['symbol', 'period'], suffixes=('_ca', '_cl'))
            if not inventory.empty:
                merged = merged.merge(inventory, on=['symbol', 'period']).rename(columns={'value': 'inventory'})
            else:
                merged['inventory'] = 0
            
            merged = merged.sort_values('period')
            
            # Calculate ratios for each period
            merged['current_ratio'] = safe_divide(merged['value_ca'], merged['value_cl'])
            merged['quick_ratio'] = safe_divide(merged['value_ca'] - merged['inventory'], merged['value_cl'])
            merged['working_capital'] = merged['value_ca'] - merged['value_cl']
            
            # Calculate trends
            current_ratio_trend = merged['current_ratio'].pct_change().mean() * 100
            quick_ratio_trend = merged['quick_ratio'].pct_change().mean() * 100
            
            # Latest vs first period
            latest_cr = merged['current_ratio'].iloc[-1]
            first_cr = merged['current_ratio'].iloc[0]
            cr_change = calculate_percentage_change(latest_cr, first_cr)
            
            latest_qr = merged['quick_ratio'].iloc[-1]
            first_qr = merged['quick_ratio'].iloc[0]
            qr_change = calculate_percentage_change(latest_qr, first_qr)
            
            return {
                'symbol': symbol,
                'periods_analyzed': len(merged),
                'current_ratio_trend_percent': round(current_ratio_trend, 2) if pd.notna(current_ratio_trend) else np.nan,
                'quick_ratio_trend_percent': round(quick_ratio_trend, 2) if pd.notna(quick_ratio_trend) else np.nan,
                'current_ratio_change_percent': round(cr_change, 2) if pd.notna(cr_change) else np.nan,
                'quick_ratio_change_percent': round(qr_change, 2) if pd.notna(qr_change) else np.nan,
                'latest_current_ratio': round(latest_cr, 2) if pd.notna(latest_cr) else np.nan,
                'latest_quick_ratio': round(latest_qr, 2) if pd.notna(latest_qr) else np.nan
            }
            
        except Exception as e:
            print(f"Error calculating liquidity trend for {symbol}: {e}")
            return None
    
    def run_analysis_for_all_companies(self):
        """Run liquidity analysis for all companies"""
        print("💧 CALCULATING LIQUIDITY INDICATORS")
        print("=" * 60)
        
        all_basic_liquidity = []
        all_cash_conversion = []
        all_liquidity_trends = []
        
        for symbol in self.loader.companies_list:
            print(f"Processing {symbol}...")
            
            company_info = self.loader.get_company_info(symbol)
            
            # Basic liquidity ratios
            basic_liquidity = self.calculate_basic_liquidity_ratios(symbol)
            if basic_liquidity:
                basic_liquidity.update({
                    'company_name': company_info['name'],
                    'sector': company_info['sector']
                })
                all_basic_liquidity.append(basic_liquidity)
            
            # Cash conversion cycle
            ccc = self.calculate_cash_conversion_cycle(symbol)
            if ccc:
                ccc.update({
                    'company_name': company_info['name'],
                    'sector': company_info['sector']
                })
                all_cash_conversion.append(ccc)
            
            # Liquidity trends
            trends = self.calculate_liquidity_trend(symbol)
            if trends:
                trends.update({
                    'company_name': company_info['name'],
                    'sector': company_info['sector']
                })
                all_liquidity_trends.append(trends)
        
        # Convert to DataFrames
        basic_df = pd.DataFrame(all_basic_liquidity)
        ccc_df = pd.DataFrame(all_cash_conversion)
        trends_df = pd.DataFrame(all_liquidity_trends)
        
        # Save results
        if not basic_df.empty:
            self.loader.save_results(basic_df, "basic_liquidity_ratios", self.output_dir)
            self.loader.save_results(all_basic_liquidity, "basic_liquidity_ratios", self.output_dir, 'json')
        
        if not ccc_df.empty:
            self.loader.save_results(ccc_df, "cash_conversion_cycle", self.output_dir)
            self.loader.save_results(all_cash_conversion, "cash_conversion_cycle", self.output_dir, 'json')
        
        if not trends_df.empty:
            self.loader.save_results(trends_df, "liquidity_trends", self.output_dir)
            self.loader.save_results(all_liquidity_trends, "liquidity_trends", self.output_dir, 'json')
        
        # Generate summary
        self.generate_liquidity_summary(basic_df, ccc_df)
        
        return basic_df, ccc_df, trends_df
    
    def generate_liquidity_summary(self, basic_df, ccc_df):
        """Generate liquidity analysis summary"""
        summary = []
        summary.append("💧 LIQUIDITY ANALYSIS SUMMARY")
        summary.append("=" * 50)
        
        if not basic_df.empty:
            summary.append(f"Companies analyzed: {len(basic_df)}")
            summary.append("")
            
            # Best current ratios
            best_current = basic_df.nlargest(10, 'current_ratio')[['symbol', 'company_name', 'sector', 'current_ratio', 'current_ratio_interpretation']]
            summary.append("🏆 BEST CURRENT RATIOS:")
            summary.append("-" * 25)
            for _, row in best_current.iterrows():
                summary.append(f"{row['symbol']}: {format_number(row['current_ratio'])} - {row['current_ratio_interpretation']} ({row['sector']})")
            summary.append("")
            
            # Best quick ratios
            best_quick = basic_df.nlargest(10, 'quick_ratio')[['symbol', 'company_name', 'sector', 'quick_ratio', 'quick_ratio_interpretation']]
            summary.append("⚡ BEST QUICK RATIOS:")
            summary.append("-" * 20)
            for _, row in best_quick.iterrows():
                summary.append(f"{row['symbol']}: {format_number(row['quick_ratio'])} - {row['quick_ratio_interpretation']} ({row['sector']})")
            summary.append("")
            
            # Poor liquidity (current ratio < 1)
            poor_liquidity = basic_df[basic_df['current_ratio'] < 1.0]
            if not poor_liquidity.empty:
                summary.append("⚠️  COMPANIES WITH POOR LIQUIDITY:")
                summary.append("-" * 35)
                for _, row in poor_liquidity.iterrows():
                    summary.append(f"{row['symbol']}: Current Ratio {format_number(row['current_ratio'])} ({row['sector']})")
                summary.append("")
        
        if not ccc_df.empty:
            # Best cash conversion cycles
            best_ccc = ccc_df.nsmallest(10, 'cash_conversion_cycle')[['symbol', 'company_name', 'sector', 'cash_conversion_cycle', 'ccc_interpretation']]
            summary.append("🔄 MOST EFFICIENT CASH CONVERSION:")
            summary.append("-" * 35)
            for _, row in best_ccc.iterrows():
                summary.append(f"{row['symbol']}: {format_number(row['cash_conversion_cycle'])} days - {row['ccc_interpretation']}")
            summary.append("")
        
        # Sector averages
        if not basic_df.empty:
            sector_avg = basic_df.groupby('sector')[['current_ratio', 'quick_ratio']].mean()
            summary.append("📊 SECTOR AVERAGE LIQUIDITY:")
            summary.append("-" * 30)
            for sector, metrics in sector_avg.iterrows():
                summary.append(f"{sector}:")
                summary.append(f"  Current Ratio: {format_number(metrics['current_ratio'])}")
                summary.append(f"  Quick Ratio: {format_number(metrics['quick_ratio'])}")
                summary.append("")
        
        summary_text = "\n".join(summary)
        self.loader.save_results(summary_text, "liquidity_summary", self.output_dir, 'txt')
        print(summary_text)

def main():
    """Main function to run liquidity analysis"""
    try:
        # Initialize data loader
        loader = FinancialDataLoader()
        companies = loader.load_all_companies()
        
        if not companies:
            print("❌ No financial data found!")
            return
        
        # Initialize liquidity calculator
        liquidity_calc = LiquidityIndicators(loader)
        
        # Run analysis
        basic_df, ccc_df, trends_df = liquidity_calc.run_analysis_for_all_companies()
        
        print(f"\n✅ Liquidity analysis completed!")
        print(f"📊 Results saved in: {liquidity_calc.output_dir}")
        print(f"💧 Basic liquidity: {len(basic_df)} companies")
        print(f"🔄 Cash conversion: {len(ccc_df)} companies")
        print(f"📈 Liquidity trends: {len(trends_df)} companies")
        
    except Exception as e:
        print(f"❌ Error in liquidity analysis: {e}")

if __name__ == "__main__":
    main() 