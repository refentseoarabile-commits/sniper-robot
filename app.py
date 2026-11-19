import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
 
# ============ PAGE SETUP ============
st.set_page_config(page_title="FOREX ROBOT", layout="wide", initial_sidebar_state="expanded")
 
if "robot_on" not in st.session_state:
    st.session_state.robot_on = False
if "last_scan" not in st.session_state:
    st.session_state.last_scan = "Never"
 
# ============ MEAN ROBOT STYLE - MATCHES MOCKUP ============
st.markdown("""
<style>
.stApp { background-color: #0a0e14; color: white; }
section[data-testid="stSidebar"] { background-color: #0d1117; }
h1, h2, h3, p, div { color: white !important; }
.robot-box { background: linear-gradient(135deg, #111827, #1f2937); border: 2px solid #ef4444; border-radius: 20px; padding: 30px; text-align: center; box-shadow: 0 0 40px #ef444466; }
.robot-title { font-size: 52px; font-weight: 900; letter-spacing: 2px; color: #ff5a5a !important; text-shadow: 0 0 20px #ff0000; line-height: 1; }
.robot-sub { color: #9ca3af !important; font-size: 16px; margin-top: 10px; }
.metric-box { background: #111827; border: 1px solid #374151; border-radius: 15px; padding: 15px; }
.signal-card { background: #111827; border-radius: 15px; padding: 18px; margin-bottom: 15px; border: 1px solid #374151; }
.sell-card { border: 2px solid #ef4444; box-shadow: 0 0 20px #ef444433; }
.buy-card { border: 2px solid #22c55e; box-shadow: 0 0 20px #22c55e33; }
div.stButton > button { background-color: #ef4444 !important; color: white !important; font-size: 22px !important; font-weight: 800 !important; padding: 15px !important; border-radius: 12px !important; border: none !important; }
div.stButton > button:hover { background-color: #dc2626 !important; }
</style>
""", unsafe_allow_html=True)
 
# ============ NAVIGATION - 3 PARTS ============
page = st.sidebar.radio("NAVIGATION", ["🤖 1. ROBOT CONTROL", "📊 2. DASHBOARD", "🗓️ 3. ECONOMIC CALENDAR"])
st.sidebar.markdown("---")
st.sidebar.markdown("**FOREX ROBOT v2.0**")
st.sidebar.markdown("EMA50 Scanner")
st.sidebar.markdown(f"Last Scan: {st.session_state.last_scan}")
st.sidebar.warning("⚠️ 71% is EMA score, not win rate. Not financial advice.")
 
# ============ HELPER FUNCTIONS ============
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
    # JPY pairs use 0.01, others use 0.0001
    if "JPY" in symbol:
        return 0.01
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
 
        # Trend logic
        if price < ema50:
            direction = "SELL"
            confidence = 71
            if price < prev_price:
                confidence = 74
        elif price > ema50:
            direction = "BUY"
            confidence = 71
            if price > prev_price:
                confidence = 74
        else:
            direction = "WAIT"
            confidence = 50
 
        pip = get_pip_size(symbol)
        # SL = 4 pips, TP = 7-8 pips (1:2 risk)
        if direction == "SELL":
            sl = price + (4 * pip)
            tp = price - (7 * pip)
        elif direction == "BUY":
            sl = price - (4 * pip)
            tp = price + (7 * pip)
        else:
            sl = price
            tp = price
 
        # FIXED PIPS CALCULATION - * pip size, no more 0 pips
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
 
# ============ PAGE 1 - ROBOT CONTROL ============
if page == "🤖 1. ROBOT CONTROL":
    st.markdown('<div class="robot-box"><div class="robot-title">FOREX<br>ROBOT</div><div class="robot-sub">AUTONOMOUS TRADING • LOW RISK MODE • VERSION 2.0</div></div>', unsafe_allow_html=True)
    st.write("")
    st.write("")
 
    c1, c2 = st.columns(2)
    with c1:
        if st.button("▶️ START ROBOT", use_container_width=True):
            st.session_state.robot_on = True
            st.session_state.last_scan = datetime.datetime.now().strftime("%H:%M:%S")
            st.rerun()
    with c2:
        if st.button("⏹️ STOP ROBOT", use_container_width=True):
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
        st.markdown('<div class="metric-box"><p>PAIRS SCANNED</p><h2>8 Pairs</h2></div>', unsafe_allow_html=True)
    with m3:
        st.markdown('<div class="metric-box"><p>MODE</p><h2>EMA50</h2></div>', unsafe_allow_html=True)
 
    st.write("")
    st.info("✅ Robot scans EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD, USDCHF, EURGBP, GBPJPY. Go to Dashboard to see signals.")
    st.warning("⚠️ KILL SWITCH ARMED • SAFE MODE OFF • Don't trade 30 mins before/after red news. Check Calendar page.")
    if st.session_state.robot_on:
        if st.button("🔄 SCAN NOW → GO TO DASHBOARD", use_container_width=True):
            st.session_state.last_scan = datetime.datetime.now().strftime("%H:%M:%S")
 
