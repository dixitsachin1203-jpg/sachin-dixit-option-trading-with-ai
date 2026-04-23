import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ---------------------------
# PAGE CONFIG (FINTECH UI)
# ---------------------------
st.set_page_config(page_title="Global Market Simulator", layout="wide")

st.markdown("""
<style>
.main {background-color:#0e1117;}
.block-container {padding-top:2rem;}
</style>
""", unsafe_allow_html=True)

st.title("🌍 Global Market Intelligence Simulator")
st.markdown("### Fake live market + technical analysis engine")

# ---------------------------
# MARKET SELECTION
# ---------------------------
market = st.selectbox("Select Market Index", [
    "🇮🇳 NIFTY 50",
    "🇮🇳 SENSEX",
    "🇺🇸 NASDAQ",
    "🇺🇸 DOW JONES"
])

# ---------------------------
# BASE PRICE SETTINGS
# ---------------------------
base_prices = {
    "🇮🇳 NIFTY 50": 22000,
    "🇮🇳 SENSEX": 72000,
    "🇺🇸 NASDAQ": 17000,
    "🇺🇸 DOW JONES": 38000
}

base = base_prices[market]

# ---------------------------
# FAKE MARKET GENERATION (LIVE SIMULATION)
# ---------------------------
np.random.seed(42)

days = 60
prices = [base]

for i in range(days):
    change = np.random.normal(0, 1.2)
    prices.append(prices[-1] * (1 + change/100))

df = pd.DataFrame({"Close": prices})

# ---------------------------
# INDICATORS
# ---------------------------
df["SMA20"] = df["Close"].rolling(20).mean()
df["SMA50"] = df["Close"].rolling(50).mean()

# RSI FUNCTION
def rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = -delta.where(delta < 0, 0).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

df["RSI"] = rsi(df["Close"])

latest = df.iloc[-1]

price = latest["Close"]
rsi_val = latest["RSI"]
sma20 = latest["SMA20"]
sma50 = latest["SMA50"]

support = df["Close"].min()
resistance = df["Close"].max()

# ---------------------------
# MARKET SIGNAL ENGINE
# ---------------------------
signal = "NEUTRAL 🟡"

if rsi_val < 30 and sma20 > sma50:
    signal = "BULLISH 🟢 (CALL bias)"
elif rsi_val > 70 and sma20 < sma50:
    signal = "BEARISH 🔴 (PUT bias)"

# ---------------------------
# DASHBOARD METRICS
# ---------------------------
col1, col2, col3 = st.columns(3)

col1.metric("Index", market)
col2.metric("Price", round(price, 2))
col3.metric("Signal", signal)

st.divider()

# ---------------------------
# CHART 1: MARKET TREND
# ---------------------------
fig = go.Figure()

fig.add_trace(go.Scatter(
    y=df["Close"],
    name="Price",
    line=dict(color="white")
))

fig.add_trace(go.Scatter(
    y=df["SMA20"],
    name="SMA 20",
    line=dict(color="blue")
))

fig.add_trace(go.Scatter(
    y=df["SMA50"],
    name="SMA 50",
    line=dict(color="orange")
))

fig.add_hline(y=support, line_color="green", annotation_text="Support")
fig.add_hline(y=resistance, line_color="red", annotation_text="Resistance")

fig.update_layout(
    template="plotly_dark",
    height=500,
    title="Market Trend Analysis"
)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# CHART 2: RSI INDICATOR
# ---------------------------
fig2 = go.Figure()

fig2.add_trace(go.Scatter(
    y=df["RSI"],
    name="RSI",
    line=dict(color="purple")
))

fig2.add_hline(y=70, line_dash="dash", line_color="red")
fig2.add_hline(y=30, line_dash="dash", line_color="green")

fig2.update_layout(
    template="plotly_dark",
    title="RSI Indicator"
)

st.plotly_chart(fig2, use_container_width=True)

# ---------------------------
# MARKET INSIGHT PANEL
# ---------------------------
st.subheader("🧠 Market Analysis Engine")

st.write(f"""
### 📊 Technical Summary
- RSI: {round(rsi_val,2) if not np.isnan(rsi_val) else 'N/A'}
- SMA 20: {round(sma20,2) if not np.isnan(sma20) else 'N/A'}
- SMA 50: {round(sma50,2) if not np.isnan(sma50) else 'N/A'}

### 📌 Levels
- Support: {round(support,2)}
- Resistance: {round(resistance,2)}

### 🎯 Signal
**{signal}**

👉 This is a technical-based sentiment signal using RSI + SMA crossover logic.
""")

# ---------------------------
# FINAL SENTIMENT CARD
# ---------------------------
st.divider()

if "BULLISH" in signal:
    st.success("Market sentiment is bullish. Buyers dominate momentum.")
elif "BEARISH" in signal:
    st.error("Market sentiment is bearish. Selling pressure dominates.")
else:
    st.warning("Market is neutral. No strong directional trend.")