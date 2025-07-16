import sqlite3
import openai
import os
import json
import re

def extract_json_from_codeblock(text):
    """
    Extracts JSON from a Markdown code block (with or without 'json' tag).
    """
    if text is None:
        print("No text is passed")
        return None
    # Remove opening code block (with or without 'json')
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    # Remove closing code block
    text = re.sub(r"\s*```$", "", text)
    return text.strip()

def fix_missing_commas(json_str):
    """
    Attempts to fix missing commas between JSON fields.
    """
    # Add a comma between a closing quote or number and a quote starting a new key
    fixed = re.sub(r'([0-9"])(\s*)\n(\s*)"', r'\1,\n"', json_str)
    return fixed

# Set your OpenAI API key
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = openai.OpenAI(api_key=OPENAI_API_KEY)

DB_PATH = '/home/tarun/MarketSentimentAnalysis/financial_reports/financial_data.db'

# 1. Connect to the database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 2. Create the ai_fundamental_analysis table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS ai_fundamental_analysis (
    symbol TEXT PRIMARY KEY,
    profitability_score REAL,
    profitability_roe REAL,
    profitability_profit_margin REAL,
    profitability_summary TEXT,
    growth_score REAL,
    growth_revenue_growth REAL,
    growth_earnings_growth REAL,
    growth_summary TEXT,
    liquidity_score REAL,
    liquidity_current_ratio REAL,
    liquidity_summary TEXT,
    leverage_score REAL,
    leverage_debt_to_equity REAL,
    leverage_summary TEXT,
    valuation_score REAL,
    valuation_pe_ratio REAL,
    valuation_summary TEXT,
    overview_score REAL,
    overview_grade TEXT,
    overview_summary TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')
conn.commit()

# 3. Get all symbols from companies table
cursor.execute('SELECT DISTINCT symbol FROM companies')
symbols = [row[0] for row in cursor.fetchall()]

