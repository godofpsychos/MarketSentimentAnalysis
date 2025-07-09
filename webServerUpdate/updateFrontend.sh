#!/bin/bash


cd /home/tarun/MarketSentimentAnalysis/frontend
rm -rf /home/tarun/MarketSentimentAnalysis/frontend/build
npm run build

# Remove only the specific files and directories that will be copied
ssh yz4vjeb32sbi@184.168.109.166 "rm -f /home/yz4vjeb32sbi/public_html/asset-manifest.json /home/yz4vjeb32sbi/public_html/index.html /home/yz4vjeb32sbi/public_html/favicon.ico /home/yz4vjeb32sbi/public_html/logo192.png /home/yz4vjeb32sbi/public_html/logo512.png /home/yz4vjeb32sbi/public_html/manifest.json /home/yz4vjeb32sbi/public_html/report.csv /home/yz4vjeb32sbi/public_html/robots.txt"
ssh yz4vjeb32sbi@184.168.109.166 "rm -rf /home/yz4vjeb32sbi/public_html/static"

# Copy the new build files to the server
scp -r /home/tarun/MarketSentimentAnalysis/frontend/build/* yz4vjeb32sbi@184.168.109.166:/home/yz4vjeb32sbi/public_html

# Copy the .htaccess file for proper routing
scp /home/tarun/MarketSentimentAnalysis/frontend/.htaccess yz4vjeb32sbi@184.168.109.166:/home/yz4vjeb32sbi/public_html/

# ssh yz4vjeb32sbi@184.168.109.166

