import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import random
from streamlit_autorefresh import st_autorefresh

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="AI Stock Market Simulator", layout="wide")

# Auto refresh every 2 seconds
st_autorefresh(interval=2000, key="refresh")

# -----------------------------
# STOCKS
# -----------------------------
STOCKS = ["AAPL", "TSLA", "INFY", "TCS", "RELIANCE"]

# -----------------------------
# SESSION INIT
# -----------------------------
if "cash" not in st.session_state:
    st.session_state.cash = 100000

if "portfolio" not in st.session_state:
    st.session_state.portfolio = {
        s: {"qty": 0, "avg_price": 0} for s in STOCKS
    }

if "prices" not in st.session_state:
    st.session_state.prices = {
        s: random.uniform(100, 3000) for s in STOCKS
    }

if "history" not in st.session_state:
    st.session_state.history = {s: [] for s in STOCKS}

if "portfolio_history" not in st.session_state:
    st.session_state.portfolio_history = []

# -----------------------------
# MARKET ENGINE
# -----------------------------
def update_prices():
    for stock in STOCKS:
        old = st.session_state.prices[stock]

        drift = random.uniform(-0.6, 0.6)
        shock = np.random.normal(0, 1.2)

        new_price = old * (1 + (drift + shock) / 100)
        new_price = max(10, new_price)

        st.session_state.prices[stock] = round(new_price, 2)

        st.session_state.history[stock].append(new_price)
        if len(st.session_state.history[stock]) > 30:
            st.session_state.history[stock].pop(0)

update_prices()

# -----------------------------
# PORTFOLIO VALUE
# -----------------------------
def portfolio_value():
    total = st.session_state.cash
    for s in STOCKS:
        qty = st.session_state.portfolio[s]["qty"]
        total += qty * st.session_state.prices[s]
    return total

# store portfolio history
st.session_state.portfolio_history.append(portfolio_value())
if len(st.session_state.portfolio_history) > 50:
    st.session_state.portfolio_history.pop(0)

# -----------------------------
# BUY / SELL
# -----------------------------
def buy(stock, qty):
    price = st.session_state.prices[stock]
    cost = price * qty

    if st.session_state.cash >= cost:
        p = st.session_state.portfolio[stock]
        new_qty = p["qty"] + qty
        new_avg = ((p["qty"] * p["avg_price"]) + cost) / new_qty

        p["qty"] = new_qty
        p["avg_price"] = new_avg
        st.session_state.cash -= cost

def sell(stock, qty):
    p = st.session_state.portfolio[stock]

    if p["qty"] >= qty:
        price = st.session_state.prices[stock]
        st.session_state.cash += price * qty
        p["qty"] -= qty

# -----------------------------
# UI HEADER
# -----------------------------
st.title("📊 AI Stock Market Simulator (Groww-like)")

# -----------------------------
# SIDEBAR
# -----------------------------
with st.sidebar:
    st.header("💼 Portfolio Summary")

    total = portfolio_value()
    pnl = total - 100000

    st.metric("Cash", f"₹{st.session_state.cash:,.2f}")
    st.metric("Total Value", f"₹{total:,.2f}")
    st.metric("P&L", f"₹{pnl:,.2f}")

    st.divider()
    st.subheader("Holdings")

    for s in STOCKS:
        qty = st.session_state.portfolio[s]["qty"]
        if qty > 0:
            st.write(f"{s}: {qty}")

# -----------------------------
# LIVE MARKET
# -----------------------------
st.subheader("📈 Live Market")

cols = st.columns(len(STOCKS))

for i, s in enumerate(STOCKS):
    price = st.session_state.prices[s]
    hist = st.session_state.history[s]

    change = np.random.uniform(-2, 2)

    with cols[i]:
        st.markdown(f"### {s}")
        st.metric("Price", f"₹{price:.2f}", f"{change:.2f}%")

        if len(hist) > 2:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                y=hist,
                mode="lines",
                line=dict(color="green" if change > 0 else "red")
            ))
            fig.update_layout(height=120,
                              margin=dict(l=0, r=0, t=0, b=0),
                              xaxis=dict(visible=False),
                              yaxis=dict(visible=False))
            st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# TRADE SECTION
# -----------------------------
st.subheader("💰 Trade Stocks")

c1, c2, c3 = st.columns(3)

with c1:
    stock = st.selectbox("Stock", STOCKS)

with c2:
    qty = st.number_input("Qty", 1, 1000, 1)

with c3:
    st.write("")
    if st.button("BUY 🟢"):
        buy(stock, qty)
        st.success("Bought!")

    if st.button("SELL 🔴"):
        if st.session_state.portfolio[stock]["qty"] >= qty:
            sell(stock, qty)
            st.success("Sold!")
        else:
            st.error("Not enough shares")

# -----------------------------
# PORTFOLIO TABLE
# -----------------------------
st.subheader("📊 Portfolio Details")

data = []

for s in STOCKS:
    qty = st.session_state.portfolio[s]["qty"]
    avg = st.session_state.portfolio[s]["avg_price"]
    current = st.session_state.prices[s]

    pnl = (current - avg) * qty if qty > 0 else 0

    data.append([s, qty, avg, current, pnl])

df = pd.DataFrame(data, columns=["Stock", "Qty", "Avg", "Current", "P&L"])
st.dataframe(df, use_container_width=True)

# -----------------------------
# 📊 PIE CHART
# -----------------------------
st.subheader("📊 Portfolio Allocation")

labels, values = [], []

for s in STOCKS:
    qty = st.session_state.portfolio[s]["qty"]
    val = qty * st.session_state.prices[s]

    if val > 0:
        labels.append(s)
        values.append(val)

if values:
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.4)])
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No holdings yet")

# -----------------------------
# 📈 PORTFOLIO GROWTH
# -----------------------------
st.subheader("📈 Portfolio Growth")

fig = go.Figure()
fig.add_trace(go.Scatter(
    y=st.session_state.portfolio_history,
    mode="lines",
    line=dict(color="blue", width=3)
))

fig.update_layout(height=400)
st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# 📉 P&L BAR CHART
# -----------------------------
st.subheader("📉 Stock-wise P&L")

stocks, profits = [], []

for s in STOCKS:
    qty = st.session_state.portfolio[s]["qty"]
    avg = st.session_state.portfolio[s]["avg_price"]
    current = st.session_state.prices[s]

    if qty > 0:
        pnl = (current - avg) * qty
        stocks.append(s)
        profits.append(pnl)

if stocks:
    fig = go.Figure(data=[
        go.Bar(
            x=stocks,
            y=profits,
            marker_color=["green" if p > 0 else "red" for p in profits]
        )
    ])
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No active positions")

# -----------------------------
# FOOTER
# -----------------------------
st.caption("⚠️ Simulation only — no real trading or money involved.")
