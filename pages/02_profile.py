import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.dashboard.utils.db import get_companies, get_ratios, get_pl, get_prosandcons

def render_profile_page():
    st.title("🔍 Company 360° Profile & Financial Deep Dive")

    df_comp = get_companies()
    if df_comp.empty:
        st.warning("No companies found in database.")
        return

    # Autocomplete Search Box
    ticker_list = df_comp["ticker"].tolist()
    selected_ticker = st.selectbox("Search Company by Ticker or Name:", ticker_list, index=0)

    # Load Company Details
    comp_row = df_comp[df_comp["ticker"] == selected_ticker]
    if comp_row.empty:
        st.error(f"Ticker '{selected_ticker}' not found - please try another.")
        return

    comp_info = comp_row.iloc[0]
    
    # 1. Company Metadata Header Card
    st.markdown(f"""
    <div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
        <h2 style="margin:0; color:#1F497D;">{comp_info['company_name']} ({comp_info['ticker']})</h2>
        <p style="margin:5px 0 0 0; color:#555;"><b>Sector:</b> {comp_info.get('sector', 'N/A')} | <b>Industry:</b> {comp_info.get('industry', 'N/A')} | <b>NSE:</b> {comp_info.get('nse_code', comp_info['ticker'])} | <b>Website:</b> <a href="{comp_info.get('website', '#')}" target="_blank">{comp_info.get('website', 'N/A')}</a></p>
    </div>
    """, unsafe_allow_html=True)

    # Load Latest Year Ratios & P&L
    df_rat = get_ratios(ticker=selected_ticker)
    df_pnl = get_pl(ticker=selected_ticker)

    if df_rat.empty:
        st.info("No ratio records available for this company.")
        return

    latest_rat = df_rat.iloc[-1]

    # 2. 6 KPI Tiles
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("ROE", f"{latest_rat.get('return_on_equity_pct', 0.0):.1f}%")
    k2.metric("ROCE", f"{latest_rat.get('return_on_capital_employed_pct', 0.0):.1f}%")
    k3.metric("NPM", f"{latest_rat.get('net_profit_margin_pct', 0.0):.1f}%")
    k4.metric("D/E", f"{latest_rat.get('debt_to_equity', 0.0):.2f}")
    k5.metric("5Y Rev CAGR", f"{latest_rat.get('revenue_cagr_5yr', 0.0):.1f}%")
    k6.metric("FCF (Latest)", f"₹{latest_rat.get('free_cash_flow_cr', 0.0):,.0f} Cr")

    st.markdown("---")

    # 3. Charts Row: 10-Year Revenue/Profit Bar & Dual-Axis ROE/ROCE Line
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("📈 10-Year Revenue & Net Profit Trend (₹ Cr)")
        if not df_pnl.empty:
            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(x=df_pnl["year"], y=df_pnl["sales"], name="Revenue", marker_color="#1f77b4"))
            fig_bar.add_trace(go.Bar(x=df_pnl["year"], y=df_pnl["pat"], name="Net Profit (PAT)", marker_color="#2ca02c"))
            fig_bar.update_layout(barmode="group", height=380, margin=dict(t=20, b=20, l=10, r=10))
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("P&L trend data not available.")

    with c2:
        st.subheader("📉 10-Year ROE vs ROCE Trend (%)")
        if not df_rat.empty:
            fig_line = go.Figure()
            fig_line.add_trace(go.Scatter(x=df_rat["year"], y=df_rat["return_on_equity_pct"], mode="lines+markers", name="ROE (%)", line=dict(color="#ff7f0e", width=3)))
            fig_line.add_trace(go.Scatter(x=df_rat["year"], y=df_rat["return_on_capital_employed_pct"], mode="lines+markers", name="ROCE (%)", line=dict(color="#9467bd", width=3)))
            fig_line.update_layout(height=380, margin=dict(t=20, b=20, l=10, r=10))
            st.plotly_chart(fig_line, use_container_width=True)

    st.markdown("---")

    # 4. Pros & Cons Badges
    st.subheader("👍 Pros & 👎 Cons Analysis")
    df_pc = get_prosandcons(selected_ticker)
    if not df_pc.empty:
        pros = df_pc[df_pc["type"] == "PRO"]
        cons = df_pc[df_pc["type"] == "CON"]
        
        p_col, c_col = st.columns(2)
        with p_col:
            st.markdown("#### ✅ High Strengths (Pros)")
            for _, p in pros.iterrows():
                st.success(f"✔️ {p['description']}")
        with c_col:
            st.markdown("#### ❌ Watchouts (Cons)")
            for _, c in cons.iterrows():
                st.error(f"⚠️ {c['description']}")
    else:
        st.info("No qualitative pros/cons recorded.")

if __name__ == "__main__" or "render_profile_page" in dir():
    render_profile_page()