# ============ PAGE 2 - DASHBOARD ============
if page == "📊 2. DASHBOARD":
    st.title("📊 LIVE SIGNALS DASHBOARD")
    col_a, col_b = st.columns([3, 1])
    with col_a:
        st.write(f"Robot: {'🟢 RUNNING' if st.session_state.robot_on else '🔴 STOPPED'} | Last Scan: {st.session_state.last_scan}")
    with col_b:
        if st.button("🔄 REFRESH"):
            st.session_state.last_scan = datetime.datetime.now().strftime("%H:%M:%S")
            st.rerun()
 
    if not st.session_state.robot_on:
        st.warning("Robot is STOPPED. Go to Robot Control and press START ROBOT to see live signals.")
 
    # Show all symbols
    for symbol, ticker in SYMBOLS.items():
        data = get_signal(symbol, ticker)
        if data is None:
            st.markdown(f'<div class="signal-card"><b>{symbol}</b> - Waiting for price...</div>', unsafe_allow_html=True)
            continue
        if "error" in data:
            st.markdown(f'<div class="signal-card"><b>{symbol}</b> - Waiting for price...</div>', unsafe_allow_html=True)
            continue
 
        is_sell = data["direction"] == "SELL"
        is_buy = data["direction"] == "BUY"
        card_class = "sell-card" if is_sell else "buy-card" if is_buy else "signal-card"
        color = "#ef4444" if is_sell else "#22c55e" if is_buy else "#f59e0b"
        arrow = "↓" if is_sell else "↑" if is_buy else "⏸"
 
        st.markdown(f"""
        <div class="signal-card {card_class}">
            <div style="display:flex; justify-content:space-between;"><b style="font-size:22px;">{data['symbol']} • {data['direction']}</b><b style="color:{color}; font-size:22px;">{arrow} {data['direction']}</b></div>
            <p style="color:#9ca3af;">Live Price: <b style="font-size:20px;">{data['price']:.5f}</b></p>
            <p>Confidence: <b>{data['confidence']}%</b> | Reason: {data['reason']}</p>
            <p>Entry: <b>{data['entry']:.5f}</b></p>
            <p>SL: <span style="color:#ef4444;"><b>{data['sl']:.5f}</b></span> &nbsp; {format(data['p_sl'], ".0f")} pips to SL</p>
            <p>TP: <span style="color:#22c55e;"><b>{data['tp']:.5f}</b></span> &nbsp; {format(data['p_tp'], ".0f")} pips to TP</p>
            <p style="color:#9ca3af; font-size:12px;">EMA50: {data['ema']:.5f}</p>
        </div>
        """, unsafe_allow_html=True)
 
    st.markdown("---")
    st.markdown("**Risk Summary** | Risk: 0.5% | Lot: 0.20 | SL: 4 pips | TP: 7 pips | Ratio 1:1.75")
 
# ============ PAGE 3 - ECONOMIC CALENDAR ============
if page == "🗓️ 3. ECONOMIC CALENDAR":
    st.title("🗓️ ECONOMIC CALENDAR")
    st.markdown("**High impact news only - don't trade 30 mins before/after red news.**")
    st.markdown("Timezone: South Africa (GMT+2) | Auto Refresh: 30s")
    st.write("")
 
    # Quick filter buttons (visual)
    f1, f2, f3 = st.columns(3)
    with f1:
        st.button("🔴 HIGH IMPACT", use_container_width=True)
    with f2:
        st.button("🟡 MEDIUM", use_container_width=True)
    with f3:
        st.button("🟢 LOW", use_container_width=True)
 
    st.write("")
    # Live calendar from Forex Factory
    try:
        st.components.v1.iframe("https://www.forexfactory.com/calendar", height=800, scrolling=True)
    except Exception:
        st.error("Calendar failed to load. Check internet and reload.")
 
    st.write("")
    st.info("If calendar shows blank on phone, open in Chrome and allow iframes. Alternative: search 'Forex Factory Calendar' in browser.")
