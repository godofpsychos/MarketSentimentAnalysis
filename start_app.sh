#!/bin/bash
# Start backend and frontend services with all dependencies
cd "$(dirname "$0")" || exit 1

echo "Setting up Market Sentiment Analysis environment..."


# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install all backend dependencies
echo "Installing backend dependencies..."
pip install --upgrade pip

# Main requirements
pip install newscatcher feedsearch newspaper3k GoogleNews flask flask_cors requests

# Backend API requirements
pip install yfinance pandas numpy sqlite3

# Corporate announcements requirements
pip install bsescraper>=1.0.6 feedparser>=6.0.10 beautifulsoup4>=4.12.0 lxml>=4.9.0 python-dateutil>=2.8.0 pytz>=2023.3

# Financial reports requirements
pip install yfinance>=0.2.18 pandas>=2.0.0 numpy>=1.24.0 requests>=2.28.0

# Additional dependencies found in the project
pip install openai anyio

echo "All dependencies installed successfully!"

# Create logs directory
mkdir -p LOGS_APP

echo "Starting Market Sentiment Analysis services..."

# Start the scrapper service
./run.sh > ./LOGS_APP/scrapper.log 2>&1 &
Scrapper_PID=$!
echo "Web scrapper service started with PID: $Scrapper_PID"
wait $Scrapper_PID

# Start the API server
echo "Starting API server..."
python3 backend_api.py > ./LOGS_APP/backend_api.log 2>&1 &
API_PID=$!
echo "API server started with PID: $API_PID"

# Wait a bit for the servers to initialize
sleep 3

# Start the React frontend
echo "Starting frontend development server..."
cd frontend && npm install && npm start > ../LOGS_APP/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend server started with PID: $FRONTEND_PID"

echo "Services are running!"
echo "- API: http://localhost:5000"
echo "- Frontend: http://localhost:3000"
echo ""
echo "Log files:"
echo "- Scrapper: ./LOGS_APP/scrapper.log"
echo "- API: ./LOGS_APP/backend_api.log"
echo "- Frontend: ./LOGS_APP/frontend.log"
echo ""
echo "Press CTRL+C to stop all services"

# Save PIDs to file for cleanup
echo "$Scrapper_PID $API_PID $FRONTEND_PID" > ./LOGS_APP/service_pids

# Wait for user to press CTRL+C
function cleanup {
  echo "Stopping services..."
  kill $Scrapper_PID $API_PID $FRONTEND_PID 2>/dev/null
  rm -f ./LOGS_APP/service_pids
  echo "Services stopped."
  exit 0
}

trap cleanup INT
wait
