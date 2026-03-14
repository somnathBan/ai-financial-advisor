import streamlit as st

# --- 1. INITIALIZATION BLOCK ---
# This must happen before any widgets are defined to ensure they match on load.
if 'age' not in st.session_state:
    st.session_state.age = 30
if 'age_num' not in st.session_state:
    st.session_state.age_num = 30
if 'age_slider' not in st.session_state:
    st.session_state.age_slider = 30

# --- 2. CALLBACK FUNCTIONS ---
def update_num():
    # Update the number box and the global state from the slider
    st.session_state.age_num = st.session_state.age_slider
    st.session_state.age = st.session_state.age_slider

def update_slider():
    # Update the slider and the global state from the number box
    st.session_state.age_slider = st.session_state.age_num
    st.session_state.age = st.session_state.age_num

# --- 3. LOGIC ---
def run_investment_agent(age, risk, amount):
    equity_p = max(0, min(100, (120 - age) + (10 if risk == "Aggressive" else -20 if risk == "Conservative" else 0)))
    debt_p = 100 - equity_p
    return equity_p, debt_p, (equity_p / 100) * amount, (debt_p / 100) * amount

# --- 4. UI SETUP ---
st.set_page_config(page_title="AI Advisor: Phase 1", layout="centered")
st.title("🛡️ AI Financial Advisor")

st.sidebar.header("User Profile")

with st.sidebar.container():
    st.write("**Enter your age**")
    
    # Numeric Input
    st.number_input(
        label="Age Numeric",
        min_value=18, max_value=100,
        step=1,
        key="age_num",
        on_change=update_slider,
        label_visibility="collapsed"
    )
    
    # Slider Input
    st.slider(
        label="Age Slider",
        min_value=18, max_value=100,
        key="age_slider",
        on_change=update_num,
        label_visibility="collapsed"
    )

user_risk = st.sidebar.selectbox("Risk Appetite", ["Conservative", "Moderate", "Aggressive"])
user_amount = st.sidebar.number_input("Amount to Invest (₹)", min_value=1000, value=50000, step=1000)

# Final Logic Execution
e_p, d_p, e_v, d_v = run_investment_agent(st.session_state.age, user_risk, user_amount)

# --- 5. DISPLAY RESULTS ---
st.divider()
st.subheader(f"Recommended Split: {e_p}% Equity / {d_p}% Debt")

col1, col2 = st.columns(2)
with col1:
    st.metric("Equity (Stocks/MFs)", f"₹{e_v:,.0f}")
with col2:
    st.metric("Debt (FDs/Bonds)", f"₹{d_v:,.0f}")

st.info(f"Currently calculating for Age: **{st.session_state.age}**")