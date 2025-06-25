#!/bin/bash
# Start backend API and frontend services with all dependencies
cd "$(dirname "$0")" || exit 1

echo "Setting up Market Sentiment Analysis UI environment..."

# Create virtual environment if it doesn't exist


# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install all backend dependencies

mkdir -p LOGS_APP

# Start the API server
echo "Starting API server..."
python3 backend_api.py > ./LOGS_APP/backend_api.log 2>&1 &
API_PID=$!
echo "API server started with PID: $API_PID"

# Wait a bit for the server to initialize
sleep 3

# Start the React frontend
echo "Starting frontend development server..."
cd frontend && npm install && npm start > ../LOGS_APP/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend server started with PID: $FRONTEND_PID"

echo "UI Services are running!"
echo "- API: http://localhost:5000"
echo "- Frontend: http://localhost:3000"
echo ""
echo "Log files:"
echo "- API: ./LOGS_APP/backend_api.log"
echo "- Frontend: ./LOGS_APP/frontend.log"
echo ""
echo "Press CTRL+C to stop all services"

# Save PIDs to file for cleanup
echo "$API_PID $FRONTEND_PID" > ./LOGS_APP/service_pids

# Wait for user to press CTRL+C
function cleanup {
  echo "Stopping services..."
  kill $API_PID $FRONTEND_PID 2>/dev/null
  rm -f ./LOGS_APP/service_pids
  echo "Services stopped."
  exit 0
}

trap cleanup INT
wait
