#!/bin/bash
# Start Market Sentiment Analysis with Advanced Fundamental Analysis Visualizations
cd "$(dirname "$0")" || exit 1

echo "🚀 Setting up Market Sentiment Analysis with Advanced Visualizations..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Please create it first:"
    echo "python3 -m venv .venv"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install backend dependencies if needed
echo "📦 Checking backend dependencies..."
pip install -q flask flask-cors yfinance pandas requests > /dev/null 2>&1

# Create logs directory
mkdir -p LOGS_APP

# Check if backend is already running
if pgrep -f "backend_api.py" > /dev/null; then
    echo "⚠️  Backend API is already running. Stopping existing instance..."
    pkill -f "backend_api.py"
    sleep 2
fi

# Start the API server with fundamental analysis endpoints
echo "🌐 Starting enhanced API server with fundamental analysis..."
python3 backend_api.py > ./LOGS_APP/backend_api.log 2>&1 &
API_PID=$!
echo "✅ API server started with PID: $API_PID"

# Wait for the server to initialize
echo "⏳ Waiting for API server to initialize..."
sleep 5

# Test API connection
if curl -s http://localhost:5000/api/stocks > /dev/null; then
    echo "✅ API server is responding correctly"
else
    echo "❌ API server failed to start properly"
    cat ./LOGS_APP/backend_api.log
    exit 1
fi

# Install frontend dependencies and start development server
echo "🎨 Starting frontend with advanced visualizations..."
cd frontend

# Install new visualization dependencies if not already installed
echo "📦 Installing visualization dependencies..."
npm install --silent > ../LOGS_APP/npm_install.log 2>&1

# Start the React development server
echo "🚀 Starting React development server..."
npm start > ../LOGS_APP/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "✅ Frontend server started with PID: $FRONTEND_PID"

echo ""
echo "🎉 Market Sentiment Analysis with Advanced Visualizations is running!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 Backend API:        http://localhost:5000"
echo "🎨 Frontend Dashboard: http://localhost:3000"
echo ""
echo "📊 Features Available:"
echo "• 📈 Sentiment Analysis Dashboard"
echo "• 💎 Advanced Fundamental Analysis"
echo "• 🎯 Interactive Visualizations (Recharts + Chart.js)"
echo "• 📱 Responsive Design with Animations"
echo "• 🔄 Real-time Data Updates"
echo ""
echo "🎪 Visualization Types:"
echo "• Radar Charts (Multi-metric Analysis)"
echo "• Pie & Bar Charts (Comparisons)"
echo "• Line & Area Charts (Trends)"
echo "• Bubble Charts (Risk vs Return)"
echo "• Gauge Charts (Health Scores)"
echo ""
echo "📊 Analysis Categories:"
echo "• 💰 Profitability (ROE, ROA, Margins)"
echo "• 💎 Valuation (P/E, P/B, DCF)"
echo "• 📈 Growth (Revenue, Earnings)"
echo "• 💧 Liquidity (Current, Quick Ratios)"
echo "• ⚖️  Leverage (Debt Ratios)"
echo "• 🏆 Sector Comparisons"
echo ""
echo "📝 Log Files:"
echo "• API Logs:      ./LOGS_APP/backend_api.log"
echo "• Frontend Logs: ./LOGS_APP/frontend.log"
echo "• NPM Install:   ./LOGS_APP/npm_install.log"
echo ""
echo "⌨️  Press CTRL+C to stop all services"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Save PIDs to file for cleanup
echo "$API_PID $FRONTEND_PID" > ./LOGS_APP/service_pids

# Wait for user to press CTRL+C
function cleanup {
  echo ""
  echo "🛑 Stopping services..."
  kill $API_PID $FRONTEND_PID 2>/dev/null
  
  # Give processes time to shutdown gracefully
  sleep 2
  
  # Force kill if still running
  pkill -f "backend_api.py" 2>/dev/null
  pkill -f "npm start" 2>/dev/null
  
  rm -f ./LOGS_APP/service_pids
  echo "✅ All services stopped successfully."
  echo "👋 Thank you for using Market Sentiment Analysis!"
  exit 0
}

trap cleanup INT

# Keep script running and show status updates
while true; do
  sleep 10
  
  # Check if processes are still running
  if ! kill -0 $API_PID 2>/dev/null; then
    echo "❌ API server stopped unexpectedly. Check logs: ./LOGS_APP/backend_api.log"
    break
  fi
  
  if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    echo "❌ Frontend server stopped unexpectedly. Check logs: ./LOGS_APP/frontend.log"
    break
  fi
done

cleanup
