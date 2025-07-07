#!/bin/bash

# Market Sentiment Analysis Backend Startup Script
# This script starts the backend API with Gunicorn WSGI server

echo "🚀 Starting Market Sentiment Analysis Backend API..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Please create one first:"
    echo "   python3 -m venv .venv"
    echo "   source .venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source .venv/bin/activate

# Check if required packages are installed
echo "🔍 Checking dependencies..."
if ! python -c "import gunicorn" 2>/dev/null; then
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Start the backend with Gunicorn
echo "🌐 Starting Gunicorn WSGI server..."
echo "   - Host: 0.0.0.0"
echo "   - Port: 5000"
echo "   - Workers: $(($(nproc) * 2 + 1))"
echo "   - Logs: logs/backend.log"

# Start Gunicorn with configuration
gunicorn \
    --config gunicorn.conf.py \
    --log-file logs/backend.log \
    --log-level info \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    wsgi:application

echo "✅ Backend API started successfully!"
echo "📊 API available at: http://localhost:5000"
echo "📋 API Documentation: http://localhost:5000/api/stocks" 