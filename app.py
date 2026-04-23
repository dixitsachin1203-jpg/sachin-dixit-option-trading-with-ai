import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# ---------------------------
# PAGE CONFIG (CLEAN UI)
# ---------------------------
st.set_page_config(page_title="Smart Trading Terminal", layout="wide")

st.title("📊 Smart Options Trading Terminal")
st.markdown("### Clean, structured and realistic trading dashboard")

# ---------------------------
# SESSION STATE
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
# MARKET ENGINE (LESS RANDOM, MORE REALISTIC)
# ---------------------------
noise = np.random.normal(0, 25)

trend_bias = np.tanh(np.mean(np.diff(st.session_state.history[-10:]))) * 10

st.session_state.price += noise + trend_bias

st.session_state.history.append(st.session_state.price)
st.session_state.history = st.session_state.history[-120:]

price = st.session_state.price
series = pd.Series(st.session_state.history)

# ---------------------------
# INDICATORS (REAL STRUCTURE)
# ---------------------------
sma20 = series.rolling(20).mean().iloc[-1]
sma50 = series.rolling(50).mean().iloc[-1]

delta = series.diff()
gain = delta.where(delta > 0, 0).rolling(14).mean()
loss = -delta.where(delta < 0, 0).rolling(14).mean()
rs = gain / loss
rsi = float(100 - (100 / (1 + rs)).iloc[-1])

# ---------------------------
# SMART SIGNAL ENGINE (FIXED LOGIC)
# ---------------------------

trend = "NEUTRAL"

if sma20 > sma50:
    trend = "UPTREND"
elif sma20 < sma50:
    trend = "DOWNTREND"

signal = "NO TRADE 🟡"

if trend == "UPTREND" and rsi < 35:
    signal = "🟢 BUY CALL (Strong Bullish Setup)"
elif trend == "DOWNTREND" and rsi > 65:
    signal = "🔴 BUY PUT (Strong Bearish Setup)"
elif rsi > 75:
    signal = "🔴 OVERBOUGHT - PUT BIAS"
elif rsi < 25:
    signal = "🟢 OVERSOLD - CALL BIAS"

# ---------------------------
# OPTION PRICING
# ---------------------------
def call_price(strike):
    return max(10, (price - strike) + np.random.uniform(60, 120))

def put_price(strike):
    return max(10, (strike - price) + np.random.uniform(60, 120))

strikes = [price + i for i in [-300, -200, -100, 0, 100, 200, 300]]

options = pd.DataFrame({
    "Strike": strikes,
    "CALL": [round(call_price(s), 2) for s in strikes],
    "PUT": [round(put_price(s), 2) for s in strikes]
})

# ---------------------------
# TOP DASHBOARD METRICS
# ---------------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("Index", round(price, 2))
col2.metric("RSI", round(rsi, 2))
col3.metric("Trend", trend)
col4.metric("Signal", signal)

st.divider()

# =========================================================
# 1️⃣ CLEAN LIVE CHART
# =========================================================
st.subheader("📈 Market Trend")

fig = go.Figure()

fig.add_trace(go.Scatter(
    y=series,
    name="Price",
    line=dict(color="white", width=2)
))

fig.add_trace(go.Scatter(
    y=series.rolling(20).mean(),
    name="SMA 20",
    line=dict(color="blue")
))

fig.add_trace(go.Scatter(
    y=series.rolling(50).mean(),
    name="SMA 50",
    line=dict(color="orange")
))

fig.update_layout(template="plotly_dark", height=450)

st.plotly_chart(fig, use_container_width=True)

# =========================================================
# 2️⃣ OPTIONS (CLEAN TABLE UI)
# =========================================================
st.subheader("📊 Option Chain")

colA, colB = st.columns(2)

with colA:
    st.markdown("### CALL OPTIONS")
    for i, row in options.iterrows():
        if st.button(f"BUY CALL {row['Strike']}", key=f"c{i}"):
            st.session_state.positions.append(("CALL", row["Strike"], row["CALL"]))
            st.session_state.balance -= row["CALL"]

        st.write(f"Strike: {row['Strike']} | Premium: {row['CALL']}")

with colB:
    st.markdown("### PUT OPTIONS")
    for i, row in options.iterrows():
        if st.button(f"BUY PUT {row['Strike']}", key=f"p{i}"):
            st.session_state.positions.append(("PUT", row["Strike"], row["PUT"]))
            st.session_state.balance -= row["PUT"]

        st.write(f"Strike: {row['Strike']} | Premium: {row['PUT']}")

st.divider()

# =========================================================
# 3️⃣ PORTFOLIO (CLEAN P&L)
# =========================================================
st.subheader("💼 Portfolio")

total_pnl = 0

for pos in st.session_state.positions:

    typ, strike, entry = pos

    if typ == "CALL":
        current = max(0, price - strike)
    else:
        current = max(0, strike - price)

    pnl = current - entry
    total_pnl += pnl

    st.write(f"{typ} | Strike {strike} | Entry {entry:.2f} | P&L {pnl:.2f}")

col1, col2 = st.columns(2)

col1.metric("Balance", round(st.session_state.balance, 2))
col2.metric("Total P&L", round(total_pnl, 2))

# =========================================================
# 4️⃣ CLEAN SIGNAL PANEL
# =========================================================
st.subheader("🧠 Trading Signal Engine (Improved)")

st.info(f"""
### 📌 Market Conditions
- Trend: {trend}
- RSI: {round(rsi,2)}
- SMA20: {round(sma20,2)}
- SMA50: {round(sma50,2)}

### 🎯 Signal
**{signal}**

### 📊 Logic Used
- Trend following (SMA crossover)
- Momentum filter (RSI)
- Overbought/oversold zones
""")
