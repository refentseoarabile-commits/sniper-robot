import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
 
# ============ PAGE SETUP ============
st.set_page_config(page_title="FOREX SNIPER", layout="wide", initial_sidebar_state="expanded")
 
if "robot_on" not in st.session_state:
    st.session_state.robot_on = False
if "last_scan" not in st.session_state:
    st.session_state.last_scan = "Never"
 
# ============ STYLE ============
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
 
# ============ NAVIGATION ============
page = st.sidebar.radio("NAVIGATION", ["🎯 1. SNIPER CONTROL", "📊 2. DASHBOARD", "🗓️ 3. ECONOMIC CALENDAR"])
st.sidebar.markdown("---")
st.sidebar.markdown("**FOREX SNIPER v2.0**")
st.sidebar.markdown("EMA50 Scanner")
st.sidebar.markdown(f"Last Scan: {st.session_state.last_scan}")
st.sidebar.warning("⚠️ 71% is EMA score, not win rate. Not financial advice.")
 
# ============ SYMBOLS - 20 PAIRS ============
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
    "GBPCHF
 
