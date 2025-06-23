#!/bin/bash
# Start the scrapper service
cd "$(dirname "$0")" || exit 1
mkdir -p LOGS_APP
echo "Starting web scrapper service..."
python3 temp.py > ./LOGS_APP/output_scrapper.txt 2>&1 &
SCRAPPER_PID=$!
echo "Web scrapper service started with PID: $SCRAPPER_PID"
wait $SCRAPPER_PID

cd ./db || exit 1
# Start the database service
echo "Starting database service..."
python3 sqllitedb.py > ../LOGS_APP/newsDB.log 2>&1 &
DB_PID=$!
echo "Database service started with PID: $DB_PID"
wait $DB_PID

cd ../insightGen || exit 1
# Start the insight generation service
echo "Starting insight generation service..."
python3 genInsight.py > ../LOGS_APP/output_insight.txt 2>&1 &
INSIGHT_PID=$!
echo "Insight generation service started with PID: $INSIGHT_PID"
wait $INSIGHT_PID

cd ../Sentiment_Analysis || exit 1
# Start the sentiment analysis service
echo "Starting sentiment analysis service..."
python3 sentiment_analysis.py > ../LOGS_APP/output_sentiment.txt 2>&1 &
SENTIMENT_PID=$!
echo "Sentiment analysis service started with PID: $SENTIMENT_PID"
wait $SENTIMENT_PID 
python3 saveResults.py > ../LOGS_APP/output_save_results.txt 2>&1 &
SAVE_RESULTS_PID=$!
echo "Save results service started with PID: $SAVE_RESULTS_PID"
wait $SAVE_RESULTS_PID  

echo "All services ran successfully!"
echo "Log files:"
echo "- Scrapper: output_scrapper.txt"
echo "- Database: newsDB.log"
echo "- Insight Generation: output_insight.txt"
echo "- Sentiment Analysis: output_sentiment.txt"
echo "- Save Results: output_save_results.txt"  
