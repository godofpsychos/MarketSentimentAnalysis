#!/usr/bin/env python3
"""
Comprehensive Fundamental Analysis Score Calculator
This module combines all fundamental indicators to provide:
1. Reliability Score (0-100)
2. Future Growth Scope (0-100)
3. Overall Investment Grade (A+ to F)
4. Risk Assessment (Low/Medium/High)
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))

from data_loader import FinancialDataLoader, safe_divide
import pandas as pd
import numpy as np
from datetime import datetime

# Import all indicator calculators
from liquidity_indicators import LiquidityIndicators
from growth_indicators import GrowthIndicators
from valuation_indicators import ValuationIndicators
from profitability_indicators import ProfitabilityIndicators
from leverage_indicators import LeverageIndicators

class FundamentalScoreCalculator:
    """Calculate comprehensive fundamental analysis scores"""
    
    def __init__(self, data_loader):
        self.loader = data_loader
        self.output_dir = "outputs/comprehensive"
        
        # Initialize all indicator calculators
        self.liquidity = LiquidityIndicators(data_loader)
        self.growth = GrowthIndicators(data_loader)
        self.valuation = ValuationIndicators(data_loader)
        self.profitability = ProfitabilityIndicators(data_loader)
        self.leverage = LeverageIndicators(data_loader)
        
    def calculate_reliability_score(self, symbol):
        """
        Calculate reliability score based on financial stability factors
        Factors: Profitability consistency, debt levels, liquidity, dividend history
        Scale: 0-100 (higher is more reliable)
        """
        try:
            score = 0
            factors = []
            
            # 1. Profitability Analysis (35 points)
            profitability_data = self.profitability.calculate_basic_profitability_ratios(symbol)
            if profitability_data:
                # ROE consistency (15 points)
                roe = profitability_data.get('roe_percent', 0)
                if roe >= 15:
                    score += 15
                    factors.append("Excellent ROE (15%+)")
                elif roe >= 10:
                    score += 12
                    factors.append("Good ROE (10-15%)")
                elif roe >= 5:
                    score += 8
                    factors.append("Average ROE (5-10%)")
                elif roe > 0:
                    score += 4
                    factors.append("Low ROE (0-5%)")
                else:
                    factors.append("Negative ROE")
                
                # Net margin (10 points)
                net_margin = profitability_data.get('net_margin_percent', 0)
                if net_margin >= 15:
                    score += 10
                    factors.append("High profit margins")
                elif net_margin >= 8:
                    score += 7
                    factors.append("Good profit margins")
                elif net_margin >= 3:
                    score += 4
                    factors.append("Average profit margins")
                elif net_margin > 0:
                    score += 2
                    factors.append("Low profit margins")
                else:
                    factors.append("Negative margins")
                
                # Operating margin (10 points)
                op_margin = profitability_data.get('operating_margin_percent', 0)
                if op_margin >= 20:
                    score += 10
                elif op_margin >= 12:
                    score += 7
                elif op_margin >= 5:
                    score += 4
                elif op_margin > 0:
                    score += 2
            
            # 2. Liquidity Analysis (25 points)
            liquidity_data = self.liquidity.calculate_basic_liquidity_ratios(symbol)
            if liquidity_data:
                # Current ratio (15 points)
                current_ratio = liquidity_data.get('current_ratio', 0)
                if current_ratio >= 2.0:
                    score += 15
                    factors.append("Excellent liquidity")
                elif current_ratio >= 1.5:
                    score += 12
                    factors.append("Good liquidity")
                elif current_ratio >= 1.0:
                    score += 8
                    factors.append("Adequate liquidity")
                elif current_ratio >= 0.8:
                    score += 4
                    factors.append("Weak liquidity")
                else:
                    factors.append("Poor liquidity")
                
                # Quick ratio (10 points)
                quick_ratio = liquidity_data.get('quick_ratio', 0)
                if quick_ratio >= 1.5:
                    score += 10
                elif quick_ratio >= 1.0:
                    score += 8
                elif quick_ratio >= 0.8:
                    score += 5
                elif quick_ratio >= 0.5:
                    score += 2
            
            # 3. Leverage Analysis (25 points)
            leverage_data = self.leverage.calculate_basic_leverage_ratios(symbol)
            if leverage_data:
                # Debt to equity (15 points)
                debt_to_equity = leverage_data.get('debt_to_equity', 0)
                if debt_to_equity <= 0.3:
                    score += 15
                    factors.append("Conservative debt levels")
                elif debt_to_equity <= 0.6:
                    score += 12
                    factors.append("Moderate debt levels")
                elif debt_to_equity <= 1.0:
                    score += 8
                    factors.append("Higher debt levels")
                elif debt_to_equity <= 2.0:
                    score += 4
                    factors.append("High leverage")
                else:
                    factors.append("Very high leverage")
                
                # Interest coverage (10 points)
                interest_coverage = leverage_data.get('interest_coverage', 0)
                if interest_coverage == float('inf') or interest_coverage > 20:
                    score += 10
                    factors.append("No interest burden")
                elif interest_coverage >= 10:
                    score += 8
                    factors.append("Excellent interest coverage")
                elif interest_coverage >= 5:
                    score += 6
                    factors.append("Good interest coverage")
                elif interest_coverage >= 2:
                    score += 3
                    factors.append("Adequate interest coverage")
                elif interest_coverage >= 1:
                    score += 1
                    factors.append("Weak interest coverage")
                else:
                    factors.append("Poor interest coverage")
            
            # 4. Growth Consistency (15 points)
            revenue_growth = self.growth.calculate_revenue_growth(symbol)
            if revenue_growth:
                revenue_volatility = revenue_growth.get('revenue_volatility', 100)
                recent_growth = revenue_growth.get('recent_avg_growth_percent', 0)
                
                # Revenue growth stability
                if revenue_volatility <= 10 and recent_growth > 0:
                    score += 10
                    factors.append("Consistent revenue growth")
                elif revenue_volatility <= 20 and recent_growth > 0:
                    score += 7
                    factors.append("Stable revenue growth")
                elif recent_growth > 0:
                    score += 4
                    factors.append("Positive revenue growth")
                elif recent_growth >= -5:
                    score += 2
                    factors.append("Stable revenue")
                else:
                    factors.append("Declining revenue")
                
                # Growth trend (5 points)
                cagr = revenue_growth.get('revenue_cagr_percent', 0)
                if cagr >= 15:
                    score += 5
                elif cagr >= 8:
                    score += 4
                elif cagr >= 3:
                    score += 2
                elif cagr > 0:
                    score += 1
            
            # Determine reliability grade
            if score >= 90:
                grade = "A+"
                description = "Exceptionally Reliable"
            elif score >= 80:
                grade = "A"
                description = "Highly Reliable"
            elif score >= 70:
                grade = "B+"
                description = "Very Reliable"
            elif score >= 60:
                grade = "B"
                description = "Reliable"
            elif score >= 50:
                grade = "C+"
                description = "Moderately Reliable"
            elif score >= 40:
                grade = "C"
                description = "Average Reliability"
            elif score >= 30:
                grade = "D"
                description = "Below Average"
            else:
                grade = "F"
                description = "Poor Reliability"
            
            return {
                'symbol': symbol,
                'reliability_score': min(score, 100),
                'reliability_grade': grade,
                'reliability_description': description,
                'key_factors': factors[:5],  # Top 5 factors
                'calculated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error calculating reliability score for {symbol}: {e}")
            return None
    
    def calculate_growth_scope(self, symbol):
        """
        Calculate future growth scope based on growth indicators and market position
        Factors: Revenue growth, earnings growth, ROE, sustainable growth rate, market position
        Scale: 0-100 (higher indicates better growth prospects)
        """
        try:
            score = 0
            factors = []
            
            # 1. Revenue Growth Analysis (30 points)
            revenue_growth = self.growth.calculate_revenue_growth(symbol)
            if revenue_growth:
                cagr = revenue_growth.get('revenue_cagr_percent', 0)
                recent_growth = revenue_growth.get('recent_avg_growth_percent', 0)
                
                # Historical growth (15 points)
                if cagr >= 20:
                    score += 15
                    factors.append("Exceptional revenue growth")
                elif cagr >= 15:
                    score += 12
                    factors.append("High revenue growth")
                elif cagr >= 10:
                    score += 9
                    factors.append("Good revenue growth")
                elif cagr >= 5:
                    score += 6
                    factors.append("Moderate revenue growth")
                elif cagr > 0:
                    score += 3
                    factors.append("Slow revenue growth")
                else:
                    factors.append("Declining revenue")
                
                # Recent trend (15 points)
                if recent_growth >= 25:
                    score += 15
                elif recent_growth >= 15:
                    score += 12
                elif recent_growth >= 8:
                    score += 9
                elif recent_growth >= 3:
                    score += 6
                elif recent_growth > 0:
                    score += 3
            
            # 2. Earnings Growth Analysis (25 points)
            earnings_growth = self.growth.calculate_earnings_growth(symbol)
            if earnings_growth:
                ni_cagr = earnings_growth.get('net_income_cagr_percent', 0)
                recent_ni_growth = earnings_growth.get('ni_recent_avg_growth_percent', 0)
                
                # Earnings CAGR (15 points)
                if ni_cagr >= 25:
                    score += 15
                    factors.append("Excellent earnings growth")
                elif ni_cagr >= 18:
                    score += 12
                    factors.append("Strong earnings growth")
                elif ni_cagr >= 12:
                    score += 9
                    factors.append("Good earnings growth")
                elif ni_cagr >= 6:
                    score += 6
                    factors.append("Moderate earnings growth")
                elif ni_cagr > 0:
                    score += 3
                    factors.append("Slow earnings growth")
                
                # Recent earnings trend (10 points)
                if recent_ni_growth >= 20:
                    score += 10
                elif recent_ni_growth >= 12:
                    score += 8
                elif recent_ni_growth >= 5:
                    score += 5
                elif recent_ni_growth > 0:
                    score += 3
            
            # 3. Profitability Efficiency (20 points)
            profitability_data = self.profitability.calculate_basic_profitability_ratios(symbol)
            if profitability_data:
                roe = profitability_data.get('roe_percent', 0)
                roa = profitability_data.get('roa_percent', 0)
                
                # ROE growth potential (12 points)
                if roe >= 20:
                    score += 12
                    factors.append("High ROE indicates strong growth capacity")
                elif roe >= 15:
                    score += 9
                elif roe >= 10:
                    score += 6
                elif roe >= 5:
                    score += 3
                
                # Asset efficiency (8 points)
                if roa >= 15:
                    score += 8
                    factors.append("Excellent asset utilization")
                elif roa >= 10:
                    score += 6
                elif roa >= 5:
                    score += 4
                elif roa > 0:
                    score += 2
            
            # 4. Financial Capacity for Growth (15 points)
            leverage_data = self.leverage.calculate_basic_leverage_ratios(symbol)
            if leverage_data:
                debt_to_equity = leverage_data.get('debt_to_equity', 0)
                
                # Debt capacity for growth (10 points)
                if debt_to_equity <= 0.3:
                    score += 10
                    factors.append("Low debt allows growth financing")
                elif debt_to_equity <= 0.6:
                    score += 8
                    factors.append("Moderate debt with growth capacity")
                elif debt_to_equity <= 1.0:
                    score += 5
                    factors.append("Higher debt limits growth")
                elif debt_to_equity <= 1.5:
                    score += 2
                else:
                    factors.append("High debt constrains growth")
            
            # Cash position (5 points)
            liquidity_data = self.liquidity.calculate_basic_liquidity_ratios(symbol)
            if liquidity_data:
                cash_ratio = liquidity_data.get('cash_ratio', 0)
                if cash_ratio >= 0.5:
                    score += 5
                    factors.append("Strong cash position")
                elif cash_ratio >= 0.3:
                    score += 3
                elif cash_ratio >= 0.15:
                    score += 2
            
            # 5. Sustainable Growth Rate (10 points)
            sgr_data = self.growth.calculate_sustainable_growth_rate(symbol)
            if sgr_data:
                sgr = sgr_data.get('sustainable_growth_rate_percent', 0)
                if sgr >= 15:
                    score += 10
                    factors.append("High sustainable growth rate")
                elif sgr >= 10:
                    score += 8
                elif sgr >= 6:
                    score += 5
                elif sgr > 0:
                    score += 3
            
            # Determine growth scope grade
            if score >= 85:
                grade = "Excellent"
                description = "Very High Growth Potential"
            elif score >= 70:
                grade = "High"
                description = "High Growth Potential"
            elif score >= 55:
                grade = "Good"
                description = "Good Growth Potential"
            elif score >= 40:
                grade = "Moderate"
                description = "Moderate Growth Potential"
            elif score >= 25:
                grade = "Low"
                description = "Limited Growth Potential"
            else:
                grade = "Poor"
                description = "Poor Growth Prospects"
            
            return {
                'symbol': symbol,
                'growth_scope_score': min(score, 100),
                'growth_scope_grade': grade,
                'growth_scope_description': description,
                'key_growth_factors': factors[:5],
                'calculated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error calculating growth scope for {symbol}: {e}")
            return None
    
    def calculate_valuation_attractiveness(self, symbol):
        """
        Calculate how attractively valued the stock is
        Factors: P/E ratio, P/B ratio, P/S ratio, relative valuation
        Scale: 0-100 (higher means more attractive/undervalued)
        """
        try:
            score = 0
            factors = []
            
            valuation_data = self.valuation.calculate_basic_valuation_ratios(symbol)
            if not valuation_data:
                return None
            
            sector = valuation_data.get('sector', 'Unknown')
            
            # 1. P/E Ratio Analysis (30 points)
            pe_ratio = valuation_data.get('pe_ratio')
            if pd.notna(pe_ratio) and pe_ratio > 0:
                if pe_ratio <= 15:
                    score += 30
                    factors.append("Very attractive P/E ratio")
                elif pe_ratio <= 20:
                    score += 25
                    factors.append("Good P/E ratio")
                elif pe_ratio <= 25:
                    score += 20
                    factors.append("Fair P/E ratio")
                elif pe_ratio <= 35:
                    score += 10
                    factors.append("High P/E ratio")
                else:
                    score += 5
                    factors.append("Very high P/E ratio")
            
            # 2. P/B Ratio Analysis (25 points)
            pb_ratio = valuation_data.get('pb_ratio')
            if pd.notna(pb_ratio) and pb_ratio > 0:
                if pb_ratio <= 1.0:
                    score += 25
                    factors.append("Trading below book value")
                elif pb_ratio <= 2.0:
                    score += 20
                    factors.append("Reasonable P/B ratio")
                elif pb_ratio <= 3.0:
                    score += 15
                    factors.append("Moderate P/B ratio")
                elif pb_ratio <= 5.0:
                    score += 8
                    factors.append("High P/B ratio")
                else:
                    score += 3
                    factors.append("Very high P/B ratio")
            
            # 3. P/S Ratio Analysis (20 points)
            ps_ratio = valuation_data.get('ps_ratio')
            if pd.notna(ps_ratio) and ps_ratio > 0:
                if ps_ratio <= 1.0:
                    score += 20
                    factors.append("Excellent P/S ratio")
                elif ps_ratio <= 2.0:
                    score += 15
                    factors.append("Good P/S ratio")
                elif ps_ratio <= 4.0:
                    score += 10
                    factors.append("Fair P/S ratio")
                elif ps_ratio <= 8.0:
                    score += 5
                    factors.append("High P/S ratio")
                else:
                    factors.append("Very high P/S ratio")
            
            # 4. DCF Valuation (25 points)
            dcf_data = self.valuation.calculate_dcf_valuation(symbol)
            if dcf_data:
                fair_value_ratio = dcf_data.get('fair_value_ratio')
                if pd.notna(fair_value_ratio):
                    if fair_value_ratio >= 1.3:
                        score += 25
                        factors.append("Significantly undervalued (DCF)")
                    elif fair_value_ratio >= 1.1:
                        score += 20
                        factors.append("Undervalued (DCF)")
                    elif fair_value_ratio >= 0.9:
                        score += 15
                        factors.append("Fair value (DCF)")
                    elif fair_value_ratio >= 0.7:
                        score += 8
                        factors.append("Overvalued (DCF)")
                    else:
                        score += 3
                        factors.append("Significantly overvalued (DCF)")
            
            # Determine valuation grade
            if score >= 85:
                grade = "Excellent"
                description = "Highly Attractive Valuation"
            elif score >= 70:
                grade = "Good"
                description = "Attractive Valuation"
            elif score >= 55:
                grade = "Fair"
                description = "Fair Valuation"
            elif score >= 40:
                grade = "Expensive"
                description = "Expensive Valuation"
            else:
                grade = "Overvalued"
                description = "Overvalued"
            
            return {
                'symbol': symbol,
                'valuation_score': min(score, 100),
                'valuation_grade': grade,
                'valuation_description': description,
                'valuation_factors': factors[:4],
                'calculated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error calculating valuation attractiveness for {symbol}: {e}")
            return None
    
    def calculate_overall_investment_grade(self, symbol):
        """
        Calculate overall investment grade combining all factors
        """
        try:
            # Get all component scores
            reliability = self.calculate_reliability_score(symbol)
            growth = self.calculate_growth_scope(symbol)
            valuation = self.calculate_valuation_attractiveness(symbol)
            
            # Handle None values with defaults instead of failing entirely
            if reliability is None:
                reliability = {
                    'reliability_score': 0,
                    'reliability_grade': 'F',
                    'reliability_description': 'Data Unavailable'
                }
            
            if growth is None:
                growth = {
                    'growth_scope_score': 0,
                    'growth_scope_grade': 'Poor',
                    'growth_scope_description': 'Data Unavailable'
                }
            
            if valuation is None:
                valuation = {
                    'valuation_score': 0,
                    'valuation_grade': 'N/A',
                    'valuation_description': 'Data Unavailable'
                }
            
            # Get scores with safe defaults
            reliability_score = reliability.get('reliability_score', 0)
            growth_score = growth.get('growth_scope_score', 0)
            valuation_score = valuation.get('valuation_score', 0)
            
            # Weights: Reliability 40%, Growth 35%, Valuation 25%
            overall_score = (reliability_score * 0.40 + 
                           growth_score * 0.35 + 
                           valuation_score * 0.25)
            
            # Risk assessment with safe defaults
            risk_factors = []
            risk_score = 0
            
            try:
                leverage_data = self.leverage.calculate_basic_leverage_ratios(symbol)
                if leverage_data:
                    debt_to_equity = leverage_data.get('debt_to_equity', 0)
                    if debt_to_equity > 2.0:
                        risk_score += 30
                        risk_factors.append("Very high debt levels")
                    elif debt_to_equity > 1.0:
                        risk_score += 15
                        risk_factors.append("High debt levels")
                    elif debt_to_equity > 0.6:
                        risk_score += 8
                        risk_factors.append("Moderate debt levels")
            except:
                risk_factors.append("Leverage data unavailable")
            
            try:
                liquidity_data = self.liquidity.calculate_basic_liquidity_ratios(symbol)
                if liquidity_data:
                    current_ratio = liquidity_data.get('current_ratio', 0)
                    if current_ratio < 1.0:
                        risk_score += 20
                        risk_factors.append("Poor liquidity")
                    elif current_ratio < 1.5:
                        risk_score += 10
                        risk_factors.append("Weak liquidity")
            except:
                risk_factors.append("Liquidity data unavailable")
            
            # Add default risk if no data available
            if not risk_factors:
                risk_factors.append("Limited financial data available")
                risk_score += 15
            
            # Determine risk level
            if risk_score >= 40:
                risk_level = "High"
            elif risk_score >= 20:
                risk_level = "Medium"
            else:
                risk_level = "Low"
            
            # Overall grade
            if overall_score >= 85:
                overall_grade = "A+"
                investment_recommendation = "Strong Buy"
            elif overall_score >= 75:
                overall_grade = "A"
                investment_recommendation = "Buy"
            elif overall_score >= 65:
                overall_grade = "B+"
                investment_recommendation = "Buy"
            elif overall_score >= 55:
                overall_grade = "B"
                investment_recommendation = "Hold"
            elif overall_score >= 45:
                overall_grade = "C+"
                investment_recommendation = "Hold"
            elif overall_score >= 35:
                overall_grade = "C"
                investment_recommendation = "Weak Hold"
            elif overall_score >= 25:
                overall_grade = "D"
                investment_recommendation = "Sell"
            elif overall_score > 0:
                overall_grade = "D-"
                investment_recommendation = "Sell"
            else:
                overall_grade = "N/A"
                investment_recommendation = "Data Unavailable"
            
            return {
                'symbol': symbol,
                'overall_score': round(max(overall_score, 0), 1),
                'overall_grade': overall_grade,
                'investment_recommendation': investment_recommendation,
                'risk_level': risk_level,
                'risk_factors': risk_factors,
                'component_scores': {
                    'reliability': max(reliability_score, 0),
                    'growth': max(growth_score, 0),
                    'valuation': max(valuation_score, 0)
                },
                'detailed_analysis': {
                    'reliability': reliability,
                    'growth': growth,
                    'valuation': valuation
                },
                'calculated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error calculating overall investment grade for {symbol}: {e}")
            # Return minimal default instead of None
            return {
                'symbol': symbol,
                'overall_score': 0,
                'overall_grade': 'N/A',
                'investment_recommendation': 'Data Unavailable',
                'risk_level': 'Unknown',
                'risk_factors': ['Calculation error'],
                'component_scores': {
                    'reliability': 0,
                    'growth': 0,
                    'valuation': 0
                },
                'detailed_analysis': {
                    'reliability': None,
                    'growth': None,
                    'valuation': None
                },
                'calculated_at': datetime.now().isoformat()
            }
    
    def generate_summary_for_frontend(self, symbol):
        """
        Generate a concise summary for frontend display in stock containers
        """
        try:
            overall_analysis = self.calculate_overall_investment_grade(symbol)
            if not overall_analysis:
                return None
            
            return {
                'symbol': symbol,
                'reliability_score': overall_analysis['component_scores']['reliability'],
                'growth_scope': overall_analysis['component_scores']['growth'],
                'valuation_score': overall_analysis['component_scores']['valuation'],
                'overall_score': overall_analysis['overall_score'],
                'overall_grade': overall_analysis['overall_grade'],
                'recommendation': overall_analysis['investment_recommendation'],
                'risk_level': overall_analysis['risk_level'],
                'key_highlights': [
                    f"Reliability: {overall_analysis['component_scores']['reliability']}/100",
                    f"Growth Potential: {overall_analysis['component_scores']['growth']}/100",
                    f"Valuation: {overall_analysis['component_scores']['valuation']}/100",
                    f"Risk: {overall_analysis['risk_level']}"
                ]
            }
            
        except Exception as e:
            print(f"Error generating summary for {symbol}: {e}")
            return None

def main():
    """Test the fundamental score calculator"""
    print("🎯 FUNDAMENTAL ANALYSIS SCORE CALCULATOR")
    print("=" * 60)
    
    # Initialize data loader
    loader = FinancialDataLoader()
    calculator = FundamentalScoreCalculator(loader)
    
    # Test with a few companies
    test_companies = ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS']
    
    for symbol in test_companies:
        print(f"\n📊 Analysis for {symbol}")
        print("-" * 40)
        
        # Generate complete analysis
        overall_analysis = calculator.calculate_overall_investment_grade(symbol)
        if overall_analysis:
            print(f"Overall Score: {overall_analysis['overall_score']}/100")
            print(f"Grade: {overall_analysis['overall_grade']}")
            print(f"Recommendation: {overall_analysis['investment_recommendation']}")
            print(f"Risk Level: {overall_analysis['risk_level']}")
            
            print("\nComponent Scores:")
            print(f"  Reliability: {overall_analysis['component_scores']['reliability']}/100")
            print(f"  Growth: {overall_analysis['component_scores']['growth']}/100")
            print(f"  Valuation: {overall_analysis['component_scores']['valuation']}/100")
        
        # Generate frontend summary
        summary = calculator.generate_summary_for_frontend(symbol)
        if summary:
            print(f"\nFrontend Summary:")
            for highlight in summary['key_highlights']:
                print(f"  • {highlight}")

if __name__ == "__main__":
    main()