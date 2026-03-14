import streamlit as st
import yfinance as yf
import pandas as pd

# --- 1. INITIALIZATION ---
if 'age' not in st.session_state:
    st.session_state.age = 30

def update_num():
    st.session_state.age_num = st.session_state.age_slider
    st.session_state.age = st.session_state.age_slider

def update_slider():
    st.session_state.age_slider = st.session_state.age_num
    st.session_state.age = st.session_state.age_num

# --- 2. AGENT 1: Data Ingestion Agent ---
@st.cache_data(ttl=3600) # Cache for 1 hour to prevent API throttling
def get_stock_data(risk):
    # Map risk to specific high-quality tickers
    mapping = {
        "Conservative": ["ITC.NS", "HDFCBANK.NS", "RELIANCE.NS"],
        "Moderate": ["INFY.NS", "ICICIBANK.NS", "TITAN.NS"],
        "Aggressive": ["TATAMOTORS.NS", "ZOMATO.NS", "ADANIENT.NS"]
    }
    
    selected_tickers = mapping.get(risk, ["^NSEI"])
    results = []
    
    for ticker in selected_tickers:
        stock = yf.Ticker(ticker)
        # Fetching a mix of Price and Fundamental data
        info = stock.info
        results.append({
            "Symbol": ticker.replace(".NS", ""),
            "Price": info.get("currentPrice", 0),
            "P/E Ratio": info.get("trailingPE", "N/A"),
            "Div. Yield (%)": f"{info.get('dividendYield', 0) * 100:.2f}%" if info.get('dividendYield') else "0.00%",
            "Recommendation": info.get("recommendationKey", "N/A").title()
        })
    
    return pd.DataFrame(results)

# --- 3. AGENT 4: Investment Logic ---
def run_investment_logic(age, risk, amount):
    equity_p = max(0, min(100, (120 - age) + (10 if risk == "Aggressive" else -20 if risk == "Conservative" else 0)))
    debt_p = 100 - equity_p
    return equity_p, debt_p, (equity_p / 100) * amount, (debt_p / 100) * amount

# --- 4. UI SETUP ---
st.set_page_config(page_title="AI Advisor MVP", layout="wide")
st.title("🛡️ AI Financial Advisor: Phase 2")

# Sidebar
st.sidebar.header("User Profile")
with st.sidebar.container():
    st.write("**Enter your age**")
    st.number_input("Age Num", 18, 100, step=1, key="age_num", on_change=update_slider, label_visibility="collapsed")
    st.slider("Age Slider", 18, 100, key="age_slider", on_change=update_num, label_visibility="collapsed")

user_risk = st.sidebar.selectbox("Risk Appetite", ["Conservative", "Moderate", "Aggressive"])
user_amount = st.sidebar.number_input("Investment Amount (₹)", min_value=1000, value=50000, step=1000)

# --- 5. EXECUTION ---
e_p, d_p, e_v, d_v = run_investment_logic(st.session_state.age, user_risk, user_amount)

# Fetch Data via Ingestion Agent
with st.spinner(f"Agent fetching {user_risk} assets..."):
    df_market = get_stock_data(user_risk)

# --- 6. DISPLAY ---
col_left, col_right = st.columns([1, 1.5])

with col_left:
    st.subheader("🎯 Portfolio Allocation")
    st.metric("Equity Value", f"₹{e_v:,.0f}", f"{e_p}% Share")
    st.metric("Debt Value", f"₹{d_v:,.0f}", f"{d_p}% Share")
    st.progress(e_p / 100)
    st.caption(f"Strategy: {user_risk} allocation based on Age {st.session_state.age}")

with col_right:
    st.subheader(f"📊 Market Intelligence for {user_risk} Profile")
    # Display the Ingestion Agent's output as a clean table
    st.table(df_market)
    st.info("💡 Pro Tip: The 'Recommendation' column is pulled directly from analyst consensus data via yfinance.")