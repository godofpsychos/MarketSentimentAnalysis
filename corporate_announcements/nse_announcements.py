"""
NSE Corporate Announcements Scraper
Uses RSS feeds and API calls to fetch corporate announcements from NSE India
"""

import feedparser
import requests
import json
import pandas as pd
from datetime import datetime
import logging
import time
from urllib.parse import urljoin

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NSEAnnouncements:
    def __init__(self):
        """Initialize NSE announcements scraper"""
        self.base_url = "https://www.nseindia.com"
        self.session = requests.Session()
        
        # Set headers to mimic browser request
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        self.session.headers.update(self.headers)
        
        # RSS Feed URLs
        self.rss_feeds = {
            'corporate_announcements': 'https://www.nseindia.com/rss/corp_announce.xml',
            'board_meetings': 'https://www.nseindia.com/rss/board_meetings.xml',
            'financial_results': 'https://www.nseindia.com/rss/financial_results.xml',
            'corporate_actions': 'https://www.nseindia.com/rss/corp_actions.xml',
            'new_listings': 'https://www.nseindia.com/rss/new_listings.xml'
        }
        
        logger.info("NSE announcements scraper initialized")
    
    def get_rss_announcements(self, feed_type='corporate_announcements', max_entries=50):
        """
        Get announcements from NSE RSS feeds
        
        Args:
            feed_type (str): Type of feed - 'corporate_announcements', 'board_meetings', 
                           'financial_results', 'corporate_actions', 'new_listings'
            max_entries (int): Maximum number of entries to return
        
        Returns:
            list: List of announcements
        """
        try:
            url = self.rss_feeds.get(feed_type)
            if not url:
                logger.error(f"Unknown feed type: {feed_type}")
                return []
            
            logger.info(f"Fetching RSS feed: {feed_type}")
            
            # First try to fetch the URL with timeout to check if it's accessible
            try:
                response = requests.get(url, timeout=15, headers=self.headers)
                if response.status_code != 200:
                    logger.error(f"RSS feed returned status code {response.status_code} for {feed_type}")
                    return []
                
                # Parse RSS feed from the response content
                feed = feedparser.parse(response.content)
                
            except requests.exceptions.Timeout:
                logger.error(f"Timeout while fetching RSS feed: {feed_type}")
                return []
            except requests.exceptions.RequestException as e:
                logger.error(f"Network error while fetching RSS feed {feed_type}: {e}")
                return []
            
            if feed.bozo:
                logger.warning(f"RSS feed parsing had issues: {feed.bozo_exception}")
                # If it's a minor parsing issue, continue. If major, return empty
                if not hasattr(feed, 'entries') or not feed.entries:
                    logger.error(f"RSS feed {feed_type} has no entries or major parsing errors")
                    return []
            
            announcements = []
            for entry in feed.entries[:max_entries]:
                announcement = {
                    'title': entry.get('title', ''),
                    'link': entry.get('link', ''),
                    'published': entry.get('published', ''),
                    'published_parsed': entry.get('published_parsed', None),
                    'summary': entry.get('summary', ''),
                    'guid': entry.get('guid', ''),
                    'feed_type': feed_type,
                    'fetched_at': datetime.now().isoformat()
                }
                
                # Parse published date if available
                if announcement['published_parsed']:
                    try:
                        pub_date = datetime(*announcement['published_parsed'][:6])
                        announcement['published_date'] = pub_date.isoformat()
                    except:
                        announcement['published_date'] = announcement['published']
                else:
                    announcement['published_date'] = announcement['published']
                
                announcements.append(announcement)
            
            logger.info(f"Found {len(announcements)} announcements in {feed_type}")
            return announcements
            
        except Exception as e:
            logger.error(f"Error fetching RSS feed {feed_type}: {e}")
            return []
    
    def get_all_rss_announcements(self, max_entries_per_feed=20):
        """
        Get announcements from all RSS feeds
        
        Args:
            max_entries_per_feed (int): Maximum entries per feed
        
        Returns:
            dict: Dictionary with feed types as keys and announcements as values
        """
        all_announcements = {}
        
        for feed_type in self.rss_feeds.keys():
            logger.info(f"Fetching {feed_type}...")
            announcements = self.get_rss_announcements(feed_type, max_entries_per_feed)
            all_announcements[feed_type] = announcements
            
            # Add small delay to be respectful to the server
            time.sleep(1)
        
        return all_announcements
    
    def get_nse_api_announcements(self):
        """
        Get announcements from NSE API (if available)
        Note: NSE API might require session cookies or may block automated requests
        
        Returns:
            dict: API response data or None
        """
        try:
            # First, get the main page to establish session
            main_page_url = "https://www.nseindia.com"
            response = self.session.get(main_page_url, timeout=10)
            
            if response.status_code != 200:
                logger.warning(f"Failed to access main page: {response.status_code}")
            
            # Try to get corporate announcements API
            api_url = "https://www.nseindia.com/api/corporates-announcements"
            
            response = self.session.get(api_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                logger.info("Successfully fetched NSE API announcements")
                return data
            else:
                logger.warning(f"NSE API request failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching NSE API announcements: {e}")
            return None
    
    def filter_announcements_by_company(self, announcements, company_name):
        """
        Filter announcements by company name
        
        Args:
            announcements (list): List of announcements
            company_name (str): Company name to filter by
        
        Returns:
            list: Filtered announcements
        """
        filtered = []
        company_name_lower = company_name.lower()
        
        for announcement in announcements:
            title = announcement.get('title', '').lower()
            summary = announcement.get('summary', '').lower()
            
            if company_name_lower in title or company_name_lower in summary:
                filtered.append(announcement)
        
        logger.info(f"Filtered {len(filtered)} announcements for company: {company_name}")
        return filtered
    
    def filter_announcements_by_keywords(self, announcements, keywords):
        """
        Filter announcements by keywords
        
        Args:
            announcements (list): List of announcements
            keywords (list): List of keywords to search for
        
        Returns:
            list: Filtered announcements
        """
        filtered = []
        keywords_lower = [kw.lower() for kw in keywords]
        
        for announcement in announcements:
            title = announcement.get('title', '').lower()
            summary = announcement.get('summary', '').lower()
            
            # Check if any keyword is found in title or summary
            if any(keyword in title or keyword in summary for keyword in keywords_lower):
                filtered.append(announcement)
        
        logger.info(f"Filtered {len(filtered)} announcements with keywords: {keywords}")
        return filtered
    
    def get_recent_announcements(self, days=7, feed_types=None):
        """
        Get recent announcements within specified days
        
        Args:
            days (int): Number of days to look back
            feed_types (list): List of feed types to check (None for all)
        
        Returns:
            list: Recent announcements
        """
        if feed_types is None:
            feed_types = list(self.rss_feeds.keys())
        
        cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
        recent_announcements = []
        
        for feed_type in feed_types:
            announcements = self.get_rss_announcements(feed_type)
            
            for announcement in announcements:
                pub_parsed = announcement.get('published_parsed')
                if pub_parsed:
                    pub_timestamp = time.mktime(pub_parsed)
                    if pub_timestamp >= cutoff_date:
                        recent_announcements.append(announcement)
        
        # Sort by published date (newest first)
        recent_announcements.sort(
            key=lambda x: x.get('published_parsed', (0,)),
            reverse=True
        )
        
        logger.info(f"Found {len(recent_announcements)} recent announcements in last {days} days")
        return recent_announcements
    
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
        """Close the session"""
        self.session.close()
        logger.info("NSE session closed")

# Example usage and testing
if __name__ == "__main__":
    # Initialize NSE announcements scraper
    nse_scraper = NSEAnnouncements()
    
    try:
        # Example 1: Get corporate announcements
        print("=== NSE Corporate Announcements ===")
        corp_announcements = nse_scraper.get_rss_announcements('corporate_announcements', max_entries=5)
        
        for announcement in corp_announcements:
            print(f"Title: {announcement['title']}")
            print(f"Published: {announcement['published']}")
            print(f"Link: {announcement['link']}")
            print("-" * 50)
        
        # Example 2: Get all RSS feeds
        print("\n=== All RSS Feeds Summary ===")
        all_announcements = nse_scraper.get_all_rss_announcements(max_entries_per_feed=3)
        
        for feed_type, announcements in all_announcements.items():
            print(f"{feed_type}: {len(announcements)} announcements")
        
        # Example 3: Filter by company
        print("\n=== Filtered by Company (TCS) ===")
        tcs_announcements = nse_scraper.filter_announcements_by_company(
            corp_announcements, 
            "TCS"
        )
        
        for announcement in tcs_announcements:
            print(f"Title: {announcement['title']}")
            print("-" * 30)
        
        # Example 4: Filter by keywords
        print("\n=== Filtered by Keywords (dividend, bonus) ===")
        keyword_announcements = nse_scraper.filter_announcements_by_keywords(
            corp_announcements,
            ["dividend", "bonus", "split"]
        )
        
        for announcement in keyword_announcements:
            print(f"Title: {announcement['title']}")
            print("-" * 30)
        
        # Example 5: Get recent announcements
        print("\n=== Recent Announcements (Last 3 Days) ===")
        recent_announcements = nse_scraper.get_recent_announcements(
            days=3,
            feed_types=['corporate_announcements', 'corporate_actions']
        )
        
        print(f"Found {len(recent_announcements)} recent announcements")
        for announcement in recent_announcements[:3]:
            print(f"Title: {announcement['title']}")
            print(f"Feed: {announcement['feed_type']}")
            print(f"Published: {announcement['published']}")
            print("-" * 30)
        
        # Save to files
        if corp_announcements:
            nse_scraper.save_announcements_to_json(corp_announcements, 'nse_corporate_announcements.json')
            nse_scraper.save_announcements_to_csv(corp_announcements, 'nse_corporate_announcements.csv')
        
        if all_announcements:
            nse_scraper.save_announcements_to_json(all_announcements, 'nse_all_announcements.json')
    
    finally:
        # Close the session
        nse_scraper.close() 