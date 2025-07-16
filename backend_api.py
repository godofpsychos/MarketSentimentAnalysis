from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import os
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
import csv
import json
import glob
import numpy as np
import math
import jwt
import bcrypt
import secrets
import requests
from functools import wraps
from dotenv import load_dotenv

# Import portfolio API
from db.portfolio_api import portfolio_api

# Load environment variables
load_dotenv()

app = Flask(__name__)

# CORS Configuration with environment variables
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 'https://yourstock.ai,https://www.yourstock.ai,http://localhost:3000,http://127.0.0.1:3000').split(',')
FRONTEND_URL = os.getenv('FRONTEND_URL', 'https://yourstock.ai')

CORS(app, 
     origins=ALLOWED_ORIGINS,
     supports_credentials=True,
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
     allow_headers=['Content-Type', 'Authorization'])



# JWT Configuration
app.config['SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-this-in-production')
app.config['JWT_ALGORITHM'] = os.getenv('JWT_ALGORITHM', 'HS256')
app.config['JWT_EXPIRATION_HOURS'] = int(os.getenv('JWT_EXPIRATION_HOURS', '24'))

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', 'your-google-client-id')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', 'your-google-client-secret')
GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI', f'{FRONTEND_URL}/auth/google/callback')

# For development, we'll use a fallback approach
DEVELOPMENT_MODE = os.getenv('DEVELOPMENT_MODE', 'True').lower() == 'true'

def sanitize_for_json(obj):
    """Convert NaN and infinity values to None for JSON serialization"""
    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_for_json(item) for item in obj]
    elif isinstance(obj, (int, float)):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    elif pd.isna(obj):
        return None
    return obj

# Base directory and paths from environment variables
BASE_DIR = os.getenv('BASE_DIR', '/home/tarun/MarketSentimentAnalysis')
DB_PATH = os.getenv('SENTIMENT_DB_PATH', os.path.join(BASE_DIR, 'Sentiment_Analysis', 'sentiment_analysis.db'))
AUTH_DB_PATH = os.getenv('AUTH_DB_PATH', os.path.join(BASE_DIR, 'db', 'auth.db'))

# Fundamental Analysis paths
FUNDAMENTAL_BASE_DIR = os.getenv('FUNDAMENTAL_BASE_DIR', os.path.join(BASE_DIR, 'FundamentalAnalysis'))
PROFITABILITY_FILE = os.getenv('PROFITABILITY_FILE', os.path.join(FUNDAMENTAL_BASE_DIR, 'outputs', 'profitability', 'profitability_ratios.json'))
VALUATION_FILE = os.getenv('VALUATION_FILE', os.path.join(FUNDAMENTAL_BASE_DIR, 'outputs', 'valuation', 'basic_valuation_ratios.json'))
GROWTH_FILE = os.getenv('GROWTH_FILE', os.path.join(FUNDAMENTAL_BASE_DIR, 'outputs', 'growth', 'revenue_growth.json'))
LIQUIDITY_FILE = os.getenv('LIQUIDITY_FILE', os.path.join(FUNDAMENTAL_BASE_DIR, 'outputs', 'liquidity', 'basic_liquidity_ratios.json'))
CCC_FILE = os.getenv('CCC_FILE', os.path.join(FUNDAMENTAL_BASE_DIR, 'outputs', 'liquidity', 'cash_conversion_cycle.json'))

# Report and data files
REPORT_CSV_PATH = os.getenv('REPORT_CSV_PATH', os.path.join(BASE_DIR, 'report.csv'))
STOCKS_LIST_PATH = os.getenv('STOCKS_LIST_PATH', os.path.join(BASE_DIR, 'stocksList.csv'))

# News and sentiment files
NEWS_JSON_PATH = os.getenv('NEWS_JSON_PATH', os.path.join(BASE_DIR, 'news.json'))
RECENT_NEWS_PATH = os.getenv('RECENT_NEWS_PATH', os.path.join(BASE_DIR, 'insightGen', 'recent_news.json'))
SENTIMENT_RESULTS_PATH = os.getenv('SENTIMENT_RESULTS_PATH', os.path.join(BASE_DIR, 'Sentiment_Analysis', 'sentiment_analysis_results.json'))

# Stock News Database Configuration
STOCK_NEWS_DB_PATH = os.getenv('STOCK_NEWS_DB_PATH', os.path.join(BASE_DIR, 'db', 'stock_news.db'))



# Initialize auth database
def init_auth_db():
    """Initialize the authentication database with users table"""
    os.makedirs(os.path.dirname(AUTH_DB_PATH), exist_ok=True)
    conn = sqlite3.connect(AUTH_DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT,
            google_id TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Add test users for development/testing
    test_users = [
        {
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'password123'
        },
        {
            'name': 'Demo User',
            'email': 'user@test.com',
            'password': 'testpass123'
        },
        {
            'name': 'Admin User',
            'email': 'demo@marketsentiment.ai',
            'password': 'demo123'
        }
    ]
    
    for user in test_users:
        # Check if user already exists
        cursor.execute('SELECT id FROM users WHERE email = ?', (user['email'],))
        if not cursor.fetchone():
            # Hash the password
            password_hash = bcrypt.hashpw(user['password'].encode('utf-8'), bcrypt.gensalt())
            cursor.execute('''
                INSERT INTO users (name, email, password_hash)
                VALUES (?, ?, ?)
            ''', (user['name'], user['email'], password_hash.decode('utf-8')))
    
    conn.commit()
    conn.close()

# Initialize the auth database on startup
init_auth_db()

def generate_token(user_id, email):
    """Generate JWT token for user"""
    payload = {
        'user_id': user_id,
        'email': email,
        'exp': datetime.utcnow() + timedelta(hours=app.config['JWT_EXPIRATION_HOURS']),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm=app.config['JWT_ALGORITHM'])

def verify_token(token):
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=[app.config['JWT_ALGORITHM']])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'No token provided'}), 401
        
        if token.startswith('Bearer '):
            token = token[7:]
        
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        request.user = payload
        return f(*args, **kwargs)
    
    return decorated_function

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

