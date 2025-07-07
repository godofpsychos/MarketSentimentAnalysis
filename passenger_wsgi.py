#!/usr/bin/env python3
"""
Passenger WSGI file for cPanel deployment
This file is used by cPanel's Passenger application server
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set environment variables for cPanel
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('BASE_DIR', os.path.dirname(os.path.abspath(__file__)))

# Import the Flask app
from backend_api import app

# For Passenger
application = app

if __name__ == '__main__':
    app.run() 