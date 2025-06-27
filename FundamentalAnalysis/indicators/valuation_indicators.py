#!/usr/bin/env python3
"""
Valuation Indicators Calculator
Calculates various valuation metrics for fundamental analysis
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))

from data_loader import FinancialDataLoader, safe_divide, format_percentage, format_number, format_currency_inr, sanitize_dict_values
import pandas as pd
import numpy as np
from datetime import datetime

class ValuationIndicators:
    """Calculate valuation indicators for companies"""
    
    def __init__(self, data_loader):
        self.loader = data_loader
        self.output_dir = "outputs/valuation"
        
    def calculate_basic_valuation_ratios(self, symbol):
        """Calculate basic valuation ratios"""
        try:
            # Get valuation metrics (pre-calculated)
            valuation = self.loader.get_valuation_metrics(symbol)
            company_info = self.loader.get_company_info(symbol)
            
            if not valuation:
                return None
            
            # Get financial data for additional calculations
            revenue = self.loader.get_specific_financial_item(symbol, 'income_statement', 'Total Revenue')
            net_income = self.loader.get_specific_financial_item(symbol, 'income_statement', 'Net Income')
            book_value = self.loader.get_specific_financial_item(symbol, 'balance_sheet', 'Stockholders Equity')
            shares = self.loader.get_specific_financial_item(symbol, 'income_statement', 'Basic Average Shares')
            
            # Calculate additional ratios if data is available
            market_cap = company_info.get('market_cap', 0)
            current_price = company_info.get('current_price', 0)
            
            # Get latest financial figures
            latest_revenue = revenue['value'].iloc[-1] if not revenue.empty else np.nan
            latest_net_income = net_income['value'].iloc[-1] if not net_income.empty else np.nan
            latest_book_value = book_value['value'].iloc[-1] if not book_value.empty else np.nan
            latest_shares = shares['value'].iloc[-1] if not shares.empty else np.nan
            
            # Calculate per share metrics
            eps = safe_divide(latest_net_income, latest_shares)
            book_value_per_share = safe_divide(latest_book_value, latest_shares)
            revenue_per_share = safe_divide(latest_revenue, latest_shares)
            
            # Calculate ratios
            pe_ratio = valuation.get('pe_ratio', safe_divide(current_price, eps))
            pb_ratio = valuation.get('price_to_book', safe_divide(current_price, book_value_per_share))
            ps_ratio = valuation.get('price_to_sales', safe_divide(market_cap, latest_revenue))
            
            result = {
                'symbol': symbol,
                'company_name': company_info.get('name', 'N/A'),
                'sector': company_info.get('sector', 'N/A'),
                'market_cap': market_cap,
                'market_cap_formatted': company_info.get('market_cap_formatted', 'N/A'),
                'current_price': current_price,
                'pe_ratio': round(pe_ratio, 2) if pd.notna(pe_ratio) else np.nan,
                'forward_pe': valuation.get('forward_pe'),
                'pb_ratio': round(pb_ratio, 2) if pd.notna(pb_ratio) else np.nan,
                'ps_ratio': round(ps_ratio, 2) if pd.notna(ps_ratio) else np.nan,
                'peg_ratio': valuation.get('peg_ratio'),
                'enterprise_value': valuation.get('enterprise_value'),
                'ev_revenue': valuation.get('ev_to_revenue'),
                'ev_ebitda': valuation.get('ev_to_ebitda'),
                'eps': round(eps, 2) if pd.notna(eps) else np.nan,
                'book_value_per_share': round(book_value_per_share, 2) if pd.notna(book_value_per_share) else np.nan,
                'revenue_per_share': round(revenue_per_share, 2) if pd.notna(revenue_per_share) else np.nan
            }
            
            return sanitize_dict_values(result)
            
        except Exception as e:
            print(f"Error calculating valuation ratios for {symbol}: {e}")
            return None
    
    def calculate_dcf_valuation(self, symbol, discount_rate=0.12, terminal_growth=0.03):
        """Calculate Discounted Cash Flow (DCF) valuation"""
        try:
            # Get cash flow data
            free_cash_flow = self.loader.get_specific_financial_item(symbol, 'cash_flow', 'Free Cash Flow')
            operating_cash_flow = self.loader.get_specific_financial_item(symbol, 'cash_flow', 'Operating Cash Flow')
            
            # Use operating cash flow if free cash flow not available
            if free_cash_flow.empty and not operating_cash_flow.empty:
                cash_flow_data = operating_cash_flow
                flow_type = "Operating Cash Flow"
            elif not free_cash_flow.empty:
                cash_flow_data = free_cash_flow
                flow_type = "Free Cash Flow"
            else:
                return None
            
            if len(cash_flow_data) < 2:
                return None
            
            # Calculate average cash flow growth rate
            cash_flow_data = cash_flow_data.sort_values('period')
            cash_flows = cash_flow_data['value'].tolist()
            
            growth_rates = []
            for i in range(1, len(cash_flows)):
                if cash_flows[i-1] > 0:
                    growth_rate = (cash_flows[i] - cash_flows[i-1]) / cash_flows[i-1]
                    growth_rates.append(growth_rate)
            
            # Use average growth rate, capped between -5% and 25%
            avg_growth_rate = np.mean(growth_rates) if growth_rates else 0.05
            avg_growth_rate = max(min(avg_growth_rate, 0.25), -0.05)
            
            # Latest cash flow
            latest_cash_flow = cash_flows[-1]
            
            if latest_cash_flow <= 0:
                return None
            
            # Project next year cash flow
            next_year_cf = latest_cash_flow * (1 + avg_growth_rate)
            
            # Calculate terminal value
            terminal_cf = next_year_cf * (1 + terminal_growth)
            terminal_value = terminal_cf / (discount_rate - terminal_growth)
            
            # Present value of next year CF and terminal value
            pv_next_year = next_year_cf / (1 + discount_rate)
            pv_terminal = terminal_value / (1 + discount_rate)
            
            # Total enterprise value
            enterprise_value = pv_next_year + pv_terminal
            
            # Get market cap for comparison
            company_info = self.loader.get_company_info(symbol)
            market_cap = company_info.get('market_cap', 0)
            
            # Calculate fair value ratio
            fair_value_ratio = safe_divide(enterprise_value, market_cap)
            
            # Determine valuation signal
            if fair_value_ratio > 1.3:
                signal = "Significantly Undervalued"
            elif fair_value_ratio > 1.1:
                signal = "Undervalued"
            elif fair_value_ratio > 0.9:
                signal = "Fair Value"
            elif fair_value_ratio > 0.7:
                signal = "Overvalued"
            else:
                signal = "Significantly Overvalued"
            
            return {
                'symbol': symbol,
                'flow_type': flow_type,
                'latest_cash_flow': latest_cash_flow,
                'growth_rate_percent': round(avg_growth_rate * 100, 2),
                'discount_rate_percent': round(discount_rate * 100, 2),
                'terminal_growth_percent': round(terminal_growth * 100, 2),
                'projected_next_year_cf': round(next_year_cf, 0),
                'terminal_value': round(terminal_value, 0),
                'enterprise_value': round(enterprise_value, 0),
                'current_market_cap': market_cap,
                'fair_value_ratio': round(fair_value_ratio, 2) if pd.notna(fair_value_ratio) else np.nan,
                'valuation_signal': signal
            }
            
        except Exception as e:
            print(f"Error calculating DCF for {symbol}: {e}")
            return None
    
    def calculate_relative_valuation(self, symbol):
        """Calculate relative valuation vs sector peers"""
        try:
            company_info = self.loader.get_company_info(symbol)
            if not company_info:
                return None
            
            sector = company_info['sector']
            
            # Get sector companies
            sector_companies = self.loader.get_companies_by_sector(sector)
            
            if len(sector_companies) < 2:
                return None
            
            # Calculate sector metrics
            sector_valuations = []
            company_valuation = None
            
            for comp_symbol in sector_companies:
                valuation = self.calculate_basic_valuation_ratios(comp_symbol)
                if valuation:
                    sector_valuations.append(valuation)
                    if comp_symbol == symbol:
                        company_valuation = valuation
            
            if not sector_valuations or not company_valuation:
                return None
            
            # Calculate sector averages
            sector_df = pd.DataFrame(sector_valuations)
            
            sector_avg_pe = sector_df['pe_ratio'].median()
            sector_avg_pb = sector_df['pb_ratio'].median()
            sector_avg_ps = sector_df['ps_ratio'].median()
            
            # Calculate relative metrics
            pe_relative = safe_divide(company_valuation['pe_ratio'], sector_avg_pe)
            pb_relative = safe_divide(company_valuation['pb_ratio'], sector_avg_pb)
            ps_relative = safe_divide(company_valuation['ps_ratio'], sector_avg_ps)
            
            return {
                'symbol': symbol,
                'sector': sector,
                'sector_companies_count': len(sector_companies),
                'company_pe': company_valuation['pe_ratio'],
                'sector_median_pe': round(sector_avg_pe, 2) if pd.notna(sector_avg_pe) else np.nan,
                'pe_relative_to_sector': round(pe_relative, 2) if pd.notna(pe_relative) else np.nan,
                'company_pb': company_valuation['pb_ratio'],
                'sector_median_pb': round(sector_avg_pb, 2) if pd.notna(sector_avg_pb) else np.nan,
                'pb_relative_to_sector': round(pb_relative, 2) if pd.notna(pb_relative) else np.nan,
                'company_ps': company_valuation['ps_ratio'],
                'sector_median_ps': round(sector_avg_ps, 2) if pd.notna(sector_avg_ps) else np.nan,
                'ps_relative_to_sector': round(ps_relative, 2) if pd.notna(ps_relative) else np.nan
            }
            
        except Exception as e:
            print(f"Error calculating relative valuation for {symbol}: {e}")
            return None
    
    def run_analysis_for_all_companies(self):
        """Run valuation analysis for all companies"""
        print("💰 CALCULATING VALUATION INDICATORS")
        print("=" * 60)
        
        all_valuations = []
        all_dcf = []
        all_relative = []
        
        for symbol in self.loader.companies_list:
            print(f"Processing {symbol}...")
            
            # Basic valuation ratios
            valuation = self.calculate_basic_valuation_ratios(symbol)
            if valuation:
                all_valuations.append(valuation)
            
            # DCF analysis
            dcf = self.calculate_dcf_valuation(symbol)
            if dcf:
                company_info = self.loader.get_company_info(symbol)
                dcf.update({
                    'company_name': company_info['name'],
                    'sector': company_info['sector']
                })
                all_dcf.append(dcf)
            
            # Relative valuation
            relative = self.calculate_relative_valuation(symbol)
            if relative:
                company_info = self.loader.get_company_info(symbol)
                relative.update({
                    'company_name': company_info['name']
                })
                all_relative.append(relative)
        
        # Convert to DataFrames
        valuations_df = pd.DataFrame(all_valuations)
        dcf_df = pd.DataFrame(all_dcf)
        relative_df = pd.DataFrame(all_relative)
        
        # Save results
        if not valuations_df.empty:
            self.loader.save_results(valuations_df, "basic_valuation_ratios", self.output_dir)
            self.loader.save_results(all_valuations, "basic_valuation_ratios", self.output_dir, 'json')
        
        if not dcf_df.empty:
            self.loader.save_results(dcf_df, "dcf_analysis", self.output_dir)
            self.loader.save_results(all_dcf, "dcf_analysis", self.output_dir, 'json')
        
        if not relative_df.empty:
            self.loader.save_results(relative_df, "relative_valuation", self.output_dir)
            self.loader.save_results(all_relative, "relative_valuation", self.output_dir, 'json')
        
        # Generate summary analysis
        self.generate_valuation_summary(valuations_df, dcf_df)
        
        return valuations_df, dcf_df, relative_df
    
    def generate_valuation_summary(self, valuations_df, dcf_df):
        """Generate valuation summary analysis"""
        if valuations_df.empty:
            return
        
        summary = []
        summary.append("💰 VALUATION ANALYSIS SUMMARY")
        summary.append("=" * 50)
        summary.append(f"Total companies analyzed: {len(valuations_df)}")
        summary.append("")
        
        # Cheapest stocks by P/E
        cheap_pe = valuations_df[valuations_df['pe_ratio'] > 0].nsmallest(10, 'pe_ratio')[['symbol', 'company_name', 'sector', 'pe_ratio']]
        summary.append("📉 CHEAPEST STOCKS BY P/E RATIO:")
        summary.append("-" * 35)
        for _, row in cheap_pe.iterrows():
            summary.append(f"{row['symbol']}: {format_number(row['pe_ratio'])} ({row['sector']})")
        summary.append("")
        
        # Most expensive stocks by P/E
        expensive_pe = valuations_df[valuations_df['pe_ratio'] > 0].nlargest(10, 'pe_ratio')[['symbol', 'company_name', 'sector', 'pe_ratio']]
        summary.append("📈 MOST EXPENSIVE STOCKS BY P/E RATIO:")
        summary.append("-" * 40)
        for _, row in expensive_pe.iterrows():
            summary.append(f"{row['symbol']}: {format_number(row['pe_ratio'])} ({row['sector']})")
        summary.append("")
        
        # Value stocks (low P/B)
        value_stocks = valuations_df[valuations_df['pb_ratio'] > 0].nsmallest(10, 'pb_ratio')[['symbol', 'company_name', 'sector', 'pb_ratio']]
        summary.append("💎 VALUE STOCKS (LOW P/B RATIO):")
        summary.append("-" * 35)
        for _, row in value_stocks.iterrows():
            summary.append(f"{row['symbol']}: {format_number(row['pb_ratio'])} ({row['sector']})")
        summary.append("")
        
        # DCF Analysis Summary
        if not dcf_df.empty:
            undervalued = dcf_df[dcf_df['fair_value_ratio'] > 1.1]
            overvalued = dcf_df[dcf_df['fair_value_ratio'] < 0.9]
            
            summary.append("🔍 DCF ANALYSIS RESULTS:")
            summary.append("-" * 25)
            summary.append(f"Undervalued companies: {len(undervalued)}")
            summary.append(f"Overvalued companies: {len(overvalued)}")
            summary.append("")
            
            if not undervalued.empty:
                summary.append("🎯 TOP UNDERVALUED STOCKS (DCF):")
                summary.append("-" * 35)
                top_undervalued = undervalued.nlargest(5, 'fair_value_ratio')
                for _, row in top_undervalued.iterrows():
                    summary.append(f"{row['symbol']}: {format_number(row['fair_value_ratio'])} - {row['valuation_signal']}")
                summary.append("")
        
        # Sector valuation averages
        sector_avg = valuations_df.groupby('sector')[['pe_ratio', 'pb_ratio', 'ps_ratio']].median()
        summary.append("📊 SECTOR VALUATION MEDIANS:")
        summary.append("-" * 30)
        for sector, metrics in sector_avg.iterrows():
            summary.append(f"{sector}:")
            summary.append(f"  P/E: {format_number(metrics['pe_ratio'])}")
            summary.append(f"  P/B: {format_number(metrics['pb_ratio'])}")
            summary.append(f"  P/S: {format_number(metrics['ps_ratio'])}")
            summary.append("")
        
        summary_text = "\n".join(summary)
        self.loader.save_results(summary_text, "valuation_summary", self.output_dir, 'txt')
        print(summary_text)

def main():
    """Main function to run valuation analysis"""
    try:
        # Initialize data loader
        loader = FinancialDataLoader()
        companies = loader.load_all_companies()
        
        if not companies:
            print("❌ No financial data found!")
            return
        
        # Initialize valuation calculator
        valuation_calc = ValuationIndicators(loader)
        
        # Run analysis
        valuations_df, dcf_df, relative_df = valuation_calc.run_analysis_for_all_companies()
        
        print(f"\n✅ Valuation analysis completed!")
        print(f"📊 Results saved in: {valuation_calc.output_dir}")
        print(f"💾 Basic valuations: {len(valuations_df)} companies")
        print(f"🔍 DCF analysis: {len(dcf_df)} companies")
        print(f"📊 Relative valuations: {len(relative_df)} companies")
        
    except Exception as e:
        print(f"❌ Error in valuation analysis: {e}")

if __name__ == "__main__":
    main() 