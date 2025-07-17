#!/bin/bash

# Check all main backend API endpoints used by the frontend
# Requires: jq (install with sudo apt install jq)

BASE_URL="https://yourstock.ai/v1/api"
STOCK="AXISBANK"
EMAIL="example@email.com"

# 1. Stocks list
echo "\n==== /api/stocks ===="
curl -s "$BASE_URL/stocks" | jq

# 2. Sentiment
echo "\n==== /api/sentiment ===="
curl -s "$BASE_URL/sentiment" | jq

# 3. Fundamental Analysis
echo "\n==== /api/fundamental-analysis/$STOCK ===="
curl -s "$BASE_URL/fundamental-analysis/$STOCK" | jq

# 4. AI Fundamental Analysis
echo "\n==== /api/ai-fundamental-analysis/$STOCK ===="
curl -s "$BASE_URL/ai-fundamental-analysis/$STOCK" | jq

# 5. Fundamental Scores
echo "\n==== /api/fundamental-scores/$STOCK ===="
curl -s "$BASE_URL/fundamental-scores/$STOCK" | jq

# 6. Stock Info
echo "\n==== /api/stock-info/$STOCK ===="
curl -s "$BASE_URL/stock-info/$STOCK" | jq

# 7. Financial Data
echo "\n==== /api/financial-data ===="
curl -s "$BASE_URL/financial-data" | jq

# 8. Stock Data (price history)
echo "\n==== /api/stock-data/$STOCK?period=1mo ===="
curl -s "$BASE_URL/stock-data/$STOCK?period=1mo" | jq

# 9. News
echo "\n==== /api/stock-news/$STOCK?page=1&per_page=5 ===="
curl -s "$BASE_URL/stock-news/$STOCK?page=1&per_page=5" | jq

# 10. Sectoral Analysis
echo "\n==== /api/sectoral-analysis ===="
curl -s "$BASE_URL/sectoral-analysis" | jq

# 11. Portfolio (GET)
echo "\n==== /api/portfolio?email=... ===="
curl -s "$BASE_URL/portfolio?email=$EMAIL" | jq 