@app.route('/api/sentiment-db-timestamp', methods=['GET'])
def get_sentiment_db_timestamp():
    """Get the timestamp of when the sentiment analysis database was last modified"""
    try:
        # Check if the database file exists
        if not os.path.exists(DB_PATH):
            return jsonify({"error": "Sentiment analysis database not found"}), 404
        
        # Get the file modification time
        modification_time = os.path.getmtime(DB_PATH)
        
        # Convert to datetime object
        modification_datetime = datetime.fromtimestamp(modification_time)
        
        # Format the timestamp
        formatted_timestamp = modification_datetime.isoformat()
        
        return jsonify({
            "database_path": DB_PATH,
            "last_modified": formatted_timestamp,
            "unix_timestamp": modification_time,
            "human_readable": modification_datetime.strftime("%Y-%m-%d %H:%M:%S"),
            "timezone": "UTC"
        })
        
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
        all_stocks = []
        try:
            # Get the stocks from our predefined list
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
            for symbol, ticker in popular_nse_stocks.items():
                all_stocks.append({
                    "symbol": symbol,
                    "ticker": ticker,
                    "exchange": "NSE"
                })
        except Exception as e:
            print(f"Error loading stock list: {e}")
            return jsonify({"error": "Failed to load stock list"}), 500
        
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

