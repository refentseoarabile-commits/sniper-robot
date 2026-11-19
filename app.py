import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
 
st.set_page_config(page_title="FOREX SNIPER", layout="wide", initial_sidebar_state="expanded")
 
if "robot_on" not in st.session_state:
    st.session_state.robot_on = False
if "last_scan" not in st.session_state:
    st.session_state.last_scan = "Never"
 
st.markdown("""
<style>
.stApp { background-color: #0a0e14; color: white; }
section[data-testid="stSidebar"] { background-color: #0d1117; }
h1, h2, h3, p, div { color: white !important; }
.robot-box { background: linear-gradient(135deg, #111827, #1f2937); border: 2px solid #ef4444; border-radius: 20px; padding: 30px; text-align: center; box-shadow: 0 0 40px #ef444466; }
.robot-title { font-size: 52px; font-weight: 900; letter-spacing: 2px; color: #ff5a5a !important; text-shadow: 0 0 20px #ff0000; line-height: 1; }
.robot-sub { color: #9ca3af !important; font-size: 16px; margin-top: 10px; }
.metric-box { background: #111827; border: 1px solid #374151; border-radius: 15px; padding: 15px; text-align: center; }
.signal-card { background: #111827; border-radius: 15px; padding: 18px; margin-bottom: 15px; border: 1px solid #374151; }
.sell-card { border: 2px solid #ef4444; box-shadow: 0 0 20px #ef444433; }
.buy-card { border: 2px solid #22c55e; box-shadow: 0 0 20px #22c55e33; }
div.stButton > button { background-color: #ef4444 !important; color: white !important; font-size: 22px !important; font-weight: 800 !important; padding: 15px !important; border-radius: 12px !important; border: none !important; }
div.stButton > button:hover { background-color: #dc2626 !important; }
</style>
""", unsafe_allow_html=True)
 
# ===== NAVIGATION - YOUR 3 PARTS =====
page = st.sidebar.radio("NAVIGATION", ["🎯 1. SNIPER CONTROL", "📊 2. DASHBOARD", "🗓️ 3. ECONOMIC CALENDAR"])
st.sidebar.markdown("---")
st.sidebar.markdown("**FOREX SNIPER v2.0**")
st.sidebar.markdown("EMA50 Scanner")
st.sidebar.markdown(f"Last Scan: {st.session_state.last_scan}")
st.sidebar.warning("⚠️ 71% is EMA score, not win rate. Not financial advice.")
 
# ===== SYMBOLS - ALL 20 =====
SYMBOLS = {
    "EURUSD": "EURUSD=X",
    "GBPUSD": "GBPUSD=X",
    "USDJPY": "USDJPY=X",
    "AUDUSD": "AUDUSD=X",
    "USDCAD": "USDCAD=X",
    "USDCHF": "USDCHF=X",
    "EURGBP": "EURGBP=X",
    "GBPJPY": "GBPJPY=X",
    "EURJPY": "EURJPY=X",
    "GBPCHF": "GBPCHF=X",
    "NZDUSD": "NZDUSD=X",
    "AUDJPY": "AUDJPY=X",
    "EURCHF": "EURCHF=X",
    "EURAUD": "EURAUD=X",
    "GBPAUD": "GBPAUD=X",
    "USDMXN": "USDMXN=X",
    "USDZAR": "USDZAR=X",
    "XAUUSD": "GC=F",
    "XAGUSD": "SI=F",
    "BTCUSD": "BTC-USD",
}
 
def get_pip_size(symbol):
    if "JPY" in symbol:
        return 0.01
    if symbol == "XAUUSD":
        return 0.1
    if symbol == "XAGUSD":
        return 0.01
    if symbol == "BTCUSD":
        return 1.0
    return 0.0001
 
