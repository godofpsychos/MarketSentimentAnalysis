#!/bin/bash

localBaseDirectory="/home/tarun/MarketSentimentAnalysis"
remoteBaseDirectory="/home/yz4vjeb32sbi/public_html/frontend"

echo "🚀 Updating Portfolio System on Production Server..."

# Portfolio database and API files
echo "📁 Uploading portfolio database..."
scp -r $localBaseDirectory/db/myportfolio.db yz4vjeb32sbi@184.168.109.166:$remoteBaseDirectory/db/myportfolio.db

echo "📁 Uploading portfolio API..."
scp -r $localBaseDirectory/db/portfolio_api.py yz4vjeb32sbi@184.168.109.166:$remoteBaseDirectory/db/portfolio_api.py

# Updated main backend with portfolio integration
echo "📁 Uploading updated backend..."
scp -r $localBaseDirectory/backend_api.py yz4vjeb32sbi@184.168.109.166:$remoteBaseDirectory/backend_api.py

# # Frontend Dashboard components
# echo "📁 Uploading Dashboard component..."
# scp -r $localBaseDirectory/frontend/src/components/Dashboard/Dashboard.js yz4vjeb32sbi@184.168.109.166:$remoteBaseDirectory/frontend/src/components/Dashboard/Dashboard.js

# echo "📁 Uploading Dashboard CSS..."
# scp -r $localBaseDirectory/frontend/src/components/Dashboard/Dashboard.css yz4vjeb32sbi@184.168.109.166:$remoteBaseDirectory/frontend/src/components/Dashboard/Dashboard.css

# # Updated config (if needed)
# echo "📁 Uploading config..."
# scp -r $localBaseDirectory/frontend/src/config/config.js yz4vjeb32sbi@184.168.109.166:$remoteBaseDirectory/frontend/src/config/config.js

echo "✅ Portfolio system update completed!"
echo "🔧 Remember to restart your backend server on production" 