@app.route('/api/financial-data', methods=['GET'])
def get_financial_data():
    """Get financial data from the CSV report"""
    try:
        # Path to the CSV file
        csv_file_path = REPORT_CSV_PATH
        
        if not os.path.exists(csv_file_path):
            return jsonify({"error": "Financial data file not found"}), 404
        
        financial_data = []
        
        # Read CSV file
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                # Convert string values to numbers
                try:
                    total_revenue = float(row['total_revenue']) if row['total_revenue'] else 0
                    total_expenditure = float(row['total_expenditure']) if row['total_expenditure'] else 0
                    net_profit = float(row['net_profit']) if row['net_profit'] else 0
                    
                    financial_data.append({
                        'symbol': row['symbol'],
                        'company_name': row['company_name'],
                        'period_date': row['period_date'],
                        'total_revenue': total_revenue,
                        'total_expenditure': total_expenditure,
                        'net_profit': net_profit
                    })
                except (ValueError, KeyError) as e:
                    print(f"Error processing row: {row}, Error: {e}")
                    continue
        
        return jsonify({
            "data": financial_data,
            "total_records": len(financial_data),
            "companies": list(set([item['symbol'] for item in financial_data]))
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Fundamental Analysis API Endpoints

@app.route('/api/fundamental-analysis/<stock_symbol>', methods=['GET'])
def get_fundamental_analysis(stock_symbol):
    """Get comprehensive fundamental analysis for a specific stock"""
    try:
        # Clean the stock symbol (remove .NS if present)
        clean_symbol = stock_symbol.replace('.NS', '').upper()
        
        # Load pre-calculated data from outputs directory
        profitability_data = load_profitability_data(clean_symbol)
        valuation_data = load_valuation_data(clean_symbol)
        growth_data = load_growth_data(clean_symbol)
        liquidity_data = load_liquidity_data(clean_symbol)
        
        # Create comprehensive analysis result
        analysis_result = {
            "company_info": {
                "symbol": clean_symbol,
                "sector": profitability_data['sector'],
                "company_name": profitability_data['company_name']
            },
            "profitability": profitability_data,
            "valuation": valuation_data,
            "growth": growth_data,
            "liquidity": liquidity_data,
            "analysis_date": datetime.now().isoformat()
        }
        
        return jsonify(analysis_result)
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": f"Failed to load fundamental analysis: {str(e)}"}), 500

@app.route('/api/fundamental-summary', methods=['GET'])
def get_fundamental_summary():
    """Get summary of fundamental analysis for all stocks"""
    try:
        summary_data = []
        
        # Load profitability data to get list of companies
        profitability_file = PROFITABILITY_FILE
        if os.path.exists(profitability_file):
            with open(profitability_file, 'r') as f:
                profitability_data = json.load(f)
            
            for item in profitability_data[:20]:  # Limit to first 20 for demo
                try:
                    symbol = item['symbol']
                    
                    # Calculate key metrics from available data
                    roe = item['roe_percent']
                    net_margin = item['net_margin_percent']
                    
                    # Load valuation data for this symbol
                    valuation_data = load_valuation_data(symbol)
                    pe_ratio = valuation_data['pe_ratio']
                    
                    key_metrics = {
                        "symbol": symbol,
                        "roe": round(roe, 2),
                        "pe_ratio": round(pe_ratio, 2),
                        "net_margin": round(net_margin, 2),
                        "sector": item['sector'],
                        "company_name": item['company_name']
                    }
                    summary_data.append(key_metrics)
                
                except Exception as e:
                    print(f"Error processing {symbol}: {e}")
                    continue
        
        return jsonify({
            "summary": summary_data,
            "total_companies": len(summary_data),
            "top_performers": sorted(summary_data, key=lambda x: x['roe'], reverse=True)[:5],
            "undervalued_stocks": [stock for stock in summary_data if stock['pe_ratio'] < 20]
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/run-fundamental-analysis', methods=['POST'])
def run_fundamental_analysis():
    """Trigger fundamental analysis computation"""
    try:
        # This would trigger the Python scripts to run analysis
        import subprocess
        
        result = subprocess.run([
            'python', os.path.join(FUNDAMENTAL_BASE_DIR, 'run_all_indicators.py'),
            '--output-format', 'json'
        ], capture_output=True, text=True, cwd=BASE_DIR)
        
        if result.returncode == 0:
            return jsonify({
                "status": "success",
                "message": "Fundamental analysis completed successfully",
                "output": result.stdout
            })
        else:
            return jsonify({
                "status": "error",
                "message": "Analysis failed",
                "error": result.stderr
            }), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/sector-analysis/<sector_name>', methods=['GET'])
def get_sector_analysis(sector_name):
    """Get sector-wise fundamental analysis"""
    try:
        sector_data = {
            "sector": sector_name,
            "avg_pe": 24.5,
            "avg_pb": 3.2,
            "avg_ps": 4.8,
            "avg_roe": 16.8,
            "avg_roa": 8.5,
            "avg_debt_equity": 0.6,
            "avg_current_ratio": 2.1,
            "total_companies": 12,
            "sector_growth": 15.2
        }
        
        return jsonify(sector_data)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/available-sectors', methods=['GET'])
def get_available_sectors():
    """Get list of available sectors"""
    try:
        sectors = [
            "Information Technology",
            "Banking & Financial Services",
            "Pharmaceuticals & Healthcare",
            "Oil, Gas & Energy",
            "Consumer Goods & FMCG",
            "Automobiles",
            "Metals & Mining",
            "Cement & Construction",
            "Telecommunications"
        ]
        
        return jsonify({"sectors": sectors})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/fundamental-scores/<stock_symbol>', methods=['GET'])
def get_fundamental_scores(stock_symbol):
    """Get comprehensive fundamental analysis scores for a stock using pre-calculated data"""
    try:
        # Clean the stock symbol (remove .NS if present)
        clean_symbol = stock_symbol.replace('.NS', '').upper()
        
        # Load pre-calculated data from outputs directory
        profitability_data = load_profitability_data(clean_symbol)
        valuation_data = load_valuation_data(clean_symbol)
        growth_data = load_growth_data(clean_symbol)
        liquidity_data = load_liquidity_data(clean_symbol)
        
        # Calculate scores based on the loaded data
        reliability_score = calculate_reliability_score_from_data(profitability_data, liquidity_data)
        growth_score = calculate_growth_score_from_data(growth_data)
        valuation_score = calculate_valuation_score_from_data(valuation_data)
        
        # Calculate overall score (weights: Reliability 40%, Growth 35%, Valuation 25%)
        overall_score = (reliability_score * 0.40 + growth_score * 0.35 + valuation_score * 0.25)
        
        # Determine overall grade
        if overall_score >= 85:
            overall_grade = "A+"
            recommendation = "Strong Buy"
        elif overall_score >= 75:
            overall_grade = "A"
            recommendation = "Buy"
        elif overall_score >= 65:
            overall_grade = "B+"
            recommendation = "Buy"
        elif overall_score >= 55:
            overall_grade = "B"
            recommendation = "Hold"
        elif overall_score >= 45:
            overall_grade = "C+"
            recommendation = "Hold"
        elif overall_score >= 35:
            overall_grade = "C"
            recommendation = "Weak Hold"
        elif overall_score >= 25:
            overall_grade = "D"
            recommendation = "Sell"
        elif overall_score > 0:
            overall_grade = "D-"
            recommendation = "Sell"
        else:
            overall_grade = "N/A"
            recommendation = "Data Unavailable"
        
        # Determine risk level
        risk_level = determine_risk_level(profitability_data, liquidity_data)
        
        # Create frontend summary
        frontend_summary = {
            'symbol': clean_symbol,
            'reliability_score': round(reliability_score, 1),
            'growth_scope': round(growth_score, 1),
            'valuation_score': round(valuation_score, 1),
            'overall_score': round(overall_score, 1),
            'overall_grade': overall_grade,
            'recommendation': recommendation,
            'risk_level': risk_level,
            'key_highlights': [
                f"Reliability: {round(reliability_score, 1)}/100",
                f"Growth Potential: {round(growth_score, 1)}/100",
                f"Valuation: {round(valuation_score, 1)}/100",
                f"Risk: {risk_level}"
            ]
        }
        
        return jsonify({
            "success": True,
            "stock_symbol": clean_symbol,
            "frontend_summary": frontend_summary,
            "calculated_at": datetime.now().isoformat()
        })
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        print(f"Error calculating fundamental scores for {stock_symbol}: {e}")
        return jsonify({"error": f"Failed to calculate fundamental scores: {str(e)}"}), 500

def load_profitability_data(symbol):
    """Load profitability data for a specific symbol"""
    try:
        file_path = PROFITABILITY_FILE
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Find the data for the specific symbol
        for item in data:
            if item.get('symbol') == symbol:
                return item
        
        # If symbol not found, raise error
        raise ValueError(f"Profitability data not found for symbol: {symbol}")
    except Exception as e:
        print(f"Error loading profitability data for {symbol}: {e}")
        raise

def load_valuation_data(symbol):
    """Load valuation data for a specific symbol"""
    try:
        file_path = VALUATION_FILE
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Find the data for the specific symbol
        for item in data:
            if item.get('symbol') == symbol:
                return item
        
        # If symbol not found, raise error
        raise ValueError(f"Valuation data not found for symbol: {symbol}")
    except Exception as e:
        print(f"Error loading valuation data for {symbol}: {e}")
        raise

def load_growth_data(symbol):
    """Load growth data for a specific symbol"""
    try:
        # Try revenue growth first
        file_path = GROWTH_FILE
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Find the data for the specific symbol
        for item in data:
            if item.get('symbol') == symbol:
                # Map the actual fields to expected frontend fields
                return {
                    'symbol': item['symbol'],
                    'company_name': item['company_name'],
                    'sector': item['sector'],
                    'revenue_growth_percent': item['revenue_cagr_percent'],
                    'earnings_growth_percent': item['recent_avg_growth_percent'],
                    'asset_growth_percent': item['latest_yoy_growth_percent'],
                    'equity_growth_percent': item['revenue_cagr_percent'] * 0.8,
                    'revenue_volatility': item['revenue_volatility'],
                    'periods_analyzed': item['periods_analyzed'],
                    'first_revenue': item['first_revenue'],
                    'latest_revenue': item['latest_revenue']
                }
        
        # If symbol not found, raise error
        raise ValueError(f"Growth data not found for symbol: {symbol}")
    except Exception as e:
        print(f"Error loading growth data for {symbol}: {e}")
        raise

def load_liquidity_data(symbol):
    """Load liquidity data for a specific symbol"""
    try:
        # Load basic liquidity ratios
        file_path = LIQUIDITY_FILE
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Find the data for the specific symbol
        liquidity_data = None
        for item in data:
            if item.get('symbol') == symbol:
                liquidity_data = item
                break
        
        if not liquidity_data:
            raise ValueError(f"Liquidity data not found for symbol: {symbol}")
        
        # Load cash conversion cycle data
        ccc_file_path = CCC_FILE
        ccc_data = None
        try:
            with open(ccc_file_path, 'r') as f:
                ccc_list = json.load(f)
            
            for item in ccc_list:
                if item.get('symbol') == symbol:
                    ccc_data = item
                    break
        except Exception as e:
            print(f"Error loading cash conversion cycle data: {e}")
            raise ValueError(f"Cash conversion cycle data not found for symbol: {symbol}")
        
        if not ccc_data:
            raise ValueError(f"Cash conversion cycle data not found for symbol: {symbol}")
        
        # Combine liquidity and cash conversion cycle data
        result = {
            'symbol': liquidity_data['symbol'],
            'company_name': liquidity_data['company_name'],
            'sector': liquidity_data['sector'],
            'current_assets': liquidity_data['current_assets'],
            'current_liabilities': liquidity_data['current_liabilities'],
            'cash_and_equivalents': liquidity_data['cash_and_equivalents'],
            'inventory': liquidity_data['inventory'],
            'accounts_receivable': liquidity_data['accounts_receivable'],
            'current_ratio': liquidity_data['current_ratio'],
            'quick_ratio': liquidity_data['quick_ratio'],
            'cash_ratio': liquidity_data['cash_ratio'],
            'working_capital': liquidity_data['working_capital'],
            'current_ratio_interpretation': liquidity_data['current_ratio_interpretation'],
            'quick_ratio_interpretation': liquidity_data['quick_ratio_interpretation'],
            'days_sales_outstanding': ccc_data['days_sales_outstanding'],
            'days_inventory_outstanding': ccc_data['days_inventory_outstanding'],
            'days_payable_outstanding': ccc_data['days_payable_outstanding'],
            'cash_conversion_cycle': ccc_data['cash_conversion_cycle'],
            'ccc_interpretation': ccc_data['ccc_interpretation'],
            'operating_cash_flow': liquidity_data['working_capital'] * 0.8,
            'investing_cash_flow': -(liquidity_data['current_assets'] * 0.1),
            'financing_cash_flow': -(liquidity_data['working_capital'] * 0.2)
        }
        
        return result
    except Exception as e:
        print(f"Error loading liquidity data for {symbol}: {e}")
        raise

def calculate_reliability_score_from_data(profitability_data, liquidity_data):
    """Calculate reliability score from pre-calculated data"""
    score = 0
    
    if profitability_data:
        # ROE scoring (35 points)
        roe = profitability_data['roe_percent']
        if roe >= 15:
            score += 15
        elif roe >= 10:
            score += 12
        elif roe >= 5:
            score += 8
        elif roe > 0:
            score += 4
        
        # Net margin scoring (10 points)
        net_margin = profitability_data['net_margin_percent']
        if net_margin >= 15:
            score += 10
        elif net_margin >= 8:
            score += 7
        elif net_margin >= 3:
            score += 4
        elif net_margin > 0:
            score += 2
        
        # Operating margin scoring (10 points)
        op_margin = profitability_data['operating_margin_percent']
        if op_margin >= 20:
            score += 10
        elif op_margin >= 12:
            score += 7
        elif op_margin >= 5:
            score += 4
        elif op_margin > 0:
            score += 2
    
    if liquidity_data:
        # Current ratio scoring (15 points)
        current_ratio = liquidity_data['current_ratio']
        if current_ratio >= 2.0:
            score += 15
        elif current_ratio >= 1.5:
            score += 12
        elif current_ratio >= 1.0:
            score += 8
        elif current_ratio >= 0.8:
            score += 4
        
        # Quick ratio scoring (10 points)
        quick_ratio = liquidity_data['quick_ratio']
        if quick_ratio >= 1.5:
            score += 10
        elif quick_ratio >= 1.0:
            score += 8
        elif quick_ratio >= 0.8:
            score += 5
        elif quick_ratio >= 0.5:
            score += 2
    
    return min(score, 100)  # Cap at 100

def calculate_growth_score_from_data(growth_data):
    """Calculate growth score from pre-calculated data"""
    score = 0
    
    if growth_data:
        # Revenue growth scoring (40 points)
        revenue_growth = growth_data['revenue_growth_percent']
        if revenue_growth >= 20:
            score += 40
        elif revenue_growth >= 15:
            score += 35
        elif revenue_growth >= 10:
            score += 30
        elif revenue_growth >= 5:
            score += 25
        elif revenue_growth >= 0:
            score += 20
        elif revenue_growth >= -5:
            score += 10
        
        # Earnings growth scoring (30 points)
        earnings_growth = growth_data['earnings_growth_percent']
        if earnings_growth >= 20:
            score += 30
        elif earnings_growth >= 15:
            score += 25
        elif earnings_growth >= 10:
            score += 20
        elif earnings_growth >= 5:
            score += 15
        elif earnings_growth >= 0:
            score += 10
        elif earnings_growth >= -5:
            score += 5
        
        # Asset growth scoring (30 points)
        asset_growth = growth_data['asset_growth_percent']
        if asset_growth >= 15:
            score += 30
        elif asset_growth >= 10:
            score += 25
        elif asset_growth >= 5:
            score += 20
        elif asset_growth >= 0:
            score += 15
        elif asset_growth >= -5:
            score += 10
    
    return min(score, 100)  # Cap at 100

def calculate_valuation_score_from_data(valuation_data):
    """Calculate valuation score from pre-calculated data"""
    score = 0
    
    if valuation_data:
        # P/E ratio scoring (40 points) - lower is better
        pe_ratio = valuation_data['pe_ratio']
        if pe_ratio <= 10:
            score += 40
        elif pe_ratio <= 15:
            score += 35
        elif pe_ratio <= 20:
            score += 30
        elif pe_ratio <= 25:
            score += 25
        elif pe_ratio <= 30:
            score += 20
        elif pe_ratio <= 40:
            score += 15
        elif pe_ratio <= 50:
            score += 10
        elif pe_ratio <= 100:
            score += 5
        
        # P/B ratio scoring (30 points) - lower is better
        pb_ratio = valuation_data['pb_ratio']
        if pb_ratio <= 1:
            score += 30
        elif pb_ratio <= 2:
            score += 25
        elif pb_ratio <= 3:
            score += 20
        elif pb_ratio <= 5:
            score += 15
        elif pb_ratio <= 8:
            score += 10
        elif pb_ratio <= 15:
            score += 5
        
        # P/S ratio scoring (30 points) - lower is better
        ps_ratio = valuation_data['ps_ratio']
        if ps_ratio <= 1:
            score += 30
        elif ps_ratio <= 2:
            score += 25
        elif ps_ratio <= 3:
            score += 20
        elif ps_ratio <= 5:
            score += 15
        elif ps_ratio <= 8:
            score += 10
        elif ps_ratio <= 15:
            score += 5
    
    return min(score, 100)  # Cap at 100

def determine_risk_level(profitability_data, liquidity_data):
    """Determine risk level based on financial data"""
    risk_score = 0
    
    if profitability_data:
        roe = profitability_data['roe_percent']
        if roe < 5:
            risk_score += 20
        elif roe < 10:
            risk_score += 10
        
        net_margin = profitability_data['net_margin_percent']
        if net_margin < 3:
            risk_score += 15
        elif net_margin < 8:
            risk_score += 8
    
    if liquidity_data:
        current_ratio = liquidity_data['current_ratio']
        if current_ratio < 1.0:
            risk_score += 25
        elif current_ratio < 1.5:
            risk_score += 15
    
    if risk_score >= 40:
        return "High"
    elif risk_score >= 20:
        return "Medium"
    else:
        return "Low"

# Authentication Routes
@app.route('/api/auth/signup', methods=['POST'])
def signup():
    """User registration endpoint"""
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        
        if not all([name, email, password]):
            return jsonify({'error': 'All fields are required'}), 400
        
        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        conn = sqlite3.connect(AUTH_DB_PATH)
        cursor = conn.cursor()
        
        # Check if user already exists
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        if cursor.fetchone():
            conn.close()
            return jsonify({'error': 'User already exists'}), 409
        
        # Create new user
        cursor.execute('''
            INSERT INTO users (name, email, password_hash)
            VALUES (?, ?, ?)
        ''', (name, email, password_hash))
        
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Generate token
        token = generate_token(user_id, email)
        
        return jsonify({
            'token': token,
            'user': {
                'id': user_id,
                'name': name,
                'email': email
            }
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/signin', methods=['POST'])
def signin():
    """User login endpoint"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not all([email, password]):
            return jsonify({'error': 'Email and password are required'}), 400
        
        conn = sqlite3.connect(AUTH_DB_PATH)
        cursor = conn.cursor()
        
        # Get user by email
        cursor.execute('SELECT id, name, email, password_hash FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        user_id, name, user_email, password_hash = user
        
        # Verify password
        if not bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Generate token
        token = generate_token(user_id, user_email)
        
        return jsonify({
            'token': token,
            'user': {
                'id': user_id,
                'name': name,
                'email': user_email
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/google/url', methods=['GET'])
def get_google_auth_url():
    """Get Google OAuth URL"""
    try:
        if DEVELOPMENT_MODE and (GOOGLE_CLIENT_ID == 'your-google-client-id' or GOOGLE_CLIENT_SECRET == 'your-google-client-secret'):
            # In development mode with placeholder credentials, return a mock response
            return jsonify({
                'error': 'Google OAuth not configured for development',
                'message': 'Please use email/password login for testing',
                'development_mode': True
            }), 400
        
        state = secrets.token_urlsafe(32)
        
        auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?" \
                  f"client_id={GOOGLE_CLIENT_ID}&" \
                  f"redirect_uri={GOOGLE_REDIRECT_URI}&" \
                  f"scope=openid%20email%20profile&" \
                  f"response_type=code&" \
                  f"state={state}"
        
        return jsonify({'authUrl': auth_url, 'state': state})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/google/callback', methods=['POST'])
def google_auth_callback():
    """Handle Google OAuth callback"""
    try:
        data = request.get_json()
        code = data.get('code')
        state = data.get('state')
        
        if not code:
            return jsonify({'error': 'Authorization code is required'}), 400
        
        # Exchange code for tokens
        token_url = 'https://oauth2.googleapis.com/token'
        token_data = {
            'client_id': GOOGLE_CLIENT_ID,
            'client_secret': GOOGLE_CLIENT_SECRET,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': GOOGLE_REDIRECT_URI
        }
        
        response = requests.post(token_url, data=token_data)
        if not response.ok:
            return jsonify({'error': 'Failed to exchange code for tokens'}), 400
        
        tokens = response.json()
        access_token = tokens.get('access_token')
        
        # Get user info from Google
        user_info_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
        headers = {'Authorization': f'Bearer {access_token}'}
        user_response = requests.get(user_info_url, headers=headers)
        
        if not user_response.ok:
            return jsonify({'error': 'Failed to get user info'}), 400
        
        user_info = user_response.json()
        google_id = user_info.get('id')
        email = user_info.get('email')
        name = user_info.get('name')
        
        conn = sqlite3.connect(AUTH_DB_PATH)
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute('SELECT id, name, email FROM users WHERE google_id = ? OR email = ?', (google_id, email))
        user = cursor.fetchone()
        
        if user:
            # User exists, update google_id if needed
            user_id, user_name, user_email = user
            if not user.get('google_id'):
                cursor.execute('UPDATE users SET google_id = ? WHERE id = ?', (google_id, user_id))
                conn.commit()
        else:
            # Create new user
            cursor.execute('''
                INSERT INTO users (name, email, google_id)
                VALUES (?, ?, ?)
            ''', (name, email, google_id))
            user_id = cursor.lastrowid
            conn.commit()
        
        conn.close()
        
        # Generate token
        token = generate_token(user_id, email)
        
        return jsonify({
            'token': token,
            'user': {
                'id': user_id,
                'name': name,
                'email': email
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/verify', methods=['GET'])
@require_auth
def verify_auth():
    """Verify authentication token"""
    return jsonify({
        'valid': True,
        'user': request.user
    })

@app.route('/api/auth/logout', methods=['POST'])
@require_auth
def logout():
    """Logout endpoint (client should remove token)"""
    return jsonify({'message': 'Logged out successfully'})

@app.route('/api/sectoral-analysis', methods=['GET'])
def get_sectoral_analysis():
    """Get sectoral analysis data"""
    try:
        # Sample sector data - in production, this would come from a database
        sector_data = {
            'sectors': [
                {
                    'name': 'Technology',
                    'performance': 2.5,
                    'sentiment': 0.7,
                    'volume': 1250000,
                    'market_cap': 85000000000,
                    'top_stocks': [
                        {'symbol': 'TCS', 'name': 'Tata Consultancy Services', 'price': 3850.50, 'change': 1.2},
                        {'symbol': 'INFY', 'name': 'Infosys Limited', 'price': 1450.75, 'change': 0.8},
                        {'symbol': 'HCLTECH', 'name': 'HCL Technologies', 'price': 1250.25, 'change': 1.5}
                    ]
                },
                {
                    'name': 'Banking & Financial',
                    'performance': 1.8,
                    'sentiment': 0.6,
                    'volume': 980000,
                    'market_cap': 120000000000,
                    'top_stocks': [
                        {'symbol': 'HDFCBANK', 'name': 'HDFC Bank', 'price': 1650.00, 'change': 0.9},
                        {'symbol': 'ICICIBANK', 'name': 'ICICI Bank', 'price': 950.50, 'change': 1.1},
                        {'symbol': 'SBIN', 'name': 'State Bank of India', 'price': 650.75, 'change': 0.7}
                    ]
                },
                {
                    'name': 'Automobiles',
                    'performance': -0.5,
                    'sentiment': 0.4,
                    'volume': 750000,
                    'market_cap': 45000000000,
                    'top_stocks': [
                        {'symbol': 'MARUTI', 'name': 'Maruti Suzuki', 'price': 10500.00, 'change': -0.3},
                        {'symbol': 'TATAMOTORS', 'name': 'Tata Motors', 'price': 850.25, 'change': 0.5},
                        {'symbol': 'M&M', 'name': 'Mahindra & Mahindra', 'price': 1850.50, 'change': -0.8}
                    ]
                },
                {
                    'name': 'Oil & Gas',
                    'performance': 3.2,
                    'sentiment': 0.8,
                    'volume': 650000,
                    'market_cap': 35000000000,
                    'top_stocks': [
                        {'symbol': 'RELIANCE', 'name': 'Reliance Industries', 'price': 2850.75, 'change': 2.1},
                        {'symbol': 'ONGC', 'name': 'Oil & Natural Gas Corp', 'price': 185.50, 'change': 1.8},
                        {'symbol': 'IOC', 'name': 'Indian Oil Corporation', 'price': 95.25, 'change': 1.2}
                    ]
                },
                {
                    'name': 'Pharmaceuticals',
                    'performance': 1.2,
                    'sentiment': 0.5,
                    'volume': 450000,
                    'market_cap': 28000000000,
                    'top_stocks': [
                        {'symbol': 'SUNPHARMA', 'name': 'Sun Pharmaceutical', 'price': 1250.00, 'change': 0.6},
                        {'symbol': 'DRREDDY', 'name': 'Dr. Reddy\'s Laboratories', 'price': 5850.75, 'change': 0.9},
                        {'symbol': 'CIPLA', 'name': 'Cipla Limited', 'price': 1250.50, 'change': 0.4}
                    ]
                },
                {
                    'name': 'Consumer Goods',
                    'performance': 0.8,
                    'sentiment': 0.6,
                    'volume': 380000,
                    'market_cap': 22000000000,
                    'top_stocks': [
                        {'symbol': 'HINDUNILVR', 'name': 'Hindustan Unilever', 'price': 2850.25, 'change': 0.3},
                        {'symbol': 'ITC', 'name': 'ITC Limited', 'price': 485.75, 'change': 0.7},
                        {'symbol': 'NESTLEIND', 'name': 'Nestle India', 'price': 2850.00, 'change': 0.5}
                    ]
                }
            ],
            'market_summary': {
                'total_market_cap': 335000000000,
                'total_volume': 4460000,
                'overall_sentiment': 0.6,
                'top_performing_sector': 'Oil & Gas',
                'worst_performing_sector': 'Automobiles'
            }
        }
        
        return jsonify(sector_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stock-news/<stock_symbol>', methods=['GET'])
def get_stock_news(stock_symbol):
    """Get latest news for a specific stock from database, sorted by timestamp in sets of 5"""
    try:
        # Get pagination parameters
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 5))
        
        # Calculate offset
        offset = (page - 1) * per_page
        
        # Get company name for display
        company_name = get_company_name(stock_symbol)
        
        # Check if database exists
        if not os.path.exists(STOCK_NEWS_DB_PATH):
            return jsonify({
                'error': 'Stock news database not found',
                'message': 'Please ensure the stock_news.db file exists in the db directory'
            }), 404
        
        # Connect to stock news database
        conn = sqlite3.connect(STOCK_NEWS_DB_PATH)
        cursor = conn.cursor()
        
        # Get table info to understand the structure
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if not tables:
            conn.close()
            return jsonify({
                'error': 'No tables found in stock news database',
                'message': 'Please ensure the database contains news tables'
            }), 404
        
        # Try to find the news table (common table names)
        news_table = None
        for table in tables:
            table_name = table[0].lower()
            if 'news' in table_name or 'article' in table_name or 'stock' in table_name:
                news_table = table[0]
                break
        
        if not news_table:
            conn.close()
            return jsonify({
                'error': 'News table not found',
                'available_tables': [table[0] for table in tables],
                'message': 'Please ensure the database contains a news table'
            }), 404
        
        # Get column info for the news table
        cursor.execute(f"PRAGMA table_info({news_table});")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Determine the correct column names based on common patterns
        stock_col = None
        title_col = None
        description_col = None
        url_col = None
        source_col = None
        timestamp_col = None
        
        for col in columns:
            col_lower = col.lower()
            if 'stock' in col_lower or 'symbol' in col_lower:
                stock_col = col
            elif 'title' in col_lower or 'headline' in col_lower:
                title_col = col
            elif 'description' in col_lower or 'content' in col_lower or 'summary' in col_lower:
                description_col = col
            elif 'url' in col_lower or 'link' in col_lower or 'source_link' in col_lower:
                url_col = col
            elif 'source' in col_lower or 'publisher' in col_lower:
                source_col = col
            elif 'timestamp' in col_lower or 'date' in col_lower or 'time' in col_lower or 'published' in col_lower or 'datetime' in col_lower:
                timestamp_col = col
        # Robust mapping for your table structure
        if set(['datetime', 'stock', 'description']).issubset(set(columns)):
            stock_col = 'stock'
            title_col = 'description'
            description_col = 'description'
            timestamp_col = 'datetime'
            if 'source_link' in columns:
                url_col = 'source_link'
        
        # Validate required columns
        if not all([stock_col, title_col, timestamp_col]):
            conn.close()
            return jsonify({
                'error': 'Required columns not found in news table',
                'available_columns': columns,
                'message': 'News table must contain stock symbol, title, and timestamp columns'
            }), 400
        
        # Get total count of articles for this stock
        cursor.execute(f'''
            SELECT COUNT(*) FROM {news_table} 
            WHERE {stock_col} = ?
        ''', (stock_symbol.upper(),))
        total_articles = cursor.fetchone()[0]
        
        # Build the SELECT query based on available columns
        select_columns = [stock_col, title_col]
        if description_col:
            select_columns.append(description_col)
        if url_col:
            select_columns.append(url_col)
        if source_col:
            select_columns.append(source_col)
        select_columns.append(timestamp_col)
        # Filter out any None values to avoid join errors
        select_columns = [col for col in select_columns if col]
        
        # Get latest 5 news articles sorted by timestamp (newest first)
        query = f'''
            SELECT {', '.join(select_columns)}
            FROM {news_table} 
            WHERE {stock_col} = ?
            ORDER BY {timestamp_col} DESC
            LIMIT ? OFFSET ?
        '''
        
        cursor.execute(query, (stock_symbol.upper(), per_page, offset))
        articles = cursor.fetchall()
        conn.close()
        
        # Format articles
        formatted_articles = []
        for article in articles:
            article_data = {}
            col_index = 0
            
            article_data['stock_symbol'] = article[col_index]
            col_index += 1
            
            article_data['title'] = article[col_index]
            col_index += 1
            
            if description_col:
                article_data['description'] = article[col_index] or 'No description available'
                col_index += 1
            else:
                article_data['description'] = 'No description available'
            
            if url_col:
                article_data['url'] = article[col_index] or '#'
                col_index += 1
            else:
                article_data['url'] = '#'
            
            if source_col:
                article_data['source'] = article[col_index] or 'Unknown'
                col_index += 1
            else:
                article_data['source'] = 'Unknown'
            
            article_data['published_at'] = article[col_index]
            
            formatted_articles.append(article_data)
        
        # Calculate pagination info
        total_pages = (total_articles + per_page - 1) // per_page
        
        return jsonify({
            'stock_symbol': stock_symbol,
            'company_name': company_name,
            'articles': formatted_articles,
            'pagination': {
                'current_page': page,
                'per_page': per_page,
                'total_articles': total_articles,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1
            },
            'database_info': {
                'table_name': news_table,
                'total_articles_found': total_articles
            },
            'last_updated': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stock-news/all', methods=['GET'])
def get_all_stock_news():
    """Get all latest news from database, sorted by timestamp in sets of 5"""
    try:
        # Get pagination parameters
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 5))
        stock_filter = request.args.get('stock', None)
        
        # Calculate offset
        offset = (page - 1) * per_page
        
        # Check if database exists
        if not os.path.exists(STOCK_NEWS_DB_PATH):
            return jsonify({
                'error': 'Stock news database not found',
                'message': 'Please ensure the stock_news.db file exists in the db directory'
            }), 404
        
        # Connect to stock news database
        conn = sqlite3.connect(STOCK_NEWS_DB_PATH)
        cursor = conn.cursor()
        
        # Get table info to understand the structure
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if not tables:
            conn.close()
            return jsonify({
                'error': 'No tables found in stock news database',
                'message': 'Please ensure the database contains news tables'
            }), 404
        
        # Try to find the news table (common table names)
        news_table = None
        for table in tables:
            table_name = table[0].lower()
            if 'news' in table_name or 'article' in table_name or 'stock' in table_name:
                news_table = table[0]
                break
        
        if not news_table:
            conn.close()
            return jsonify({
                'error': 'News table not found',
                'available_tables': [table[0] for table in tables],
                'message': 'Please ensure the database contains a news table'
            }), 404
        
        # Get column info for the news table
        cursor.execute(f"PRAGMA table_info({news_table});")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Determine the correct column names based on common patterns
        stock_col = None
        title_col = None
        description_col = None
        url_col = None
        source_col = None
        timestamp_col = None
        
        for col in columns:
            col_lower = col.lower()
            if 'stock' in col_lower or 'symbol' in col_lower:
                stock_col = col
            elif 'title' in col_lower or 'headline' in col_lower:
                title_col = col
            elif 'description' in col_lower or 'content' in col_lower or 'summary' in col_lower:
                description_col = col
            elif 'url' in col_lower or 'link' in col_lower or 'source_link' in col_lower:
                url_col = col
            elif 'source' in col_lower or 'publisher' in col_lower:
                source_col = col
            elif 'timestamp' in col_lower or 'date' in col_lower or 'time' in col_lower or 'published' in col_lower or 'datetime' in col_lower:
                timestamp_col = col
        # Robust mapping for your table structure
        if set(['datetime', 'stock', 'description']).issubset(set(columns)):
            stock_col = 'stock'
            title_col = 'description'
            description_col = 'description'
            timestamp_col = 'datetime'
            if 'source_link' in columns:
                url_col = 'source_link'
        
        # Validate required columns
        if not all([stock_col, title_col, timestamp_col]):
            conn.close()
            return jsonify({
                'error': 'Required columns not found in news table',
                'available_columns': columns,
                'message': 'News table must contain stock symbol, title, and timestamp columns'
            }), 400
        
        # Build the SELECT query based on available columns
        select_columns = [stock_col, title_col]
        if description_col:
            select_columns.append(description_col)
        if url_col:
            select_columns.append(url_col)
        if source_col:
            select_columns.append(source_col)
        select_columns.append(timestamp_col)
        # Filter out any None values to avoid join errors
        select_columns = [col for col in select_columns if col]
        
        # Build query based on filters
        if stock_filter:
            # Get total count for specific stock
            cursor.execute(f'''
                SELECT COUNT(*) FROM {news_table} 
                WHERE {stock_col} = ?
            ''', (stock_filter.upper(),))
            total_articles = cursor.fetchone()[0]
            
            # Get articles for specific stock
            query = f'''
                SELECT {', '.join(select_columns)}
                FROM {news_table} 
                WHERE {stock_col} = ?
                ORDER BY {timestamp_col} DESC
                LIMIT ? OFFSET ?
            '''
            cursor.execute(query, (stock_filter.upper(), per_page, offset))
        else:
            # Get total count for all articles
            cursor.execute(f'SELECT COUNT(*) FROM {news_table}')
            total_articles = cursor.fetchone()[0]
            
            # Get all articles
            query = f'''
                SELECT {', '.join(select_columns)}
                FROM {news_table} 
                ORDER BY {timestamp_col} DESC
                LIMIT ? OFFSET ?
            '''
            cursor.execute(query, (per_page, offset))
        
        articles = cursor.fetchall()
        conn.close()
        
        # Format articles
        formatted_articles = []
        for article in articles:
            article_data = {}
            col_index = 0
            
            article_data['stock_symbol'] = article[col_index]
            col_index += 1
            
            article_data['title'] = article[col_index]
            col_index += 1
            
            if description_col:
                article_data['description'] = article[col_index] or 'No description available'
                col_index += 1
            else:
                article_data['description'] = 'No description available'
            
            if url_col:
                article_data['url'] = article[col_index] or '#'
                col_index += 1
            else:
                article_data['url'] = '#'
            
            if source_col:
                article_data['source'] = article[col_index] or 'Unknown'
                col_index += 1
            else:
                article_data['source'] = 'Unknown'
            
            article_data['published_at'] = article[col_index]
            article_data['company_name'] = get_company_name(article_data['stock_symbol'])
            
            formatted_articles.append(article_data)
        
        # Calculate pagination info
        total_pages = (total_articles + per_page - 1) // per_page
        
        return jsonify({
            'articles': formatted_articles,
            'pagination': {
                'current_page': page,
                'per_page': per_page,
                'total_articles': total_articles,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1
            },
            'filters': {
                'stock': stock_filter
            },
            'database_info': {
                'table_name': news_table,
                'total_articles_found': total_articles
            },
            'last_updated': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_company_name(stock_symbol):
    """Get company name from stock symbol"""
    company_names = {
        'RELIANCE': 'Reliance Industries',
        'TCS': 'Tata Consultancy Services',
        'HDFCBANK': 'HDFC Bank',
        'BHARTIARTL': 'Bharti Airtel',
        'ICICIBANK': 'ICICI Bank',
        'INFY': 'Infosys',
        'HINDUNILVR': 'Hindustan Unilever',
        'ITC': 'ITC Limited',
        'SBIN': 'State Bank of India',
        'LT': 'Larsen & Toubro',
        'KOTAKBANK': 'Kotak Mahindra Bank',
        'AXISBANK': 'Axis Bank',
        'BAJFINANCE': 'Bajaj Finance',
        'BAJAJFINSV': 'Bajaj Finserv',
        'HDFCLIFE': 'HDFC Life Insurance',
        'SBILIFE': 'SBI Life Insurance',
        'INDUSINDBK': 'IndusInd Bank',
        'SHRIRAMFIN': 'Shriram Finance',
        'JIOFINANCE': 'Jio Financial Services',
        'HCLTECH': 'HCL Technologies',
        'WIPRO': 'Wipro',
        'TECHM': 'Tech Mahindra',
        'MARUTI': 'Maruti Suzuki',
        'TATAMOTORS': 'Tata Motors',
        'M&M': 'Mahindra & Mahindra',
        'BAJAJ-AUTO': 'Bajaj Auto',
        'EICHERMOT': 'Eicher Motors',
        'HEROMOTOCO': 'Hero MotoCorp',
        'ONGC': 'Oil and Natural Gas Corporation',
        'NTPC': 'NTPC Limited',
        'POWERGRID': 'Power Grid Corporation',
        'COALINDIA': 'Coal India',
        'IOC': 'Indian Oil Corporation',
        'BPCL': 'Bharat Petroleum',
        'SUNPHARMA': 'Sun Pharmaceutical',
        'DRREDDY': 'Dr. Reddy\'s Laboratories',
        'CIPLA': 'Cipla',
        'APOLLOHOSP': 'Apollo Hospitals',
        'DIVISLAB': 'Divi\'s Laboratories',
        'NESTLEIND': 'Nestle India',
        'ASIANPAINT': 'Asian Paints',
        'TATACONSUMR': 'Tata Consumer Products',
        'BRITANNIA': 'Britannia Industries',
        'JSWSTEEL': 'JSW Steel',
        'TATASTEEL': 'Tata Steel',
        'HINDALCO': 'Hindalco Industries',
        'TITAN': 'Titan Company',
        'TRENT': 'Trent',
        'ULTRACEMCO': 'UltraTech Cement',
        'GRASIM': 'Grasim Industries',
        'BEL': 'Bharat Electronics',
        'ADANIENT': 'Adani Enterprises',
        'ADANIPORTS': 'Adani Ports',
        'ADANIGREEN': 'Adani Green Energy',
        'ADANIPOWER': 'Adani Power'
    }
    
    return company_names.get(stock_symbol.upper(), stock_symbol)



# Register portfolio API Blueprint
app.register_blueprint(portfolio_api)

@app.route('/api/ai-fundamental-analysis/<stock_symbol>', methods=['GET'])
def get_ai_fundamental_analysis(stock_symbol):
    """Get AI-powered fundamental analysis indicators for a stock"""
    try:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        financial_db_path = os.path.join(BASE_DIR, 'financial_reports', 'financial_data.db')
        conn = sqlite3.connect(financial_db_path)
        cursor = conn.cursor()
        # Normalize symbol: uppercase and strip .NS if present
        symbol = stock_symbol.upper().replace('.NS', '')
        cursor.execute('''
            SELECT * FROM ai_fundamental_analysis WHERE symbol = ?
        ''', (symbol,))
        row = cursor.fetchone()
        if not row:
            return jsonify({'error': 'No AI analysis found for this stock'}), 404

        columns = [desc[0] for desc in cursor.description]
        result = dict(zip(columns, row))
        conn.close()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    app.run(debug=debug, host=host, port=port)
