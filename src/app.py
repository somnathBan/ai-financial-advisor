import streamlit as st
import pandas as pd
from graph import app_brain  # The Orchestrator

# --- 1. INITIALIZATION & SESSION STATE ---
if 'age' not in st.session_state:
    st.session_state.age = 30

def update_num():
    st.session_state.age_num = st.session_state.age_slider
    st.session_state.age = st.session_state.age_slider
def update_slider():
    st.session_state.age_slider = st.session_state.age_num
    st.session_state.age = st.session_state.age_num

# --- 2. UI SETUP ---
st.set_page_config(page_title="AI Financial Advisor MVP", layout="wide")
st.title("🛡️ AI Financial Advisor")
st.caption("Powered by LangGraph Multi-Agent Orchestration & Hunter Alpha")

# --- 3. SIDEBAR CONTROLS ---
st.sidebar.header("User Profile")
with st.sidebar.container():
    st.write("**Enter your age**")
    st.number_input("Age Num", 18, 100, step=1, key="age_num", on_change=update_slider, label_visibility="collapsed")
    st.slider("Age Slider", 18, 100, key="age_slider", on_change=update_num, label_visibility="collapsed")

user_risk = st.sidebar.selectbox("Risk Appetite", ["Conservative", "Moderate", "Aggressive"])
user_amount = st.sidebar.number_input("Investment Amount (₹)", min_value=1000, value=50000, step=1000)

st.sidebar.divider()

# --- 4. EXECUTION LAYER (The Trigger) ---
if st.sidebar.button("Generate AI Strategy", type="primary"):
    # Build initial state
    inputs = {
        "age": st.session_state.age,
        "risk": user_risk,
        "amount": user_amount
    }
    
    with st.spinner("🤖 Coordination in progress: Ingesting data & reasoning..."):
        try:
            # A. Invoke the Graph (This runs all 3 nodes: Ingest -> Strategy -> Reasoning)
            final_output = app_brain.invoke(inputs)
            
            # B. Extract results
            e_p = final_output["portfolio_split"]["equity"]
            d_p = final_output["portfolio_split"]["debt"]
            e_v = (e_p / 100) * user_amount
            d_v = (d_p / 100) * user_amount
            df_market = final_output["recommendations_df"]
            ai_reasoning = final_output.get("ai_reasoning", "Analysis unavailable.")

            # C. DISPLAY RESULTS
            col_left, col_right = st.columns([1, 1.5])

            with col_left:
                st.subheader("🎯 Portfolio Allocation")
                st.metric("Equity Value", f"₹{e_v:,.0f}", f"{e_p}% Share")
                st.metric("Debt Value", f"₹{d_v:,.0f}", f"{d_p}% Share")
                st.progress(e_p / 100)
                st.caption(f"Strategy: {user_risk} allocation based on Age {st.session_state.age}")

            with col_right:
                st.subheader(f"📊 Market Intelligence: {user_risk}")
                st.table(df_market)
                st.info("💡 Data sourced via Yahoo Finance API using real-time fundamental ratios.")

            # --- D. THE REASONING BLOCK ---
            st.divider()
            st.subheader("🧠 AI Advisor's Analysis")
            # We use a container to make the AI text stand out
            with st.container():
                st.markdown(f"**Personalized Strategy Memo:**")
                # Display the reasoning text
                st.write(final_output.get("ai_reasoning", "Analysis unavailable."))
                
                # Display the dynamic model name in the caption
                model_used = final_output.get("actual_model_used", "Auto-Router")
                st.caption(f"🛡️ Strategy verified by: **{model_used}**")

        except Exception as e:
            st.error(f"Graph Execution Error: {e}")
            st.warning("Ensure that your OpenRouter Key is active and your nodes are returning the correct keys.")
else:
    st.info("👈 Adjust your profile in the sidebar and click 'Generate AI Strategy' to run the agentic workflow.")