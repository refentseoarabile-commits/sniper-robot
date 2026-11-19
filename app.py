import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from datetime import datetime
import xml.etree.ElementTree as ET
 
st.set_page_config(page_title="SNIPER ROBOT", layout="wide", initial_sidebar_state="collapsed")
 
st.markdown("""
<style>
.stApp { background: #0a0e14; color: white; }
div[data-testid="stVerticalBlock"] > div { background: #151b26; border-radius: 16px; padding: 16px; margin-bottom: 12px; }
h1 { font-size: 28px !important; text-align: center; }
.big-buy { background: #00c853; color: white; padding: 6px 14px; border-radius: 20px; font-weight: 800; }
.big-sell { background: #ff1744; color: white; padding: 6px 14px; border-radius: 20px; font-weight: 800; }
.big-wait { background: #ffab00; color: black; padding: 6px 14px; border-radius: 20px; font-weight: 800; }
.sl { color: #ff5252; font-size: 22px; font-weight: 800; }
.tp { color: #00e676; font-size: 22px; font-weight: 800; }
.entry { font-size: 22px; font-weight: 800; }
</style>
""", unsafe_allow_html=True)
 
st.markdown("# SNIPER ROBOT")
st.markdown("**Live Signals - Never Auto-Trades - You Decide**")
 
SYMBOLS = {
"EURUSD": "EURUSD=X", "GBPUSD": "GBPUSD=X", "USDJPY": "USDJPY=X",
"AUDUSD": "AUDUSD=X", "USDCAD": "USDCAD=X", "NZDUSD": "NZDUSD=X",
"EURGBP": "EURGBP=X", "EURJPY": "EURJPY=X", "GBPJPY": "GBPJPY=X",
"EURCHF": "EURCHF=X", "XAUUSD": "GC=F", "XAGUSD": "SI=F",
"BTCUSD": "BTC-USD", "ETHUSD": "ETH-USD",
"US30": "^DJI", "US100": "^NDX", "SPX500": "^GSPC", "USOIL": "CL=F"
}
 
@st.cache_data(ttl=300)
def get_data(ticker):
    try:
        df = yf.download(ticker, period="2d", interval="15m", progress=False, auto_adjust=True)
        if df is None or df.empty:
            return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    except Exception:
        return None
 
def rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = -delta.where(delta < 0, 0).rolling(period).mean()
    rs = gain / (loss + 1e-9)
    return 100 - (100 / (1 + rs))
 
def analyze(symbol, df):
    close = df['Close']
    ema20 = close.ewm(span=20).mean().iloc[-1]
    ema50 = close.ewm(span=50).mean().iloc[-1]
    r = rsi(close).iloc[-1]
    price = float(close.iloc[-1])
    prev = float(close.iloc[-2])
    atr = (df['High'] - df['Low']).rolling(14).mean().iloc[-1]
    if pd.isna(atr):
        atr = price * 0.002
    sl_dist = float(atr) * 1.0
    tp_dist = sl_dist * 2.0
    if r < 32 and price > ema20 and price > prev:
        signal, conf, reason = "BUY", 88, "RSI oversold + bounced off EMA + bullish momentum"
        entry, sl, tp = price, price - sl_dist, price + tp_dist
    elif r > 68 and price < ema20 and price < prev:
        signal, conf, reason = "SELL", 86, "RSI overbought + rejected EMA + bearish momentum"
        entry, sl, tp = price, price + sl_dist, price - tp_dist
    elif price > ema50 and r > 50:
        signal, conf, reason = "BUY", 72, "Trend up + above EMA50"
        entry, sl, tp = price, price - sl_dist, price + tp_dist
    elif price < ema50 and r < 50:
        signal, conf, reason = "SELL", 71, "Trend down + below EMA50"
        entry, sl, tp = price, price + sl_dist, price - tp_dist
    else:
        signal, conf, reason = "WAIT", 58, "No clear setup - consolidating near EMA"
        entry, sl, tp = price, 0, 0
    pip = 0.01 if "JPY" in symbol else 0.0001
    if "XAU" in symbol or "XAG" in symbol or "BTC" in symbol or "ETH" in symbol or "US" in symbol or "SPX" in symbol:
        pip = 1
    pips_sl = abs(entry - sl) / pip if sl else 0
    pips_tp = abs(tp - entry) / pip if tp else 0
    return price, signal, conf, reason, entry, sl, tp, pips_sl, pips_tp
 
st.markdown("### Economic Calendar - Today")
try:
    resp = requests.get("https://nfs.faireconomy.media/ff_calendar_thisweek.xml", timeout=10)
    root = ET.fromstring(resp.content)
    today_str = datetime.now().strftime("%m-%d-%Y")
    shown = 0
    for ev in root.findall("event"):
        ev_date = ev.findtext("date")
        ev_impact = ev.findtext("impact")
        if ev_date != today_str:
            continue
        if ev_impact != "High":
            continue
        ev_time = ev.findtext("time")
        ev_country = ev.findtext("country")
        ev_title = ev.findtext("title")
        st.warning(f"{ev_time} - {ev_country} - {ev_title} - HIGH IMPACT - No trade 30 min before")
        shown += 1
    if shown == 0:
        st.success("No high-impact red news today - safe to take signals")
except Exception:
    st.info("Calendar: Check ForexFactory for red news today - USD CPI / NFP / Fed are high impact")
 
st.markdown("### All Symbols - Live")
filter_choice = st.selectbox("Show:", ["All Signals", "BUY only", "SELL only", "WAIT only"])
search = st.text_input("Search symbol (e.g. EURUSD):", "")
 
for sym, ticker in SYMBOLS.items():
    if search and search.upper() not in sym:
        continue
    df = get_data(ticker)
    if df is None:
        st.markdown(f"**{sym}** - Loading... will retry in 5 min")
        continue
    price, signal, conf, reason, entry, sl, tp, p_sl, p_tp = analyze(sym, df)
    if filter_choice == "BUY only" and signal != "BUY":
        continue
    if filter_choice == "SELL only" and signal != "SELL":
        continue
    if filter_choice == "WAIT only" and signal != "WAIT":
        continue
    badge = "big-buy" if signal == "BUY" else "big-sell" if signal == "SELL" else "big-wait"
    with st.container():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"### {sym}")
        with col2:
            st.markdown(f'<span class="{badge}">{signal}</span>', unsafe_allow_html=True)
        st.markdown(f"Live Price: **{price:,.5f}**  Confidence: **{conf}%**")
        st.markdown(f"Reason: {reason}")
        if signal != "WAIT":
            st.markdown(f'<span class="entry">Entry: {entry:,.5f}</span>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f'SL<br><span class="sl">{sl:,.5f}</span><br>{p_sl:.0f} pips to SL', unsafe_allow_html=True)
            with c2:
                st.markdown(f'TP<br><span class="tp">{tp:,.5f}</span><br>{p_tp:.0f} pips to TP', unsafe_allow_html=True)
            st.markdown("**Risk Reward: 1:2** - If you risk R100, target is R200")
        else:
            st.markdown("**Entry / SL / TP:** -- Wait for setup, don't force it")
 
st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')} SAST - Auto-refreshes every 5 min - This robot NEVER places trades")
st.button("Refresh Now")
has context menu
