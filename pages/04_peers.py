import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from src.dashboard.utils.db import get_ratios, get_companies, get_peers

def render_peers_page():
    st.title("🎯 Peer Group Percentile & Benchmark Analytics")
    st.markdown("Compare company fundamentals and percentile ranks across 11 sector peer groups.")

    df_comp = get_companies()
    df_ratios = get_ratios(year=2024)

    if df_comp.empty or df_ratios.empty:
        st.warning("Data not available.")
        return

    # 1. Peer Group & Company Selector
    sectors = df_comp["sector"].dropna().unique().tolist()
    
    col1, col2 = st.columns(2)
    with col1:
        selected_sector = st.selectbox("Select Sector Peer Group:", sectors, index=0)
    
    sec_companies = df_comp[df_comp["sector"] == selected_sector]["ticker"].tolist()
    with col2:
        selected_ticker = st.selectbox("Select Target Company:", sec_companies, index=0 if sec_companies else 0)

    # 2. Peer Group Data
    df_sec_ratios = df_ratios[df_ratios["sector"] == selected_sector].copy()
    if df_sec_ratios.empty:
        st.info(f"No peer records found for sector '{selected_sector}'.")
        return

    target_row = df_sec_ratios[df_sec_ratios["ticker"] == selected_ticker]
    if target_row.empty:
        target_row = df_sec_ratios.iloc[0:1]

    target_comp = target_row.iloc[0]

    st.markdown("---")

    # 3. Plotly 8-Axis Polar Radar Chart
    st.subheader(f"🕸️ 8-Axis Radar Chart: {selected_ticker} vs {selected_sector} Peer Average")

    radar_metrics = [
        ("ROE", "return_on_equity_pct"),
        ("ROCE", "return_on_capital_employed_pct"),
        ("NPM", "net_profit_margin_pct"),
        ("D/E", "debt_to_equity"),
        ("FCF", "free_cash_flow_cr"),
        ("PAT CAGR", "pat_cagr_5yr"),
        ("Rev CAGR", "revenue_cagr_5yr"),
        ("Composite", "composite_quality_score")
    ]

    labels = [m[0] for m in radar_metrics]
    
    # Calculate company & sector average values (scaled 0-100 for radar)
    comp_vals = []
    sec_avg_vals = []

    for _, m_col in radar_metrics:
        v = target_comp.get(m_col, 0.0)
        comp_vals.append(min(100.0, max(0.0, float(v if pd.notnull(v) else 0.0))))
        
        avg_v = df_sec_ratios[m_col].dropna().mean() if m_col in df_sec_ratios.columns else 0.0
        sec_avg_vals.append(min(100.0, max(0.0, float(avg_v if pd.notnull(avg_v) else 0.0))))

    # Close polar loop
    labels_closed = labels + [labels[0]]
    comp_vals_closed = comp_vals + [comp_vals[0]]
    sec_avg_closed = sec_avg_vals + [sec_avg_vals[0]]

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=comp_vals_closed, theta=labels_closed, fill='toself', name=f"{selected_ticker}", line_color="#1f77b4"
    ))
    fig_radar.add_trace(go.Scatterpolar(
        r=sec_avg_closed, theta=labels_closed, fill='none', name=f"{selected_sector} Avg", line=dict(color="#ff7f0e", dash="dash")
    ))

    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=True, height=450, margin=dict(t=30, b=30, l=40, r=40)
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    st.markdown("---")

    # 4. Side-by-Side KPI Comparison Table
    st.subheader(f"📊 {selected_sector} Sector Peer Scorecard & Benchmark")
    
    disp_cols = ["ticker", "company_name", "composite_quality_score", "return_on_equity_pct",
                 "return_on_capital_employed_pct", "net_profit_margin_pct", "debt_to_equity",
                 "free_cash_flow_cr", "revenue_cagr_5yr", "pat_cagr_5yr", "pe_ratio"]
    existing_cols = [c for c in disp_cols if c in df_sec_ratios.columns]
    
    df_sec_disp = df_sec_ratios[existing_cols].copy().sort_values("composite_quality_score", ascending=False)
    df_sec_disp.columns = ["Ticker", "Company", "Quality Score", "ROE (%)", "ROCE (%)", "NPM (%)", "D/E", "FCF (Cr)", "5Y Rev CAGR", "5Y PAT CAGR", "P/E"]

    # Highlight target company
    def highlight_target(row):
        if row["Ticker"] == selected_ticker:
            return ['background-color: #FFD700; font-weight: bold; color: black;'] * len(row)
        return [''] * len(row)

    st.dataframe(df_sec_disp.style.apply(highlight_target, axis=1), hide_index=True, use_container_width=True)

if __name__ == "__main__" or "render_peers_page" in dir():
    render_peers_page()
