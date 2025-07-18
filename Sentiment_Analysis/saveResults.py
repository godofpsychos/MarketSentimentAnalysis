import sqlite3
from datetime import datetime
import json
import os

with open('/home/tarun/MarketSentimentAnalysis/Sentiment_Analysis/sentiment_analysis_results.json', 'r') as f:
    data = json.load(f)

# Connect to SQLite database (or create it)
conn = sqlite3.connect('sentiment_analysis.db')
cursor = conn.cursor()

# Check if the new columns exist, and add them if not
# (SQLite doesn't support IF NOT EXISTS for ALTER TABLE ADD COLUMN, so we check pragma)
def column_exists(cursor, table, column):
    cursor.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cursor.fetchall())

# Create table with new schema if not exists
cursor.execute('''
CREATE TABLE IF NOT EXISTS sentimentResult (
    datetime TEXT,
    stock TEXT,
    sentiment FLOAT,
    impact_time_frame TEXT,
    signal_strength FLOAT,
    PRIMARY KEY (stock,datetime)
)
''')

# Add new columns if they don't exist (for existing DBs)
if not column_exists(cursor, 'sentimentResult', 'sentiment'):
    cursor.execute('ALTER TABLE sentimentResult ADD COLUMN sentiment FLOAT')
if not column_exists(cursor, 'sentimentResult', 'impact_time_frame'):
    cursor.execute('ALTER TABLE sentimentResult ADD COLUMN impact_time_frame TEXT')
if not column_exists(cursor, 'sentimentResult', 'signal_strength'):
    cursor.execute('ALTER TABLE sentimentResult ADD COLUMN signal_strength FLOAT')

# Prepare data for insertion
for stock, value in data.items():
    for key, val in value.items():
        dt_iso = datetime.fromisoformat(key).isoformat()
        sentiment = val.get('sentiment', 'na')
        impact_time_frame = val.get('impact_time_frame', 'na')
        signal_strength = val.get('signal_strength', 'na')
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO sentimentResult (datetime, stock, sentiment, impact_time_frame, signal_strength)
                VALUES (?, ?, ?, ?, ?)
            ''', (dt_iso, stock, sentiment, impact_time_frame, signal_strength))
            conn.commit()
        except sqlite3.IntegrityError as e:
            print("Integrity error:", e)

# Query to check data
cursor.execute('SELECT * FROM sentimentResult ORDER BY datetime DESC ')
values = cursor.fetchall()
for row in values:
    print(row)

conn.close()

