from gnews import GNews
import json
google_news = GNews()
STOCK = "RELIANCE, TCS, HDFCBANK, ICICIBANK, INFY, ITC, LTIM, LT, HINDUNILVR, AXISBANK, KOTAKBANK, SBIN, BHARTIARTL, HCLTECH, MARUTI, ASIANPAINT, BAJFINANCE, BAJAJFINSV, TITAN, ULTRACEMCO, SUNPHARMA, NESTLEIND, POWERGRID, ADANIENT, ADANIGREEN, ADANIPORTS, ADANIPOWER, APOLLOHOSP, BPCL, BRITANNIA, CIPLA, COALINDIA, DIVISLAB, DRREDDY, EICHERMOT, GRASIM, HDFCLIFE, HEROMOTOCO, HINDALCO, INDUSINDBK, JSWSTEEL, M&M, NTPC, ONGC, SBI, SHREECEM, TATACONSUM, TATAMOTORS, TATASTEEL, TECHM, WIPRO"
news ={}
for stock in STOCK.split(','):
    stock = stock.strip()
    news_temp = google_news.get_news(stock)
    print(f"Scrapping for stock:{stock}")
    if news_temp:
        news[stock] = news_temp
    else:
        news[stock] = "No news found for this stock"
# news_temp = google_news.get_news('Reliance')


with open('news.json', 'w') as f:
    json.dump(news, f, indent=4, ensure_ascii=False)