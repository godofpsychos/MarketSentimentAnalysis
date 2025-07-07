#!/bin/bash

# cPanel Deployment Preparation Script
echo "🚀 Preparing files for cPanel deployment..."

# Create deployment directory
mkdir -p backend-deploy
cd backend-deploy

# Copy essential Python files
echo "📁 Copying Python files..."
cp ../backend_api.py .
cp ../passenger_wsgi.py .
cp ../requirements-cpanel.txt requirements.txt
cp ../cpanel.env .env

# Copy data directories
echo "📊 Copying data directories..."
cp -r ../Sentiment_Analysis .
cp -r ../db .
cp -r ../FundamentalAnalysis .
cp -r ../insightGen .

# Copy data files
echo "📄 Copying data files..."
cp ../report.csv .
cp ../stocksList.csv .
cp ../news.json .

# Create logs directory
echo "📝 Creating logs directory..."
mkdir -p logs

# Set permissions
echo "🔐 Setting file permissions..."
chmod 755 passenger_wsgi.py
chmod 644 .env
chmod -R 755 logs/
chmod -R 755 db/
chmod -R 755 Sentiment_Analysis/

# Create deployment info
echo "📋 Creating deployment info..."
cat > DEPLOYMENT_INFO.txt << EOF
cPanel Deployment Package
========================

Created: $(date)
Files included:
- passenger_wsgi.py (Passenger WSGI file)
- backend_api.py (Main Flask application)
- requirements.txt (Python dependencies)
- .env (Environment configuration)
- Data directories and files

Next steps:
1. Upload this folder to your cPanel public_html/backend/
2. Configure Python app in cPanel
3. Install dependencies
4. Update .env with your domain settings
5. Test the endpoints

For detailed instructions, see CPANEL_DEPLOYMENT.md
EOF

echo "✅ Deployment package ready in 'backend-deploy' folder!"
echo "📦 Upload this folder to your cPanel public_html/backend/"
echo "📖 See CPANEL_DEPLOYMENT.md for detailed instructions" 