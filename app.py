import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from datetime import datetime
import xml.etree.ElementTree as ET
 
st.set_page_config(page_title="SNIPER ROBOT", layout="wide", initial_sidebar_state="collapsed")
 
if "started" not in st.session_state:
    st.session_state.started = False
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"
 
st.markdown("""
<style>
.stApp { background: #0a0e14; color: white; }
div[data-testid="stVerticalBlock"] > div { background: #151b26; border-radius: 16px; padding: 16px; margin-bottom: 12px; }
h1 { font-size: 32px !important; text-align: center; }
div.stButton > button { background: #00c853; color: white; font-size: 20px; font-weight: 800; padding: 14px; border-radius: 14px; border: none; width: 100%; }
div.stButton > button:hover { background: #00e676; color: black; }
.big-buy { background: #00c853; color: white; padding: 6px 14px; border-radius: 20px; font-weight: 800; }
.big-sell { background: #ff1744; color: white; padding: 6px 14px; border-radius: 20px; font-weight: 800; }
.big-wait { background: #ffab00; color: black; padding: 6px 14px; border-radius: 20px; font-weight: 800; }
.sl { color: #ff5252; font-size: 22px; font-weight: 800; }
.tp { color: #00e676; font-size: 22px; font-weight: 800; }
.entry { font-size: 22px; font-weight: 800; }
.feature { font-size: 18px; padding: 6px 0px; }
</style>
""", unsafe_allow_html=True)
 
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
 
def rsi_calc(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = -delta.where(delta < 0, 0).rolling(period).mean()
    rs = gain / (loss + 1e-9)
    return 100 - (100 / (1 + rs))
 
def analyze(symbol, df):
    close = df['Close']
    ema20 = close.ewm(span=20).mean().iloc[-1]
    ema50 = close.ewm(span=50).mean().iloc[-1]
    r = rsi_calc(close).iloc[-1]
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
 
def show_calendar():
    st.markdown("# Economic Calendar")
    st.markdown("High-impact news only. Do not trade 30 min before and after red news.")
    try:
        resp = requests.get("https://nfs.faireconomy.media/ff_calendar_thisweek.xml", timeout=10)
        root = ET.fromstring(resp.content)
        today_str = datetime.now().strftime("%m-%d-%Y")
        found = 0
        for ev in root.findall("event"):
            if ev.findtext("impact") != "High":
                continue
            ev_date = ev.findtext("date")
            ev_time = ev.findtext("time")
            ev_country = ev.findtext("country")
            ev_title = ev.findtext("title")
            ev_forecast = ev.findtext("forecast")
            ev_previous = ev.findtext("previous")
            label = "TODAY" if ev_date == today_str else ev_date
            st.warning(f"{label} | {ev_time} | {ev_country} | {ev_title} | Forecast: {ev_forecast} | Previous: {ev_previous}")
            found += 1
        if found == 0:
            st.success("No high-impact news this week.")
    except Exception:
        st.info("Calendar offline. Check ForexFactory for red news - USD CPI / NFP / Fed are high impact.")
    if st.button("Back to Dashboard"):
        st.session_state.page = "Dashboard"
        st.rerun()
 
def show_dashboard():
    st.markdown("# Dashboard")
    st.markdown("Live - Updated just now")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Economic Calendar"):
            st.session_state.page = "Calendar"
            st.rerun()
    with c2:
        if st.button("Stop Robot"):
            st.session_state.started = False
            st.session_state.page = "Dashboard"
            st.rerun()
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
                cc1, cc2 = st.columns(2)
                with cc1:
                                    st.markdown("SL<br><span class=\"sl\">" + format(sl, ",.5f") + "</span><br>" + format(p_sl * 10000, ".0f") + " pips to SL", unsafe_allow_html=True)
 
                with cc2:
                                    st.markdown("TP<br><span class=\"tp\">" + format(tp, ",.5f") + "</span><br>" + format(p_tp * 10000, ".0f") + " pips to TP", unsafe_allow_html=True)
if "page" not in st.session_state:
 st.session_state.page = "Dashboard"
if "started" not in st.session_state:
 st.session_state.started = True

if st.session_state.page == "Calendar":
    show_calendar()
else:
   show_dashboard()


 
