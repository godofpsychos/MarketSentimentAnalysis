import sqlite3
from datetime import datetime
import json

with open('/home/tarun/MarketSentimentAnalysis/Sentiment_Analysis/sentiment_analysis_results.json', 'r') as f:
    data = json.load(f)


# Connect to SQLite database (or create it)
conn = sqlite3.connect('sentiment_analysis.db')
cursor = conn.cursor()

# Drop table if exists (optional, for fresh start)
# cursor.execute('DROP TABLE IF EXISTS news')

# Create table with composite primary key (datetime, stock)
cursor.execute('''
CREATE TABLE IF NOT EXISTS sentimentResult (
    datetime TEXT,
    stock TEXT,
    marketSentiment float,
    PRIMARY KEY (stock,datetime)
)
''')

# Prepare data for insertion
for stock, value in data.items():
    rows = []
    for key, val in value.items():
        dt_iso = datetime.fromisoformat(key).isoformat()
        row = (dt_iso, stock, val)
        try:
            cursor.execute('INSERT INTO sentimentResult (datetime, stock, marketSentiment) VALUES (?, ?, ?)', (row))
            conn.commit()
        except sqlite3.IntegrityError as e:
            print("Integrity error:", e)
        rows.append(row)    
# Insert data (if duplicate primary key, will raise error)
# try:
#     cursor.executemany('INSERT INTO news (datetime, stock, description, source_link) VALUES (?, ?, ?, ?)', rows)
#     conn.commit()
# except sqlite3.IntegrityError as e:
    # print("Integrity error:", e)
# print(rows)
# print('-'*100)
# Query to check data
cursor.execute('SELECT * FROM sentimentResult ORDER BY datetime DESC ')
values = cursor.fetchall()
for row in values:
    print(row)

conn.close()

