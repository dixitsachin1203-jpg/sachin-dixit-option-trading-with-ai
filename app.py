import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(page_title="Institutional Trading Terminal", layout="wide")

st.title("🏦 Institutional Trading Terminal v4 (Ultra Pro Simulator)")
st.markdown("### Realistic market engine + options chain + trading desk")

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
# MARKET ENGINE (REALISTIC DYNAMICS)
# ---------------------------
trend_bias = np.random.choice([-1, 0, 1], p=[0.3, 0.4, 0.3])

volatility = np.random.normal(0, 40)

shock = np.random.choice([0, 0, 0, 80, -80])  # news spikes

move = trend_bias * 20 + volatility + shock * 0.2

st.session_state.price += move
st.session_state.history.append(st.session_state.price)

st.session_state.history = st.session_state.history[-120:]

price = st.session_state.price

# ---------------------------
# CANDLESTICK DATA GENERATION
# ---------------------------
df = pd.DataFrame(st.session_state.history, columns=["Close"])

df["Open"] = df["Close"].shift(1)
df["High"] = df[["Open", "Close"]].max(axis=1) + np.random.uniform(5, 30, len(df))
df["Low"] = df[["Open", "Close"]].min(axis=1) - np.random.uniform(5, 30, len(df))

df = df.dropna()

# ---------------------------
# RSI + SMA
# ---------------------------
delta = df["Close"].diff()
gain = delta.where(delta > 0, 0).rolling(14).mean()
loss = -delta.where(delta < 0, 0).rolling(14).mean()
rs = gain / loss
rsi = float(100 - (100 / (1 + rs)).iloc[-1])

df["SMA20"] = df["Close"].rolling(20).mean()
df["SMA50"] = df["Close"].rolling(50).mean()

# ---------------------------
# SIGNAL ENGINE (INSTITUTIONAL LOGIC)
# ---------------------------
signal = "NO TRADE 🟡"

if rsi < 30 and df["SMA20"].iloc[-1] > df["SMA50"].iloc[-1]:
    signal = "🟢 BUY CALL (Institutional Long Setup)"
elif rsi > 70 and df["SMA20"].iloc[-1] < df["SMA50"].iloc[-1]:
    signal = "🔴 BUY PUT (Institutional Short Setup)"

# ---------------------------
# STRIKES + OPTIONS
# ---------------------------
strikes = [price + i for i in [-300, -200, -100, 0, 100, 200, 300]]

def call_premium(strike):
    return max(10, (price - strike) + np.random.uniform(100, 200))

def put_premium(strike):
    return max(10, (strike - price) + np.random.uniform(100, 200))

options = []
for s in strikes:
    options.append({
        "Strike": round(s),
        "CALL": round(call_premium(s), 2),
        "PUT": round(put_premium(s), 2)
    })

opt_df = pd.DataFrame(options)

# ---------------------------
# TOP METRICS
# ---------------------------
col1, col2, col3 = st.columns(3)

col1.metric("NIFTY INDEX", round(price, 2))
col2.metric("RSI", round(rsi, 2))
col3.metric("SIGNAL", signal)

st.divider()

# =========================================================
# 1️⃣ CANDLESTICK CHART (INSTITUTIONAL STYLE)
# =========================================================
st.subheader("📈 NIFTY Candlestick Chart")

fig = go.Figure()

fig.add_trace(go.Candlestick(
    open=df["Open"],
    high=df["High"],
    low=df["Low"],
    close=df["Close"],
    name="NIFTY"
))

fig.add_trace(go.Scatter(
    y=df["SMA20"],
    name="SMA20",
    line=dict(color="blue")
))

fig.add_trace(go.Scatter(
    y=df["SMA50"],
    name="SMA50",
    line=dict(color="orange")
))

fig.update_layout(template="plotly_dark", height=500)

st.plotly_chart(fig, use_container_width=True)

# =========================================================
# 2️⃣ OPTION CHAIN (LIVE LINKED)
# =========================================================
st.subheader("📊 Options Chain (Live Linked to Index)")

colA, colB = st.columns(2)

with colA:
    st.markdown("### 📈 CALLS")

    for i, row in opt_df.iterrows():
        if st.button(f"BUY CALL {row['Strike']}", key=f"c{i}"):
            st.session_state.positions.append(("CALL", row["Strike"], row["CALL"]))
            st.session_state.balance -= row["CALL"]

        st.write(f"{row['Strike']} | {row['CALL']}")

with colB:
    st.markdown("### 📉 PUTS")

    for i, row in opt_df.iterrows():
        if st.button(f"BUY PUT {row['Strike']}", key=f"p{i}"):
            st.session_state.positions.append(("PUT", row["Strike"], row["PUT"]))
            st.session_state.balance -= row["PUT"]

        st.write(f"{row['Strike']} | {row['PUT']}")

st.divider()

# =========================================================
# 3️⃣ PORTFOLIO + P&L ENGINE
# =========================================================
st.subheader("💼 Trading Portfolio")

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

st.metric("Account Balance", round(st.session_state.balance, 2))
st.metric("Total P&L", round(total_pnl, 2))

st.divider()

# =========================================================
# 4️⃣ PAYOFF GRAPH (OPTION EXPIRY VIEW)
# =========================================================
st.subheader("📉 Option Payoff Diagram (Expiry View)")

spot_range = np.linspace(price - 500, price + 500, 50)

payoff_call = np.maximum(spot_range - price, 0)
payoff_put = np.maximum(price - spot_range, 0)

fig2 = go.Figure()

fig2.add_trace(go.Scatter(
    x=spot_range,
    y=payoff_call,
    name="CALL Payoff",
    line=dict(color="green")
))

fig2.add_trace(go.Scatter(
    x=spot_range,
    y=payoff_put,
    name="PUT Payoff",
    line=dict(color="red")
))

fig2.update_layout(template="plotly_dark", height=400)

st.plotly_chart(fig2, use_container_width=True)

# =========================================================
# 5️⃣ INSTITUTIONAL SIGNAL PANEL
# =========================================================
st.subheader("🧠 Institutional Signal Engine")

st.write(f"""
### 📌 Market Intelligence
- RSI: {round(rsi,2)}
- SMA Trend: {'Bullish' if df["SMA20"].iloc[-1] > df["SMA50"].iloc[-1] else 'Bearish'}
- Volatility: High Simulation Mode

### 🎯 Signal
**{signal}**

### 🏦 Strategy Logic
- RSI oversold + trend up → CALL accumulation
- RSI overbought + trend down → PUT accumulation
- Otherwise → No trade zone
""")
