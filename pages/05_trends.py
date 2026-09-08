import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.dashboard.utils.db import get_companies, get_ratios, get_pl

def render_trends_page():
    st.title("📈 Multi-Metric Historical Trend Analysis")
    st.markdown("Overlay up to 3 financial metrics over a 10-year timeline with YoY growth annotations.")

    df_comp = get_companies()
    if df_comp.empty:
        st.warning("No companies found.")
        return

    col1, col2 = st.columns([1, 2])
    with col1:
        ticker_list = df_comp["ticker"].tolist()
        selected_ticker = st.selectbox("Select Company:", ticker_list, index=0)
    
    df_rat = get_ratios(ticker=selected_ticker)
    df_pnl = get_pl(ticker=selected_ticker)

    if df_rat.empty:
        st.info("No trend data available for this company.")
        return

    # Merge P&L sales into ratios if needed
    if "sales" not in df_rat.columns and not df_pnl.empty:
        df_rat = df_rat.merge(df_pnl[["year", "sales", "pat"]], on="year", how="left")

    available_metrics = {
        "Revenue (Sales ₹ Cr)": "sales",
        "Net Profit (PAT ₹ Cr)": "pat",
        "Return on Equity (ROE %)": "return_on_equity_pct",
        "Return on Capital Employed (ROCE %)": "return_on_capital_employed_pct",
        "Debt-to-Equity (D/E)": "debt_to_equity",
        "Free Cash Flow (FCF ₹ Cr)": "free_cash_flow_cr",
        "Operating Profit Margin (OPM %)": "operating_profit_margin_pct"
    }

    with col2:
        selected_labels = st.multiselect("Select up to 3 Metrics to Overlay:", list(available_metrics.keys()), default=["Return on Equity (ROE %)", "Return on Capital Employed (ROCE %)"])

    if not selected_labels:
        st.info("Please select at least one metric to display.")
        return

    selected_labels = selected_labels[:3]

    st.markdown("---")
    st.subheader(f"📊 {selected_ticker} 10-Year Timeline ({', '.join(selected_labels)})")

    fig = go.Figure()

    colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]
    for i, label in enumerate(selected_labels):
        col_name = available_metrics[label]
        if col_name in df_rat.columns:
            series_val = df_rat[col_name].fillna(0.0)
            
            # Compute YoY % change annotations
            yoy_text = []
            for idx in range(len(series_val)):
                if idx == 0:
                    yoy_text.append(f"{series_val.iloc[idx]:.1f}")
                else:
                    prev_v = series_val.iloc[idx-1]
                    curr_v = series_val.iloc[idx]
                    chg = ((curr_v - prev_v) / abs(prev_v) * 100.0) if prev_v != 0 else 0.0
                    yoy_text.append(f"{curr_v:.1f} ({chg:+.1f}%)")

            fig.add_trace(go.Scatter(
                x=df_rat["year"], y=series_val, mode="lines+markers+text",
                name=label, text=yoy_text, textposition="top center",
                line=dict(color=colors[i % 3], width=3),
                marker=dict(size=8)
            ))

    fig.update_layout(height=480, margin=dict(t=30, b=30, l=20, r=20), hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__" or "render_trends_page" in dir():
    render_trends_page()
