import streamlit as st
import pandas as pd
from src.dashboard.utils.db import get_ratios
from src.screener.engine import ScreenerEngine, load_screener_config

def render_screener_page():
    st.title("⚡ Interactive Stock Screener & Filter Engine")
    st.markdown("Filter Nifty 100 universe using custom sliders or preset strategy buttons.")

    screener_engine = ScreenerEngine()
    config = screener_engine.config

    # Load Latest Year Ratios
    df_ratios = get_ratios(year=2024)
    if df_ratios.empty:
        st.warning("No ratio data available.")
        return

    # Sidebar 6 Preset Strategy Buttons
    st.sidebar.subheader("🎯 Preset Screening Strategies")
    preset_col1, preset_col2 = st.sidebar.columns(2)
    
    if "screener_filters" not in st.session_state:
        st.session_state.screener_filters = {}

    if preset_col1.button("🏆 Quality"):
        st.session_state.screener_filters = config["presets"]["quality_compounder"]["filters"]
    if preset_col2.button("💎 Value"):
        st.session_state.screener_filters = config["presets"]["value_pick"]["filters"]
    if preset_col1.button("🚀 Growth"):
        st.session_state.screener_filters = config["presets"]["growth_accelerator"]["filters"]
    if preset_col2.button("💰 Dividend"):
        st.session_state.screener_filters = config["presets"]["dividend_champion"]["filters"]
    if preset_col1.button("🛡️ Debt-Free"):
        st.session_state.screener_filters = config["presets"]["debt_free_blue_chip"]["filters"]
    if preset_col2.button("🔄 Turnaround"):
        st.session_state.screener_filters = config["presets"]["turnaround_watch"]["filters"]

    # 10 Metric Sliders
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎛️ Metric Threshold Sliders")

    sf = st.session_state.screener_filters
    
    roe_min = st.sidebar.slider("ROE Min (%)", 0.0, 50.0, float(sf.get("return_on_equity_pct_min", 0.0)))
    de_max = st.sidebar.slider("D/E Max", 0.0, 5.0, float(sf.get("debt_to_equity_max", 5.0)))
    fcf_min = st.sidebar.slider("FCF Min (₹ Cr)", -1000.0, 10000.0, float(sf.get("free_cash_flow_cr_min", -1000.0)))
    rev_cagr_min = st.sidebar.slider("Revenue CAGR 5Y Min (%)", -20.0, 50.0, float(sf.get("revenue_cagr_5yr_min", -20.0)))
    pat_cagr_min = st.sidebar.slider("PAT CAGR 5Y Min (%)", -20.0, 50.0, float(sf.get("pat_cagr_5yr_min", -20.0)))
    opm_min = st.sidebar.slider("OPM Min (%)", 0.0, 50.0, float(sf.get("operating_profit_margin_pct_min", 0.0)))
    pe_max = st.sidebar.slider("P/E Max", 5.0, 100.0, float(sf.get("pe_ratio_max", 100.0)))
    pb_max = st.sidebar.slider("P/B Max", 0.5, 20.0, float(sf.get("pb_ratio_max", 20.0)))
    div_min = st.sidebar.slider("Dividend Yield Min (%)", 0.0, 10.0, float(sf.get("dividend_yield_min", 0.0)))
    icr_min = st.sidebar.slider("Interest Coverage Min", 0.0, 50.0, float(sf.get("interest_coverage_min", 0.0)))

    active_filters = {
        "return_on_equity_pct_min": roe_min,
        "debt_to_equity_max": de_max,
        "free_cash_flow_cr_min": fcf_min,
        "revenue_cagr_5yr_min": rev_cagr_min,
        "pat_cagr_5yr_min": pat_cagr_min,
        "operating_profit_margin_pct_min": opm_min,
        "pe_ratio_max": pe_max,
        "pb_ratio_max": pb_max,
        "dividend_yield_min": div_min,
        "interest_coverage_min": icr_min
    }

    # Run Screener Engine Filter
    df_filtered = screener_engine.filter_universe(df_ratios, active_filters)
    match_cnt = len(df_filtered)

    # Result Header & CSV Download Button
    head_col1, head_col2 = st.columns([3, 1])
    with head_col1:
        st.subheader(f"✅ Filter Results: {match_cnt} Companies Match Your Criteria")
    with head_col2:
        if not df_filtered.empty:
            csv_data = df_filtered.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Export Results CSV",
                data=csv_data,
                file_name="screener_results.csv",
                mime="text/csv"
            )

    # Display Table
    if not df_filtered.empty:
        disp_cols = ["ticker", "company_name", "sector", "composite_quality_score",
                     "return_on_equity_pct", "debt_to_equity", "free_cash_flow_cr",
                     "revenue_cagr_5yr", "pat_cagr_5yr", "pe_ratio"]
        existing_cols = [c for c in disp_cols if c in df_filtered.columns]
        
        df_disp = df_filtered[existing_cols].copy()
        df_disp.columns = ["Ticker", "Company", "Sector", "Quality Score", "ROE (%)", "D/E", "FCF (Cr)", "5Y Rev CAGR", "5Y PAT CAGR", "P/E"]
        st.dataframe(df_disp, hide_index=True, use_container_width=True)
    else:
        st.info("No companies match the selected filter criteria. Try relaxing your threshold sliders.")

if __name__ == "__main__" or "render_screener_page" in dir():
    render_screener_page()