for symbol in symbols:
    # Get latest update time from source tables
    cursor.execute('''
        SELECT MAX(created_at) FROM (
            SELECT created_at FROM financial_health WHERE symbol = ?
            UNION ALL
            SELECT created_at FROM valuation_metrics WHERE symbol = ?
        )
    ''', (symbol, symbol))
    source_updated_at = cursor.fetchone()[0]

    # Get last analysis time from ai_fundamental_analysis
    cursor.execute('SELECT created_at FROM ai_fundamental_analysis WHERE symbol = ?', (symbol,))
    row = cursor.fetchone()
    if row:
        analysis_created_at = row[0]
        # Only skip if analysis is newer or same as source data
        if analysis_created_at and source_updated_at and analysis_created_at >= source_updated_at:
            print(f"Skipping {symbol}: analysis is up-to-date.")
            break

    # Fetch metrics from all relevant tables
    # Profitability
    cursor.execute('SELECT return_on_equity, profit_margin FROM financial_health WHERE symbol = ?', (symbol,))
    prof_row = cursor.fetchone() or (None, None)
    roe, profit_margin = prof_row

    # Growth
    cursor.execute('SELECT revenue_growth, earnings_growth FROM financial_health WHERE symbol = ?', (symbol,))
    growth_row = cursor.fetchone() or (None, None)
    revenue_growth, earnings_growth = growth_row

    # Liquidity
    cursor.execute('SELECT current_ratio FROM financial_health WHERE symbol = ?', (symbol,))
    liquidity_row = cursor.fetchone() or (None,)
    current_ratio = liquidity_row[0]

    # Leverage
    cursor.execute('SELECT debt_to_equity FROM financial_health WHERE symbol = ?', (symbol,))
    leverage_row = cursor.fetchone() or (None,)
    debt_to_equity = leverage_row[0]

    # Valuation
    cursor.execute('SELECT pe_ratio FROM valuation_metrics WHERE symbol = ?', (symbol,))
    valuation_row = cursor.fetchone() or (None,)
    pe_ratio = valuation_row[0]

    # Prepare metrics for AI
    metrics = {
        "roe": roe,
        "profit_margin": profit_margin,
        "revenue_growth": revenue_growth,
        "earnings_growth": earnings_growth,
        "current_ratio": current_ratio,
        "debt_to_equity": debt_to_equity,
        "pe_ratio": pe_ratio
    }
    print(symbol)
    print(metrics)
    # break
    # 4. Use OpenAI API to get indicator scores and summaries for each tab and overview
    prompt = f"""
    Given the following financial metrics for a company, generate the following for each tab:
    - Profitability Tab: Profitability Score (0-100), ROE, Profit Margin, and a one-sentence AI summary.
    - Growth Tab: Growth Score (0-100), Revenue Growth, Earnings Growth, and a one-sentence AI summary.
    - Liquidity Tab: Liquidity Score (0-100), Current Ratio, and a one-sentence AI summary.
    - Leverage Tab: Leverage Score (0-100), Debt to Equity, and a one-sentence AI summary.
    - Valuation Tab: Valuation Score (0-100), P/E Ratio, and a one-sentence AI summary.
    - Overview Tab: Composite Score (0-100), Health Grade (A+, A, B, etc.), and a one-sentence AI summary.
    Metrics: {json.dumps(metrics)}
    Respond with strict, valid JSON (no comments, no trailing commas, all fields comma-separated, no markdown or code block). Use these keys: profitability_score, profitability_roe, profitability_profit_margin, profitability_summary, growth_score, growth_revenue_growth, growth_earnings_growth, growth_summary, liquidity_score, liquidity_current_ratio, liquidity_summary, leverage_score, leverage_debt_to_equity, leverage_summary, valuation_score, valuation_pe_ratio, valuation_summary, overview_score, overview_grade, overview_summary.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful financial analysis assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.2
        )
        content = response.choices[0].message.content
        print(f"Raw OpenAI response for {symbol}:\n{content}\n---")
        # Save raw response for auditing
        with open("ai_raw_responses.log", "a") as f:
            f.write(f"{symbol}:\n{content}\n---\n")
        content = extract_json_from_codeblock(content)
        print(f"extract_json_from_codeblock function processed content {content}")
        if not content:
            print(f"OpenAI API returned no content for {symbol}")
            break
        try:
            ai_result = json.loads(content)
        except json.JSONDecodeError as e:
            print(f"Initial JSON parsing error: {e}")
            # Try to auto-fix missing commas
            fixed_content = fix_missing_commas(content)
            print(f"Trying to parse after auto-fix:\n{fixed_content}")
            ai_result = json.loads(fixed_content)
        print(f"Processed ai contents for symbol {symbol} : {content}")
        # Validate required keys
        required_keys = [
            "profitability_score", "growth_score", "liquidity_score", "leverage_score",
            "valuation_score", "overview_score", "overview_grade", "overview_summary"
        ]
        missing = [k for k in required_keys if k not in ai_result]
        if missing:
            print(f"Warning: Missing keys in AI result for {symbol}: {missing}")
    except Exception as e:
        print(f"OpenAI API error for {symbol}: {e}")
        break

    # 5. Insert or update the results in the ai_fundamental_analysis table
    cursor.execute('''
        INSERT OR REPLACE INTO ai_fundamental_analysis (
            symbol, profitability_score, profitability_roe, profitability_profit_margin, profitability_summary,
            growth_score, growth_revenue_growth, growth_earnings_growth, growth_summary,
            liquidity_score, liquidity_current_ratio, liquidity_summary,
            leverage_score, leverage_debt_to_equity, leverage_summary,
            valuation_score, valuation_pe_ratio, valuation_summary,
            overview_score, overview_grade, overview_summary
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        symbol,
        ai_result.get('profitability_score'),
        ai_result.get('profitability_roe'),
        ai_result.get('profitability_profit_margin'),
        ai_result.get('profitability_summary'),
        ai_result.get('growth_score'),
        ai_result.get('growth_revenue_growth'),
        ai_result.get('growth_earnings_growth'),
        ai_result.get('growth_summary'),
        ai_result.get('liquidity_score'),
        ai_result.get('liquidity_current_ratio'),
        ai_result.get('liquidity_summary'),
        ai_result.get('leverage_score'),
        ai_result.get('leverage_debt_to_equity'),
        ai_result.get('leverage_summary'),
        ai_result.get('valuation_score'),
        ai_result.get('valuation_pe_ratio'),
        ai_result.get('valuation_summary'),
        ai_result.get('overview_score'),
        ai_result.get('overview_grade'),
        ai_result.get('overview_summary')
    ))
    conn.commit()
    print(f"Stored AI fundamental analysis for {symbol}")
    # break

conn.close()
