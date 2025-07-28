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
        "Please analyze the following news headlines and respond in JSON format with three fields: 'sentiment' (a number from 1 to 10, where 1 is very negative and 10 is very positive), 'impact_time_frame' (a short phrase, e.g., 'short-term', 'medium-term', 'long-term'), and 'signal_strength' (a number from 1 to 10 indicating how strong the signal is for affecting the market). Respond ONLY with the JSON object, nothing else. Example: {\"sentiment\": 7, \"impact_time_frame\": \"short-term\", \"signal_strength\": 8}\n\n"
        f"{text}"
    )
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": "You are a helpful sentiment analysis assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=100,
        )
        print(f"Response from OpenAI: {response.choices}")
        content = response.choices[0].message.content
        if content is not None:
            content = content.strip()
        else:
            print("OpenAI response content is None.")
            return {
                "sentiment": 5,
                "impact_time_frame": "unknown",
                "signal_strength": 5
            }
        try:
            result = json.loads(content)
            sentiment = float(result.get("sentiment", 5))
            impact_time_frame = result.get("impact_time_frame", "unknown")
            signal_strength = float(result.get("signal_strength", 5))
            sentiment = max(1, min(sentiment, 10))
            signal_strength = max(1, min(signal_strength, 10))
            return {
                "sentiment": sentiment,
                "impact_time_frame": impact_time_frame,
                "signal_strength": signal_strength
            }
        except Exception as parse_err:
            print(f"Error parsing response JSON: {parse_err}\nRaw content: {content}")
            return {
                "sentiment": 5,
                "impact_time_frame": "unknown",
                "signal_strength": 5
            }
    except Exception as e:
        print(f"Error analyzing sentiment: {e}")
        return {
            "sentiment": 5,
            "impact_time_frame": "unknown",
            "signal_strength": 5
        }

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
    result = analyze_sentiment(combined_text)
    analysis_score[company] = {timestamp: result}
    
# Save results
with open("sentiment_analysis_results.json", "w") as f:
    json.dump(analysis_score, f, indent=4)

print("\n✅ Sentiment analysis complete. Results saved to 'sentiment_analysis_results.json'.")
