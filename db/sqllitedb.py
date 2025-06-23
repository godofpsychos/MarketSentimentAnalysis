import sqlite3
from datetime import datetime
import json

with open('/home/tarun/MarketSentimentAnalysis/news.json', 'r') as f:
    data = json.load(f)


# Connect to SQLite database (or create it)
conn = sqlite3.connect('stock_news.db')
cursor = conn.cursor()

# Drop table if exists (optional, for fresh start)
# cursor.execute('DROP TABLE IF EXISTS news')

# Create table with composite primary key (datetime, stock)
cursor.execute('''
CREATE TABLE IF NOT EXISTS news (
    datetime TEXT,
    stock TEXT,
    description TEXT,
    source_link TEXT,
    PRIMARY KEY (stock,datetime)
)
''')

# Prepare data for insertion
for stock, articles in data.items():
    rows = []
    for article in articles:
        dt_obj = datetime.strptime(article["published date"], '%a, %d %b %Y %H:%M:%S %Z')
        dt_iso = dt_obj.isoformat()
        row = (dt_iso,stock,article["description"],article["url"] )
        # rows.append(row)
        try:
            cursor.execute('INSERT INTO news (datetime, stock, description, source_link) VALUES (?, ?, ?, ?)', row)
            conn.commit()
        except sqlite3.IntegrityError as e:
            print("Integrity error:", e)
# Insert data (if duplicate primary key, will raise error)
# try:
#     cursor.executemany('INSERT INTO news (datetime, stock, description, source_link) VALUES (?, ?, ?, ?)', rows)
#     conn.commit()
# except sqlite3.IntegrityError as e:
    # print("Integrity error:", e)
# print(rows)
# print('-'*100)
# Query to check data
cursor.execute('SELECT * FROM news ORDER BY datetime DESC ')
values = cursor.fetchall()
for row in values:
    print(row)

conn.close()