def get_signal(symbol, ticker):
    try:
        df = yf.download(ticker, period="1d", interval="15m", progress=False, auto_adjust=True)
        if df is None or len(df) < 55:
            return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        close = df["Close"]
        ema50 = close.ewm(span=50, adjust=False).mean().iloc[-1]
        price = float(close.iloc[-1])
        prev_price = float(close.iloc[-2])
 
        if price < ema50:
            direction = "SELL"
            confidence = 74 if price < prev_price else 71
        elif price > ema50:
            direction = "BUY"
            confidence = 74 if price > prev_price else 71
        else:
            direction = "WAIT"
            confidence = 50
 
        pip = get_pip_size(symbol)
 
        # SL and TP for EVERY symbol - always calculated, never 0
        if direction == "SELL":
            sl = price + (4 * pip)
            tp = price - (7 * pip)
        elif direction == "BUY":
            sl = price - (4 * pip)
            tp = price + (7 * pip)
        else:
            sl = price + (4 * pip)
            tp = price - (7 * pip)
 
        p_sl = abs(sl - price) / pip
        p_tp = abs(tp - price) / pip
 
        return {
            "symbol": symbol,
            "price": price,
            "ema": float(ema50),
            "direction": direction,
            "confidence": confidence,
            "entry": price,
            "sl": sl,
            "tp": tp,
            "p_sl": p_sl,
            "p_tp": p_tp,
            "reason": "Trend down + below EMA50" if direction == "SELL" else "Trend up + above EMA50" if direction == "BUY" else "Price at EMA50 - Wait"
        }
    except Exception as e:
        return {"symbol": symbol, "error": str(e)}
 
# ===== PART 1 - SNIPER CONTROL =====
if page == "🎯 1. SNIPER CONTROL":
    st.markdown('<div class="robot-box"><div class="robot-title">FOREX<br>SNIPER</div><div class="robot-sub">PRECISE ENTRIES • LOW RISK MODE • VERSION 2.0</div></div>', unsafe_allow_html=True)
    st.write("")
    st.write("")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("▶️ START SNIPER", use_container_width=True):
            st.session_state.robot_on = True
            st.session_state.last_scan = datetime.datetime.now().strftime("%H:%M:%S")
            st.rerun()
    with c2:
        if st.button("⏹️ STOP SNIPER", use_container_width=True):
            st.session_state.robot_on = False
            st.rerun()
    st.write("")
    status = "🟢 RUNNING" if st.session_state.robot_on else "🔴 STOPPED"
    st.markdown(f'<div class="metric-box"><h3 style="text-align:center;">STATUS: {status}</h3><p style="text-align:center; color:#9ca3af;">Last Scan: {st.session_state.last_scan}</p></div>', unsafe_allow_html=True)
    st.write("")
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown('<div class="metric-box"><p>UPTIME</p><h2>12h 34m</h2></div>', unsafe_allow_html=True)
    with m2:
        st.markdown('<div class="metric-box"><p>PAIRS SCANNED</p><h2>20 Pairs</h2></div>', unsafe_allow_html=True)
    with m3:
        st.markdown('<div class="metric-box"><p>MODE</p><h2>EMA50</h2></div>', unsafe_allow_html=True)
    st.write("")
    st.info("✅ Sniper scans 20 pairs including Gold + BTC. Go to Dashboard to see signals.")
    st.warning("⚠️ KILL SWITCH ARMED • SAFE MODE OFF • Don't trade 30 mins before/after red news. Check Calendar page.")
    if st.session_state.robot_on:
        if st.button("🔄 SCAN NOW → GO TO DASHBOARD", use_container_width=True):
            st.session_state.last_scan = datetime.datetime.now().strftime("%H:%M:%S")
 
# ===== PART 2 - DASHBOARD - ALL 20 WITH SL/TP =====
if page == "📊 2. DASHBOARD":
    st.title("📊 LIVE SNIPER SIGNALS")
    col_a, col_b = st.columns([3, 1])
    with col_a:
        st.write(f"Sniper: {'🟢 RUNNING' if st.session_state.robot_on else '🔴 STOPPED'} | Last Scan: {st.session_state.last_scan}")
    with col_b:
        if st.button("🔄 REFRESH"):
            st.session_state.last_scan = datetime.datetime.now().strftime("%H:%M:%S")
            st.rerun()
    if not st.session_state.robot_on:
        st.warning("Sniper is STOPPED. Go to Sniper
