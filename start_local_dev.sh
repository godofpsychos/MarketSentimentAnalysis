#!/bin/bash

# Local Development Startup Script for YourStock.AI
# This script helps you start both frontend and backend for local development

echo "🚀 Starting YourStock.AI Local Development Environment"
echo "======================================================"

# Check if we're in the right directory
if [ ! -f "backend_api.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Error: Virtual environment not found. Please create one first:"
    echo "   python3 -m venv .venv"
    echo "   source .venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        return 0
    else
        return 1
    fi
}

# Function to start backend
start_backend() {
    echo "🔧 Starting Backend API..."
    
    # Activate virtual environment
    source .venv/bin/activate
    
    # Load local environment variables
    export $(cat backend.env.local | xargs)
    
    # Check if port 5000 is available
    if check_port 5000; then
        echo "⚠️  Port 5000 is already in use. Trying to kill existing process..."
        pkill -f "python.*backend_api.py" || true
        sleep 2
    fi
    
    # Start backend in background
    python backend_api.py &
    BACKEND_PID=$!
    
    echo "✅ Backend started with PID: $BACKEND_PID"
    echo "📊 Backend API: http://localhost:5000"
    
    # Wait a moment for backend to start
    sleep 3
    
    # Test if backend is running
    if curl -s http://localhost:5000/api/stocks > /dev/null; then
        echo "✅ Backend is responding correctly"
    else
        echo "❌ Backend might not be running properly"
    fi
}

# Function to start frontend
start_frontend() {
    echo "🎨 Starting Frontend..."
    
    cd frontend
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        echo "📦 Installing frontend dependencies..."
        npm install
    fi
    
    # Check if port 3000 is available
    if check_port 3000; then
        echo "⚠️  Port 3000 is already in use. Please close other React apps first."
        return 1
    fi
    
    # Start frontend in background
    npm start &
    FRONTEND_PID=$!
    
    echo "✅ Frontend started with PID: $FRONTEND_PID"
    echo "🌐 Frontend: http://localhost:3000"
    
    cd ..
}

# Main execution
echo "🔍 Checking prerequisites..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed"
    exit 1
fi

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed"
    exit 1
fi

# Check if npm is available
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed"
    exit 1
fi

echo "✅ All prerequisites found"

# Start services
start_backend
start_frontend

echo ""
echo "🎉 Development environment started successfully!"
echo "======================================================"
echo "🌐 Frontend Dashboard: http://localhost:3000"
echo "📊 Backend API:        http://localhost:5000"
echo "📋 API Documentation:  http://localhost:5000/api/stocks"
echo ""
echo "📝 Useful commands:"
echo "   - Test API: curl http://localhost:5000/api/stocks"
echo "   - Stop all: pkill -f 'python.*backend_api.py' && pkill -f 'react-scripts'"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user to stop
trap 'echo "🛑 Stopping services..."; pkill -f "python.*backend_api.py" || true; pkill -f "react-scripts" || true; exit 0' INT

# Keep script running
while true; do
    sleep 1
done 