import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(page_title="Live Market Simulator", layout="wide")

st.title("🌍 Real-Time Market Dynamics Simulator")
st.markdown("### Simulated live market with changing volatility & trends")

# ---------------------------
# AUTO REFRESH (LIVE FEEL)
# ---------------------------
st_autorefresh = st.empty()

# ---------------------------
# MARKET SELECT
# ---------------------------
market = st.selectbox("Select Index", ["NIFTY 50", "SENSEX", "NASDAQ", "DOW JONES"])

base_prices = {
    "NIFTY 50": 22000,
    "SENSEX": 72000,
    "NASDAQ": 17000,
    "DOW JONES": 38000
}

base = base_prices[market]

# ---------------------------
# SESSION STATE (LIVE MEMORY)
# ---------------------------
if "prices" not in st.session_state:
    st.session_state.prices = [base]
    st.session_state.trend = np.random.choice(["bull", "bear", "sideways"])

# ---------------------------
# TREND SWITCHING ENGINE
# ---------------------------
def change_trend():
    return np.random.choice(["bull", "bear", "sideways"], p=[0.4, 0.3, 0.3])

# ---------------------------
# PRICE GENERATOR (REALISTIC DYNAMICS)
# ---------------------------
def generate_next_price(prev, trend):
    # base noise
    noise = np.random.normal(0, 0.6)

    # trend bias
    if trend == "bull":
        drift = 0.4
    elif trend == "bear":
        drift = -0.4
    else:
        drift = 0

    # volatility spike (news-like shock)
    shock = np.random.choice([0, 0, 0, 2, -2])

    return prev * (1 + (noise + drift + shock) / 100)

# ---------------------------
# UPDATE PRICE
# ---------------------------
if np.random.rand() < 0.1:
    st.session_state.trend = change_trend()

new_price = generate_next_price(st.session_state.prices[-1], st.session_state.trend)
st.session_state.prices.append(new_price)

# keep last 80 points
st.session_state.prices = st.session_state.prices[-80:]

df = pd.DataFrame({"Close": st.session_state.prices})

# ---------------------------
# INDICATORS
# ---------------------------
df["SMA20"] = df["Close"].rolling(20).mean()
df["SMA50"] = df["Close"].rolling(50).mean()

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

# ---------------------------
# SUPPORT / RESISTANCE
# ---------------------------
support = df["Close"].min()
resistance = df["Close"].max()

# ---------------------------
# SIGNAL ENGINE (REALISTIC LOGIC)
# ---------------------------
signal = "NEUTRAL 🟡"

if rsi_val < 30 and sma20 > sma50:
    signal = "BULLISH 🟢 (CALL BIAS)"
elif rsi_val > 70 and sma20 < sma50:
    signal = "BEARISH 🔴 (PUT BIAS)"

# ---------------------------
# DASHBOARD METRICS
# ---------------------------
col1, col2, col3 = st.columns(3)

col1.metric("Index", market)
col2.metric("Price", round(price, 2))
col3.metric("Market Mood", st.session_state.trend.upper())

st.divider()

# ---------------------------
# LIVE PRICE CHART
# ---------------------------
fig = go.Figure()

fig.add_trace(go.Scatter(
    y=df["Close"],
    name="Price",
    line=dict(color="white", width=2)
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

fig.update_layout(template="plotly_dark", height=550)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# RSI CHART
# ---------------------------
fig2 = go.Figure()

fig2.add_trace(go.Scatter(
    y=df["RSI"],
    name="RSI",
    line=dict(color="purple")
))

fig2.add_hline(y=70, line_dash="dash", line_color="red")
fig2.add_hline(y=30, line_dash="dash", line_color="green")

fig2.update_layout(template="plotly_dark", title="RSI Indicator")

st.plotly_chart(fig2, use_container_width=True)

# ---------------------------
# INSIGHT PANEL
# ---------------------------
st.subheader("🧠 Live Market Intelligence")

st.write(f"""
### 📊 Current Market State
- Trend Regime: {st.session_state.trend}
- RSI: {round(rsi_val,2) if not np.isnan(rsi_val) else 'N/A'}
- SMA20 vs SMA50: {'Bullish' if sma20 > sma50 else 'Bearish'}

### 🎯 Signal
**{signal}**

### ⚠️ Note
This is a simulated market with dynamic trend switching + volatility shocks.
""")

# ---------------------------
# AUTO REFRESH LOOP
# ---------------------------
time.sleep(1)
st.rerun()
