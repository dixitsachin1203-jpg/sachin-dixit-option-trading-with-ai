import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(page_title="Options Chain Simulator", layout="wide")

st.title("📊 Options Chain Trading Simulator (CALL vs PUT)")
st.markdown("### Paper trading terminal with live-like option movement")

# ---------------------------
# SESSION STATE (TRADING ACCOUNT)
# ---------------------------
if "balance" not in st.session_state:
    st.session_state.balance = 100000
    st.session_state.positions = []

# ---------------------------
# SIMULATED INDEX
# ---------------------------
base_price = 22000

if "price" not in st.session_state:
    st.session_state.price = base_price

# simulate movement
move = np.random.normal(0, 50)
st.session_state.price += move

index_price = st.session_state.price

# ---------------------------
# RSI SIMULATION
# ---------------------------
rsi = np.random.randint(25, 75)

# ---------------------------
# OPTION PRICING MODEL (SIMPLIFIED)
# ---------------------------
def call_premium(strike, spot):
    return max(0, spot - strike + np.random.uniform(80, 200))

def put_premium(strike, spot):
    return max(0, strike - spot + np.random.uniform(80, 200))

# ---------------------------
# STRIKE GENERATION
# ---------------------------
strikes = [index_price + i for i in [-300, -200, -100, 0, 100, 200, 300]]

data = []

for strike in strikes:
    data.append({
        "Strike": strike,
        "CALL": round(call_premium(strike, index_price), 2),
        "PUT": round(put_premium(strike, index_price), 2)
    })

df = pd.DataFrame(data)

# ---------------------------
# SIGNAL ENGINE
# ---------------------------
signal = "NEUTRAL 🟡"

if rsi < 30:
    signal = "BULLISH 🟢 (CALL BUY BIAS)"
elif rsi > 70:
    signal = "BEARISH 🔴 (PUT BUY BIAS)"

# ---------------------------
# UI TOP METRICS
# ---------------------------
col1, col2, col3 = st.columns(3)

col1.metric("Index", round(index_price, 2))
col2.metric("RSI", rsi)
col3.metric("Market Bias", signal)

st.divider()

# ---------------------------
# CALL & PUT TABLE SIDE BY SIDE
# ---------------------------
colA, colB = st.columns(2)

with colA:
    st.subheader("📈 CALL OPTIONS")
    for i, row in df.iterrows():
        if st.button(f"BUY CALL {row['Strike']}", key=f"call_{i}"):
            st.session_state.positions.append(("CALL", row["Strike"], row["CALL"]))
            st.session_state.balance -= row["CALL"]

        st.write(f"Strike: {row['Strike']} | Premium: {row['CALL']}")

with colB:
    st.subheader("📉 PUT OPTIONS")
    for i, row in df.iterrows():
        if st.button(f"BUY PUT {row['Strike']}", key=f"put_{i}"):
            st.session_state.positions.append(("PUT", row["Strike"], row["PUT"]))
            st.session_state.balance -= row["PUT"]

        st.write(f"Strike: {row['Strike']} | Premium: {row['PUT']}")

st.divider()

# ---------------------------
# PORTFOLIO / P&L
# ---------------------------
st.subheader("💼 Paper Trading Portfolio")

if st.session_state.positions:
    total_value = 0

    for pos in st.session_state.positions:
        typ, strike, premium = pos
        pnl = np.random.uniform(-50, 150)  # simulated P&L
        total_value += pnl
        st.write(f"{typ} {strike} | Entry: {premium} | P&L: {round(pnl,2)}")

    st.metric("Account Balance", st.session_state.balance)
    st.metric("Total P&L", round(total_value, 2))
else:
    st.info("No positions yet")

# ---------------------------
# VISUAL CHART
# ---------------------------
fig = go.Figure()

fig.add_trace(go.Scatter(
    y=df["CALL"],
    name="CALL Premiums",
    line=dict(color="green")
))

fig.add_trace(go.Scatter(
    y=df["PUT"],
    name="PUT Premiums",
    line=dict(color="red")
))

fig.update_layout(template="plotly_dark", title="Options Premium Curve")

st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# FINAL INSIGHT
# ---------------------------
st.subheader("🧠 Trading Signal Engine")

st.write(f"""
- Index Movement: Simulated live
- RSI: {rsi}
- Market Bias: {signal}

👉 Use CALL when bullish momentum  
👉 Use PUT when bearish momentum  
👉 Avoid trades in neutral zones
""")
