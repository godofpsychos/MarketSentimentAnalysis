from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import os
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

DB_PATH = "/home/tarun/MarketSentimentAnalysis/Sentiment_Analysis/sentiment_analysis.db"

# Complete Mapping of all 50 Nifty 50 stocks to Yahoo Finance tickers
STOCK_TICKER_MAP = {
    # Top 10 by market cap
    'RELIANCE': 'RELIANCE.NS',
    'TCS': 'TCS.NS',
    'HDFCBANK': 'HDFCBANK.NS',
    'BHARTIARTL': 'BHARTIARTL.NS',
    'ICICIBANK': 'ICICIBANK.NS',
    'INFY': 'INFY.NS',
    'HINDUNILVR': 'HINDUNILVR.NS',
    'ITC': 'ITC.NS',
    'SBIN': 'SBIN.NS',
    'LT': 'LT.NS',
    
    # Banking & Financial Services
    'KOTAKBANK': 'KOTAKBANK.NS',
    'AXISBANK': 'AXISBANK.NS',
    'BAJFINANCE': 'BAJFINANCE.NS',
    'BAJAJFINSV': 'BAJAJFINSV.NS',
    'HDFCLIFE': 'HDFCLIFE.NS',
    'SBILIFE': 'SBILIFE.NS',
    'INDUSINDBK': 'INDUSINDBK.NS',
    'SHRIRAMFIN': 'SHRIRAMFIN.NS',
    'JIOFINANCE': 'JIOFINANCE.NS',
    
    # IT & Technology
    'HCLTECH': 'HCLTECH.NS',
    'WIPRO': 'WIPRO.NS',
    'TECHM': 'TECHM.NS',
    
    # Automobiles
    'MARUTI': 'MARUTI.NS',
    'TATAMOTORS': 'TATAMOTORS.NS',
    'M&M': 'M&M.NS',
    'BAJAJ-AUTO': 'BAJAJ-AUTO.NS',
    'EICHERMOT': 'EICHERMOT.NS',
    'HEROMOTOCO': 'HEROMOTOCO.NS',
    
    # Oil, Gas & Energy
    'ONGC': 'ONGC.NS',
    'NTPC': 'NTPC.NS',
    'POWERGRID': 'POWERGRID.NS',
    'COALINDIA': 'COALINDIA.NS',
    'IOC': 'IOC.NS',
    'BPCL': 'BPCL.NS',
    
    # Pharmaceuticals & Healthcare
    'SUNPHARMA': 'SUNPHARMA.NS',
    'DRREDDY': 'DRREDDY.NS',
    'CIPLA': 'CIPLA.NS',
    'APOLLOHOSP': 'APOLLOHOSP.NS',
    'DIVISLAB': 'DIVISLAB.NS',
    
    # Consumer Goods & FMCG
    'NESTLEIND': 'NESTLEIND.NS',
    'ASIANPAINT': 'ASIANPAINT.NS',
    'TATACONSUMR': 'TATACONSUMR.NS',
    'BRITANNIA': 'BRITANNIA.NS',
    
    # Metals & Mining
    'JSWSTEEL': 'JSWSTEEL.NS',
    'TATASTEEL': 'TATASTEEL.NS',
    'HINDALCO': 'HINDALCO.NS',
    
    # Retail & Consumer Services
    'TITAN': 'TITAN.NS',
    'TRENT': 'TRENT.NS',
    
    # Cement & Construction
    'ULTRACEMCO': 'ULTRACEMCO.NS',
    'GRASIM': 'GRASIM.NS',
    
    # Defence
    'BEL': 'BEL.NS',
    
    # Miscellaneous
    'ADANIENT': 'ADANIENT.NS',
    'ADANIPORTS': 'ADANIPORTS.NS',
    'ADANIGREEN': 'ADANIGREEN.NS',
    'ADANIPOWER': 'ADANIPOWER.NS'
}

