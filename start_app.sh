#!/bin/bash
# Start backend and frontend services
cd "$(dirname "$0")" || exit 1
mkdir -p LOGS_APP
echo "Starting Market Sentiment Analysis services..."
./run.sh > ./LOGS_APP/scrapper.log 2>&1 &
Scrapper_PID=$!
echo "Web scrapper service started with PID: $Scrapper_PID"
wait $Scrapper_PID

cd "$(dirname "$0")" || exit 1
# mkdir -p LOGS_APP
# Start the API server
echo "Starting API server..."
python3 backend_api.py > ./LOGS_APP/backend_api.log 2>&1 &
API_PID=$!
echo "API server started with PID: $API_PID"

# Wait a bit for the servers to initialize
sleep 3

# Start the React frontend
echo "Starting frontend development server..."
cd frontend && npm start > ../LOGS_APP/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend server started with PID: $FRONTEND_PID"

echo "Services are running!"
echo "- API: http://localhost:5000"
echo "- Frontend: http://localhost:3000"
echo ""
echo "Log files:"
echo "- Backend: backend.log"
echo "- API: backend_api.log"
echo "- Frontend: frontend.log"
echo ""
echo "Press CTRL+C to stop all services"

# Save PIDs to file for cleanup
echo "$BACKEND_PID $API_PID $FRONTEND_PID" > ./LOGS_APP/service_pids

# Wait for user to press CTRL+C
function cleanup {
  echo "Stopping services..."
  kill $BACKEND_PID $API_PID $FRONTEND_PID
  rm ./LOGS_APP/service_pids
  echo "Stopped."
  exit 0
}

trap cleanup INT
wait
