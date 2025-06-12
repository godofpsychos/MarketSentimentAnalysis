import time
from datetime import datetime, timedelta
from GoogleNews import GoogleNews

STOCK = "WIPRO"
# STOCK = "RELIANCE, TCS, HDFCBANK, ICICIBANK, INFY, ITC, LTIM, LT, HINDUNILVR, AXISBANK, KOTAKBANK, SBIN, BHARTIARTL, HCLTECH, MARUTI, ASIANPAINT, BAJFINANCE, BAJAJFINSV, TITAN, ULTRACEMCO, SUNPHARMA, NESTLEIND, POWERGRID, ADANIENT, ADANIGREEN, ADANIPORTS, ADANIPOWER, APOLLOHOSP, BPCL, BRITANNIA, CIPLA, COALINDIA, DIVISLAB, DRREDDY, EICHERMOT, GRASIM, HDFCLIFE, HEROMOTOCO, HINDALCO, INDUSINDBK, JSWSTEEL, M&M, NTPC, ONGC, SBI, SHREECEM, TATACONSUM, TATAMOTORS, TATASTEEL, TECHM, WIPRO"
START_HOUR = 8
INTERVAL_MINUTES = 30
END_HOUR = 15

# Calculate the end datetime (3pm next day)
now = datetime.now()
start_time = now.replace(hour=START_HOUR, minute=0, second=0, microsecond=0)
if now > start_time:
    start_time = now
end_time = (start_time + timedelta(days=1)).replace(hour=END_HOUR, minute=0, second=0, microsecond=0)

def scrape_news(stock, from_date=None, to_date=None):
    googlenews = GoogleNews(lang='en', region='India')
    googlenews.set_encode('utf-8')
    googlenews.set_time_range('01/01/2025', datetime.now().strftime('%m/%d/%Y'))  # Default to all time
    googlenews.set_period('d')  # Set to daily news
    # if from_date and to_date:
    #     googlenews.set_time_range(from_date, to_date)
    googlenews.search(stock)
    news = googlenews.result()
    print(f"Top news for {stock} at {datetime.now()}:")
    for n in news:
        print(f"- {n['title']}")
    print("-"*40)

def main():
    for stock in STOCK.split(','):
        stock = stock.strip()
        scrape_news(stock)
        time.sleep(60)  # Add a 60-second delay between requests to avoid HTTP 429
        # while datetime.now() < end_time:
        #     current_time = datetime.now()
        #     if current_time >= start_time and (current_time.hour < END_HOUR or (current_time.hour == END_HOUR and current_time.minute == 0)):
        #     else:
        #         print(f"Waiting for the next interval... Current time: {current_time}")
        #     time.sleep(INTERVAL_MINUTES * 60)
if __name__ == "__main__":
    main()