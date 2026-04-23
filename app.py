import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(page_title="Pro Trading Terminal", layout="wide")

st.title("📊 Pro Options Trading Terminal (Simulated)")
st.markdown("### Live Index + Options Chain + Paper Trading")

# ---------------------------
# SESSION STATE
# ---------------------------
if "price" not in st.session_state:
    st.session_state.price = 22000

if "positions" not in st.session_state:
    st.session_state.positions = []

if "balance" not in st.session_state:
    st.session_state.balance = 100000

if "history" not in st.session_state:
    st.session_state.history = [st.session_state.price]

# ---------------------------
# SIMULATED LIVE MARKET MOVEMENT
# ---------------------------
move = np.random.normal(0, 40)
st.session_state.price += move
st.session_state.history.append(st.session_state.price)

# keep last 80 points
st.session_state.history = st.session_state.history[-80:]

index_price = st.session_state.price

# ---------------------------
# RSI (SIMPLIFIED)
# ---------------------------
series = pd.Series(st.session_state.history)
delta = series.diff()
gain = delta.where(delta > 0, 0).rolling(14).mean()
loss = -delta.where(delta < 0, 0).rolling(14).mean()
rs = gain / loss
rsi = float(100 - (100 / (1 + rs)).iloc[-1])

# ---------------------------
# MARKET BIAS
# ---------------------------
bias = "NEUTRAL 🟡"

if rsi < 30:
    bias = "BULLISH 🟢 (CALL ZONE)"
elif rsi > 70:
    bias = "BEARISH 🔴 (PUT ZONE)"

# ---------------------------
# OPTION PRICING MODEL
# ---------------------------
def call_price(strike, spot):
    return max(10, (spot - strike) + np.random.uniform(80, 180))

def put_price(strike, spot):
    return max(10, (strike - spot) + np.random.uniform(80, 180))

# ---------------------------
# STRIKES GENERATION
# ---------------------------
strikes = [index_price + i for i in [-300, -200, -100, 0, 100, 200, 300]]

options = []
for s in strikes:
    options.append({
        "Strike": round(s),
        "CALL": round(call_price(s, index_price), 2),
        "PUT": round(put_price(s, index_price), 2)
    })

df = pd.DataFrame(options)

# ---------------------------
# TOP METRICS
# ---------------------------
col1, col2, col3 = st.columns(3)

col1.metric("Index Level", round(index_price, 2))
col2.metric("RSI", round(rsi, 2))
col3.metric("Market Bias", bias)

st.divider()

# ---------------------------
# MAIN LAYOUT (CHART + OPTION CHAIN)
# ---------------------------
left, right = st.columns([2, 1])

# ---------------------------
# LIVE INDEX CHART
# ---------------------------
with left:
    st.subheader("📈 Live Index Chart")

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        y=st.session_state.history,
        name="Index",
        line=dict(color="white")
    ))

    fig.update_layout(
        template="plotly_dark",
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# OPTION CHAIN + TRADING
# ---------------------------
with right:
    st.subheader("📊 Option Chain")

    for i, row in df.iterrows():

        c1, c2 = st.columns(2)

        with c1:
            if st.button(f"BUY CALL {row['Strike']}", key=f"c{i}"):
                st.session_state.positions.append(
                    ("CALL", row["Strike"], row["CALL"])
                )
                st.session_state.balance -= row["CALL"]

        with c2:
            if st.button(f"BUY PUT {row['Strike']}", key=f"p{i}"):
                st.session_state.positions.append(
                    ("PUT", row["Strike"], row["PUT"])
                )
                st.session_state.balance -= row["PUT"]

        st.write(f"Strike: {row['Strike']} | C: {row['CALL']} | P: {row['PUT']}")

st.divider()

# ---------------------------
# POSITIONS + P&L
# ---------------------------
st.subheader("💼 Open Positions")

total_pnl = 0

if st.session_state.positions:

    for i, pos in enumerate(st.session_state.positions):

        typ, strike, entry = pos

        # simulated live P&L
        if typ == "CALL":
            current = max(0, index_price - strike)
        else:
            current = max(0, strike - index_price)

        pnl = current - entry
        total_pnl += pnl

        st.write(f"{typ} | Strike: {strike} | Entry: {entry:.2f} | P&L: {pnl:.2f}")

else:
    st.info("No open positions")

# ---------------------------
# ACCOUNT SUMMARY
# ---------------------------
st.divider()

colA, colB = st.columns(2)

colA.metric("Account Balance", round(st.session_state.balance, 2))
colB.metric("Total P&L", round(total_pnl, 2))

# ---------------------------
# MARKET INSIGHT
# ---------------------------
st.subheader("🧠 Market Intelligence")

st.write(f"""
- RSI: {round(rsi,2)}
- Bias: {bias}
- Trend: {'Bullish Momentum' if rsi < 30 else 'Bearish Pressure' if rsi > 70 else 'Sideways Market'}

👉 CALL options work better in bullish zones  
👉 PUT options work better in bearish zones  
👉 Avoid trading in neutral markets
""")
