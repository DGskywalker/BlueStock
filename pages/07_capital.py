import streamlit as st
import pandas as pd
import plotly.express as px
from src.dashboard.utils.db import get_ratios

def render_capital_page():
    st.title("🗺️ Capital Allocation Map (8-Pattern Treemap)")
    st.markdown("Visualizing cash reinvestment, dividend distributions, debt financing, and asset liquidation across Nifty 100.")

    df_ratios = get_ratios(year=2024)
    if df_ratios.empty:
        st.warning("Data not available.")
        return

    # Default pattern label if missing
    if "capital_allocation_pattern" not in df_ratios.columns:
        df_ratios["capital_allocation_pattern"] = "Reinvestor"

    df_ratios["capital_allocation_pattern"] = df_ratios["capital_allocation_pattern"].fillna("Mixed")
    df_ratios["free_cash_flow_abs"] = df_ratios["free_cash_flow_cr"].abs().fillna(100.0)

    st.markdown("---")

    # 1. Plotly Treemap (Grouped by Capital Allocation Pattern & Sector)
    st.subheader("🌳 Treemap: Companies Grouped by Capital Allocation Strategy")

    fig_tree = px.treemap(
        df_ratios,
        path=["capital_allocation_pattern", "sector", "ticker"],
        values="free_cash_flow_abs",
        color="capital_allocation_pattern",
        hover_data=["company_name", "return_on_equity_pct", "debt_to_equity"],
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_tree.update_layout(height=520, margin=dict(t=20, b=20, l=10, r=10))
    st.plotly_chart(fig_tree, use_container_width=True)

    st.markdown("---")

    # 2. Interactive Pattern Breakdown List
    st.subheader("📋 Filter Companies by Capital Allocation Pattern")
    
    patterns = df_ratios["capital_allocation_pattern"].unique().tolist()
    selected_pattern = st.selectbox("Select Capital Allocation Pattern:", patterns, index=0)

    df_pattern_comps = df_ratios[df_ratios["capital_allocation_pattern"] == selected_pattern]
    st.markdown(f"**{len(df_pattern_comps)} Companies classified as '{selected_pattern}':**")

    cols_disp = ["ticker", "company_name", "sector", "free_cash_flow_cr", "cfo_quality_score", "return_on_equity_pct", "debt_to_equity"]
    existing_cols = [c for c in cols_disp if c in df_pattern_comps.columns]
    
    df_p_disp = df_pattern_comps[existing_cols].copy().sort_values("free_cash_flow_cr", ascending=False)
    df_p_disp.columns = ["Ticker", "Company", "Sector", "FCF (₹ Cr)", "CFO Quality Score", "ROE (%)", "D/E"]
    st.dataframe(df_p_disp, hide_index=True, use_container_width=True)

if __name__ == "__main__" or "render_capital_page" in dir():
    render_capital_page()
