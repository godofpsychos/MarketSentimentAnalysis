# Market Sentiment Analysis Backend API

A production-ready Flask API with WSGI deployment for market sentiment analysis.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
# Activate virtual environment
source .venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 2. Start the Backend

#### Option A: Using the startup script (Recommended)
```bash
./start_backend.sh
```

#### Option B: Using Gunicorn directly
```bash
gunicorn --config gunicorn.conf.py wsgi:application
```

#### Option C: Development mode
```bash
python wsgi.py
```

## 📁 File Structure

```
├── backend_api.py          # Main Flask application
├── wsgi.py                 # WSGI entry point
├── gunicorn.conf.py        # Gunicorn configuration
├── start_backend.sh        # Startup script
├── backend.env             # Environment variables
├── requirements.txt        # Python dependencies
├── systemd/                # Systemd service files
│   └── market-sentiment-api.service
└── logs/                   # Log files (created automatically)
    ├── backend.log
    ├── access.log
    └── error.log
```

## ⚙️ Configuration

### Environment Variables
Copy `backend.env` to `.env` and modify as needed:
```bash
cp backend.env .env
```

### Gunicorn Configuration
Edit `gunicorn.conf.py` to customize:
- Number of workers
- Port and host
- Logging settings
- SSL certificates

## 🔧 Production Deployment

### 1. Systemd Service (Recommended)
```bash
# Copy service file
sudo cp systemd/market-sentiment-api.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable and start service
sudo systemctl enable market-sentiment-api
sudo systemctl start market-sentiment-api

# Check status
sudo systemctl status market-sentiment-api
```

### 2. Nginx Reverse Proxy (Optional)
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 📊 API Endpoints

### Core Endpoints
- `GET /api/stocks` - Get list of stocks
- `GET /api/sentiment` - Get sentiment data
- `GET /api/stock-data/<symbol>` - Get stock data
- `GET /api/fundamental-analysis/<symbol>` - Get fundamental analysis

### Authentication
- `POST /api/auth/signup` - User registration
- `POST /api/auth/signin` - User login
- `GET /api/auth/verify` - Verify token
- `POST /api/auth/logout` - User logout

### Sector Analysis
- `GET /api/sectoral-analysis` - Get sector data
- `GET /api/sector-analysis/<sector>` - Get specific sector

## 🔍 Monitoring

### Logs
- **Application logs**: `logs/backend.log`
- **Access logs**: `logs/access.log`
- **Error logs**: `logs/error.log`

### Health Check
```bash
curl http://localhost:5000/api/stocks
```

### Process Management
```bash
# Check if running
ps aux | grep gunicorn

# Restart service
sudo systemctl restart market-sentiment-api

# View logs
sudo journalctl -u market-sentiment-api -f
```

## 🛠️ Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   sudo lsof -i :5000
   sudo kill -9 <PID>
   ```

2. **Permission denied**
   ```bash
   chmod +x start_backend.sh
   chmod 755 logs/
   ```

3. **Virtual environment not found**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

### Performance Tuning

1. **Adjust workers** in `gunicorn.conf.py`:
   ```python
   workers = multiprocessing.cpu_count() * 2 + 1
   ```

2. **Memory optimization**:
   ```python
   max_requests = 1000
   max_requests_jitter = 50
   ```

## 🔒 Security

- Change JWT secret key in production
- Use HTTPS in production
- Configure firewall rules
- Regular security updates

## 📈 Scaling

- Use load balancer for multiple instances
- Database connection pooling
- Redis for caching
- CDN for static assets 