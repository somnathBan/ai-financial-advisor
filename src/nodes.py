# src/nodes.py
import yfinance as yf
import pandas as pd
import os
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI  # Stable bridge for OpenRouter
from state import AgentState

# 1. Load the vault
load_dotenv("../.env")

# 2. Get the OpenRouter key (Safe for Local and Streamlit Cloud)
api_key = os.getenv("OPENROUTER_API_KEY") or st.secrets.get("OPENROUTER_API_KEY")

# 3. Initialize the LLM via OpenRouter Bridge
# Using 'anthropic/claude-3.5-sonnet' for superior reasoning
llm = ChatOpenAI(
    model="openrouter/hunter-alpha",
    openai_api_key=api_key,
    base_url="https://openrouter.ai/api/v1",
    default_headers={
        "HTTP-Referer": "http://localhost:8501", 
        "X-Title": "AI Advisor App"
    }
)

# --- NODE 1: Data Ingestion ---
def ingestion_node(state: AgentState):
    print("--- 🤖 AGENT: Fetching Universe Data ---")
    universe = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "ITC.NS", "TATAMOTORS.NS"]
    results = []
    
    for ticker in universe:
        stock = yf.Ticker(ticker)
        info = stock.info
        results.append({
            "Symbol": ticker.replace(".NS", ""),
            "Price": info.get("currentPrice", 0),
            "PE": info.get("trailingPE", 100),
            "DE": info.get("debtToEquity", 100),
            "DivYield": info.get("dividendYield", 0) or 0
        })
    
    return {"universe_data": pd.DataFrame(results)}

# --- NODE 2: Strategy & Screening ---
def strategy_node(state: AgentState):
    print("--- 🤖 AGENT: Calculating Strategy ---")
    age = state["age"]
    risk = state["risk"]
    
    # Portfolio Allocation Logic
    equity_p = max(0, min(100, (120 - age) + (10 if risk == "Aggressive" else -20 if risk == "Conservative" else 0)))
    debt_p = 100 - equity_p
    
    # Quantitative Screening Logic
    df = state["universe_data"]
    if risk == "Conservative":
        recs = df[df['DE'] < 50].sort_values(by="DivYield", ascending=False)
    elif risk == "Moderate":
        recs = df[df['PE'] < 30]
    else:
        recs = df.sort_values(by="PE", ascending=False)
        
    return {
        "portfolio_split": {"equity": equity_p, "debt": debt_p},
        "recommendations_df": recs.head(3)
    }

# --- NODE 3: AI Reasoning ---
def reasoning_node(state: AgentState):
    print("--- 🧠 AGENT: Generating AI Reasoning ---")
    
    risk = state.get("risk")
    split = state.get("portfolio_split")
    stocks = state.get("recommendations_df").to_dict(orient="records")
    
    prompt = f"""
    You are a professional Financial Planner.
    Profile: {risk} risk appetite. 
    Strategy: {split['equity']}% Equity, {split['debt']}% Debt.
    Top Stock Picks Screened: {stocks}

    Task: In 3 clear, professional sentences, explain why this allocation is right for them. 
    Highlight why one of these stocks is a safe or growth-oriented choice based on its metrics.
    """
    # 1. Call the model
    response = llm.invoke(prompt)

    # 2. Extract the actual model name from OpenRouter's metadata
    # OpenRouter returns the specific model ID in the 'model_name' or 'system_fingerprint' field
    actual_model = response.response_metadata.get("model_name", "openrouter/auto:free")

    # 3. Return both the text and the model name
    return {
        "ai_reasoning": response.content,
        "actual_model_used": actual_model # <--- Add this new key
    }