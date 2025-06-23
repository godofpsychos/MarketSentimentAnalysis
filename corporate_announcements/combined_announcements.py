"""
Combined Corporate Announcements Scraper
Uses both BSE and NSE sources to get comprehensive corporate announcements
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from bse_announcements import BSEAnnouncements
from nse_announcements import NSEAnnouncements
import pandas as pd
import json
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CombinedAnnouncements:
    def __init__(self):
        """Initialize combined announcements scraper"""
        self.bse_scraper = BSEAnnouncements()
        self.nse_scraper = NSEAnnouncements()
        
        # Common company mappings (BSE code to NSE symbol)
        self.company_mapping = {
            # BSE Code: NSE Symbol
            532540: 'TCS',           # TCS
            500180: 'HDFCBANK',      # HDFC Bank
            500325: 'RELIANCE',      # Reliance
            500209: 'INFY',          # Infosys
            532174: 'ICICIBANK',     # ICICI Bank
            500034: 'BAJFINANCE',    # Bajaj Finance
            500696: 'HINDUNILVR',    # Hindustan Unilever
            532215: 'AXISBANK',      # Axis Bank
            500010: 'HDFC',          # HDFC
            500875: 'ITC',           # ITC
            500112: 'SBIN',          # State Bank of India
            500820: 'ASIANPAINT',    # Asian Paints
            532281: 'HCLTECH',       # HCL Technologies
            507685: 'WIPRO',         # Wipro
            500470: 'TATASTEEL',     # Tata Steel
            532454: 'BHARTIARTL',    # Bharti Airtel
            500400: 'TATACONSUM',    # Tata Consumer Products
            500295: 'NESTLEIND',     # Nestle India
            532755: 'TECHM',         # Tech Mahindra
            500114: 'TITAN',         # Titan Company
        }
        
        logger.info("Combined announcements scraper initialized")
    
    def get_company_announcements(self, bse_code=None, nse_symbol=None, company_name=None, days_back=30):
        """
        Get announcements from both BSE and NSE for a company
        
        Args:
            bse_code (int): BSE security code
            nse_symbol (str): NSE symbol
            company_name (str): Company name for searching
            days_back (int): Days to look back
        
        Returns:
            dict: Combined announcements from both exchanges
        """
        result = {
            'company_info': {
                'bse_code': bse_code,
                'nse_symbol': nse_symbol,
                'company_name': company_name
            },
            'bse_announcements': [],
            'nse_announcements': [],
            'combined_count': 0,
            'fetched_at': datetime.now().isoformat()
        }
        
        # Get BSE announcements
        if bse_code:
            logger.info(f"Fetching BSE announcements for code: {bse_code}")
            bse_announcements = self.bse_scraper.get_corporate_announcements(bse_code, days_back)
            result['bse_announcements'] = bse_announcements
            logger.info(f"Found {len(bse_announcements)} BSE announcements")
        
        # Get NSE announcements
        if nse_symbol or company_name:
            search_term = nse_symbol or company_name
            logger.info(f"Fetching NSE announcements for: {search_term}")
            
            try:
                # Get all corporate announcements from NSE
                all_nse_announcements = self.nse_scraper.get_rss_announcements('corporate_announcements', max_entries=100)
                
                # Filter by company if we got results
                if all_nse_announcements:
                    nse_announcements = self.nse_scraper.filter_announcements_by_company(all_nse_announcements, search_term)
                    result['nse_announcements'] = nse_announcements
                    logger.info(f"Found {len(nse_announcements)} NSE announcements")
                else:
                    logger.warning(f"No NSE announcements available for {search_term} - RSS feed may be down")
                    result['nse_announcements'] = []
                    
            except Exception as e:
                logger.error(f"Error fetching NSE announcements for {search_term}: {e}")
                result['nse_announcements'] = []
        
        result['combined_count'] = len(result['bse_announcements']) + len(result['nse_announcements'])
        return result
    
    def get_multiple_companies_announcements(self, companies, days_back=30):
        """
        Get announcements for multiple companies
        
        Args:
            companies (list): List of dicts with company info
                            [{'bse_code': 532540, 'nse_symbol': 'TCS', 'name': 'TCS'}]
            days_back (int): Days to look back
        
        Returns:
            dict: Announcements for all companies
        """
        all_results = {}
        
        for company in companies:
            company_key = company.get('name', f"BSE_{company.get('bse_code', 'Unknown')}")
            logger.info(f"Processing company: {company_key}")
            
            result = self.get_company_announcements(
                bse_code=company.get('bse_code'),
                nse_symbol=company.get('nse_symbol'),
                company_name=company.get('name'),
                days_back=days_back
            )
            
            all_results[company_key] = result
        
        return all_results
    
    def get_announcements_by_keywords(self, keywords, days_back=30, exchanges=['bse', 'nse']):
        """
        Get announcements filtered by keywords from both exchanges
        
        Args:
            keywords (list): List of keywords to search for
            days_back (int): Days to look back
            exchanges (list): Which exchanges to search ['bse', 'nse']
        
        Returns:
            dict: Filtered announcements from both exchanges
        """
        result = {
            'keywords': keywords,
            'bse_announcements': [],
            'nse_announcements': [],
            'combined_count': 0,
            'fetched_at': datetime.now().isoformat()
        }
        
        # Get BSE announcements with keywords
        if 'bse' in exchanges:
            logger.info(f"Searching BSE announcements with keywords: {keywords}")
            bse_results = []
            
            # Search across multiple major companies
            for bse_code in [532540, 500180, 500325, 500209, 532174]:  # TCS, HDFC Bank, Reliance, Infosys, ICICI
                try:
                    announcements = self.bse_scraper.get_announcements_with_keywords(
                        company_code=bse_code,
                        keywords=keywords,
                        days_back=days_back
                    )
                    for announcement in announcements:
                        announcement['bse_code'] = bse_code
                        bse_results.append(announcement)
                except Exception as e:
                    logger.warning(f"Error fetching BSE announcements for code {bse_code}: {e}")
            
            result['bse_announcements'] = bse_results
            logger.info(f"Found {len(bse_results)} BSE announcements with keywords")
        
        # Get NSE announcements with keywords
        if 'nse' in exchanges:
            logger.info(f"Searching NSE announcements with keywords: {keywords}")
            
            # Get all corporate announcements from NSE
            all_nse_announcements = self.nse_scraper.get_all_rss_announcements(max_entries_per_feed=50)
            
            nse_results = []
            for feed_type, announcements in all_nse_announcements.items():
                filtered = self.nse_scraper.filter_announcements_by_keywords(announcements, keywords)
                for announcement in filtered:
                    announcement['feed_source'] = feed_type
                    nse_results.append(announcement)
            
            result['nse_announcements'] = nse_results
            logger.info(f"Found {len(nse_results)} NSE announcements with keywords")
        
        result['combined_count'] = len(result['bse_announcements']) + len(result['nse_announcements'])
        return result
    
    def get_recent_corporate_actions(self, days=7):
        """
        Get recent corporate actions (dividends, bonuses, splits) from both exchanges
        
        Args:
            days (int): Number of days to look back
        
        Returns:
            dict: Recent corporate actions
        """
        corporate_action_keywords = [
            'dividend', 'bonus', 'split', 'rights', 'buyback',
            'merger', 'demerger', 'spin-off', 'allotment'
        ]
        
        logger.info(f"Fetching recent corporate actions for last {days} days")
        
        # Get keyword-based announcements
        keyword_results = self.get_announcements_by_keywords(
            keywords=corporate_action_keywords,
            days_back=days,
            exchanges=['bse', 'nse']
        )
        
        # Get NSE corporate actions RSS feed
        nse_corp_actions = self.nse_scraper.get_recent_announcements(
            days=days,
            feed_types=['corporate_actions']
        )
        
        result = {
            'period_days': days,
            'keyword_based_results': keyword_results,
            'nse_corporate_actions_feed': nse_corp_actions,
            'total_actions': keyword_results['combined_count'] + len(nse_corp_actions),
            'fetched_at': datetime.now().isoformat()
        }
        
        return result
    
    def generate_summary_report(self, data):
        """
        Generate a summary report from announcement data
        
        Args:
            data (dict): Announcement data
        
        Returns:
            dict: Summary report
        """
        summary = {
            'report_generated_at': datetime.now().isoformat(),
            'total_announcements': 0,
            'exchange_breakdown': {},
            'top_companies': {},
            'announcement_types': {},
            'recent_highlights': []
        }
        
        # Process different data types
        if 'bse_announcements' in data and 'nse_announcements' in data:
            # Single company data
            summary['total_announcements'] = data.get('combined_count', 0)
            summary['exchange_breakdown'] = {
                'BSE': len(data.get('bse_announcements', [])),
                'NSE': len(data.get('nse_announcements', []))
            }
        
        elif isinstance(data, dict) and any('announcements' in str(v) for v in data.values()):
            # Multiple companies data
            total = 0
            bse_total = 0
            nse_total = 0
            
            for company, company_data in data.items():
                if isinstance(company_data, dict):
                    bse_count = len(company_data.get('bse_announcements', []))
                    nse_count = len(company_data.get('nse_announcements', []))
                    company_total = bse_count + nse_count
                    
                    total += company_total
                    bse_total += bse_count
                    nse_total += nse_count
                    
                    if company_total > 0:
                        summary['top_companies'][company] = company_total
            
            summary['total_announcements'] = total
            summary['exchange_breakdown'] = {
                'BSE': bse_total,
                'NSE': nse_total
            }
        
        return summary
    
    def save_combined_data(self, data, base_filename):
        """
        Save combined announcement data in multiple formats
        
        Args:
            data (dict): Combined announcement data
            base_filename (str): Base filename (without extension)
        """
        try:
            # Save as JSON
            json_filename = f"{base_filename}.json"
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            logger.info(f"Data saved to {json_filename}")
            
            # Generate and save summary
            summary = self.generate_summary_report(data)
            summary_filename = f"{base_filename}_summary.json"
            with open(summary_filename, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False, default=str)
            logger.info(f"Summary saved to {summary_filename}")
            
        except Exception as e:
            logger.error(f"Error saving data: {e}")
    
    def close(self):
        """Close all scrapers"""
        if self.nse_scraper:
            self.nse_scraper.close()
        logger.info("Combined scraper closed")

# Example usage and testing
if __name__ == "__main__":
    # Initialize combined scraper
    combined_scraper = CombinedAnnouncements()
    
    try:
        # Example 1: Get announcements for TCS from both exchanges
        print("=== TCS Announcements from Both Exchanges ===")
        tcs_data = combined_scraper.get_company_announcements(
            bse_code=532540,
            nse_symbol='TCS',
            company_name='TCS',
            days_back=30
        )
        
        print(f"BSE Announcements: {len(tcs_data['bse_announcements'])}")
        print(f"NSE Announcements: {len(tcs_data['nse_announcements'])}")
        print(f"Total: {tcs_data['combined_count']}")
        
        # Example 2: Get announcements for multiple companies
        print("\n=== Multiple Companies Announcements ===")
        companies = [
            {'bse_code': 532540, 'nse_symbol': 'TCS', 'name': 'TCS'},
            {'bse_code': 500180, 'nse_symbol': 'HDFCBANK', 'name': 'HDFC Bank'},
            {'bse_code': 500325, 'nse_symbol': 'RELIANCE', 'name': 'Reliance'}
        ]
        
        multi_data = combined_scraper.get_multiple_companies_announcements(companies, days_back=15)
        
        for company, data in multi_data.items():
            print(f"{company}: {data['combined_count']} total announcements")
        
        # Example 3: Search by keywords
        print("\n=== Dividend/Bonus Announcements ===")
        keyword_data = combined_scraper.get_announcements_by_keywords(
            keywords=['dividend', 'bonus'],
            days_back=30
        )
        
        print(f"BSE Results: {len(keyword_data['bse_announcements'])}")
        print(f"NSE Results: {len(keyword_data['nse_announcements'])}")
        print(f"Total: {keyword_data['combined_count']}")
        
        # Example 4: Get recent corporate actions
        print("\n=== Recent Corporate Actions ===")
        corp_actions = combined_scraper.get_recent_corporate_actions(days=7)
        print(f"Total Corporate Actions: {corp_actions['total_actions']}")
        
        # Save data
        combined_scraper.save_combined_data(tcs_data, 'tcs_combined_announcements')
        combined_scraper.save_combined_data(multi_data, 'multiple_companies_announcements')
        combined_scraper.save_combined_data(keyword_data, 'dividend_bonus_announcements')
        combined_scraper.save_combined_data(corp_actions, 'recent_corporate_actions')
        
        print("\n=== Data saved to files ===")
        
    finally:
        # Close scrapers
        combined_scraper.close() 