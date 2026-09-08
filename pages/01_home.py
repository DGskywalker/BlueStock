import streamlit as st
import pandas as pd
import plotly.express as px
from src.dashboard.utils.db import get_ratios, get_sectors

def render_home_page():
    st.title("📊 Nifty 100 Financial Analytics & Overview")
    st.markdown("Comprehensive financial fundamentals, ratio metrics, and quality analysis across Nifty 100 companies.")

    # Sidebar Year Filter
    st.sidebar.header("🔍 Global Filters")
    selected_year = st.sidebar.selectbox("Select Financial Year", [2024, 2023, 2022, 2021, 2020, 2019], index=0)

    # Load Data
    df_ratios = get_ratios(year=selected_year)
    if df_ratios.empty:
        st.warning(f"No financial data available for Year {selected_year}.")
        return

    # 1. 6 KPI Summary Tiles
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    avg_roe = df_ratios["return_on_equity_pct"].dropna().mean()
    med_pe = df_ratios["pe_ratio"].dropna().median()
    med_de = df_ratios["debt_to_equity"].dropna().median()
    tot_comp = df_ratios["company_id"].nunique()
    med_rev_cagr = df_ratios["revenue_cagr_5yr"].dropna().median()
    debt_free_cnt = len(df_ratios[df_ratios["debt_to_equity"] == 0.0])

    col1.metric("Average ROE", f"{avg_roe:.1f}%" if pd.notnull(avg_roe) else "N/A")
    col2.metric("Median P/E", f"{med_pe:.1f}x" if pd.notnull(med_pe) else "N/A")
    col3.metric("Median D/E", f"{med_de:.2f}" if pd.notnull(med_de) else "N/A")
    col4.metric("Total Companies", f"{tot_comp}")
    col5.metric("Median 5Y Rev CAGR", f"{med_rev_cagr:.1f}%" if pd.notnull(med_rev_cagr) else "N/A")
    col6.metric("Debt-Free Companies", f"{debt_free_cnt}")

    st.markdown("---")

    # 2. Charts Row: Donut Chart & Top 5 Quality Table
    chart_col1, chart_col2 = st.columns([1, 1])

    with chart_col1:
        st.subheader("🏢 Sector Distribution (Company Count)")
        df_sec = get_sectors()
        fig_donut = px.pie(
            df_sec, names="sector", values="company_count", hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_donut.update_layout(margin=dict(t=20, b=20, l=10, r=10), height=380)
        st.plotly_chart(fig_donut, use_container_width=True)

    with chart_col2:
        st.subheader("🏆 Top 5 Companies by Composite Quality Score")
        df_top5 = df_ratios.sort_values("composite_quality_score", ascending=False).head(5)
        cols_disp = ["ticker", "company_name", "sector", "composite_quality_score", "return_on_equity_pct", "debt_to_equity"]
        df_top5_disp = df_top5[[c for c in cols_disp if c in df_top5.columns]].copy()
        df_top5_disp.columns = ["Ticker", "Company", "Sector", "Quality Score", "ROE (%)", "D/E"]
        st.dataframe(df_top5_disp, hide_index=True, use_container_width=True)

if __name__ == "__main__" or "render_home_page" in dir():
    render_home_page()
