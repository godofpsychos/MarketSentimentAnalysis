from flask import Blueprint, request, jsonify
import sqlite3
import os
import csv

portfolio_api = Blueprint('portfolio_api', __name__)
DB_PATH = os.path.join(os.path.dirname(__file__), 'myportfolio.db')
STOCKS_LIST_PATH = os.path.join(os.path.dirname(__file__), '..', 'stocksList.csv')

def get_valid_stocks():
    """Get list of valid stock symbols from stocksList.csv"""
    valid_stocks = set()
    try:
        with open(STOCKS_LIST_PATH, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                valid_stocks.add(row['SYMBOL'].strip())
    except Exception as e:
        print(f"Error reading stocks list: {e}")
    return valid_stocks

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@portfolio_api.route('/api/portfolio', methods=['GET'])
def get_portfolio():
    email = request.args.get('email')
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    conn = get_db_connection()
    stocks = conn.execute('SELECT stock_symbol, stock_name, added_date FROM portfolio WHERE email = ?', (email,)).fetchall()
    conn.close()
    return jsonify({'portfolio': [dict(row) for row in stocks]})

@portfolio_api.route('/api/portfolio/add', methods=['POST'])
def add_to_portfolio():
    data = request.get_json()
    email = data.get('email')
    stock_symbol = data.get('stock_symbol')
    stock_name = data.get('stock_name')
    if not (email and stock_symbol and stock_name):
        return jsonify({'error': 'Missing data'}), 400
    
    # Validate that the stock symbol is in our allowed list
    valid_stocks = get_valid_stocks()
    if stock_symbol not in valid_stocks:
        return jsonify({'error': f'Stock {stock_symbol} is not in the allowed list of Indian stocks'}), 400
    
    conn = get_db_connection()
    try:
        conn.execute('INSERT OR IGNORE INTO portfolio (email, stock_symbol, stock_name) VALUES (?, ?, ?)', (email, stock_symbol, stock_name))
        conn.commit()
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500
    conn.close()
    return jsonify({'message': 'Stock added to portfolio'})

@portfolio_api.route('/api/portfolio/remove', methods=['POST'])
def remove_from_portfolio():
    data = request.get_json()
    email = data.get('email')
    stock_symbol = data.get('stock_symbol')
    if not (email and stock_symbol):
        return jsonify({'error': 'Missing data'}), 400
    conn = get_db_connection()
    conn.execute('DELETE FROM portfolio WHERE email = ? AND stock_symbol = ?', (email, stock_symbol))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Stock removed from portfolio'})
