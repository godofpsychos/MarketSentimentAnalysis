#!/bin/bash

# Update the main .htaccess file on the server
echo "Updating main .htaccess file on server..."

# Copy the updated .htaccess file to the server root
scp /home/tarun/MarketSentimentAnalysis/.htaccess yz4vjeb32sbi@184.168.109.166:/home/yz4vjeb32sbi/public_html/
scp /home/tarun/MarketSentimentAnalysis/.htaccess yz4vjeb32sbi@184.168.109.166:/home/yz4vjeb32sbi/

echo "Main .htaccess file updated successfully!" 