import json
import os
import datetime
import openai
# from dotenv import load_dotenv
# # Initialize OpenAI client with API key
# load_dotenv()  # Load environment variables from .env file
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_sentiment(text):
    prompt = (
        "Please rate the overall sentiment of the following news headlines based on their significance "
        "and impact on a scale from 1 (very negative) to 10 (very positive), and respond only with the number:\n\n"
        f"{text}"
    )
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful sentiment analysis assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=5,
        )
        print(f"Response from OpenAI: {response.choices}")
        sentiment_str = response.choices[0].message.content.strip()
        score = float(sentiment_str)
        return max(1, min(score, 10))  # Clamp score between 1 and 10
    except Exception as e:
        print(f"Error analyzing sentiment: {e}")
        return 5  # Neutral fallback

# Load news data
filepath = "/home/tarun/MarketSentimentAnalysis/insightGen/recent_news.json"
with open(filepath, "r") as f:
    news_data = json.load(f)

# Analyze and store sentiment scores
analysis_score = {}
timestamp = datetime.datetime.now().isoformat()

for company, news_dict in news_data.items():
    print(f"\nAnalyzing sentiment for company: {company}")
    headlines = list(news_dict.values())
    if not headlines:
        print("  No headlines found for this company.")
        continue
    combined_text = f"News Headlines for stock {company}:\n" + "\n".join(headlines)
    score = analyze_sentiment(combined_text)
    analysis_score[company] = {timestamp: score}

# Save results
with open("sentiment_analysis_results.json", "w") as f:
    json.dump(analysis_score, f, indent=4)

print("\n✅ Sentiment analysis complete. Results saved to 'sentiment_analysis_results.json'.")
