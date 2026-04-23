import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import random
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="AI Stock Market Simulator", layout="wide")

# Auto refresh every 2 seconds
st_autorefresh(interval=2000, key="market_refresh")

# -----------------------------
# INITIAL SETUP
# -----------------------------
STOCKS = ["AAPL", "TSLA", "INFY", "TCS", "RELIANCE"]

if "cash" not in st.session_state:
    st.session_state.cash = 100000

if "portfolio" not in st.session_state:
    st.session_state.portfolio = {s: {"qty": 0, "avg_price": 0} for s in STOCKS}

if "prices" not in st.session_state:
    st.session_state.prices = {s: random.uniform(100, 3000) for s in STOCKS}

if "history" not in st.session_state:
    st.session_state.history = {s: [] for s in STOCKS}

# -----------------------------
# MARKET SIMULATION ENGINE
# -----------------------------
def update_prices():
    for stock in STOCKS:
        old_price = st.session_state.prices[stock]

        # random walk with drift + volatility
        drift = random.uniform(-0.5, 0.5)
        shock = np.random.normal(0, 1)

        new_price = old_price * (1 + (drift + shock) / 100)

        new_price = max(10, new_price)  # prevent collapse

        st.session_state.prices[stock] = round(new_price, 2)

        # store history (last 30 points)
        st.session_state.history[stock].append(new_price)
        if len(st.session_state.history[stock]) > 30:
            st.session_state.history[stock].pop(0)

update_prices()

# -----------------------------
# CALCULATIONS
# -----------------------------
def portfolio_value():
    total = st.session_state.cash
    for stock in STOCKS:
        qty = st.session_state.portfolio[stock]["qty"]
        total += qty * st.session_state.prices[stock]
    return total

# -----------------------------
# BUY / SELL FUNCTIONS
# -----------------------------
def buy(stock, qty):
    price = st.session_state.prices[stock]
    cost = price * qty

    if st.session_state.cash >= cost:
        p = st.session_state.portfolio[stock]

        new_qty = p["qty"] + qty
        new_avg = ((p["qty"] * p["avg_price"]) + cost) / new_qty if new_qty > 0 else 0

        st.session_state.portfolio[stock]["qty"] = new_qty
        st.session_state.portfolio[stock]["avg_price"] = new_avg

        st.session_state.cash -= cost

def sell(stock, qty):
    p = st.session_state.portfolio[stock]
    if p["qty"] >= qty:
        price = st.session_state.prices[stock]
        revenue = price * qty

        p["qty"] -= qty
        st.session_state.cash += revenue

# -----------------------------
# UI LAYOUT
# -----------------------------
st.title("📊 AI Stock Market Simulator (Groww-like)")

# Sidebar - Portfolio Summary
with st.sidebar:
    st.header("💼 Portfolio")

    total_value = portfolio_value()
    pnl = total_value - 100000

    st.metric("Cash Balance", f"₹{st.session_state.cash:,.2f}")
    st.metric("Total Portfolio Value", f"₹{total_value:,.2f}")
    st.metric("P&L", f"₹{pnl:,.2f}")

    st.divider()

    st.subheader("Holdings")
    for s in STOCKS:
        qty = st.session_state.portfolio[s]["qty"]
        if qty > 0:
            st.write(f"{s}: {qty} shares")

# -----------------------------
# STOCK TABLE
# -----------------------------
st.subheader("📈 Live Market")

cols = st.columns(len(STOCKS))

for i, stock in enumerate(STOCKS):
    price = st.session_state.prices[stock]
    history = st.session_state.history[stock]

    change = np.random.uniform(-2, 2)

    with cols[i]:
        st.markdown(f"### {stock}")
        st.metric("Price", f"₹{price:.2f}", f"{change:.2f}%")

        # mini sparkline
        if len(history) > 2:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                y=history,
                mode="lines",
                line=dict(color="green" if change >= 0 else "red")
            ))
            fig.update_layout(
                height=120,
                margin=dict(l=0, r=0, t=0, b=0),
                xaxis=dict(visible=False),
                yaxis=dict(visible=False)
            )
            st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# TRADING PANEL
# -----------------------------
st.subheader("💰 Trade Stocks")

col1, col2, col3 = st.columns(3)

with col1:
    selected_stock = st.selectbox("Select Stock", STOCKS)

with col2:
    qty = st.number_input("Quantity", min_value=1, step=1)

with col3:
    st.write("")
    buy_btn = st.button("Buy 🟢")
    sell_btn = st.button("Sell 🔴")

if buy_btn:
    buy(selected_stock, qty)
    st.success(f"Bought {qty} {selected_stock}")

if sell_btn:
    if st.session_state.portfolio[selected_stock]["qty"] >= qty:
        sell(selected_stock, qty)
        st.success(f"Sold {qty} {selected_stock}")
    else:
        st.error("Not enough shares to sell")

# -----------------------------
# PORTFOLIO DETAILS TABLE
# -----------------------------
st.subheader("📊 Detailed Portfolio")

rows = []

for stock in STOCKS:
    qty = st.session_state.portfolio[stock]["qty"]
    avg = st.session_state.portfolio[stock]["avg_price"]
    current = st.session_state.prices[stock]

    pnl = (current - avg) * qty if qty > 0 else 0

    rows.append([stock, qty, avg, current, pnl])

df = pd.DataFrame(rows, columns=[
    "Stock", "Qty", "Avg Price", "Current Price", "P&L"
])

st.dataframe(df, use_container_width=True)

# -----------------------------
# FOOTER
# -----------------------------
st.caption("⚠️ This is a simulated trading environment. No real money involved.")
