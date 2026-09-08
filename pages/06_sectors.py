import streamlit as st
import pandas as pd
import plotly.express as px
from src.dashboard.utils.db import get_ratios, get_pl, get_sectors

def render_sectors_page():
    st.title("🏭 Sector Deep Dive & Competitive Landscape")
    st.markdown("Analyze company positioning, revenue scale, and profit margins across 11 sectors.")

    df_sec_summary = get_sectors()
    if df_sec_summary.empty:
        st.warning("No sectors found.")
        return

    sectors_list = df_sec_summary["sector"].tolist()
    selected_sector = st.selectbox("Select Sector to Explore:", sectors_list, index=0)

    # Load Latest Ratios
    df_ratios = get_ratios(year=2024)
    df_pnl = get_pl("") # Load all P&L for latest year sales

    df_sec = df_ratios[df_ratios["sector"] == selected_sector].copy()
    if df_sec.empty:
        st.info(f"No company records found for sector '{selected_sector}'.")
        return

    # Merge sales if missing
    if "sales" not in df_sec.columns and not df_pnl.empty:
        pnl_2024 = df_pnl[df_pnl["year"] == 2024][["company_id", "sales"]]
        df_sec = df_sec.merge(pnl_2024, on="company_id", how="left")

    df_sec["sales"] = df_sec["sales"].fillna(2000.0)
    df_sec["market_cap_proxy"] = df_sec["sales"] * 2.5

    st.markdown("---")

    # 1. Bubble Scatter Chart (X = Revenue, Y = ROE, Size = Market Cap, Colour = Industry)
    st.subheader(f"🫧 {selected_sector} Sector Bubble Landscape (X=Revenue, Y=ROE, Size=Market Cap)")

    fig_bubble = px.scatter(
        df_sec,
        x="sales",
        y="return_on_equity_pct",
        size="market_cap_proxy",
        color="industry" if "industry" in df_sec.columns else "sector",
        hover_name="ticker",
        text="ticker",
        labels={"sales": "Revenue (Sales ₹ Cr)", "return_on_equity_pct": "Return on Equity (ROE %)", "market_cap_proxy": "Market Cap Proxy"},
        size_max=50
    )
    fig_bubble.update_traces(textposition='top center')
    fig_bubble.update_layout(height=450, margin=dict(t=20, b=20, l=10, r=10))
    st.plotly_chart(fig_bubble, use_container_width=True)

    st.markdown("---")

    # 2. Sector Median KPI Bar Chart
    st.subheader(f"📊 {selected_sector} Median KPIs vs Nifty 100 Median")

    metrics_list = ["return_on_equity_pct", "return_on_capital_employed_pct", "net_profit_margin_pct", "debt_to_equity", "revenue_cagr_5yr"]
    metric_names = ["ROE (%)", "ROCE (%)", "NPM (%)", "D/E Ratio", "5Y Rev CAGR (%)"]

    sec_medians = [df_sec[m].dropna().median() if m in df_sec.columns else 0.0 for m in metrics_list]
    all_medians = [df_ratios[m].dropna().median() if m in df_ratios.columns else 0.0 for m in metrics_list]

    df_kpi_comp = pd.DataFrame({
        "KPI Metric": metric_names,
        f"{selected_sector} Median": [round(v, 2) for v in sec_medians],
        "Nifty 100 Median": [round(v, 2) for v in all_medians]
    })

    fig_bar = px.bar(
        df_kpi_comp, x="KPI Metric", y=[f"{selected_sector} Median", "Nifty 100 Median"],
        barmode="group", color_discrete_sequence=["#1f77b4", "#ff7f0e"]
    )
    fig_bar.update_layout(height=380, margin=dict(t=20, b=20, l=10, r=10))
    st.plotly_chart(fig_bar, use_container_width=True)

if __name__ == "__main__" or "render_sectors_page" in dir():
    render_sectors_page()
