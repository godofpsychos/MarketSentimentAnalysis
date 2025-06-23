#!/usr/bin/env python3
"""
Corporate Actions Scraper Runner
Simple script to run corporate actions scraping for all stocks in stocksList.csv
"""

import sys
import os
from datetime import datetime

# Add corporate_announcements directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'corporate_announcements'))

from corporate_announcements.scrape_stocks_from_csv import StockCSVScraper

def main():
    """Run the corporate actions scraper"""
    print("🚀 Corporate Actions Scraper for Market Sentiment Analysis")
    print("=" * 60)
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📊 Reading stocks from: stocksList.csv")
    print("🔍 Scraping period: Last 7 days")
    print("=" * 60)
    
    # Initialize and run scraper
    scraper = StockCSVScraper(csv_file_path='stocksList.csv')
    
    try:
        results = scraper.run_scraping(days_back=365, save_results=True)
        
        if results:
            print("\n🎉 SCRAPING COMPLETED SUCCESSFULLY!")
            print("📁 Output files created in corporate_announcements/ directory:")
            if 'output_files' in results:
                print(f"   📄 Detailed: {results['output_files']['detailed']}")
                print(f"   📋 Summary: {results['output_files']['summary']}")
            
            # Show summary
            summary = results['summary']
            print(f"\n📈 RESULTS SUMMARY:")
            print(f"   📊 Total stocks processed: {summary['total_stocks_scraped']}")
            print(f"   🏢 Stocks with announcements: {summary['stocks_with_announcements']}")
            print(f"   📢 Total announcements: {summary['total_announcements']}")
            print(f"   🏦 BSE announcements: {summary['bse_announcements']}")
            print(f"   🏛️  NSE announcements: {summary['nse_announcements']}")
            
        else:
            print("\n❌ SCRAPING FAILED!")
            print("Check the log files for more details.")
            
    except Exception as e:
        print(f"\n💥 ERROR: {e}")
        print("Check the log files for more details.")
    
    finally:
        scraper.close()
        print(f"\n🏁 Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main() 