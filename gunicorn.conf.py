#!/usr/bin/env python3
"""
Gunicorn configuration file for Market Sentiment Analysis API
"""

import multiprocessing
import os

# Server socket
bind = os.getenv('GUNICORN_BIND', "0.0.0.0:5000")
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
preload_app = True

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "market-sentiment-api"

# Server mechanics
daemon = False
pidfile = "/tmp/market-sentiment-api.pid"
user = None
group = None
tmp_upload_dir = None

# SSL (uncomment and configure for HTTPS)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

# Environment variables
raw_env = [
    "FLASK_ENV=production",
]

# Timeout settings
timeout = 30
keepalive = 2
graceful_timeout = 30

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 50 