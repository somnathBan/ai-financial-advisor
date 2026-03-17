import streamlit as st
import pandas as pd
import pytz
from datetime import datetime, timedelta
import os
from graph import app_brain  # The Orchestrator

# --- 1. INITIALIZATION & SESSION STATE ---
if 'age' not in st.session_state:
    st.session_state.age = 30
if 'age_num' not in st.session_state:
    st.session_state.age_num = 30
if 'age_slider' not in st.session_state:
    st.session_state.age_slider = 30

def update_num():
    st.session_state.age = st.session_state.age_slider
    st.session_state.age_num = st.session_state.age_slider
def update_slider():
    st.session_state.age = st.session_state.age_num
    st.session_state.age_slider = st.session_state.age_num

# --- 2. UI SETUP ---
st.set_page_config(page_title="MF Alpha Architect", layout="wide")

# PREMIUM INVESTMENT CSS + MOBILE OPTIMIZATIONS
st.markdown("""
    <style>
    /* Global Styles */
    .stApp { background-color: #0E1117; color: #E0E0E0; }
    [data-testid="stSidebar"] { background-color: #050505; border-right: 1px solid #1E1E1E; }
    
    /* Allocation Bar Styling */
    .allocation-container {
        display: flex;
        height: 40px;
        width: 100%;
        border-radius: 8px;
        overflow: hidden;
        margin: 20px 0;
        border: 1px solid #30363D;
    }
    .equity-bar { background-color: #04B488; height: 100%; display: flex; align-items: center; justify-content: center; color: black; font-weight: bold; font-size: 0.9rem; }
    .debt-bar { background-color: #FFA000; height: 100%; display: flex; align-items: center; justify-content: center; color: black; font-weight: bold; font-size: 0.9rem; }

    .stMetric {
        background-color: #161B22 !important;
        border: 1px solid #30363D !important;
        border-radius: 12px !important;
        padding: 15px !important;
    }
    
    div[data-testid="stVerticalBlock"] > div[style*="border"] {
        background-color: #161B22 !important;
        border: 1px solid #30363D !important;
        border-radius: 12px !important;
        padding: 20px !important;
        color: white !important;
    }

    .stDataFrame { border: 1px solid #30363D !important; border-radius: 8px !important; }
    h1, h2, h3 { color: #FFFFFF !important; font-weight: 700; }
    .stButton>button { background-color: #04B488 !important; color: white !important; width: 100%; border-radius: 6px; font-weight: 600; }
    .stSpinner > div > div { border-top-color: #04B488 !important; }

    /* --- MOBILE RESPONSIVENESS FIXES --- */
    @media (max-width: 640px) {
        /* Reduce header sizes on mobile */
        h1 { font-size: 1.8rem !important; }
        .stMarkdown p { font-size: 14px !important; }
        
        /* Adjust padding for small screens */
        .block-container { padding: 1rem 1rem !important; }
        
        /* Highlight the sidebar 'Carrot' button for visibility */
        button[kind="headerNoContext"] {
            background-color: #04B488 !important;
            border-radius: 50% !important;
            color: black !important;
            box-shadow: 0px 0px 10px rgba(4, 180, 136, 0.5);
        }
        
        /* Make allocation bar labels smaller for small screens */
        .equity-bar, .debt-bar { font-size: 0.7rem !important; }
    }

    /* Force visibility of text regardless of system dark mode */
    p, span, label { color: #E0E0E0 !important; }
    </style>
    """, unsafe_allow_html=True) 

st.title("💸 Wealth Intelligence: Your AI Assistant for Mutual Funds")
st.caption("Institutional Wealth Intelligence | AI Powered High-Performance Portfolio")

# --- 3. SIDEBAR CONTROLS ---
st.sidebar.header("Investor Profile")

current_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(current_dir, "all_mf_database.parquet")

if os.path.exists(db_path):
    mtime = os.path.getmtime(db_path)
    last_updated = datetime.fromtimestamp(mtime, tz=pytz.timezone('Asia/Kolkata'))
    st.sidebar.markdown("---")
    st.sidebar.caption(f"🕒 **Last Data Sync:** \n{last_updated.strftime('%d %b %Y | %I:%M %p')} IST")
