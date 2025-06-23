#!/bin/bash

# Corporate Actions Scraper - Cron Job Script
# This script runs the corporate actions scraper with proper logging and error handling

# Set script directory
SCRIPT_DIR="/home/tarun/MarketSentimentAnalysis"
LOG_DIR="/home/tarun/MarketSentimentAnalysis/LOGS_APP"
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Log files
MAIN_LOG="$LOG_DIR/cron_corporate_scraper.log"
ERROR_LOG="$LOG_DIR/cron_corporate_scraper_error.log"

# Function to log with timestamp
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$MAIN_LOG"
}

# Function to log errors
log_error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" >> "$ERROR_LOG"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" >> "$MAIN_LOG"
}

# Start logging
log_message "=========================================="
log_message "Starting Corporate Actions Scraper (Cron)"
log_message "=========================================="

# Change to project directory
cd "$SCRIPT_DIR" || {
    log_error "Failed to change to project directory: $SCRIPT_DIR"
    exit 1
}

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    log_error "Virtual environment not found at $SCRIPT_DIR/.venv"
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate || {
    log_error "Failed to activate virtual environment"
    exit 1
}

log_message "Virtual environment activated successfully"

# Check if the scraper script exists
if [ ! -f "run_corporate_scraper.py" ]; then
    log_error "Corporate scraper script not found: run_corporate_scraper.py"
    exit 1
fi

# Run the corporate actions scraper
log_message "Running corporate actions scraper..."

# Run with timeout to prevent hanging (30 minutes max)
timeout 1800 python run_corporate_scraper.py >> "$MAIN_LOG" 2>> "$ERROR_LOG"
EXIT_CODE=$?

# Check exit status
if [ $EXIT_CODE -eq 0 ]; then
    log_message "Corporate actions scraper completed successfully"
elif [ $EXIT_CODE -eq 124 ]; then
    log_error "Corporate actions scraper timed out after 30 minutes"
else
    log_error "Corporate actions scraper failed with exit code: $EXIT_CODE"
fi

# Deactivate virtual environment
deactivate

# Log completion
log_message "Corporate actions scraper cron job finished"
log_message "=========================================="

# Clean up old log files (keep last 30 days)
find "$LOG_DIR" -name "cron_corporate_scraper*.log" -mtime +30 -delete 2>/dev/null

exit $EXIT_CODE 