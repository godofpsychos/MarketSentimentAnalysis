#!/usr/bin/env python3
"""
Stock Corporate Actions Scraper from CSV
Reads stock symbols from stocksList.csv and scrapes corporate actions for the last 7 days
"""

import sys
import os
import csv
import json
from datetime import datetime, timedelta
import logging

# Add the current directory to Python path
sys.path.append(os.path.dirname(__file__))

# Import our existing scrapers
from combined_announcements import CombinedAnnouncements

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('stock_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class StockCSVScraper:
    def __init__(self, csv_file_path='../stocksList.csv'):
        """
        Initialize the stock scraper
        
        Args:
            csv_file_path (str): Path to the CSV file containing stock symbols
        """
        self.csv_file_path = csv_file_path
        self.combined_scraper = CombinedAnnouncements()
        self.stocks = []
        
        # NSE to BSE mapping for major stocks (this helps us get data from both exchanges)
        self.nse_to_bse_mapping = {
            'RELIANCE': 500325,
            'TCS': 532540,
            'HDFCBANK': 500180,
            'ICICIBANK': 532174,
            'INFY': 500209,
            'ITC': 500875,
            'LTIM': 541540,
            'LT': 500510,
            'HINDUNILVR': 500696,
            'AXISBANK': 532215,
            'KOTAKBANK': 500247,
            'SBIN': 500112,
            'BHARTIARTL': 532454,
            'HCLTECH': 532281,
            'MARUTI': 532500,
            'ASIANPAINT': 500820,
            'BAJFINANCE': 500034,
            'BAJAJFINSV': 532978,
            'TITAN': 500114,
            'ULTRACEMCO': 532538,
            'SUNPHARMA': 524715,
            'NESTLEIND': 500790,
            'POWERGRID': 532898,
            'ADANIENT': 512599,
            'ADANIGREEN': 541450,
            'ADANIPORTS': 532921,
            'ADANIPOWER': 533096,
            'APOLLOHOSP': 526777,
            'BPCL': 500547,
            'BRITANNIA': 500825,
            'CIPLA': 500087,
            'COALINDIA': 533278,
            'DIVISLAB': 532488,
            'DRREDDY': 500124,
            'EICHERMOT': 505200,
            'GRASIM': 500300,
            'HDFCLIFE': 540777,
            'HEROMOTOCO': 500182,
            'HINDALCO': 500440,
            'INDUSINDBK': 532187,
            'JSWSTEEL': 500228,
            'M&M': 500520,
            'NTPC': 532555,
            'ONGC': 500312,
            'SBI': 500112,
            'SHREECEM': 500387,
            'TATACONSUM': 500800,
            'TATAMOTORS': 500570,
            'TATASTEEL': 500470,
            'TECHM': 532755,
            'WIPRO': 507685
        }
        
        logger.info(f"Stock CSV Scraper initialized with file: {csv_file_path}")
    
    def load_stocks_from_csv(self):
        """
        Load stock symbols from CSV file
        
        Returns:
            list: List of stock symbols
        """
        try:
            stocks = []
            with open(self.csv_file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    symbol = row['SYMBOL'].strip()
                    if symbol:  # Only add non-empty symbols
                        stocks.append(symbol)
            
            self.stocks = stocks
            logger.info(f"Successfully loaded {len(stocks)} stock symbols from CSV")
            return stocks
            
        except FileNotFoundError:
            logger.error(f"CSV file not found: {self.csv_file_path}")
            return []
        except Exception as e:
            logger.error(f"Error reading CSV file: {e}")
            return []
    
    def prepare_company_list(self):
        """
        Prepare company list with both NSE symbols and BSE codes where available
        
        Returns:
            list: List of company dictionaries
        """
        companies = []
        
        for stock_symbol in self.stocks:
            company_info = {
                'nse_symbol': stock_symbol,
                'name': stock_symbol
            }
            
            # Add BSE code if we have mapping
            if stock_symbol in self.nse_to_bse_mapping:
                company_info['bse_code'] = self.nse_to_bse_mapping[stock_symbol]
            
            companies.append(company_info)
        
        logger.info(f"Prepared {len(companies)} companies for scraping")
        return companies
    
    def scrape_corporate_actions_for_all_stocks(self, days_back=7):
        """
        Scrape corporate actions for all stocks from CSV for the specified time period
        
        Args:
            days_back (int): Number of days to look back (default: 7)
        
        Returns:
            dict: Corporate actions data for all stocks
        """
        logger.info(f"Starting corporate actions scraping for {len(self.stocks)} stocks for last {days_back} days")
        
        # Prepare companies list
        companies = self.prepare_company_list()
        
        # Get announcements for all companies
        all_announcements = self.combined_scraper.get_multiple_companies_announcements(
            companies=companies,
            days_back=days_back
        )
        
        # Also get general recent corporate actions
        recent_actions = self.combined_scraper.get_recent_corporate_actions(days=days_back)
        
        # Combine results
        result = {
            'scraping_info': {
                'total_stocks': len(self.stocks),
                'days_back': days_back,
                'scraped_at': datetime.now().isoformat(),
                'csv_file': self.csv_file_path
            },
            'stock_symbols': self.stocks,
            'individual_stock_announcements': all_announcements,
            'general_corporate_actions': recent_actions,
            'summary': self._generate_summary(all_announcements, recent_actions)
        }
        
        logger.info(f"Scraping completed. Found announcements for {len(all_announcements)} stocks")
        return result
    
    def _generate_summary(self, stock_announcements, general_actions):
        """
        Generate a summary of the scraped data
        
        Args:
            stock_announcements (dict): Individual stock announcements
            general_actions (dict): General corporate actions
        
        Returns:
            dict: Summary information
        """
        total_announcements = 0
        stocks_with_announcements = 0
        bse_total = 0
        nse_total = 0
        
        for stock, data in stock_announcements.items():
            if isinstance(data, dict):
                bse_count = len(data.get('bse_announcements', []))
                nse_count = len(data.get('nse_announcements', []))
                stock_total = bse_count + nse_count
                
                if stock_total > 0:
                    stocks_with_announcements += 1
                
                total_announcements += stock_total
                bse_total += bse_count
                nse_total += nse_count
        
        return {
            'total_stocks_scraped': len(stock_announcements),
            'stocks_with_announcements': stocks_with_announcements,
            'total_announcements': total_announcements,
            'bse_announcements': bse_total,
            'nse_announcements': nse_total,
            'general_corporate_actions': general_actions.get('total_actions', 0)
        }
    
    def save_results(self, data, filename_prefix='stock_corporate_actions'):
        """
        Save scraping results to files
        
        Args:
            data (dict): Scraping results
            filename_prefix (str): Prefix for output files
        """
        try:
            # Create timestamp for unique filenames
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Save detailed results as JSON
            detailed_filename = f"{filename_prefix}_{timestamp}.json"
            with open(detailed_filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            logger.info(f"Detailed results saved to: {detailed_filename}")
            
            # Save summary as separate file
            summary_filename = f"{filename_prefix}_summary_{timestamp}.json"
            summary_data = {
                'summary': data['summary'],
                'scraping_info': data['scraping_info'],
                'stock_symbols': data['stock_symbols']
            }
            with open(summary_filename, 'w', encoding='utf-8') as f:
                json.dump(summary_data, f, indent=2, ensure_ascii=False, default=str)
            logger.info(f"Summary saved to: {summary_filename}")
            
            return detailed_filename, summary_filename
            
        except Exception as e:
            logger.error(f"Error saving results: {e}")
            return None, None
    
    def run_scraping(self, days_back=7, save_results=True):
        """
        Run the complete scraping process
        
        Args:
            days_back (int): Number of days to look back
            save_results (bool): Whether to save results to files
        
        Returns:
            dict: Complete scraping results
        """
        logger.info("=" * 60)
        logger.info("STARTING STOCK CORPORATE ACTIONS SCRAPING")
        logger.info("=" * 60)
        
        try:
            # Load stocks from CSV
            stocks = self.load_stocks_from_csv()
            if not stocks:
                logger.error("No stocks loaded from CSV. Exiting.")
                return None
            
            # Scrape corporate actions
            results = self.scrape_corporate_actions_for_all_stocks(days_back=days_back)
            
            # Save results if requested
            if save_results:
                detailed_file, summary_file = self.save_results(results)
                results['output_files'] = {
                    'detailed': detailed_file,
                    'summary': summary_file
                }
            
            # Print summary
            logger.info("=" * 60)
            logger.info("SCRAPING COMPLETED - SUMMARY")
            logger.info("=" * 60)
            summary = results['summary']
            logger.info(f"Total stocks scraped: {summary['total_stocks_scraped']}")
            logger.info(f"Stocks with announcements: {summary['stocks_with_announcements']}")
            logger.info(f"Total announcements found: {summary['total_announcements']}")
            logger.info(f"  - BSE announcements: {summary['bse_announcements']}")
            logger.info(f"  - NSE announcements: {summary['nse_announcements']}")
            logger.info(f"General corporate actions: {summary['general_corporate_actions']}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error during scraping process: {e}")
            return None
        
        finally:
            # Clean up
            self.combined_scraper.close()
    
    def close(self):
        """Close the scraper"""
        if self.combined_scraper:
            self.combined_scraper.close()
        logger.info("Stock CSV Scraper closed")

# Main execution
if __name__ == "__main__":
    # Initialize scraper
    scraper = StockCSVScraper()
    
    try:
        # Run scraping for last 7 days
        results = scraper.run_scraping(days_back=7, save_results=True)
        
        if results:
            print("\n" + "="*60)
            print("SCRAPING SUCCESSFUL!")
            print("="*60)
            print(f"Check the output files:")
            if 'output_files' in results:
                print(f"  - Detailed results: {results['output_files']['detailed']}")
                print(f"  - Summary: {results['output_files']['summary']}")
            print("Check the log file: stock_scraper.log")
        else:
            print("\n" + "="*60)
            print("SCRAPING FAILED!")
            print("="*60)
            print("Check the log file: stock_scraper.log for details")
    
    finally:
        # Clean up
        scraper.close() 