import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import time

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(page_title="Live Trading Terminal", layout="wide")

st.title("📊 LIVE Trading Terminal (Simulated Real Market)")

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
# LIVE MARKET ENGINE
# ---------------------------
def update_market():
    move = np.random.normal(0, 30)

    # trend bias
    bias = np.random.choice([-1, 0, 1], p=[0.3, 0.4, 0.3])

    shock = np.random.choice([0, 0, 0, 60, -60])

    new_price = st.session_state.price + move + bias * 10 + shock * 0.2

    st.session_state.price = new_price
    st.session_state.history.append(new_price)

    st.session_state.history = st.session_state.history[-120:]

# ---------------------------
# RUN MARKET UPDATE (LIVE FEEL)
# ---------------------------
update_market()

price = st.session_state.price

# ---------------------------
# RSI CALC
# ---------------------------
series = pd.Series(st.session_state.history)

delta = series.diff()
gain = delta.where(delta > 0, 0).rolling(14).mean()
loss = -delta.where(delta < 0, 0).rolling(14).mean()

rs = gain / loss
rsi = float(100 - (100 / (1 + rs)).iloc[-1])

# ---------------------------
# SIGNAL ENGINE
# ---------------------------
signal = "NEUTRAL 🟡"

if rsi < 30:
    signal = "🟢 BUY CALL ZONE"
elif rsi > 70:
    signal = "🔴 BUY PUT ZONE"

# ---------------------------
# OPTION PRICING (LIVE LINKED)
# ---------------------------
def call_price(strike):
    return max(10, (price - strike) + np.random.uniform(80, 160))

def put_price(strike):
    return max(10, (strike - price) + np.random.uniform(80, 160))

strikes = [price + i for i in [-300, -200, -100, 0, 100, 200, 300]]

options = []
for s in strikes:
    options.append({
        "Strike": round(s),
        "CALL": round(call_price(s), 2),
        "PUT": round(put_price(s), 2)
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

# =========================================================
# 1️⃣ LIVE MOVING CHART (AUTO UPDATING)
# =========================================================
chart_placeholder = st.empty()

fig = go.Figure()

fig.add_trace(go.Scatter(
    y=st.session_state.history,
    name="NIFTY",
    line=dict(color="white", width=2)
))

fig.update_layout(
    template="plotly_dark",
    height=450
)

chart_placeholder.plotly_chart(fig, use_container_width=True)

# =========================================================
# 2️⃣ LIVE OPTION CHAIN (MOVING WITH MARKET)
# =========================================================
st.subheader("📊 Live Option Chain")

colA, colB = st.columns(2)

with colA:
    st.markdown("### CALLS")

    for i, row in df.iterrows():
        if st.button(f"BUY CALL {row['Strike']}", key=f"c{i}"):
            st.session_state.positions.append(("CALL", row["Strike"], row["CALL"]))
            st.session_state.balance -= row["CALL"]

        st.write(f"{row['Strike']} | {row['CALL']}")

with colB:
    st.markdown("### PUTS")

    for i, row in df.iterrows():
        if st.button(f"BUY PUT {row['Strike']}", key=f"p{i}"):
            st.session_state.positions.append(("PUT", row["Strike"], row["PUT"]))
            st.session_state.balance -= row["PUT"]

        st.write(f"{row['Strike']} | {row['PUT']}")

st.divider()

# =========================================================
# 3️⃣ LIVE P&L SYSTEM
# =========================================================
st.subheader("💼 Live Positions")

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

st.metric("Balance", round(st.session_state.balance, 2))
st.metric("Total P&L", round(total_pnl, 2))

# =========================================================
# 4️⃣ RSI LIVE CHART
# =========================================================
st.subheader("📉 RSI Momentum")

rsi_fig = go.Figure()

rsi_fig.add_trace(go.Scatter(
    y=series,
    name="Price",
    line=dict(color="white")
))

rsi_fig.add_trace(go.Scatter(
    y=[rsi]*len(series),
    name="RSI Trend",
    line=dict(color="orange")
))

rsi_fig.update_layout(template="plotly_dark", height=300)

st.plotly_chart(rsi_fig, use_container_width=True)

# =========================================================
# 5️⃣ AUTO REFRESH LOOP (LIVE FEEL)
# =========================================================
time.sleep(1)
st.rerun()
