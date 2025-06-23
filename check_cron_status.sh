#!/bin/bash

# Cron Status Check Script for Market Sentiment Analysis
# This script provides a quick overview of your automated jobs

echo "🚀 Market Sentiment Analysis - Cron Status Check"
echo "================================================="

# Check cron service
echo "📋 Cron Service Status:"
if systemctl is-active --quiet cron; then
    echo "   ✅ Cron service is ACTIVE"
else
    echo "   ❌ Cron service is INACTIVE"
fi

echo ""

# Show active cron jobs
echo "⏰ Active Cron Jobs:"
crontab -l | grep -v "^#" | grep -v "^$" | while read line; do
    echo "   📅 $line"
done

echo ""

# Check recent corporate scraper runs
echo "📊 Recent Corporate Scraper Activity:"
if [ -f "LOGS_APP/cron_corporate_scraper.log" ]; then
    echo "   📝 Last 3 successful runs:"
    grep "Corporate actions scraper completed successfully" LOGS_APP/cron_corporate_scraper.log | tail -3 | while read line; do
        echo "      ✅ $line"
    done
    
    echo ""
    echo "   📈 Latest run summary:"
    tail -10 LOGS_APP/cron_corporate_scraper.log | grep -E "(Total stocks processed|Total announcements found)" | while read line; do
        echo "      📊 $line"
    done
else
    echo "   ⚠️  No corporate scraper logs found yet"
fi

echo ""

# Check for recent errors
echo "🚨 Recent Errors:"
if [ -f "LOGS_APP/cron_corporate_scraper_error.log" ] && [ -s "LOGS_APP/cron_corporate_scraper_error.log" ]; then
    echo "   ❌ Recent errors found:"
    tail -5 LOGS_APP/cron_corporate_scraper_error.log | while read line; do
        echo "      🔴 $line"
    done
else
    echo "   ✅ No recent errors found"
fi

echo ""

# Check output files
echo "📁 Recent Output Files:"
if ls corporate_announcements/stock_corporate_actions_*.json 1> /dev/null 2>&1; then
    echo "   📄 Latest files:"
    ls -lt corporate_announcements/stock_corporate_actions_*.json | head -3 | while read line; do
        echo "      📋 $line"
    done
else
    echo "   ⚠️  No output files found yet"
fi

echo ""

# System resources
echo "💾 System Resources:"
echo "   🖥️  Disk usage: $(df -h . | tail -1 | awk '{print $5}') used"
echo "   📊 Log directory size: $(du -sh LOGS_APP/ 2>/dev/null | cut -f1)"
echo "   📁 Corporate data size: $(du -sh corporate_announcements/ 2>/dev/null | cut -f1)"

echo ""
echo "================================================="
echo "✅ Status check completed!"
echo "💡 For detailed logs: tail -50 LOGS_APP/cron_corporate_scraper.log"
echo "🔧 To edit cron jobs: crontab -e"
echo "📖 Full documentation: see CRON_SETUP_GUIDE.md" 