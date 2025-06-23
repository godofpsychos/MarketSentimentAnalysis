"""
BSE Corporate Announcements Scraper
Uses bsescraper library to fetch corporate announcements from BSE India
"""

import bsescraper
import pandas as pd
from datetime import datetime, timedelta
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BSEAnnouncements:
    def __init__(self):
        """Initialize BSE scraper"""
        try:
            self.bs = bsescraper.BSE()
            logger.info("BSE scraper initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize BSE scraper: {e}")
            self.bs = None
    
    def get_company_code(self, company_name):
        """
        Get BSE security code for a company
        
        Args:
            company_name (str): Full company name (e.g., "HDFC Bank Ltd")
        
        Returns:
            int: BSE security code or None if not found
        """
        if not self.bs:
            logger.error("BSE scraper not initialized")
            return None
        
        try:
            code = self.bs.get_code(company_name)
            logger.info(f"Found code {code} for {company_name}")
            return code
        except Exception as e:
            logger.error(f"Error getting code for {company_name}: {e}")
            return None
    
    def get_corporate_announcements(self, company_code, days_back=30, category='All'):
        """
        Get corporate announcements for a company
        
        Args:
            company_code (int): BSE security code
            days_back (int): Number of days to look back (default: 30)
            category (str): Category filter - 'All', 'Board Meeting', 'Company Update', 
                           'Corp. Action', 'AGM/EGM', 'New Listing', 'Results', 'Others'
        
        Returns:
            list: List of announcements with headline, subject, date
        """
        if not self.bs:
            logger.error("BSE scraper not initialized")
            return []
        
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            # Format dates for BSE API (dd/mm/yyyy)
            start_date_str = start_date.strftime('%d/%m/%Y')
            end_date_str = end_date.strftime('%d/%m/%Y')
            
            logger.info(f"Fetching announcements for code {company_code} from {start_date_str} to {end_date_str}")
            
            # Get announcements
            announcements = self.bs.get_corporate_ann(
                code=company_code,
                category=category,
                startdate=start_date_str,
                enddate=end_date_str
            )
            
            logger.info(f"Found {len(announcements)} announcements")
            return announcements
            
        except Exception as e:
            logger.error(f"Error fetching announcements for code {company_code}: {e}")
            return []
    
    def get_announcements_with_keywords(self, company_code, keywords, days_back=30, category='All'):
        """
        Get corporate announcements filtered by keywords
        
        Args:
            company_code (int): BSE security code
            keywords (list): List of keywords to filter by
            days_back (int): Number of days to look back
            category (str): Category filter
        
        Returns:
            list: Filtered announcements
        """
        if not self.bs:
            logger.error("BSE scraper not initialized")
            return []
        
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            start_date_str = start_date.strftime('%d/%m/%Y')
            end_date_str = end_date.strftime('%d/%m/%Y')
            
            logger.info(f"Fetching announcements with keywords {keywords} for code {company_code}")
            
            # Get filtered announcements
            announcements = self.bs.get_corporate_ann_keywords(
                keywords=keywords,
                code=company_code,
                category=category,
                startdate=start_date_str,
                enddate=end_date_str
            )
            
            logger.info(f"Found {len(announcements)} announcements with keywords")
            return announcements
            
        except Exception as e:
            logger.error(f"Error fetching filtered announcements: {e}")
            return []
    
    def get_multiple_companies_announcements(self, company_codes, days_back=30):
        """
        Get announcements for multiple companies
        
        Args:
            company_codes (list): List of BSE security codes
            days_back (int): Number of days to look back
        
        Returns:
            dict: Dictionary with company codes as keys and announcements as values
        """
        all_announcements = {}
        
        for code in company_codes:
            logger.info(f"Fetching announcements for company code: {code}")
            announcements = self.get_corporate_announcements(code, days_back)
            all_announcements[code] = announcements
        
        return all_announcements
    
    def save_announcements_to_json(self, announcements, filename):
        """
        Save announcements to JSON file
        
        Args:
            announcements (list or dict): Announcements data
            filename (str): Output filename
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(announcements, f, indent=2, ensure_ascii=False, default=str)
            logger.info(f"Announcements saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving to {filename}: {e}")
    
    def save_announcements_to_csv(self, announcements, filename):
        """
        Save announcements to CSV file
        
        Args:
            announcements (list): List of announcements
            filename (str): Output filename
        """
        try:
            if announcements:
                df = pd.DataFrame(announcements)
                df.to_csv(filename, index=False, encoding='utf-8')
                logger.info(f"Announcements saved to {filename}")
            else:
                logger.warning("No announcements to save")
        except Exception as e:
            logger.error(f"Error saving to CSV {filename}: {e}")
    
    def close(self):
        """
        Close the BSE scraper session
        """
        try:
            if hasattr(self, 'bs') and self.bs:
                # BSE scraper doesn't need explicit closing, but we'll log it
                logger.info("BSE scraper session closed")
        except Exception as e:
            logger.error(f"Error closing BSE scraper: {e}")

# Example usage and testing
if __name__ == "__main__":
    # Initialize BSE announcements scraper
    bse_scraper = BSEAnnouncements()
    
    # Example company codes (you can add more)
    COMPANY_CODES = {
        'TCS': 532540,
        'HDFC_BANK': 500180,
        'RELIANCE': 500325,
        'INFOSYS': 500209,
        'ICICI_BANK': 532174
    }
    
    # Example 1: Get announcements for TCS
    print("=== TCS Announcements ===")
    tcs_announcements = bse_scraper.get_corporate_announcements(
        company_code=COMPANY_CODES['TCS'],
        days_back=30
    )
    
    for announcement in tcs_announcements[:3]:  # Show first 3
        print(f"Date: {announcement.get('date', 'N/A')}")
        print(f"Headline: {announcement.get('headline', 'N/A')}")
        print(f"Subject: {announcement.get('subject', 'N/A')}")
        print("-" * 50)
    
    # Example 2: Get announcements with keywords
    print("\n=== Dividend/Bonus Announcements ===")
    dividend_announcements = bse_scraper.get_announcements_with_keywords(
        company_code=COMPANY_CODES['HDFC_BANK'],
        keywords=['dividend', 'bonus', 'split'],
        days_back=90,
        category='Corp. Action'
    )
    
    for announcement in dividend_announcements:
        print(f"Date: {announcement.get('date', 'N/A')}")
        print(f"Headline: {announcement.get('headline', 'N/A')}")
        print("-" * 30)
    
    # Example 3: Get announcements for multiple companies
    print("\n=== Multiple Companies Announcements ===")
    multiple_announcements = bse_scraper.get_multiple_companies_announcements(
        company_codes=[COMPANY_CODES['TCS'], COMPANY_CODES['INFOSYS']],
        days_back=15
    )
    
    for code, announcements in multiple_announcements.items():
        print(f"Company Code {code}: {len(announcements)} announcements")
    
    # Save to files
    if tcs_announcements:
        bse_scraper.save_announcements_to_json(tcs_announcements, 'tcs_announcements.json')
        bse_scraper.save_announcements_to_csv(tcs_announcements, 'tcs_announcements.csv') 