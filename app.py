import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(page_title="Live Options Terminal", layout="wide")

st.title("📊 Live NIFTY Options Trading Terminal (Simulated)")

# ---------------------------
# SESSION STATE INIT
# ---------------------------
if "price" not in st.session_state:
    st.session_state.price = 22000

if "history" not in st.session_state:
    st.session_state.history = [st.session_state.price]

if "positions" not in st.session_state:
    st.session_state.positions = []

if "balance" not in st.session_state:
    st.session_state.balance = 100000

# ---------------------------
# LIVE NIFTY SIMULATION
# ---------------------------
move = np.random.normal(0, 35)
st.session_state.price += move
st.session_state.history.append(st.session_state.price)

st.session_state.history = st.session_state.history[-100:]

price = st.session_state.price

# ---------------------------
# RSI CALCULATION
# ---------------------------
series = pd.Series(st.session_state.history)

delta = series.diff()
gain = delta.where(delta > 0, 0).rolling(14).mean()
loss = -delta.where(delta < 0, 0).rolling(14).mean()
rs = gain / loss
rsi = float(100 - (100 / (1 + rs)).iloc[-1])

# ---------------------------
# SIGNAL ENGINE (OPTIONS BIAS)
# ---------------------------
signal = "NEUTRAL 🟡"

if rsi < 30:
    signal = "🟢 BUY CALL (Bullish Setup)"
elif rsi > 70:
    signal = "🔴 BUY PUT (Bearish Setup)"

# ---------------------------
# OPTION PRICING (SIMPLIFIED DYNAMIC)
# ---------------------------
def call_price(strike, spot):
    return max(10, (spot - strike) + np.random.uniform(80, 150))

def put_price(strike, spot):
    return max(10, (strike - spot) + np.random.uniform(80, 150))

strikes = [price + i for i in [-300, -200, -100, 0, 100, 200, 300]]

options = []
for s in strikes:
    options.append({
        "Strike": round(s),
        "CALL": round(call_price(s, price), 2),
        "PUT": round(put_price(s, price), 2)
    })

df = pd.DataFrame(options)

# ---------------------------
# TOP METRICS
# ---------------------------
col1, col2, col3 = st.columns(3)

col1.metric("NIFTY", round(price, 2))
col2.metric("RSI", round(rsi, 2))
col3.metric("Signal", signal)

st.divider()

# ==========================================================
# 1️⃣ LIVE NIFTY CHART (TOP)
# ==========================================================
st.subheader("📈 Live NIFTY Movement")

fig1 = go.Figure()

fig1.add_trace(go.Scatter(
    y=st.session_state.history,
    name="NIFTY",
    line=dict(color="white", width=2)
))

fig1.update_layout(
    template="plotly_dark",
    height=450
)

st.plotly_chart(fig1, use_container_width=True)

# ==========================================================
# 2️⃣ OPTION CHAIN (MOVES WITH NIFTY)
# ==========================================================
st.subheader("📊 Options Chain (Live Relative Movement)")

colA, colB = st.columns(2)

with colA:
    st.markdown("### 📈 CALL OPTIONS")

    for i, row in df.iterrows():
        if st.button(f"BUY CALL {row['Strike']}", key=f"c{i}"):
            st.session_state.positions.append(("CALL", row["Strike"], row["CALL"]))
            st.session_state.balance -= row["CALL"]

        st.write(f"Strike: {row['Strike']} | Premium: {row['CALL']}")

with colB:
    st.markdown("### 📉 PUT OPTIONS")

    for i, row in df.iterrows():
        if st.button(f"BUY PUT {row['Strike']}", key=f"p{i}"):
            st.session_state.positions.append(("PUT", row["Strike"], row["PUT"]))
            st.session_state.balance -= row["PUT"]

        st.write(f"Strike: {row['Strike']} | Premium: {row['PUT']}")

st.divider()

# ==========================================================
# 3️⃣ POSITIONS + P&L SYSTEM
# ==========================================================
st.subheader("💼 My Open Positions")

total_pnl = 0

if st.session_state.positions:

    for pos in st.session_state.positions:

        typ, strike, entry = pos

        if typ == "CALL":
            current = max(0, price - strike)
        else:
            current = max(0, strike - price)

        pnl = current - entry
        total_pnl += pnl

        st.write(f"{typ} | Strike {strike} | Entry {entry:.2f} | P&L {pnl:.2f}")

else:
    st.info("No active positions")

# ==========================================================
# 4️⃣ ACCOUNT SUMMARY
# ==========================================================
st.divider()

c1, c2 = st.columns(2)

c1.metric("Balance", round(st.session_state.balance, 2))
c2.metric("Total P&L", round(total_pnl, 2))

# ==========================================================
# 5️⃣ TECHNICAL VISUALS (RSI CHART)
# ==========================================================
st.subheader("📊 RSI Momentum Indicator")

fig2 = go.Figure()

fig2.add_trace(go.Scatter(
    y=series,
    name="Price",
    line=dict(color="white")
))

fig2.add_trace(go.Scatter(
    y=[rsi]*len(series),
    name="RSI (trend)",
    line=dict(color="orange")
))

fig2.update_layout(template="plotly_dark", height=300)

st.plotly_chart(fig2, use_container_width=True)

# ==========================================================
# 6️⃣ MARKET INSIGHT PANEL
# ==========================================================
st.subheader("🧠 AI Market Signal Engine")

st.write(f"""
### 📌 Market Status
- RSI: {round(rsi,2)}
- Signal: **{signal}**

### 🎯 Strategy Logic
- RSI < 30 → CALL Buying Zone 🟢  
- RSI > 70 → PUT Buying Zone 🔴  
- Else → No trade / wait
""")
