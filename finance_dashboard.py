import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

REFRESH_INTERVAL = 60
STOCKS = ["AAPL", "GOOGL", "MSFT", "TSLA"]

def get_stock_data(symbol):
    ticker = yf.Ticker(symbol)
    df = ticker.history(period="1d", interval="5m")
    if df.empty:
        return None
    return df

st.set_page_config(page_title="Live Finance Dashboard", layout="wide")
st.title("📈 Live Stock Price Dashboard")
st.caption(f"Auto-refreshes every {REFRESH_INTERVAL} seconds")

st_autorefresh(interval=60000, key="refresh")

selected = st.selectbox("Select a Stock Symbol", STOCKS)

df = get_stock_data(selected)

if df is None:
    st.error("⚠️ Could not fetch data. Market may be closed.")
else:
    last_price = df["Close"].iloc[-1]
    prev_price = df["Close"].iloc[-2]
    change = last_price - prev_price
    pct_change = (change / prev_price) * 100

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Last Price", f"${last_price:.2f}", f"{change:+.2f}")
    col2.metric("% Change", f"{pct_change:+.2f}%")
    col3.metric("Day High", f"${df['High'].max():.2f}")
    col4.metric("Day Low",  f"${df['Low'].min():.2f}")

    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        name=selected
    )])
    fig.update_layout(
        title=f"{selected} — Intraday (5-min intervals)",
        xaxis_title="Time", yaxis_title="Price (USD)",
        xaxis_rangeslider_visible=False,
        template="plotly_dark", height=450
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📊 Volume")
    st.bar_chart(df["Volume"])

    with st.expander("🔍 View Raw Data"):
        st.dataframe(df.tail(20).sort_index(ascending=False))

st.caption(f"⏱ Last updated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")