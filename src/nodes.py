import os
import time
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import pytz
from mftool import Mftool
from state import AgentState
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# 1. Configuration
load_dotenv("../.env")
mf = Mftool()
api_key = os.getenv("OPENROUTER_API_KEY")

llm = ChatOpenAI(
    model="nvidia/nemotron-3-super-120b-a12b",
    openai_api_key=api_key,
    base_url="https://openrouter.ai/api/v1",
    default_headers={
        "HTTP-Referer": "http://localhost:8501", 
        "X-Title": "MF Alpha Architect"
    }
)

# --- UTILITIES: Math & Sync ---

def sync_all_funds():
    # Dynamic dates for deep history
    past_date = (datetime.now() - timedelta(days=15*365)).strftime("%d-%m-%Y")
    today_str = datetime.now().strftime("%d-%m-%Y")
    
    print(f"--- 🔄 10Y MEDIAN ROLLING SYNC (LIVE: {today_str}) ---")
    
    # 1. Benchmark: Nifty 50
    try:
        nifty = yf.download("^NSEI", period="15y", progress=False)['Close']
        nifty = nifty.sort_index(ascending=True)
        if isinstance(nifty, pd.DataFrame): nifty = nifty.iloc[:, 0]
        
        # Benchmark 10Y Rolling Median (2400 trading days)
        n_roll = (nifty / nifty.shift(2400))**(1/10) - 1
        bench_median = float(n_roll.median()) * 100
        print(f"📈 Nifty 50 10Y Median Rolling Benchmark: {bench_median:.2f}%")
    except Exception as e:
        print(f"❌ Benchmark Error: {e}")
        return

    all_schemes = mf.get_scheme_codes()
    results = []
    processed = 0

    print(f"🚀 Scanning {len(all_schemes)} schemes. This may take 10-15 mins...")

    for code, name in all_schemes.items():
        nl = name.lower()
        
        # Filter for Direct + Growth
        if "direct" in nl and "growth" in nl:
            try:
                # 2. Fetch Deep History as Dictionary (Positional Arguments)
                # Signature: (code, from_date, to_date)
                raw_data = mf.get_scheme_historical_nav(code, past_date, today_str)
                
                if not raw_data or 'data' not in raw_data or not raw_data['data']:
                    continue
                
                # 3. Manual Conversion to DataFrame
                df = pd.DataFrame(raw_data['data'])
                
                # Clean: Ensure NAV is numeric and Date is index
                df['nav'] = pd.to_numeric(df['nav'], errors='coerce')
                df['date'] = pd.to_datetime(df['date'], dayfirst=True)
                df = df.set_index('date').sort_index(ascending=True).dropna()

                # 4. Window Check (Using 2400 for 10Y consistency)
                window = 2400 
                if len(df) < window: 
                    continue 

                # 5. Median Rolling Math
                f_roll = (df['nav'] / df['nav'].shift(window))**(1/10) - 1
                fund_median = float(f_roll.median()) * 100

                # 6. Sanity Filter (Anti-Anomalies)
                is_liquid = any(x in nl for x in ["liquid", "overnight"])
                if is_liquid:
                    if fund_median < 4.5 or fund_median > 11.0: continue
                else:
                    if fund_median < 1.0 or fund_median > 45.0: continue

                alpha = fund_median - bench_median
                
                # 7. Categorization logic
                if any(x in nl for x in ["large cap", "bluechip"]): 
                    cat = "Equity"
                elif any(x in nl for x in ["bond", "debt", "gilt", "liquid"]): 
                    cat = "Debt"
                elif any(x in nl for x in ["hybrid", "balanced", "arbitrage"]): 
                    cat = "Hybrid"
                else: 
                    cat = "Other"

                results.append({
                    "Scheme": str(name),
                    "Category": cat,
                    "Alpha": float(round(alpha, 2)),
                    "10Y_Rolling_Median": float(round(fund_median, 2)),
                    "Last_Updated": today_str
                })
                
                processed += 1
                if processed % 20 == 0:
                    print(f"✅ [{processed}] Added: {name[:40]}... (Median: {fund_median:.2f}%)")
                
                # Small sleep to be polite to the AMFI server
                time.sleep(0.05)
                
            except Exception:
                continue

    # 8. Final Save
    if results:
        final_df = pd.DataFrame(results)
        final_df.to_parquet("all_mf_database.parquet")
        print(f"--- ✅ SUCCESS: {len(final_df)} Clean Funds Saved ---")
    else:
        print("❌ CRITICAL: No funds passed the filters. Check window size or category filters.")

def should_trigger_sync(db_path):
    IST = pytz.timezone('Asia/Kolkata')
    now_ist = datetime.now(IST)
    if not os.path.exists(db_path): return True
    if (time.time() - os.path.getmtime(db_path)) > 86400: return True
    last_mod_ist = datetime.fromtimestamp(os.path.getmtime(db_path), IST)
    if now_ist.hour >= 23:
        if last_mod_ist.date() < now_ist.date() or last_mod_ist.hour < 23:
            return True
    return False

# --- NODE 1: Analysis & Filtering ---

def mf_analysis_node(state: AgentState):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, "all_mf_database.parquet")
    df = pd.read_parquet(db_path)

    # 1. Grab the Top 50 funds based on 10Y Alpha
    # This gives the LLM the 'Best of the Best' across all categories
    top_50 = df.sort_values('Alpha', ascending=False).head(500)

    # 2. Keep your Allocation Logic (The "Constraints")
    age = state.get("age", 30)
    risk = state.get("risk", "Moderate")
    base_equity = 120 - age
    adj = 10 if risk == "Aggressive" else -20 if risk == "Conservative" else 0
    equity_p = max(0, min(100, base_equity + adj))

    return {
        "top_mf_recommendations": top_50,
        "portfolio_split": {"equity": equity_p, "debt": 100 - equity_p}
    }

# --- NODE 2: Strategic Reasoning ---

def reasoning_node(state: AgentState):
    print("--- 🧠 AGENT: Generating Strategic SIP Memo ---")
    
    # Format the data cleanly for the LLM
    funds_context = state['top_mf_recommendations'][['Scheme', 'Category', 'Alpha', '10Y_Rolling_Median']].to_dict(orient='records')

    prompt = f"""
    You are an elite Investment Strategist.
    User Profile: Age {state['age']}, {state['risk']} risk profile. 
    Investment: SIP of ₹{state['amount']}.
    Target Allocation: {state['portfolio_split']['equity']}% Equity / {state['portfolio_split']['debt']}% Debt & Hybrid.

    THE UNIVERSE (Top 50 Funds in India):
    {funds_context}

    INSTRUCTIONS:
    1. From the 50 funds provided, select the 5-6 best-suited funds for this specific user.
    2. Categorize your selection: Ensure you meet the target {state['portfolio_split']['equity']}/{state['portfolio_split']['debt']} split.
    3. Be specific: If the user is {state['age']} and {state['risk']}, explain why you chose more 'Debt' or more 'Large Cap'.
    4. Output a Markdown Table: | Fund Name | Category | SIP Amount (₹) | 10Y Rolling Median | Rationale |
    5. The 'SIP Amount' total must equal exactly ₹{state['amount']}.
    """
    
    res = llm.invoke(prompt)
    return {
        "ai_reasoning": res.content,
        "actual_model_used": res.response_metadata.get("model_name", "Hunter-Alpha")
    }