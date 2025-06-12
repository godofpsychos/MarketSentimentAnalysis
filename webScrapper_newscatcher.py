from newspaper import Article
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup

STOCK = "WIPRO"
# Example: STOCK = "RELIANCE, TCS, HDFCBANK, ICICIBANK, INFY, ITC, LTIM, LT, HINDUNILVR, AXISBANK, KOTAKBANK, SBIN, BHARTIARTL, HCLTECH, MARUTI, ASIANPAINT, BAJFINANCE, BAJAJFINSV, TITAN, ULTRACEMCO, SUNPHARMA, NESTLEIND, POWERGRID, ADANIENT, ADANIGREEN, ADANIPORTS, ADANIPOWER, APOLLOHOSP, BPCL, BRITANNIA, CIPLA, COALINDIA, DIVISLAB, DRREDDY, EICHERMOT, GRASIM, HDFCLIFE, HEROMOTOCO, HINDALCO, INDUSINDBK, JSWSTEEL, M&M, NTPC, ONGC, SBI, SHREECEM, TATACONSUM, TATAMOTORS, TATASTEEL, TECHM, WIPRO"


def fetch_newspaper3k_news(stock, max_articles=5):
    query = f"{stock} news"
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}&tbm=nws"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = []
    for g in soup.find_all('a'):
        href = g.get('href')
        if href and href.startswith('http') and 'google' not in href:
            links.append(href)
        if len(links) >= max_articles:
            break
    print(f"Top news for {stock}:")
    for link in links:
        try:
            article = Article(link)
            article.download()
            article.parse()
            print(f"- {article.title}")
        except Exception as e:
            print(f"- Error fetching article: {e}")
    print("-"*40)


def main():
    for stock in STOCK.split(','):
        stock = stock.strip()
        fetch_newspaper3k_news(stock)
        # Add delay if needed

if __name__ == "__main__":
    main()