@app.route('/api/stocks', methods=['GET'])
def get_stocks():
    """Get list of all stocks in the database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT stock FROM sentimentResult")
        stocks = [row[0] for row in cursor.fetchall()]
        conn.close()
        return jsonify({"stocks": stocks})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/sentiment', methods=['GET'])
def get_sentiment():
    """Get latest sentiment for all stocks or a specific stock"""
    stock = request.args.get('stock', None)
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        if stock:
            # Get latest sentiment for a specific stock
            query = """
            SELECT datetime, stock, marketSentiment 
            FROM sentimentResult 
            WHERE stock = ? 
            ORDER BY datetime DESC 
            LIMIT 1
            """
            cursor.execute(query, (stock,))
        else:
            # Get latest sentiment for each stock
            query = """
            WITH ranked AS (
                SELECT 
                    datetime, 
                    stock, 
                    marketSentiment,
                    ROW_NUMBER() OVER (PARTITION BY stock ORDER BY datetime DESC) as rn
                FROM sentimentResult
            )
            SELECT datetime, stock, marketSentiment 
            FROM ranked 
            WHERE rn = 1
            """
            cursor.execute(query)
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "datetime": row[0],
                "stock": row[1],
                "sentiment": row[2]
            })
        
        conn.close()
        return jsonify({"data": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stock-data/<stock_symbol>', methods=['GET'])
def get_stock_data(stock_symbol):
    """Get historical stock data from Yahoo Finance"""
    try:
        # Get period from query parameters (default to 1 month)
        period = request.args.get('period', '1mo')  # 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
        
        # Map our stock symbol to Yahoo Finance ticker
        ticker_symbol = STOCK_TICKER_MAP.get(stock_symbol.upper())
        if not ticker_symbol:
            # If not in our predefined map, try the standard NSE format
            ticker_symbol = f"{stock_symbol.upper()}.NS"
        
        # Fetch data from Yahoo Finance
        stock = yf.Ticker(ticker_symbol)
        hist = stock.history(period=period)
        
        if hist.empty:
            return jsonify({"error": f"No data found for {stock_symbol}. Please check if the symbol is correct or the stock is listed on NSE."}), 404
        
        # Convert to list of dictionaries for JSON response
        data = []
        for date, row in hist.iterrows():
            data.append({
                "date": date.strftime('%Y-%m-%d'),
                "open": round(float(row['Open']), 2),
                "high": round(float(row['High']), 2),
                "low": round(float(row['Low']), 2),
                "close": round(float(row['Close']), 2),
                "volume": int(row['Volume']) if pd.notna(row['Volume']) else 0
            })
        
        # Get current stock info
        info = stock.info
        current_price = info.get('currentPrice', hist['Close'].iloc[-1])
        
        return jsonify({
            "symbol": stock_symbol,
            "ticker": ticker_symbol,
            "current_price": round(float(current_price), 2),
            "currency": info.get('currency', 'INR'),
            "data": data
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stock-info/<stock_symbol>', methods=['GET'])
def get_stock_info(stock_symbol):
    """Get basic stock information from Yahoo Finance"""
    try:
        # Map our stock symbol to Yahoo Finance ticker
        ticker_symbol = STOCK_TICKER_MAP.get(stock_symbol.upper())
        if not ticker_symbol:
            # If not in our predefined map, try the standard NSE format
            ticker_symbol = f"{stock_symbol.upper()}.NS"
        
        # Fetch basic info from Yahoo Finance
        stock = yf.Ticker(ticker_symbol)
        info = stock.info
        
        # Check if we got valid data
        if not info or 'symbol' not in info:
            return jsonify({"error": f"No information found for {stock_symbol}. Please check if the symbol is correct or the stock is listed on NSE."}), 404
        
        return jsonify({
            "symbol": stock_symbol,
            "ticker": ticker_symbol,
            "name": info.get('longName', stock_symbol),
            "current_price": info.get('currentPrice', 0),
            "currency": info.get('currency', 'INR'),
            "market_cap": info.get('marketCap', 0),
            "day_high": info.get('dayHigh', 0),
            "day_low": info.get('dayLow', 0),
            "previous_close": info.get('previousClose', 0),
            "fifty_two_week_high": info.get('fiftyTwoWeekHigh', 0),
            "fifty_two_week_low": info.get('fiftyTwoWeekLow', 0)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/nse-stocks', methods=['GET'])
def get_nse_stocks():
    """Get a comprehensive list of popular NSE stocks"""
    try:
        # Extended list of popular NSE stocks beyond Nifty 50
        popular_nse_stocks = {
            # Nifty 50 stocks (already in STOCK_TICKER_MAP)
            **STOCK_TICKER_MAP,
            
            # Additional popular large-cap stocks
            'AMBUJACEM': 'AMBUJACEM.NS',
            'ACC': 'ACC.NS',
            'BANKBARODA': 'BANKBARODA.NS',
            'CANBK': 'CANBK.NS',
            'PNB': 'PNB.NS',
            'UNIONBANK': 'UNIONBANK.NS',
            'GODREJCP': 'GODREJCP.NS',
            'DABUR': 'DABUR.NS',
            'MARICO': 'MARICO.NS',
            'COLPAL': 'COLPAL.NS',
            'PIDILITIND': 'PIDILITIND.NS',
            'BERGEPAINT': 'BERGEPAINT.NS',
            'KANSAINER': 'KANSAINER.NS',
            'VOLTAS': 'VOLTAS.NS',
            'BLUEDART': 'BLUEDART.NS',
            'CONCOR': 'CONCOR.NS',
            'IRCTC': 'IRCTC.NS',
            'ZOMATO': 'ZOMATO.NS',
            'PAYTM': 'PAYTM.NS',
            'NYKAA': 'NYKAA.NS',
            'POLICYBZR': 'POLICYBZR.NS',
            'DMART': 'DMART.NS',
            'RELAXO': 'RELAXO.NS',
            'BATAINDIA': 'BATAINDIA.NS',
            'PAGEIND': 'PAGEIND.NS',
            'VEDL': 'VEDL.NS',
            'SAIL': 'SAIL.NS',
            'NMDC': 'NMDC.NS',
            'MOIL': 'MOIL.NS',
            'RVNL': 'RVNL.NS',
            'IRFC': 'IRFC.NS',
            'RAILTEL': 'RAILTEL.NS',
            'HAL': 'HAL.NS',
            'MAZAGON': 'MAZAGON.NS',
            'COCHINSHIP': 'COCHINSHIP.NS',
            'SJVN': 'SJVN.NS',
            'NHPC': 'NHPC.NS',
            'RECLTD': 'RECLTD.NS',
            'PFC': 'PFC.NS',
            'IREDA': 'IREDA.NS',
            'SUZLON': 'SUZLON.NS',
            'RPOWER': 'RPOWER.NS',
            'TATAPOWER': 'TATAPOWER.NS',
            'TORNTPOWER': 'TORNTPOWER.NS',
            'CESC': 'CESC.NS',
            'MOTHERSON': 'MOTHERSON.NS',
            'BALKRISIND': 'BALKRISIND.NS',
            'APOLLOTYRE': 'APOLLOTYRE.NS',
            'MRF': 'MRF.NS',
            'CEAT': 'CEAT.NS',
            'ASHOKLEY': 'ASHOKLEY.NS',
            'ESCORTS': 'ESCORTS.NS',
            'TVSMOTORS': 'TVSMOTORS.NS',
            'BAJAJHLDNG': 'BAJAJHLDNG.NS',
            'TVSMOTOR': 'TVSMOTOR.NS',
            'FORCEMOT': 'FORCEMOT.NS',
            'MINDTREE': 'MINDTREE.NS',
            'LTI': 'LTI.NS',
            'COFORGE': 'COFORGE.NS',
            'PERSISTENT': 'PERSISTENT.NS',
            'LTTS': 'LTTS.NS',
            'MPHASIS': 'MPHASIS.NS',
            'OFSS': 'OFSS.NS',
            'KPITTECH': 'KPITTECH.NS',
            'TATAELXSI': 'TATAELXSI.NS',
            'CYIENT': 'CYIENT.NS',
            'RBLBANK': 'RBLBANK.NS',
            'FEDERALBNK': 'FEDERALBNK.NS',
            'SOUTHBANK': 'SOUTHBANK.NS',
            'IDFCFIRSTB': 'IDFCFIRSTB.NS',
            'BANDHANBNK': 'BANDHANBNK.NS',
            'AUBANK': 'AUBANK.NS',
            'CHOLAFIN': 'CHOLAFIN.NS',
            'MUTHOOTFIN': 'MUTHOOTFIN.NS',
            'M&MFIN': 'M&MFIN.NS',
            'PEL': 'PEL.NS',
            'WHIRLPOOL': 'WHIRLPOOL.NS',
            'CROMPTON': 'CROMPTON.NS',
            'HAVELLS': 'HAVELLS.NS',
            'ORIENTELEC': 'ORIENTELEC.NS',
            'DIXON': 'DIXON.NS',
            'AMBER': 'AMBER.NS',
            'AUROPHARMA': 'AUROPHARMA.NS',
            'LUPIN': 'LUPIN.NS',
            'BIOCON': 'BIOCON.NS',
            'CADILAHC': 'CADILAHC.NS',
            'GLENMARK': 'GLENMARK.NS',
            'TORNTPHARM': 'TORNTPHARM.NS',
            'ALKEM': 'ALKEM.NS',
            'LALPATHLAB': 'LALPATHLAB.NS',
            'METROPOLIS': 'METROPOLIS.NS',
            'FORTIS': 'FORTIS.NS',
            'MAXHEALTH': 'MAXHEALTH.NS',
            'AARTIIND': 'AARTIIND.NS',
            'DEEPAKNTR': 'DEEPAKNTR.NS',
            'GNFC': 'GNFC.NS',
            'TATACHEM': 'TATACHEM.NS',
            'UPL': 'UPL.NS',
            'PIIND': 'PIIND.NS',
            'CHAMBLFERT': 'CHAMBLFERT.NS',
            'COROMANDEL': 'COROMANDEL.NS',
            'RALLIS': 'RALLIS.NS',
            'JUBLFOOD': 'JUBLFOOD.NS',
            'VARUN': 'VARUN.NS',
            'RADICO': 'RADICO.NS',
            'UBL': 'UBL.NS',
            'MCDOWELL-N': 'MCDOWELL-N.NS',
            'CCL': 'CCL.NS',
            'VBL': 'VBL.NS',
            'TATACONSUM': 'TATACONSUM.NS',
            'GODREJIND': 'GODREJIND.NS',
            'EMAMILTD': 'EMAMILTD.NS',
            'JYOTHYLAB': 'JYOTHYLAB.NS',
            'GILLETTE': 'GILLETTE.NS',
            'HONAUT': 'HONAUT.NS',
            'THERMAX': 'THERMAX.NS',
            'CUMMINSIND': 'CUMMINSIND.NS',
            'SIEMENS': 'SIEMENS.NS',
            'ABB': 'ABB.NS',
            'SCHNEIDER': 'SCHNEIDER.NS',
            'CROMPTON': 'CROMPTON.NS',
            'BAJAJCON': 'BAJAJCON.NS',
            'STARCEMENT': 'STARCEMENT.NS',
            'HEIDELBERG': 'HEIDELBERG.NS',
            'JKCEMENT': 'JKCEMENT.NS',
            'RAMCOCEM': 'RAMCOCEM.NS',
            'DALMIACEM': 'DALMIACEM.NS',
            'INDIACEM': 'INDIACEM.NS',
            'SHREECEM': 'SHREECEM.NS',
            'JSWINFRA': 'JSWINFRA.NS',
            'GMRINFRA': 'GMRINFRA.NS',
            'IRB': 'IRB.NS',
            'SADBHAV': 'SADBHAV.NS',
            'WELCORP': 'WELCORP.NS',
            'WELSPUNIND': 'WELSPUNIND.NS',
            'RAYMOND': 'RAYMOND.NS',
            'ARVIND': 'ARVIND.NS',
            'VARDHMAN': 'VARDHMAN.NS',
            'TRIDENT': 'TRIDENT.NS',
            'ALOKTEXT': 'ALOKTEXT.NS',
            'SRTRANSFIN': 'SRTRANSFIN.NS',
            'LICHSGFIN': 'LICHSGFIN.NS',
            'CANFINHOME': 'CANFINHOME.NS',
            'GRINFRA': 'GRINFRA.NS',
            'HUDCO': 'HUDCO.NS',
            'SUNTV': 'SUNTV.NS',
            'ZEEL': 'ZEEL.NS',
            'PVRINOX': 'PVRINOX.NS',
            'INOXLEISUR': 'INOXLEISUR.NS',
            'EIDPARRY': 'EIDPARRY.NS',
            'BALRAMCHIN': 'BALRAMCHIN.NS',
            'DHANUKA': 'DHANUKA.NS',
            'MONSANTO': 'MONSANTO.NS',
            'SHRIRAMCIT': 'SHRIRAMCIT.NS'
        }
        
        # Convert to list format with additional info
        stocks_list = []
        for symbol, ticker in popular_nse_stocks.items():
            stocks_list.append({
                "symbol": symbol,
                "ticker": ticker,
                "exchange": "NSE"
            })
        
        return jsonify({
            "total_stocks": len(stocks_list),
            "exchange": "National Stock Exchange (NSE)",
            "note": "This list includes Nifty 50 and other popular NSE stocks. You can also try any NSE stock symbol - the system will automatically add .NS suffix.",
            "stocks": sorted(stocks_list, key=lambda x: x['symbol'])
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/search-stock/<search_term>', methods=['GET'])
def search_stock(search_term):
    """Search for stocks by symbol or name"""
    try:
        # For now, this is a simple search in our predefined list
        # In a production system, you'd integrate with a proper stock database
        
        search_term = search_term.upper()
        matching_stocks = []
        
        # Get all stocks from our extended list
        response = get_nse_stocks()
        all_stocks = response.get_json()['stocks']
        
        # Search by symbol
        for stock in all_stocks:
            if search_term in stock['symbol']:
                matching_stocks.append(stock)
        
        return jsonify({
            "search_term": search_term,
            "matches": len(matching_stocks),
            "stocks": matching_stocks[:20]  # Limit to 20 results
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
