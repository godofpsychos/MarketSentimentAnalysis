#!/usr/bin/env python3
"""
Growth Indicators Calculator
Calculates various growth metrics for fundamental analysis
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))

from data_loader import FinancialDataLoader, safe_divide, format_percentage, format_number, calculate_percentage_change, sanitize_dict_values
import pandas as pd
import numpy as np

class GrowthIndicators:
    """Calculate growth indicators for companies"""
    
    def __init__(self, data_loader):
        self.loader = data_loader
        self.output_dir = "outputs/growth"
        
    def calculate_revenue_growth(self, symbol):
        """Calculate revenue growth trends"""
        try:
            revenue = self.loader.get_specific_financial_item(symbol, 'income_statement', 'Total Revenue')
            
            if revenue.empty or len(revenue) < 2:
                return None
            
            revenue = revenue.sort_values('period')
            
            # Calculate year-over-year growth
            revenue['yoy_growth'] = revenue['value'].pct_change() * 100
            
            # Calculate CAGR over available period - skip NaN values
            # Find first non-NaN positive value
            valid_values = revenue[revenue['value'].notna() & (revenue['value'] > 0)]
            
            if len(valid_values) >= 2:
                first_value = valid_values['value'].iloc[0]
                last_value = valid_values['value'].iloc[-1]
                
                # Calculate years between first and last valid values
                first_period = valid_values['period'].iloc[0]
                last_period = valid_values['period'].iloc[-1]
                years_diff = (last_period - first_period).days / 365.25
                
                if years_diff > 0:
                    cagr = ((last_value / first_value) ** (1/years_diff) - 1) * 100
                else:
                    cagr = np.nan
            else:
                cagr = np.nan
            
            # Recent trend (last 3 years average growth)
            recent_growth = revenue['yoy_growth'].tail(3).mean()
            
            result = {
                'symbol': symbol,
                'periods_analyzed': len(revenue),
                'first_revenue': first_value,
                'latest_revenue': last_value,
                'revenue_cagr_percent': round(cagr, 2) if pd.notna(cagr) else np.nan,
                'recent_avg_growth_percent': round(recent_growth, 2) if pd.notna(recent_growth) else np.nan,
                'latest_yoy_growth_percent': round(revenue['yoy_growth'].iloc[-1], 2) if pd.notna(revenue['yoy_growth'].iloc[-1]) else np.nan,
                'revenue_volatility': round(revenue['yoy_growth'].std(), 2) if len(revenue) > 2 else np.nan
            }
            
            return sanitize_dict_values(result)
            
        except Exception as e:
            print(f"Error calculating revenue growth for {symbol}: {e}")
            return None
    
    def calculate_earnings_growth(self, symbol):
        """Calculate earnings growth trends"""
        try:
            net_income = self.loader.get_specific_financial_item(symbol, 'income_statement', 'Net Income')
            operating_income = self.loader.get_specific_financial_item(symbol, 'income_statement', 'Operating Income')
            ebitda = self.loader.get_specific_financial_item(symbol, 'income_statement', 'EBITDA')
            
            if net_income.empty or len(net_income) < 2:
                return None
            
            results = {}
            
            # Net Income Growth
            net_income = net_income.sort_values('period')
            net_income['yoy_growth'] = net_income['value'].pct_change() * 100
            
            # Calculate CAGR for net income - skip NaN values
            # Find first non-NaN positive value
            valid_values = net_income[net_income['value'].notna() & (net_income['value'] > 0)]
            
            if len(valid_values) >= 2:
                first_ni = valid_values['value'].iloc[0]
                last_ni = valid_values['value'].iloc[-1]
                
                # Calculate years between first and last valid values
                first_period = valid_values['period'].iloc[0]
                last_period = valid_values['period'].iloc[-1]
                years_diff = (last_period - first_period).days / 365.25
                
                if years_diff > 0:
                    ni_cagr = ((last_ni / first_ni) ** (1/years_diff) - 1) * 100
                else:
                    ni_cagr = np.nan
            else:
                ni_cagr = np.nan
            
            results.update({
                'symbol': symbol,
                'net_income_cagr_percent': round(ni_cagr, 2) if pd.notna(ni_cagr) else np.nan,
                'latest_ni_yoy_growth_percent': round(net_income['yoy_growth'].iloc[-1], 2) if pd.notna(net_income['yoy_growth'].iloc[-1]) else np.nan,
                'ni_recent_avg_growth_percent': round(net_income['yoy_growth'].tail(3).mean(), 2) if len(net_income) >= 3 else np.nan,
                'earnings_volatility': round(net_income['yoy_growth'].std(), 2) if len(net_income) > 2 else np.nan
            })
            
            # Operating Income Growth
            if not operating_income.empty and len(operating_income) >= 2:
                operating_income = operating_income.sort_values('period')
                operating_income['yoy_growth'] = operating_income['value'].pct_change() * 100
                
                results.update({
                    'latest_oi_yoy_growth_percent': round(operating_income['yoy_growth'].iloc[-1], 2) if pd.notna(operating_income['yoy_growth'].iloc[-1]) else np.nan,
                    'oi_recent_avg_growth_percent': round(operating_income['yoy_growth'].tail(3).mean(), 2) if len(operating_income) >= 3 else np.nan
                })
            
            # EBITDA Growth
            if not ebitda.empty and len(ebitda) >= 2:
                ebitda = ebitda.sort_values('period')
                ebitda['yoy_growth'] = ebitda['value'].pct_change() * 100
                
                results.update({
                    'latest_ebitda_yoy_growth_percent': round(ebitda['yoy_growth'].iloc[-1], 2) if pd.notna(ebitda['yoy_growth'].iloc[-1]) else np.nan,
                    'ebitda_recent_avg_growth_percent': round(ebitda['yoy_growth'].tail(3).mean(), 2) if len(ebitda) >= 3 else np.nan
                })
            
            return results
            
        except Exception as e:
            print(f"Error calculating earnings growth for {symbol}: {e}")
            return None
    
    def calculate_sustainable_growth_rate(self, symbol):
        """Calculate sustainable growth rate: ROE × (1 - Payout Ratio)"""
        try:
            # Get financial health data for ROE
            health = self.loader.get_financial_health(symbol)
            
            # Get net income for dividend calculations
            net_income = self.loader.get_specific_financial_item(symbol, 'income_statement', 'Net Income')
            
            # Get dividend data
            dividends = self.loader.get_dividends(symbol)
            
            if not health or net_income.empty:
                return None
            
            roe = health.get('return_on_equity', 0)
            
            # Calculate dividend payout ratio
            latest_ni = net_income['value'].iloc[-1] if not net_income.empty else 0
            
            # Calculate total dividends for latest year
            if dividends:
                latest_year = str(net_income['period'].iloc[-1].year) if not net_income.empty else None
                total_dividends = 0
                
                for date, dividend_info in dividends.items():
                    if latest_year and date.startswith(latest_year):
                        total_dividends += dividend_info.get('amount', 0)
                
                payout_ratio = safe_divide(total_dividends, latest_ni) if latest_ni > 0 else 0
            else:
                payout_ratio = 0
            
            # Calculate sustainable growth rate
            retention_ratio = 1 - payout_ratio
            sgr = roe * retention_ratio * 100
            
            # Interpret SGR
            if sgr > 15:
                interpretation = "High growth potential"
            elif sgr > 8:
                interpretation = "Moderate growth potential"
            elif sgr > 0:
                interpretation = "Limited growth potential"
            else:
                interpretation = "Needs external financing"
            
            return {
                'symbol': symbol,
                'roe_percent': round(roe * 100, 2),
                'payout_ratio_percent': round(payout_ratio * 100, 2),
                'retention_ratio_percent': round(retention_ratio * 100, 2),
                'sustainable_growth_rate_percent': round(sgr, 2),
                'total_dividends': total_dividends if 'total_dividends' in locals() else 0,
                'interpretation': interpretation
            }
            
        except Exception as e:
            print(f"Error calculating sustainable growth rate for {symbol}: {e}")
            return None
    
    def calculate_growth_quality_score(self, symbol):
        """Calculate growth quality based on consistency and sustainability"""
        try:
            # Get growth data
            revenue_growth = self.calculate_revenue_growth(symbol)
            earnings_growth = self.calculate_earnings_growth(symbol)
            
            if not revenue_growth or not earnings_growth:
                return None
            
            # Scoring factors (0-100 scale)
            score = 0
            factors = []
            
            # 1. Revenue Growth (25 points)
            rev_cagr = revenue_growth.get('revenue_cagr_percent', 0)
            if rev_cagr > 15:
                rev_score = 25
            elif rev_cagr > 10:
                rev_score = 20
            elif rev_cagr > 5:
                rev_score = 15
            elif rev_cagr > 0:
                rev_score = 10
            else:
                rev_score = 0
            
            score += rev_score
            factors.append(f"Revenue Growth: {rev_score}/25")
            
            # 2. Earnings Growth (25 points)
            ni_cagr = earnings_growth.get('net_income_cagr_percent', 0)
            if pd.notna(ni_cagr):
                if ni_cagr > 20:
                    earn_score = 25
                elif ni_cagr > 15:
                    earn_score = 20
                elif ni_cagr > 10:
                    earn_score = 15
                elif ni_cagr > 0:
                    earn_score = 10
                else:
                    earn_score = 0
            else:
                earn_score = 0
            
            score += earn_score
            factors.append(f"Earnings Growth: {earn_score}/25")
            
            # 3. Growth Consistency (25 points)
            rev_volatility = revenue_growth.get('revenue_volatility', 100)
            earn_volatility = earnings_growth.get('earnings_volatility', 100)
            
            if pd.notna(rev_volatility) and pd.notna(earn_volatility):
                avg_volatility = (rev_volatility + earn_volatility) / 2
                if avg_volatility < 10:
                    consistency_score = 25
                elif avg_volatility < 20:
                    consistency_score = 20
                elif avg_volatility < 30:
                    consistency_score = 15
                elif avg_volatility < 50:
                    consistency_score = 10
                else:
                    consistency_score = 0
            else:
                consistency_score = 10  # Default moderate score
            
            score += consistency_score
            factors.append(f"Consistency: {consistency_score}/25")
            
            # 4. Recent Performance (25 points)
            recent_rev_growth = revenue_growth.get('recent_avg_growth_percent', 0)
            recent_earn_growth = earnings_growth.get('ni_recent_avg_growth_percent', 0)
            
            if pd.notna(recent_rev_growth) and pd.notna(recent_earn_growth):
                avg_recent = (recent_rev_growth + recent_earn_growth) / 2
                if avg_recent > 15:
                    recent_score = 25
                elif avg_recent > 10:
                    recent_score = 20
                elif avg_recent > 5:
                    recent_score = 15
                elif avg_recent > 0:
                    recent_score = 10
                else:
                    recent_score = 0
            else:
                recent_score = 0
            
            score += recent_score
            factors.append(f"Recent Performance: {recent_score}/25")
            
            # Interpret score
            if score >= 80:
                quality = "Excellent Growth Quality"
            elif score >= 65:
                quality = "Good Growth Quality"
            elif score >= 50:
                quality = "Average Growth Quality"
            elif score >= 35:
                quality = "Below Average Growth Quality"
            else:
                quality = "Poor Growth Quality"
            
            return {
                'symbol': symbol,
                'growth_quality_score': round(score, 1),
                'quality_interpretation': quality,
                'score_breakdown': "; ".join(factors)
            }
            
        except Exception as e:
            print(f"Error calculating growth quality for {symbol}: {e}")
            return None
    
    def run_analysis_for_all_companies(self):
        """Run growth analysis for all companies"""
        print("📈 CALCULATING GROWTH INDICATORS")
        print("=" * 60)
        
        all_revenue_growth = []
        all_earnings_growth = []
        all_sustainable_growth = []
        all_quality_scores = []
        
        for symbol in self.loader.companies_list:
            print(f"Processing {symbol}...")
            
            company_info = self.loader.get_company_info(symbol)
            
            # Revenue growth
            revenue_growth = self.calculate_revenue_growth(symbol)
            if revenue_growth:
                revenue_growth.update({
                    'company_name': company_info['name'],
                    'sector': company_info['sector']
                })
                all_revenue_growth.append(revenue_growth)
            
            # Earnings growth
            earnings_growth = self.calculate_earnings_growth(symbol)
            if earnings_growth:
                earnings_growth.update({
                    'company_name': company_info['name'],
                    'sector': company_info['sector']
                })
                all_earnings_growth.append(earnings_growth)
            
            # Sustainable growth rate
            sgr = self.calculate_sustainable_growth_rate(symbol)
            if sgr:
                sgr.update({
                    'company_name': company_info['name'],
                    'sector': company_info['sector']
                })
                all_sustainable_growth.append(sgr)
            
            # Growth quality score
            quality = self.calculate_growth_quality_score(symbol)
            if quality:
                quality.update({
                    'company_name': company_info['name'],
                    'sector': company_info['sector']
                })
                all_quality_scores.append(quality)
        
        # Convert to DataFrames
        revenue_df = pd.DataFrame(all_revenue_growth)
        earnings_df = pd.DataFrame(all_earnings_growth)
        sgr_df = pd.DataFrame(all_sustainable_growth)
        quality_df = pd.DataFrame(all_quality_scores)
        
        # Save results
        if not revenue_df.empty:
            self.loader.save_results(revenue_df, "revenue_growth", self.output_dir)
            self.loader.save_results(all_revenue_growth, "revenue_growth", self.output_dir, 'json')
        
        if not earnings_df.empty:
            self.loader.save_results(earnings_df, "earnings_growth", self.output_dir)
            self.loader.save_results(all_earnings_growth, "earnings_growth", self.output_dir, 'json')
        
        if not sgr_df.empty:
            self.loader.save_results(sgr_df, "sustainable_growth_rate", self.output_dir)
            self.loader.save_results(all_sustainable_growth, "sustainable_growth_rate", self.output_dir, 'json')
        
        if not quality_df.empty:
            self.loader.save_results(quality_df, "growth_quality_scores", self.output_dir)
            self.loader.save_results(all_quality_scores, "growth_quality_scores", self.output_dir, 'json')
        
        # Generate summary
        self.generate_growth_summary(revenue_df, earnings_df, quality_df)
        
        return revenue_df, earnings_df, sgr_df, quality_df
    
    def generate_growth_summary(self, revenue_df, earnings_df, quality_df):
        """Generate growth analysis summary"""
        summary = []
        summary.append("📈 GROWTH ANALYSIS SUMMARY")
        summary.append("=" * 50)
        
        if not revenue_df.empty:
            summary.append(f"Companies analyzed: {len(revenue_df)}")
            summary.append("")
            
            # Top revenue growers
            top_revenue = revenue_df.nlargest(10, 'revenue_cagr_percent')[['symbol', 'company_name', 'sector', 'revenue_cagr_percent']]
            summary.append("🚀 TOP REVENUE GROWERS (CAGR):")
            summary.append("-" * 30)
            for _, row in top_revenue.iterrows():
                summary.append(f"{row['symbol']}: {format_percentage(row['revenue_cagr_percent'])} ({row['sector']})")
            summary.append("")
        
        if not earnings_df.empty:
            # Top earnings growers
            top_earnings = earnings_df.nlargest(10, 'net_income_cagr_percent')[['symbol', 'company_name', 'sector', 'net_income_cagr_percent']]
            summary.append("💰 TOP EARNINGS GROWERS (CAGR):")
            summary.append("-" * 30)
            for _, row in top_earnings.iterrows():
                summary.append(f"{row['symbol']}: {format_percentage(row['net_income_cagr_percent'])} ({row['sector']})")
            summary.append("")
        
        if not quality_df.empty:
            # Best growth quality
            top_quality = quality_df.nlargest(10, 'growth_quality_score')[['symbol', 'company_name', 'sector', 'growth_quality_score', 'quality_interpretation']]
            summary.append("⭐ BEST GROWTH QUALITY:")
            summary.append("-" * 25)
            for _, row in top_quality.iterrows():
                summary.append(f"{row['symbol']}: {row['growth_quality_score']}/100 - {row['quality_interpretation']}")
            summary.append("")
        
        # Sector growth averages
        if not revenue_df.empty:
            sector_growth = revenue_df.groupby('sector')[['revenue_cagr_percent']].mean()
            summary.append("📊 SECTOR AVERAGE REVENUE GROWTH:")
            summary.append("-" * 35)
            for sector, metrics in sector_growth.iterrows():
                summary.append(f"{sector}: {format_percentage(metrics['revenue_cagr_percent'])}")
            summary.append("")
        
        summary_text = "\n".join(summary)
        self.loader.save_results(summary_text, "growth_summary", self.output_dir, 'txt')
        print(summary_text)

def main():
    """Main function to run growth analysis"""
    try:
        # Initialize data loader
        loader = FinancialDataLoader()
        companies = loader.load_all_companies()
        
        if not companies:
            print("❌ No financial data found!")
            return
        
        # Initialize growth calculator
        growth_calc = GrowthIndicators(loader)
        
        # Run analysis
        revenue_df, earnings_df, sgr_df, quality_df = growth_calc.run_analysis_for_all_companies()
        
        print(f"\n✅ Growth analysis completed!")
        print(f"📊 Results saved in: {growth_calc.output_dir}")
        print(f"📈 Revenue growth: {len(revenue_df)} companies")
        print(f"💰 Earnings growth: {len(earnings_df)} companies")
        print(f"🎯 Sustainable growth: {len(sgr_df)} companies")
        print(f"⭐ Quality scores: {len(quality_df)} companies")
        
    except Exception as e:
        print(f"❌ Error in growth analysis: {e}")

if __name__ == "__main__":
    main() 