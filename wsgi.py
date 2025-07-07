#!/usr/bin/env python3
"""
WSGI entry point for Market Sentiment Analysis API
This file is used by WSGI servers like Gunicorn or uWSGI
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the Flask app from backend_api
from backend_api import app

# For WSGI servers
application = app

if __name__ == "__main__":
    # For development
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    app.run(debug=debug, host=host, port=port) 