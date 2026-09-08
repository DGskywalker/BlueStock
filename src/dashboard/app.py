#!/usr/bin/env python3
"""
Main Streamlit Entry Point (src/dashboard/app.py)
Multi-page dashboard application supporting all 8 screens:
  1. Home Overview (pages/01_home.py)
  2. Company 360 Profile (pages/02_profile.py)
  3. Interactive Screener (pages/03_screener.py)
  4. Peer Comparison (pages/04_peers.py)
  5. Trend Analysis (pages/05_trends.py)
  6. Sector Deep Dive (pages/06_sectors.py)
  7. Capital Allocation Map (pages/07_capital.py)
  8. Annual Reports (pages/08_reports.py)
"""

import sys
import os
import streamlit as st

# Ensure root directory is on sys.path
sys.path.insert(0, os.path.abspath("."))

# Page Config
st.set_page_config(
    page_title="Nifty 100 Analytics Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar App Branding & Navigation
st.sidebar.title("🔷 BlueStock Fintech")
st.sidebar.markdown("**Nifty 100 Analytics Platform**")
st.sidebar.markdown("---")

# Navigation Menu
nav_selection = st.sidebar.radio(
    "Navigation Menu",
    [
        "01 🏠 Home Overview",
        "02 🔍 Company Profile",
        "03 ⚡ Stock Screener",
        "04 🎯 Peer Analytics",
        "05 📈 Trend Analysis",
        "06 🏭 Sector Analysis",
        "07 🗺️ Capital Allocation",
        "08 📑 Annual Reports"
    ]
)

st.sidebar.markdown("---")

# Render Selected Screen Module
if "01" in nav_selection:
    from pages import page_01_home
    page_01_home.render_home_page()
elif "02" in nav_selection:
    from pages import page_02_profile
    page_02_profile.render_profile_page()
elif "03" in nav_selection:
    from pages import page_03_screener
    page_03_screener.render_screener_page()
elif "04" in nav_selection:
    from pages import page_04_peers
    page_04_peers.render_peers_page()
elif "05" in nav_selection:
    from pages import page_05_trends
    page_05_trends.render_trends_page()
elif "06" in nav_selection:
    from pages import page_06_sectors
    page_06_sectors.render_sectors_page()
elif "07" in nav_selection:
    from pages import page_07_capital
    page_07_capital.render_capital_page()
elif "08" in nav_selection:
    from pages import page_08_reports
    page_08_reports.render_reports_page()
