import sqlite3
from datetime import datetime, timedelta
import json
# Connect DB
conn = sqlite3.connect('/home/tarun/MarketSentimentAnalysis/db/stock_news.db')
cursor = conn.cursor()

# Get current datetime
now = datetime.now()  # Use timezone-aware datetime if needed

# Helper to get previous weekday
def previous_weekday(d, weekday):
    """Get previous weekday date from date d. Weekday: Monday=0, Sunday=6."""
    days_behind = (d.weekday() - weekday) % 7 or 7
    return d - timedelta(days=days_behind)

# Calculate time ranges
# 11:59 hrs is basically 11:59 AM, so cutoff at 12:00 PM
cutoff_time = now.replace(hour=12, minute=0, second=0, microsecond=0)
print("Time Now:",now)
print("Cutoff Time:",cutoff_time)
print("Now < Cutoff Time:",now < cutoff_time)
if now < cutoff_time:
    # Before 12 PM logic
    if now.weekday() == 0:  # Monday
        # Fetch news from last Friday 12:00 PM till now
        last_friday = previous_weekday(now.date(), 4)  # Friday = 4
        start_dt = datetime.combine(last_friday, datetime.min.time()).replace(hour=12)
        end_dt = now
    elif now.weekday() > 0:  # Tuesday
        # Fetch news from Monday 12:00 PM till now
        monday = previous_weekday(now.date(), now.weekday()-1)  # Monday=0
        start_dt = datetime.combine(monday, datetime.min.time()).replace(hour=12)
        end_dt = now
    else:
        # Default: fetch news from start of today 12:00 PM till now
        start_dt = now.replace(hour=12, minute=0, second=0, microsecond=0)
        end_dt = now
else:
    # After 12 PM logic
    # Fetch news from same day 9 hours before now till now
    start_dt = now - timedelta(hours=9)
    end_dt = now

# Convert to ISO string for querying SQLite
start_iso = start_dt.isoformat()
end_iso = end_dt.isoformat()

print(f"Fetching news from {start_iso} to {end_iso}")

# Query DB
query = """
SELECT * FROM news
WHERE datetime BETWEEN ? AND ?
ORDER BY datetime ASC
"""

cursor.execute(query, (start_iso, end_iso))
results = cursor.fetchall()
data = {}
for row in results:
    if row[1] not in data:
        data[row[1]] = {}
    data[row[1]][row[0]]= row[2]
    print(row)

conn.close()

with open('recent_news.json', 'w') as f:
    json.dump(data, f)