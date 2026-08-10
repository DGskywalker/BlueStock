import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="BlueStock Mutual Fund Analytics — Executive Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Bluestock Dark Modern Theme)
st.markdown("""
<style>
    .stApp {
        background-color: #0b132b;
        color: #ffffff;
    }
    .metric-card {
        background-color: #1c2541;
        border-left: 4px solid #00b4d8;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .metric-title {
        color: #90e0ef;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    .metric-val {
        color: #ffffff;
        font-size: 1.8rem;
        font-weight: 700;
    }
    .metric-sub {
        color: #06d6a0;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to load data
@st.cache_data
def load_data():
    def p(name):
        paths = [os.path.join("data", "processed", name), os.path.join("csv", name), name]
        for path in paths:
            if os.path.exists(path): return path
        return name

    nav_df = pd.read_csv(p("02_nav_history.csv"))
    nav_df["date"] = pd.to_datetime(nav_df["date"])

    fm_df = pd.read_csv(p("01_fund_master.csv"))
    aum_df = pd.read_csv(p("03_aum_by_fund_house.csv"))
    sip_df = pd.read_csv(p("04_monthly_sip_inflows.csv"))
    cat_df = pd.read_csv(p("05_category_inflows.csv"))
    folio_df = pd.read_csv(p("06_industry_folio_count.csv"))
    sp_df = pd.read_csv(p("07_scheme_performance.csv"))
    tx_df = pd.read_csv(p("08_investor_transactions.csv"))
    ph_df = pd.read_csv(p("09_portfolio_holdings.csv"))
    bi_df = pd.read_csv(p("10_benchmark_indices.csv"))
    bi_df["date"] = pd.to_datetime(bi_df["date"])
    scorecard_df = pd.read_csv(p("fund_scorecard.csv"))

    return nav_df, fm_df, aum_df, sip_df, cat_df, folio_df, sp_df, tx_df, ph_df, bi_df, scorecard_df

nav_df, fm_df, aum_df, sip_df, cat_df, folio_df, sp_df, tx_df, ph_df, bi_df, scorecard_df = load_data()

# Sidebar Navigation & Filters
st.sidebar.title("BlueStock Analytics")
st.sidebar.markdown("---")

selected_category = st.sidebar.multiselect("Filter Fund Category", options=fm_df["category"].unique(), default=fm_df["category"].unique())
selected_fh = st.sidebar.multiselect("Filter Fund House (AMC)", options=fm_df["fund_house"].unique(), default=fm_df["fund_house"].unique()[:4])

st.sidebar.markdown("---")
st.sidebar.info("💡 **Capstone Project**: Indian Mutual Fund Analytics Platform (Release v1.0)")

# Main Header
st.title("📊 BlueStock Mutual Fund Analytics — Interactive Dashboard")
st.markdown("Real-Time Industry Overview, Quantitative Risk Diagnostics & Portfolio Analytics Engine")

# Tabs Navigation
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Industry Overview",
    "🏆 Fund Performance",
    "👥 Investor Demographics",
    "📈 SIP & Market Trends",
    "🤖 Interactive Recommender"
])

# -----------------------------------------------------------------------------
# TAB 1: Industry Overview
# -----------------------------------------------------------------------------
with tab1:
    st.header("Industry Overview & Asset Allocation")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="metric-card"><div class="metric-title">TOTAL INDUSTRY AUM</div><div class="metric-val">₹81.4 Lakh Cr</div><div class="metric-sub">+18.4% YoY Growth</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card"><div class="metric-title">MONTHLY SIP INFLOW</div><div class="metric-val">₹31,002 Cr</div><div class="metric-sub">Record High (Dec 2025)</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card"><div class="metric-title">TOTAL MF FOLIOS</div><div class="metric-val">26.12 Crore</div><div class="metric-sub">97% Growth (2022-2025)</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="metric-card"><div class="metric-title">ACTIVE SCHEMES</div><div class="metric-val">1,908 Schemes</div><div class="metric-sub">40 Sampled Benchmark Funds</div></div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Industry AUM Growth Trend (2022–2025)")
        aum_m = aum_df.groupby("date")["aum_crore"].sum() / 100000.0
        fig_aum = px.line(x=aum_m.index, y=aum_m.values, labels={"x": "Date", "y": "AUM (₹ Lakh Cr)"}, title="Industry Monthly Total AUM")
        fig_aum.update_traces(line_color="#00b4d8", line_width=3)
        fig_aum.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig_aum, use_container_width=True)
    with c2:
        st.subheader("Top AMC Asset Allocations")
        top_amc = aum_df.groupby("fund_house")["aum_crore"].max().sort_values(ascending=False).head(6) / 100000.0
        fig_amc = px.bar(x=top_amc.index, y=top_amc.values, labels={"x": "AMC", "y": "AUM (₹ Lakh Cr)"}, title="Top 6 AMCs by AUM", color=top_amc.index, color_discrete_sequence=px.colors.qualitative.Set3)
        fig_amc.update_layout(template="plotly_dark", height=400, showlegend=False)
        st.plotly_chart(fig_amc, use_container_width=True)

# -----------------------------------------------------------------------------
# TAB 2: Fund Performance
# -----------------------------------------------------------------------------
with tab2:
    st.header("Fund Performance & Scorecard Diagnostics")
    
    # Filter scorecard by selected category
    filtered_scorecard = scorecard_df[scorecard_df["category"].isin(selected_category) & scorecard_df["fund_house"].isin(selected_fh)]
    
    st.subheader("Executive Fund Scorecard Table (Sortable)")
    st.dataframe(filtered_scorecard[["overall_rank", "fund_score", "scheme_name", "fund_house", "category", "cagr_3yr_pct", "sharpe_ratio", "sortino_ratio", "alpha_pct", "max_drawdown_pct", "expense_ratio_pct"]].style.highlight_max(axis=0, color="#1b4965"), use_container_width=True)

    st.subheader("Risk vs. Return Scatter Tradeoff")
    fig_scat = px.scatter(filtered_scorecard, x="max_drawdown_pct", y="cagr_3yr_pct", size="aum_crore", color="category", hover_name="scheme_name", labels={"max_drawdown_pct": "Max Drawdown Risk (%)", "cagr_3yr_pct": "3-Year CAGR Return (%)"}, title="3Y Return vs. Drawdown Risk (Bubble Size = AUM)")
    fig_scat.update_layout(template="plotly_dark", height=450)
    st.plotly_chart(fig_scat, use_container_width=True)

# -----------------------------------------------------------------------------
# TAB 3: Investor Demographics
# -----------------------------------------------------------------------------
with tab3:
    st.header("Investor Demographics & Behavioral Profiling")
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Transaction Type Breakdown")
        tx_types = tx_df["transaction_type"].value_counts()
        fig_pie = px.pie(values=tx_types.values, names=tx_types.index, title="SIP vs Lumpsum vs Redemption Split", color_discrete_sequence=["#06d6a0", "#118ab2", "#ef476f"], hole=0.4)
        fig_pie.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig_pie, use_container_width=True)
    with c2:
        st.subheader("SIP Ticket Size by Age Cohort")
        sip_txs = tx_df[tx_df["transaction_type"] == "SIP"]
        age_sip = sip_txs.groupby("age_group")["amount_inr"].mean().reset_index()
        fig_age = px.bar(age_sip, x="age_group", y="amount_inr", labels={"age_group": "Age Group", "amount_inr": "Avg SIP Amount (INR)"}, title="Average Ticket Size Across Age Groups", color="age_group")
        fig_age.update_layout(template="plotly_dark", height=400, showlegend=False)
        st.plotly_chart(fig_age, use_container_width=True)

# -----------------------------------------------------------------------------
# TAB 4: SIP & Market Trends
# -----------------------------------------------------------------------------
with tab4:
    st.header("SIP Growth & Market Index Correlation")
    
    fig_sip = px.line(sip_df, x="month", y="sip_inflow_crore", markers=True, title="Monthly SIP Inflow Trend (Jan 2022 – Dec 2025)", labels={"month": "Month", "sip_inflow_crore": "SIP Inflow (₹ Cr)"})
    fig_sip.add_annotation(x="2025-12", y=31002, text="Peak: ₹31,002 Cr", showarrow=True, arrowhead=2, arrowcolor="red")
    fig_sip.update_traces(line_color="#00b4d8", line_width=3)
    fig_sip.update_layout(template="plotly_dark", height=450)
    st.plotly_chart(fig_sip, use_container_width=True)

# -----------------------------------------------------------------------------
# TAB 5: Interactive Recommender Engine
# -----------------------------------------------------------------------------
with tab5:
    st.header("🤖 Smart Fund Recommender Engine")
    st.markdown("Select your investor risk profile to receive tailored, top-performing fund recommendations.")
    
    risk_choice = st.radio("Select Investor Risk Appetite:", ["Low", "Moderate", "High"], horizontal=True)
    
    risk_map = {
        "Low": ["Low", "Debt"],
        "Moderate": ["Moderate", "Hybrid", "Large Cap"],
        "High": ["Equity", "Small Cap", "Mid Cap"]
    }

    if st.button("Generate Fund Recommendations"):
        filtered_recs = scorecard_df[scorecard_df["category"].isin(risk_map[risk_choice]) | scorecard_df["sub_category"].isin(risk_map[risk_choice])].sort_values("sharpe_ratio", ascending=False).head(3)
        if len(filtered_recs) == 0:
            filtered_recs = scorecard_df.sort_values("sharpe_ratio", ascending=False).head(3)
            
        st.success(f"Top 3 Recommended Schemes for **'{risk_choice}'** Risk Profile:")
        st.table(filtered_recs[["overall_rank", "fund_score", "scheme_name", "fund_house", "category", "cagr_3yr_pct", "sharpe_ratio", "alpha_pct", "expense_ratio_pct"]])
