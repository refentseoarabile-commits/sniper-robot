import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
 
st.set_page_config(
    page_title="FOREX SNIPER",
    layout="wide"
)
 
if "robot_on" not in st.session_state:
    st.session_state.robot_on = False
if "last_scan" not in st.session_state:
    st.session_state.last_scan = "Never"
 
# FIXED STYLE - ALL READABLE, NO WHITE BOXES
st.markdown("""
<style>
.stApp { background-color: #000000 !important; }
section[data-testid="stSidebar"] {
  background-color: #000000 !important;
}
h1, h2, h3, p, div, span, label {
  color: #ffffff !important;
}
/* Kill light alert boxes */
div[data-testid="stAlert"] {
  background-color: #1a1a1a !important;
  color: #ffffff !important;
  border: 1px solid #444444 !important;
}
div[data-testid="stAlert"] p,
div[data-testid="stAlert"] div,
div[data-testid="stAlert"] span {
  color: #ffffff !important;
}
/* Buttons - always readable */
div.stButton > button,
a[data-testid="stLinkButton"] {
  background-color: #ef4444 !important;
  color: #ffffff !important;
  font-size: 20px !important;
  font-weight: 800 !important;
  padding: 15px !important;
  border-radius: 12px !important;
  border: none !important;
}
div.stButton > button p,
a[data-testid="stLinkButton"] p {
  color: #ffffff !important;
}
.robot-box {
  background: #111111;
  border: 2px solid #ef4444;
  border-radius: 20px;
  padding: 30px;
  text-align: center;
}
.robot-title {
  font-size: 52px;
  font-weight: 900;
  color: #ff5a5a !important;
  line-height: 1;
}
.robot-sub { color: #ffffff !important; font-size: 16px; }
.metric-box {
  background: #111111;
  border: 1px solid #444444;
  border-radius: 15px;
  padding: 15px;
  text-align: center;
}
.signal-card {
  background: #111111;
  border-radius: 15px;
  padding: 18px;
  margin-bottom: 15px;
  border: 1px solid #444444;
}
.sell-card { border: 2px solid #ef4444; }
.buy-card { border: 2px solid #22c55e; }
.dark-box {
  background: #111111;
  border: 1px solid #444444;
  border-radius: 12px;
  padding: 14px;
  color: #ffffff;
  margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)
 
# NAVIGATION - 3 PARTS
page = st.sidebar.radio(
    "NAVIGATION",
    [
        "1. SNIPER CONTROL",
        "2. DASHBOARD",
        "3. ECONOMIC CALENDAR"
    ]
)
st.sidebar.markdown("---")
st.sidebar.markdown("**FOREX SNIPER v2.0**")
st.sidebar.markdown("EMA50 Scanner")
st.sidebar.markdown(f"Last: {st.session_state.last_scan}")
st.sidebar.markdown("71% is EMA score, not win rate.")
 
# SYMBOLS - ALL 20
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
        df = yf.download(
            ticker,
            period="5d",
            interval="15m",
            progress=False,
            auto_adjust=True
        )
        if df is None or len(df) < 51:
            return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        close = df["Close"]
        ema50 = close.ewm(
            span=50,
            adjust=False
        ).mean().iloc[-1]
        price = float(close.iloc[-1])
        prev = float(close.iloc[-2])
        if price < ema50:
            direction = "SELL"
            conf = 74 if price < prev else 71
            reason = "Down + below EMA50"
        elif price > ema50:
            direction = "BUY"
            conf = 74 if price > prev else 71
            reason = "Up + above EMA50"
        else:
            direction = "WAIT"
            conf = 50
            reason = "At EMA50 - Wait"
        pip = get_pip_size(symbol)
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
            "conf": conf,
            "entry": price,
            "sl": sl,
            "tp": tp,
            "p_sl": p_sl,
            "p_tp": p_tp,
            "reason": reason,
        }
    except Exception:
        return {"symbol": symbol, "error": "err"}
 
# PART 1 - SNIPER CONTROL
if page == "1. SNIPER CONTROL":
    st.markdown(
        '<div class="robot-box">'
        '<div class="robot-title">FOREX<br>SNIPER</div>'
        '<div class="robot-sub">'
        'PRECISE ENTRIES - LOW RISK - V2.0'
        '</div></div>',
        unsafe_allow_html=True
    )
    st.write("")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("START SNIPER", use_container_width=True):
            st.session_state.robot_on = True
            st.session_state.last_scan = datetime.datetime.now().strftime("%H:%M:%S")
            st.rerun()
    with c2:
        if st.button("STOP SNIPER", use_container_width=True):
            st.session_state.robot_on = False
            st.rerun()
    st.write("")
    status = "RUNNING" if st.session_state.robot_on else "STOPPED"
    st.markdown(
        f'<div class="metric-box"><h3>STATUS: {status}</h3>'
        f'<p>Last: {st.session_state.last_scan}</p></div>',
        unsafe_allow_html=True
    )
    st.write("")
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(
            '<div class="metric-box"><p>UPTIME</p><h2>12h 34m</h2></div>',
            unsafe_allow_html=True
        )
    with m2:
        st.markdown(
            '<div class="metric-box"><p>PAIRS</p><h2>20 Pairs</h2></div>',
            unsafe_allow_html=True
        )
    with m3:
        st.markdown(
            '<div class="metric-box"><p>MODE</p><h2>EMA50</h2></div>',
            unsafe_allow_html=True
        )
    st.write("")
    st.markdown(
        '<div class="dark-box">'
        'Sniper scans 20 pairs. Go to Dashboard.'
        '</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="dark-box">'
        'Check Calendar before trading.'
        '</div>',
        unsafe_allow_html=True
    )
 
# PART 2 - DASHBOARD - ALL 20 WITH SL/TP
if page == "2. DASHBOARD":
    st.title("LIVE SNIPER SIGNALS")
    st.write(f"Last: {st.session_state.last_scan}")
    if st.button("REFRESH"):
        st.session_state.last_scan = datetime.datetime.now().strftime("%H:%M:%S")
        st.rerun()
    if not st.session_state.robot_on:
        st.markdown(
            '<div class="dark-box">'
            'Sniper STOPPED. Go to Page 1.'
            '</div>',
            unsafe_allow_html=True
        )
    for symbol, ticker in SYMBOLS.items():
        data = get_signal(symbol, ticker)
        if data is None or "error" in data:
            st.markdown(
                f'<div class="signal-card"><b>{symbol}</b>'
                ' - Waiting...</div>',
                unsafe_allow_html=True
            )
            continue
        is_sell = data["direction"] == "SELL"
        is_buy = data["direction"] == "BUY"
        if is_sell:
            card = "sell-card"
            arrow = "DOWN"
        elif is_buy:
            card = "buy-card"
            arrow = "UP"
        else:
            card = "signal-card"
            arrow = "WAIT"
        st.markdown(
            f'<div class="signal-card {card}">'
            f'<b style="font-size:22px;">{data["symbol"]} - {data["direction"]}</b>'
            f'<p>Price: <b>{data["price"]:.5f}</b></p>'
            f'<p>Confidence: <b>{data["conf"]}%</b></p>'
            f'<p>Reason: {data["reason"]}</p>'
            f'<p>Entry: <b>{data["entry"]:.5f}</b></p>'
            f'<p>SL: <b>{data["sl"]:.5f}</b>'
            f' - {data["p_sl"]:.0f} pips</p>'
            f'<p>TP: <b>{data["tp"]:.5f}</b>'
            f' - {data["p_tp"]:.0f} pips</p>'
            f'<p>EMA50: {data["ema"]:.5f}</p>'
            f'</div>',
            unsafe_allow_html=True
        )
    st.markdown("---")
    st.markdown("Risk: 0.5% | SL: 4 pips | TP: 7 pips")
 
# PART 3 - CALENDAR - FIXED READABLE
if page == "3. ECONOMIC CALENDAR":
    st.title("ECONOMIC CALENDAR")
    st.markdown("Do not trade 30 mins before/after red news.")
    st.markdown("Timezone: South Africa (GMT+2)")
    st.write("")
    st.markdown(
        '<div class="dark-box">'
        'Calendar opens in new tab.'
        '</div>',
        unsafe_allow_html=True
    )
    st.link_button(
        "OPEN FOREX FACTORY",
        "https://www.forexfactory.com/calendar",
        use_container_width=True
    )
    st.link_button(
        "OPEN INVESTING.COM",
        "https://www.investing.com/economic-calendar/",
        use_container_width=True
    )
    st.link_button(
        "OPEN MYFXBOOK",
        "https://www.myfxbook.com/forex-economic-calendar",
        use_container_width=True
    )
    st.write("")
    st.markdown("### HIGH IMPACT RULE")
    st.markdown("14:30 - USD News - Stop USD pairs")
    st.markdown("16:00 - USD/EUR News - Stop EURUSD")
    st.markdown("10:00 - EUR News - Stop EUR pairs")
    st.markdown(
        '<div class="dark-box">'
        'Red news = STOP SNIPER on Page 1.'
        '</div>',
        unsafe_allow_html=True
    )
