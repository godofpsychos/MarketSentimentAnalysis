# Cron Jobs Setup - Market Sentiment Analysis System

Your Market Sentiment Analysis system is now fully automated with systematic cron jobs running in the background!

## 🕐 Current Schedule

### **Weekdays (Monday-Friday)**

| Time | Job | Description |
|------|-----|-------------|
| **06:30 AM** | Corporate Scraper | Pre-market corporate actions check |
| **08:00 AM** | Main Analysis | Your existing market sentiment analysis |
| **09:30 AM** | Corporate Scraper | Post-market opening corporate actions |
| **12:05 PM** | Main Analysis | Your existing midday analysis |
| **06:00 PM** | Corporate Scraper | Post-market closing corporate actions |

### **Weekends**

| Time | Job | Description |
|------|-----|-------------|
| **Saturday 10:00 AM** | Corporate Scraper | Weekly corporate actions summary |
| **Sunday 02:00 AM** | System Cleanup | Remove old log files (30+ days) |
| **Sunday 02:30 AM** | Data Cleanup | Remove old JSON files (15+ days) |

## 📁 Files Created

### **Scripts**
- `cron_corporate_scraper.sh` - Dedicated cron script for corporate actions
- `crontab_config.txt` - Complete cron configuration
- `run_corporate_scraper.py` - Main corporate scraper (can also run manually)

### **Log Files** (in `LOGS_APP/` directory)
- `cron_corporate_scraper.log` - Main execution log
- `cron_corporate_scraper_error.log` - Error-specific log

### **Output Files** (in `corporate_announcements/` directory)
- `stock_corporate_actions_YYYYMMDD_HHMMSS.json` - Detailed results
- `stock_corporate_actions_summary_YYYYMMDD_HHMMSS.json` - Summary results

## 🔧 Management Commands

### **View Current Cron Jobs**
```bash
crontab -l
```

### **Edit Cron Jobs**
```bash
crontab -e
```

### **Apply New Configuration**
```bash
crontab crontab_config.txt
```

### **Check Cron Service Status**
```bash
systemctl is-active cron
systemctl status cron
```

### **View Recent Cron Logs**
```bash
# Corporate scraper logs
tail -50 LOGS_APP/cron_corporate_scraper.log

# System cron logs
sudo journalctl -u cron -f
```

## 📊 What Runs Automatically

### **Corporate Actions Scraper**
- ✅ Reads all 51 stocks from `stocksList.csv`
- ✅ Scrapes BSE and NSE for corporate actions
- ✅ Looks for: dividends, bonuses, splits, rights, buybacks, mergers, etc.
- ✅ Saves timestamped JSON results
- ✅ Comprehensive logging with error handling
- ✅ 30-minute timeout protection
- ✅ Automatic cleanup of old files

### **System Maintenance**
- ✅ Automatic log rotation (keeps 30 days)
- ✅ Automatic data cleanup (keeps 15 days of JSON files)
- ✅ Error logging and monitoring

## 🚨 Monitoring & Troubleshooting

### **Check if Jobs are Running**
```bash
# Check recent executions
grep "Corporate actions scraper completed" LOGS_APP/cron_corporate_scraper.log | tail -5

# Check for errors
tail -20 LOGS_APP/cron_corporate_scraper_error.log
```

### **Manual Test Run**
```bash
# Test the cron script manually
./cron_corporate_scraper.sh

# Or run the scraper directly
source .venv/bin/activate
python run_corporate_scraper.py
```

### **Common Issues & Solutions**

#### **Job Not Running**
1. Check if cron service is active: `systemctl is-active cron`
2. Verify crontab: `crontab -l`
3. Check system logs: `sudo journalctl -u cron -n 50`

#### **Script Errors**
1. Check error log: `cat LOGS_APP/cron_corporate_scraper_error.log`
2. Verify file permissions: `ls -la cron_corporate_scraper.sh`
3. Test virtual environment: `source .venv/bin/activate && python --version`

#### **No Output Files**
1. Check if script completed: `tail LOGS_APP/cron_corporate_scraper.log`
2. Verify directory permissions: `ls -la corporate_announcements/`
3. Run manual test: `./cron_corporate_scraper.sh`

## 📈 Benefits of This Setup

### **Automation**
- ✅ **No manual intervention needed** - Runs automatically
- ✅ **Multiple daily checks** - Catches corporate actions quickly
- ✅ **Weekend monitoring** - Weekly summaries
- ✅ **Self-maintaining** - Automatic cleanup

### **Reliability**
- ✅ **Error handling** - Graceful failure recovery
- ✅ **Timeout protection** - Prevents hanging processes
- ✅ **Comprehensive logging** - Easy troubleshooting
- ✅ **Virtual environment** - Isolated dependencies

### **Data Management**
- ✅ **Timestamped files** - No overwrites
- ✅ **Automatic cleanup** - Prevents disk space issues
- ✅ **Structured logging** - Easy monitoring
- ✅ **JSON output** - Easy integration

## 📅 Schedule Summary

**Total automated runs per week:**
- **Corporate Scraper**: 16 times (3x weekdays + 1x weekend)
- **Main Analysis**: 10 times (2x weekdays)
- **System Maintenance**: 2 times (Sunday cleanup)

Your system now runs **completely in the background** and will:
1. 🔄 Automatically scrape corporate actions multiple times daily
2. 📊 Continue your existing market sentiment analysis
3. 🧹 Keep itself clean and organized
4. 📝 Log everything for monitoring
5. ⚡ Handle errors gracefully

## 🎯 Next Steps

1. **Monitor for a few days** - Check logs to ensure everything works
2. **Adjust timing if needed** - Edit `crontab_config.txt` and reapply
3. **Set up alerts** (optional) - Email notifications for failures
4. **Review output files** - Verify data quality

Your Market Sentiment Analysis system is now **fully automated**! 🚀 