else:
    st.sidebar.warning("⚠️ Database not found")

with st.sidebar.container():
    st.number_input("Age Input", 18, 100, step=1, key="age_num", on_change=update_slider)
    st.slider("Age Range", 18, 100, key="age_slider", on_change=update_num, label_visibility="collapsed")

user_risk = st.sidebar.selectbox("Risk Profile", ["Conservative", "Moderate", "Aggressive"])
user_amount = st.sidebar.number_input("Monthly SIP (₹)", min_value=1000, value=25000, step=1000)

st.sidebar.divider()

# --- 4. EXECUTION LAYER ---
if st.sidebar.button("Generate Strategic Portfolio", type="primary"):
    inputs = {"age": st.session_state.age, "risk": user_risk, "amount": user_amount}
    
    with st.spinner("🏗️ Architecting Portfolio & Analyzing 500+ Mutual Funds..."):
        try:
            final_output = app_brain.invoke(inputs)
            
            # --- A. TARGET ASSET ALLOCATION ---
            st.subheader("📊 Target Asset Allocation")
            split = final_output.get("portfolio_split", {"equity": 70, "debt": 30})
            e_p = split['equity']
            d_p = split['debt']

            # Use st.columns(1) on very small screens, 3 on large
            c1, c2, c3 = st.columns([1, 1, 1])
            c1.metric("Equity", f"{e_p}%")
            c2.metric("Debt/Hybrid", f"{d_p}%")
            c3.metric("Monthly SIP", f"₹{user_amount:,.0f}")

            st.markdown(f"""
                <div class="allocation-container">
                    <div class="equity-bar" style="width: {e_p}%;">EQUITY {e_p}%</div>
                    <div class="debt-bar" style="width: {d_p}%;">DEBT/HYBRID {d_p}%</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.divider()

            # --- B. AI ADVISOR RECOMMENDATION ---
            st.subheader("🕵️‍♂️ Mutual Fund: Advisory Memo")
            with st.container(border=True):
                st.markdown(final_output.get("ai_reasoning", "Analysis unavailable."))
                st.caption(f"Governance Model: {final_output.get('actual_model_used', 'Hunter-Alpha')}")

            st.divider()

            # --- C. MARKET INTELLIGENCE: TOP 20 ---
            st.subheader("📈 Other Funds That Could Be Considered")
            st.write("Beyond the AI's primary picks, these top 20 MFs represent funds with high Alpha")
            df_top = final_output["top_mf_recommendations"].sort_values('Alpha', ascending=False)
            display_df = df_top[['Scheme', '10Y_Rolling_Median', 'Alpha']].head(20)
            
            def apply_premium_heatmap(val):
                if val >= 4.0: color = '#04B488'
                elif val >= 2.5: color = '#C9A227'
                else: color = '#A63D40'
                return f'background-color: {color}; color: black; font-weight: 600;'

            styled_df = display_df.style.applymap(apply_premium_heatmap, subset=['Alpha'])
            
            st.dataframe(
                styled_df,
                column_config={
                    "Scheme": st.column_config.TextColumn("Fund Identity", width="large"),
                    "10Y_Rolling_Median": st.column_config.NumberColumn("10Y Median", format="%.2f%%"),
                    "Alpha": st.column_config.NumberColumn("Alpha", format="%.2f%%")
                },
                hide_index=True,
                use_container_width=True
            )

        except Exception as e:
            st.error(f"System Alert: {e}")
else:
    # Landing Page - Simplified for Mobile
    st.markdown("""
        <div style='padding: 30px; text-align: center; border: 1px solid #30363D; border-radius: 15px; background-color: #161B22;'>
            <h2 style='margin-bottom: 0;'>Welcome to Wealth Intelligence</h2>
            <p style='color: #8B949E; margin-top: 10px;'>Precision-engineered portfolios derived from a decade of performance data.</p>
            <p style='color: #04B488; font-weight: 600; margin-top: 25px;'> 👈 Configure your profile in the Investor Profile pannel to begin.</p>
        </div>
    """, unsafe_allow_html=True)