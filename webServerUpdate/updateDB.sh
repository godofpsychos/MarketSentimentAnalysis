localBaseDirectory="/home/tarun/MarketSentimentAnalysis"
remoteBaseDirectory="/home/yz4vjeb32sbi/public_html/frontend"

# ./db/stock_news.db
# ./db/auth.db
# ./Sentiment_Analysis/sentiment_analysis.db
# ./financial_reports/financial_data.db

# scp -r $localBaseDirectory/* yz4vjeb32sbi@184.168.109.166:$remoteBaseDirectory
scp -r $localBaseDirectory/db/stock_news.db yz4vjeb32sbi@184.168.109.166:$remoteBaseDirectory/db/stock_news.db
scp -r $localBaseDirectory/db/auth.db yz4vjeb32sbi@184.168.109.166:$remoteBaseDirectory/db/auth.db
scp -r $localBaseDirectory/Sentiment_Analysis/sentiment_analysis.db yz4vjeb32sbi@184.168.109.166:$remoteBaseDirectory/Sentiment_Analysis/sentiment_analysis.db
scp -r $localBaseDirectory/financial_reports/financial_data.db yz4vjeb32sbi@184.168.109.166:$remoteBaseDirectory/financial_reports/financial_data.db
