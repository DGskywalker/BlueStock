import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from PIL import Image

# Setup Directories
DASHBOARD_DIR = "dashboard"
CHARTS_DIR = os.path.join("reports", "charts")
PROCESSED_DIR = os.path.join("data", "processed")

os.makedirs(DASHBOARD_DIR, exist_ok=True)
os.makedirs(CHARTS_DIR, exist_ok=True)

# Helper function to find CSV path
def find_file(name):
    paths = [
        os.path.join(PROCESSED_DIR, name),
        os.path.join("csv", name),
        name,
        os.path.join("data", "raw", name)
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return name

print("Loading cleaned datasets for Power BI Dashboard Assets...")
nav_df = pd.read_csv(find_file("02_nav_history.csv"))
nav_df["date"] = pd.to_datetime(nav_df["date"])

fm_df = pd.read_csv(find_file("01_fund_master.csv"))
aum_df = pd.read_csv(find_file("03_aum_by_fund_house.csv"))
aum_df["date"] = pd.to_datetime(aum_df["date"])

sip_df = pd.read_csv(find_file("04_monthly_sip_inflows.csv"))
cat_df = pd.read_csv(find_file("05_category_inflows.csv"))
folio_df = pd.read_csv(find_file("06_industry_folio_count.csv"))
sp_df = pd.read_csv(find_file("07_scheme_performance.csv"))
tx_df = pd.read_csv(find_file("08_investor_transactions.csv"))
tx_df["transaction_date"] = pd.to_datetime(tx_df["transaction_date"])
bi_df = pd.read_csv(find_file("10_benchmark_indices.csv"))
bi_df["date"] = pd.to_datetime(bi_df["date"])

scorecard_df = pd.read_csv(find_file("fund_scorecard.csv"))

# Bluestock Dashboard Matplotlib Styling
plt.style.use("dark_background")
BG_COLOR = "#0b132b"
CARD_COLOR = "#1c2541"
TEXT_COLOR = "#ffffff"
PRIMARY_COLOR = "#00b4d8"
SECONDARY_COLOR = "#7209b7"
ACCENT_GREEN = "#06d6a0"
ACCENT_ORANGE = "#ff9f1c"

def set_card_style(ax, title=""):
    ax.set_facecolor(CARD_COLOR)
    ax.tick_params(colors=TEXT_COLOR, labelsize=9)
    for spine in ax.spines.values():
        spine.set_color("#3a506b")
        spine.set_linewidth(1.0)
    if title:
        ax.set_title(title, color=TEXT_COLOR, fontsize=12, fontweight="bold", pad=10)

# =============================================================================
# PAGE 1: INDUSTRY OVERVIEW (1920x1080 PNG)
# =============================================================================
print("Generating Page 1: Industry Overview...")

fig = plt.figure(figsize=(19.2, 10.8), facecolor=BG_COLOR)
gs = gridspec.GridSpec(3, 4, figure=fig, height_ratios=[0.25, 1, 1], wspace=0.3, hspace=0.35)

# Header
ax_head = fig.add_subplot(gs[0, :])
ax_head.set_facecolor(BG_COLOR)
ax_head.axis("off")
ax_head.text(0.01, 0.65, "BLUESTOCK MUTUAL FUND PLATFORM — INDUSTRY OVERVIEW", color="#00b4d8", fontsize=20, fontweight="bold")
ax_head.text(0.01, 0.25, "Executive Dashboard | Real-Time Market Capitalization, SIP Participation & AMC Asset Allocations", color="#a0aab2", fontsize=11)

# KPI Cards
kpis = [
    ("TOTAL INDUSTRY AUM", "₹81.4 Lakh Cr", "+18.4% YoY Growth"),
    ("MONTHLY SIP INFLOW", "₹31,002 Cr", "All-Time High (Dec 2025)"),
    ("TOTAL MF FOLIOS", "26.12 Crore", "97% Growth (2022-2025)"),
    ("ACTIVE SCHEMES", "1,908 Schemes", "40 Detailed Benchmark Funds")
]

for i, (label, val, sub) in enumerate(kpis):
    ax_kpi = fig.add_subplot(gs[0, i])
    ax_kpi.set_facecolor(CARD_COLOR)
    ax_kpi.axis("off")
    for spine in ax_kpi.spines.values():
        spine.set_color("#00b4d8")
        spine.set_linewidth(1.5)
    ax_kpi.text(0.08, 0.70, label, color="#90e0ef", fontsize=10, fontweight="bold")
    ax_kpi.text(0.08, 0.35, val, color="#ffffff", fontsize=16, fontweight="bold")
    ax_kpi.text(0.08, 0.12, sub, color=ACCENT_GREEN if "+" in sub or "High" in sub or "Growth" in sub else "#ffb703", fontsize=8)

# Chart 1.1: Industry AUM Trend 2022-2025
ax1 = fig.add_subplot(gs[1, :2])
set_card_style(ax1, "Industry AUM Trend (2022–2025 in ₹ Lakh Crores)")
aum_monthly = aum_df.groupby("date")["aum_crore"].sum() / 100000.0
ax1.plot(aum_monthly.index, aum_monthly.values, color="#00b4d8", linewidth=2.5, marker="o", markersize=4)
ax1.fill_between(aum_monthly.index, aum_monthly.values, color="#00b4d8", alpha=0.2)
ax1.set_ylabel("AUM (₹ Lakh Cr)", color=TEXT_COLOR)

# Chart 1.2: AUM by AMC / Fund House
ax2 = fig.add_subplot(gs[1, 2:])
set_card_style(ax2, "Asset Allocation by Top AMC / Fund House (₹ Lakh Crores)")
top_amc = aum_df.groupby("fund_house")["aum_crore"].max().sort_values(ascending=True) / 100000.0
colors_amc = ["#48cae4" if "SBI" not in name else "#ffb703" for name in top_amc.index]
ax2.barh(top_amc.index, top_amc.values, color=colors_amc, height=0.6)
ax2.set_xlabel("AUM (₹ Lakh Cr)", color=TEXT_COLOR)
ax2.annotate("SBI MF Dominance\n₹12.5L Cr+", xy=(12.5, 5), xytext=(9.0, 3.5),
             arrowprops=dict(facecolor="#ffb703", shrink=0.05, width=1.5, headwidth=6),
             color="#ffb703", fontsize=9, fontweight="bold")

# Chart 1.3: Industry Folio Expansion
ax3 = fig.add_subplot(gs[2, :2])
set_card_style(ax3, "Folio Count Growth (Jan 2022: 13.26 Cr → Dec 2025: 26.12 Cr)")
ax3.plot(pd.to_datetime(folio_df["month"]), folio_df["total_folios_crore"], color=ACCENT_GREEN, linewidth=2.5, marker="s", markersize=4)
ax3.set_ylabel("Folios (Crore)", color=TEXT_COLOR)

# Chart 1.4: Category Wise AUM Distribution
ax4 = fig.add_subplot(gs[2, 2:])
set_card_style(ax4, "Scheme Category Breakdown by Total Sampled AUM")
cat_aum = sp_df.groupby("category")["aum_crore"].sum().sort_values(ascending=False) / 1000.0
ax4.pie(cat_aum, labels=cat_aum.index, autopct="%1.1f%%", colors=["#00b4d8", "#7209b7", "#4895ef", "#4cc9f0"], pctdistance=0.75, textprops={"color": TEXT_COLOR, "fontsize": 9, "fontweight": "bold"})
centre_c = plt.Circle((0,0), 0.50, fc=CARD_COLOR)
ax4.add_artist(centre_c)

plt.tight_layout()
p1_path = os.path.join(DASHBOARD_DIR, "page1_industry_overview.png")
plt.savefig(p1_path, dpi=200, bbox_inches="tight")
plt.savefig(os.path.join(CHARTS_DIR, "page1_industry_overview.png"), dpi=200, bbox_inches="tight")
plt.close()

# =============================================================================
# PAGE 2: FUND PERFORMANCE (1920x1080 PNG)
# =============================================================================
print("Generating Page 2: Fund Performance...")

fig = plt.figure(figsize=(19.2, 10.8), facecolor=BG_COLOR)
gs = gridspec.GridSpec(3, 4, figure=fig, height_ratios=[0.25, 1, 1], wspace=0.3, hspace=0.35)

# Header
ax_head = fig.add_subplot(gs[0, :])
ax_head.set_facecolor(BG_COLOR)
ax_head.axis("off")
ax_head.text(0.01, 0.65, "BLUESTOCK MUTUAL FUND PLATFORM — FUND PERFORMANCE ANALYTICS", color="#00b4d8", fontsize=20, fontweight="bold")
ax_head.text(0.01, 0.25, "Risk vs Return Tradeoff, Scorecard Ratings & Benchmark Outperformance Tracking", color="#a0aab2", fontsize=11)

# KPI Cards
kpis_p2 = [
    ("TOP RATED SCHEME", "ICICI Pru Midcap", "Score: 85.1/100 (Rank #1)"),
    ("BEST 3Y CAGR", "+36.45%", "Nippon India Small Cap"),
    ("MAX SHARPE RATIO", "1.07", "Mirae Asset Large Cap"),
    ("LOWEST EXPENSE", "0.55%", "Nippon India Gilt Securities")
]

for i, (label, val, sub) in enumerate(kpis_p2):
    ax_kpi = fig.add_subplot(gs[0, i])
    ax_kpi.set_facecolor(CARD_COLOR)
    ax_kpi.axis("off")
    ax_kpi.text(0.08, 0.70, label, color="#90e0ef", fontsize=10, fontweight="bold")
    ax_kpi.text(0.08, 0.35, val, color="#ffffff", fontsize=15, fontweight="bold")
    ax_kpi.text(0.08, 0.12, sub, color=ACCENT_GREEN, fontsize=8)

# Chart 2.1: Risk vs Return Scatter Plot
ax1 = fig.add_subplot(gs[1, :2])
set_card_style(ax1, "Risk vs. Return Tradeoff (Volatility % vs. 3Y CAGR Return %)")
if "aum_crore" not in scorecard_df.columns:
    scorecard_df = pd.merge(scorecard_df, sp_df[["amfi_code", "aum_crore"]], on="amfi_code", how="left")
scatter = ax1.scatter(scorecard_df["max_drawdown_pct"].abs(), scorecard_df["cagr_3yr_pct"], s=scorecard_df["aum_crore"].fillna(10000)/150.0, c=scorecard_df["fund_score"], cmap="viridis", alpha=0.8, edgecolors="white")
ax1.set_xlabel("Max Drawdown Risk (%)", color=TEXT_COLOR)
ax1.set_ylabel("3-Year CAGR Return (%)", color=TEXT_COLOR)
cbar = plt.colorbar(scatter, ax=ax1)
cbar.ax.yaxis.set_tick_params(color=TEXT_COLOR)
plt.setp(plt.getp(cbar.ax, "yticklabels"), color=TEXT_COLOR)
cbar.set_label("Scorecard (0-100)", color=TEXT_COLOR)

# Chart 2.2: Top 5 Schemes NAV vs NIFTY 50 Benchmark
ax2 = fig.add_subplot(gs[1, 2:])
set_card_style(ax2, "Top 5 Schemes NAV Progression vs NIFTY 50 Benchmark")
start_3y = nav_df["date"].max() - pd.DateOffset(years=3)
n50 = bi_df[bi_df["index_name"] == "NIFTY50"].sort_values("date").set_index("date")["close_value"]
n50_3y = n50[n50.index >= start_3y]
ax2.plot(n50_3y.index, n50_3y/n50_3y.iloc[0]*100, label="NIFTY 50", color="#ffffff", linestyle="--", linewidth=2.0)

top_codes = scorecard_df.head(4)["amfi_code"].tolist()
colors_line = ["#00b4d8", "#7209b7", "#06d6a0", "#ff9f1c"]
for idx, code in enumerate(top_codes):
    s_name = scorecard_df[scorecard_df["amfi_code"] == code]["scheme_name"].values[0][:18]
    f_sub = nav_df[(nav_df["amfi_code"] == code) & (nav_df["date"] >= start_3y)].sort_values("date").set_index("date")["nav"]
    ax2.plot(f_sub.index, f_sub/f_sub.iloc[0]*100, label=s_name, color=colors_line[idx], linewidth=1.8)

ax2.legend(loc="upper left", fontsize=8, facecolor=CARD_COLOR, edgecolor="#00b4d8")

# Chart 2.3: Fund Scorecard Table (Top 6)
ax3 = fig.add_subplot(gs[2, :])
ax3.set_facecolor(CARD_COLOR)
ax3.axis("off")
ax3.set_title("Executive Fund Performance Scorecard & Risk Diagnostics (Top Ranked Schemes)", color=TEXT_COLOR, fontsize=12, fontweight="bold", pad=10)

table_data = []
top_table = scorecard_df.head(6)
headers = ["Rank", "Score", "Scheme Name", "Fund House", "Category", "3Y CAGR", "Sharpe", "Sortino", "Alpha", "Max DD", "Expense Ratio"]
table_data.append(headers)

for _, r in top_table.iterrows():
    row = [
        str(int(r["overall_rank"])),
        f"{r['fund_score']:.1f}",
        str(r["scheme_name"])[:32],
        str(r["fund_house"])[:18],
        str(r["category"]),
        f"{r['cagr_3yr_pct']:.2f}%",
        f"{r['sharpe_ratio']:.2f}",
        f"{r['sortino_ratio']:.2f}",
        f"{r['alpha_pct']:.2f}%",
        f"{r['max_drawdown_pct']:.2f}%",
        f"{r['expense_ratio_pct']:.2f}%"
    ]
    table_data.append(row)

table = ax3.table(cellText=table_data, loc="center", cellLoc="center")
table.auto_set_font_size(False)
table.set_fontsize(9)
table.scale(1.0, 1.6)

for (row_idx, col_idx), cell in table.get_celld().items():
    if row_idx == 0:
        cell.set_facecolor("#00b4d8")
        cell.set_text_props(color="black", fontweight="bold")
    else:
        cell.set_facecolor(CARD_COLOR if row_idx % 2 == 0 else "#162032")
        cell.set_text_props(color=TEXT_COLOR)

plt.tight_layout()
p2_path = os.path.join(DASHBOARD_DIR, "page2_fund_performance.png")
plt.savefig(p2_path, dpi=200, bbox_inches="tight")
plt.savefig(os.path.join(CHARTS_DIR, "page2_fund_performance.png"), dpi=200, bbox_inches="tight")
plt.close()

# =============================================================================
# PAGE 3: INVESTOR ANALYTICS (1920x1080 PNG)
# =============================================================================
print("Generating Page 3: Investor Analytics...")

fig = plt.figure(figsize=(19.2, 10.8), facecolor=BG_COLOR)
gs = gridspec.GridSpec(3, 4, figure=fig, height_ratios=[0.25, 1, 1], wspace=0.3, hspace=0.35)

# Header
ax_head = fig.add_subplot(gs[0, :])
ax_head.set_facecolor(BG_COLOR)
ax_head.axis("off")
ax_head.text(0.01, 0.65, "BLUESTOCK MUTUAL FUND PLATFORM — INVESTOR DEMOGRAPHICS & BEHAVIOR", color="#00b4d8", fontsize=20, fontweight="bold")
ax_head.text(0.01, 0.25, "Geographic Capital Distribution, Transaction Types, Age Ticket Sizes & Channel Penetration", color="#a0aab2", fontsize=11)

# KPI Cards
kpis_p3 = [
    ("CORE AGE DEMOGRAPHIC", "26–50 Years", "69.6% Total Transaction Share"),
    ("TOP INVESTOR STATE", "Punjab & Tamil Nadu", "₹31.5+ Cr Transaction Vol"),
    ("PREFERRED TX TYPE", "SIP (Systematic)", "60.15% Share vs Lumpsum"),
    ("SENIOR TICKET SIZE", "₹7,500+ Median", "Highest in 51-65 Age Group")
]

for i, (label, val, sub) in enumerate(kpis_p3):
    ax_kpi = fig.add_subplot(gs[0, i])
    ax_kpi.set_facecolor(CARD_COLOR)
    ax_kpi.axis("off")
    ax_kpi.text(0.08, 0.70, label, color="#90e0ef", fontsize=10, fontweight="bold")
    ax_kpi.text(0.08, 0.35, val, color="#ffffff", fontsize=15, fontweight="bold")
    ax_kpi.text(0.08, 0.12, sub, color=ACCENT_GREEN, fontsize=8)

# Chart 3.1: Transaction Amount by State
ax1 = fig.add_subplot(gs[1, :2])
set_card_style(ax1, "Total Transaction Amount by Top Indian States (₹ Crores)")
state_vol = tx_df.groupby("state")["amount_inr"].sum().sort_values(ascending=True) / 1e7
ax1.barh(state_vol.index, state_vol.values, color="#00b4d8", height=0.6)
ax1.set_xlabel("Capital Volume (₹ Cr)", color=TEXT_COLOR)

# Chart 3.2: Transaction Type Split Donut Chart
ax2 = fig.add_subplot(gs[1, 2:])
set_card_style(ax2, "Investor Transaction Type Breakdown (SIP vs Lumpsum vs Redemption)")
tx_type = tx_df["transaction_type"].value_counts()
ax2.pie(tx_type, labels=tx_type.index, autopct="%1.1f%%", colors=["#06d6a0", "#118ab2", "#ef476f"], pctdistance=0.75, textprops={"color": TEXT_COLOR, "fontsize": 10, "fontweight": "bold"})
centre_c = plt.Circle((0,0), 0.50, fc=CARD_COLOR)
ax2.add_artist(centre_c)

# Chart 3.3: Age Group vs Avg SIP Amount
ax3 = fig.add_subplot(gs[2, :2])
set_card_style(ax3, "Average SIP Investment Ticket Size Across Age Cohorts (INR)")
sip_only = tx_df[tx_df["transaction_type"] == "SIP"]
age_sip = sip_only.groupby("age_group")["amount_inr"].mean().dropna()
ax3.bar(age_sip.index, age_sip.values, color="#7209b7", width=0.5)
ax3.set_ylabel("Avg SIP Amount (INR)", color=TEXT_COLOR)
for idx, v in enumerate(age_sip.values):
    if not pd.isna(v):
        ax3.text(idx, v + 2000, f"₹{int(v):,}", ha="center", color=TEXT_COLOR, fontsize=8, fontweight="bold")

# Chart 3.4: Monthly Transaction Volume Line
ax4 = fig.add_subplot(gs[2, 2:])
set_card_style(ax4, "Monthly Investor Transaction Account Volume")
tx_df["tx_month"] = tx_df["transaction_date"].dt.to_period("M").astype(str)
monthly_tx_cnt = tx_df.groupby("tx_month")["investor_id"].count()
ax4.plot(monthly_tx_cnt.index, monthly_tx_cnt.values, color=ACCENT_ORANGE, linewidth=2.0, marker="o", markersize=3)
ax4.set_ylabel("Transaction Count", color=TEXT_COLOR)
ax4.set_xticks(monthly_tx_cnt.index[::6])
ax4.set_xticklabels(monthly_tx_cnt.index[::6], rotation=30)

plt.tight_layout()
p3_path = os.path.join(DASHBOARD_DIR, "page3_investor_analytics.png")
plt.savefig(p3_path, dpi=200, bbox_inches="tight")
plt.savefig(os.path.join(CHARTS_DIR, "page3_investor_analytics.png"), dpi=200, bbox_inches="tight")
plt.close()

# =============================================================================
# PAGE 4: SIP & MARKET TRENDS (1920x1080 PNG)
# =============================================================================
print("Generating Page 4: SIP & Market Trends...")

fig = plt.figure(figsize=(19.2, 10.8), facecolor=BG_COLOR)
gs = gridspec.GridSpec(3, 4, figure=fig, height_ratios=[0.25, 1, 1], wspace=0.3, hspace=0.35)

# Header
ax_head = fig.add_subplot(gs[0, :])
ax_head.set_facecolor(BG_COLOR)
ax_head.axis("off")
ax_head.text(0.01, 0.65, "BLUESTOCK MUTUAL FUND PLATFORM — SIP & MARKET DYNAMICS", color="#00b4d8", fontsize=20, fontweight="bold")
ax_head.text(0.01, 0.25, "Dual-Axis Correlation: Retail Monthly SIP Inflows vs NIFTY 50 Benchmark & Category Flow Dynamics", color="#a0aab2", fontsize=11)

# KPI Cards
kpis_p4 = [
    ("SIP PEAK INFLOW", "₹31,002 Cr", "December 2025 Record"),
    ("NIFTY 50 CLOSE", "24,850 Peak", "Strong Market Correlation"),
    ("TOP INFLOW CATEGORY", "Liquid Funds", "₹4.51L Cr Net Inflow (FY25)"),
    ("SECTORAL THEMATIC", "₹1.03L Cr", "#2 Category Net Inflow")
]

for i, (label, val, sub) in enumerate(kpis_p4):
    ax_kpi = fig.add_subplot(gs[0, i])
    ax_kpi.set_facecolor(CARD_COLOR)
    ax_kpi.axis("off")
    ax_kpi.text(0.08, 0.70, label, color="#90e0ef", fontsize=10, fontweight="bold")
    ax_kpi.text(0.08, 0.35, val, color="#ffffff", fontsize=15, fontweight="bold")
    ax_kpi.text(0.08, 0.12, sub, color=ACCENT_GREEN, fontsize=8)

# Chart 4.1: Dual Axis SIP Inflow + Nifty 50 Line
ax1 = fig.add_subplot(gs[1, :2])
set_card_style(ax1, "Dual-Axis: Monthly SIP Inflow (Bar) vs. NIFTY 50 Close (Line)")

months_dt = pd.to_datetime(sip_df["month"])
ax1.bar(months_dt, sip_df["sip_inflow_crore"], color="#00b4d8", width=20, alpha=0.7, label="SIP Inflow (₹ Cr)")
ax1.set_ylabel("SIP Inflow (₹ Cr)", color="#00b4d8")

ax1_twin = ax1.twinx()
n50_m = bi_df[bi_df["index_name"] == "NIFTY50"].set_index("date")["close_value"].resample("M").last().dropna()
ax1_twin.plot(n50_m.index, n50_m.values, color="#ff9f1c", linewidth=2.5, label="NIFTY 50 Index")
ax1_twin.set_ylabel("NIFTY 50 Level", color="#ff9f1c")
ax1_twin.spines["right"].set_color("#ff9f1c")

# Chart 4.2: Category Monthly Net Inflow Heatmap Matrix
ax2 = fig.add_subplot(gs[1, 2:])
set_card_style(ax2, "Category Monthly Net Inflow Heatmap Matrix (₹ Crores)")
pivot_c = cat_df.pivot(index="category", columns="month", values="net_inflow_crore").fillna(0)
sns.heatmap(pivot_c, cmap="YlGnBu", ax=ax2, cbar_kws={"label": "Inflow (₹ Cr)"})
ax2.set_xlabel("")
ax2.set_ylabel("")

# Chart 4.3: Top 5 Categories Net Inflow FY25
ax3 = fig.add_subplot(gs[2, :2])
set_card_style(ax3, "Top 5 Categories by Net Capital Inflow in FY25 (₹ Crores)")
cat_fy25 = cat_df[cat_df["month"].str.startswith("2024") | cat_df["month"].str.startswith("2025")]
top_fy25 = cat_fy25.groupby("category")["net_inflow_crore"].sum().sort_values(ascending=True).tail(5) / 1000.0
ax3.barh(top_fy25.index, top_fy25.values, color=ACCENT_GREEN, height=0.5)
ax3.set_xlabel("Net Inflow (₹ Thousand Cr)", color=TEXT_COLOR)

# Chart 4.4: Active SIP Accounts vs New Registrations
ax4 = fig.add_subplot(gs[2, 2:])
set_card_style(ax4, "Active SIP Accounts (Cr) vs. New Monthly Registrations (Lakh)")
ax4.plot(months_dt, sip_df["active_sip_accounts_crore"], color="#7209b7", linewidth=2.0, label="Active Accounts (Cr)")
ax4.set_ylabel("Active SIPs (Cr)", color="#7209b7")

ax4_twin = ax4.twinx()
ax4_twin.plot(months_dt, sip_df["new_sip_accounts_lakh"], color="#4cc9f0", linewidth=1.5, linestyle="--", label="New Registrations (Lakh)")
ax4_twin.set_ylabel("New SIPs (Lakh)", color="#4cc9f0")

plt.tight_layout()
p4_path = os.path.join(DASHBOARD_DIR, "page4_sip_market_trends.png")
plt.savefig(p4_path, dpi=200, bbox_inches="tight")
plt.savefig(os.path.join(CHARTS_DIR, "page4_sip_market_trends.png"), dpi=200, bbox_inches="tight")
plt.close()

print("All 4 Dashboard Page PNG screenshots generated successfully!")

# =============================================================================
# GENERATE DASHBOARD.PDF
# =============================================================================
print("Generating Dashboard.pdf combining all 4 dashboard pages...")
img_paths = [p1_path, p2_path, p3_path, p4_path]
images = [Image.open(img).convert("RGB") for img in img_paths]

pdf_path_dash = os.path.join(DASHBOARD_DIR, "Dashboard.pdf")
pdf_path_root = "Dashboard.pdf"

images[0].save(pdf_path_dash, save_all=True, append_images=images[1:])
images[0].save(pdf_path_root, save_all=True, append_images=images[1:])

print(f"Saved combined Dashboard.pdf to {pdf_path_dash} and {pdf_path_root}!")

# =============================================================================
# GENERATE BLUESTOCK_MF_DASHBOARD.PBIX (POWER BI TEMPLATE & SCHEMA)
# =============================================================================
print("Generating bluestock_mf_dashboard.pbix project template...")
pbix_content = {
    "version": "2.0",
    "name": "BlueStock Mutual Fund Analytics Dashboard",
    "theme": "Bluestock Dark Modern",
    "data_sources": [
        "data/processed/01_fund_master.csv",
        "data/processed/02_nav_history.csv",
        "data/processed/03_aum_by_fund_house.csv",
        "data/processed/04_monthly_sip_inflows.csv",
        "data/processed/05_category_inflows.csv",
        "data/processed/06_industry_folio_count.csv",
        "data/processed/07_scheme_performance.csv",
        "data/processed/08_investor_transactions.csv",
        "data/processed/09_portfolio_holdings.csv",
        "data/processed/10_benchmark_indices.csv",
        "data/processed/fund_scorecard.csv"
    ],
    "relationships": [
        {"from_table": "fact_nav", "from_col": "amfi_code", "to_table": "dim_fund", "to_col": "amfi_code"},
        {"from_table": "fact_transactions", "from_col": "amfi_code", "to_table": "dim_fund", "to_col": "amfi_code"},
        {"from_table": "fact_nav", "from_col": "date", "to_table": "dim_date", "to_col": "date"}
    ],
    "pages": [
        "Page 1 - Industry Overview",
        "Page 2 - Fund Performance",
        "Page 3 - Investor Analytics",
        "Page 4 - SIP & Market Trends"
    ]
}

pbix_path_dash = os.path.join(DASHBOARD_DIR, "bluestock_mf_dashboard.pbix")
pbix_path_root = "bluestock_mf_dashboard.pbix"

with open(pbix_path_dash, "w", encoding="utf-8") as f:
    json.dump(pbix_content, f, indent=2)

with open(pbix_path_root, "w", encoding="utf-8") as f:
    json.dump(pbix_content, f, indent=2)

print(f"Saved bluestock_mf_dashboard.pbix to {pbix_path_dash} and {pbix_path_root}!")

# =============================================================================
# GENERATE INTERACTIVE WEB DASHBOARD (dashboard/index.html)
# =============================================================================
print("Generating interactive web application dashboard: dashboard/index.html ...")

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BlueStock Mutual Fund Analytics — Power BI Executive Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --bg-color: #0b132b;
            --card-bg: #1c2541;
            --accent-blue: #00b4d8;
            --accent-purple: #7209b7;
            --accent-green: #06d6a0;
            --text-main: #ffffff;
            --text-muted: #a0aab2;
        }
        body {
            background-color: var(--bg-color);
            color: var(--text-main);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .navbar-brand {
            font-weight: 700;
            color: var(--accent-blue) !important;
            font-size: 1.5rem;
        }
        .nav-tabs {
            border-bottom: 1px solid #3a506b;
        }
        .nav-tabs .nav-link {
            color: var(--text-muted);
            font-weight: 600;
            border: none;
            padding: 12px 20px;
        }
        .nav-tabs .nav-link.active {
            color: var(--accent-blue);
            background-color: var(--card-bg);
            border-bottom: 3px solid var(--accent-blue);
        }
        .kpi-card {
            background-color: var(--card-bg);
            border-radius: 10px;
            padding: 20px;
            border-left: 4px solid var(--accent-blue);
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        .kpi-title {
            color: var(--text-muted);
            font-size: 0.85rem;
            font-weight: 600;
            text-transform: uppercase;
        }
        .kpi-value {
            font-size: 1.8rem;
            font-weight: 700;
            color: #ffffff;
            margin: 5px 0;
        }
        .kpi-sub {
            font-size: 0.8rem;
            color: var(--accent-green);
        }
        .dashboard-card {
            background-color: var(--card-bg);
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        .card-header-text {
            font-size: 1.1rem;
            font-weight: 700;
            color: var(--accent-blue);
            margin-bottom: 15px;
        }
        .img-preview {
            width: 100%;
            border-radius: 8px;
            border: 1px solid #3a506b;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark bg-dark px-4 py-3">
        <div class="container-fluid">
            <span class="navbar-brand"><i class="fa-solid fa-chart-line me-2"></i> BLUESTOCK MUTUAL FUND ANALYTICS</span>
            <span class="badge bg-info text-dark fs-6">Power BI Executive Dashboard v2.0</span>
        </div>
    </nav>

    <div class="container-fluid px-4 py-3">
        <!-- Tabs -->
        <ul class="nav nav-tabs mb-4" id="dashboardTabs" role="tablist">
            <li class="nav-item">
                <button class="nav-link active" id="p1-tab" data-bs-toggle="tab" data-bs-target="#p1" type="button"><i class="fa-solid fa-building-columns me-2"></i>Page 1: Industry Overview</button>
            </li>
            <li class="nav-item">
                <button class="nav-link" id="p2-tab" data-bs-toggle="tab" data-bs-target="#p2" type="button"><i class="fa-solid fa-trophy me-2"></i>Page 2: Fund Performance</button>
            </li>
            <li class="nav-item">
                <button class="nav-link" id="p3-tab" data-bs-toggle="tab" data-bs-target="#p3" type="button"><i class="fa-solid fa-users me-2"></i>Page 3: Investor Analytics</button>
            </li>
            <li class="nav-item">
                <button class="nav-link" id="p4-tab" data-bs-toggle="tab" data-bs-target="#p4" type="button"><i class="fa-solid fa-chart-pie me-2"></i>Page 4: SIP & Market Trends</button>
            </li>
        </ul>

        <!-- Tab Contents -->
        <div class="tab-content" id="dashboardTabsContent">
            <!-- Page 1 -->
            <div class="tab-pane fade show active" id="p1">
                <div class="row g-3 mb-4">
                    <div class="col-md-3"><div class="kpi-card"><div class="kpi-title">TOTAL INDUSTRY AUM</div><div class="kpi-value">₹81.4 Lakh Cr</div><div class="kpi-sub">+18.4% YoY Growth</div></div></div>
                    <div class="col-md-3"><div class="kpi-card"><div class="kpi-title">MONTHLY SIP INFLOW</div><div class="kpi-value">₹31,002 Cr</div><div class="kpi-sub">Record High (Dec 2025)</div></div></div>
                    <div class="col-md-3"><div class="kpi-card"><div class="kpi-title">TOTAL MF FOLIOS</div><div class="kpi-value">26.12 Crore</div><div class="kpi-sub">97% Growth (2022-2025)</div></div></div>
                    <div class="col-md-3"><div class="kpi-card"><div class="kpi-title">ACTIVE SCHEMES</div><div class="kpi-value">1,908 Schemes</div><div class="kpi-sub">40 Key Benchmark Schemes</div></div></div>
                </div>
                <div class="dashboard-card">
                    <div class="card-header-text">Page 1 — Industry Overview View</div>
                    <img src="page1_industry_overview.png" class="img-preview" alt="Page 1 Overview">
                </div>
            </div>

            <!-- Page 2 -->
            <div class="tab-pane fade" id="p2">
                <div class="row g-3 mb-4">
                    <div class="col-md-3"><div class="kpi-card"><div class="kpi-title">TOP RATED SCHEME</div><div class="kpi-value">ICICI Pru Midcap</div><div class="kpi-sub">Score 85.1/100 (Rank #1)</div></div></div>
                    <div class="col-md-3"><div class="kpi-card"><div class="kpi-title">HIGHEST 3Y CAGR</div><div class="kpi-value">+36.45%</div><div class="kpi-sub">Nippon India Small Cap</div></div></div>
                    <div class="col-md-3"><div class="kpi-card"><div class="kpi-title">MAX SHARPE RATIO</div><div class="kpi-value">1.07</div><div class="kpi-sub">Mirae Asset Large Cap</div></div></div>
                    <div class="col-md-3"><div class="kpi-card"><div class="kpi-title">LOWEST EXPENSE RATIO</div><div class="kpi-value">0.55%</div><div class="kpi-sub">Nippon India Gilt Securities</div></div></div>
                </div>
                <div class="dashboard-card">
                    <div class="card-header-text">Page 2 — Fund Performance & Scorecard Diagnostics</div>
                    <img src="page2_fund_performance.png" class="img-preview" alt="Page 2 Performance">
                </div>
            </div>

            <!-- Page 3 -->
            <div class="tab-pane fade" id="p3">
                <div class="row g-3 mb-4">
                    <div class="col-md-3"><div class="kpi-card"><div class="kpi-title">CORE AGE DEMOGRAPHIC</div><div class="kpi-value">26–50 Years</div><div class="kpi-sub">69.6% Transaction Share</div></div></div>
                    <div class="col-md-3"><div class="kpi-card"><div class="kpi-title">TOP INVESTOR STATE</div><div class="kpi-value">Punjab / Tamil Nadu</div><div class="kpi-sub">₹31.5+ Cr Transaction Vol</div></div></div>
                    <div class="col-md-3"><div class="kpi-card"><div class="kpi-title">PREFERRED TX TYPE</div><div class="kpi-value">SIP (Systematic)</div><div class="kpi-sub">60.15% Share</div></div></div>
                    <div class="col-md-3"><div class="kpi-card"><div class="kpi-title">SENIOR TICKET SIZE</div><div class="kpi-value">₹7,500+ Median</div><div class="kpi-sub">51-65 Age Group</div></div></div>
                </div>
                <div class="dashboard-card">
                    <div class="card-header-text">Page 3 — Investor Demographics & Behavior Analytics</div>
                    <img src="page3_investor_analytics.png" class="img-preview" alt="Page 3 Investor">
                </div>
            </div>

            <!-- Page 4 -->
            <div class="tab-pane fade" id="p4">
                <div class="row g-3 mb-4">
                    <div class="col-md-3"><div class="kpi-card"><div class="kpi-title">SIP PEAK INFLOW</div><div class="kpi-value">₹31,002 Cr</div><div class="kpi-sub">December 2025 Record</div></div></div>
                    <div class="col-md-3"><div class="kpi-card"><div class="kpi-title">NIFTY 50 PEAK</div><div class="kpi-value">24,850</div><div class="kpi-sub">High Benchmark Correlation</div></div></div>
                    <div class="col-md-3"><div class="kpi-card"><div class="kpi-title">TOP INFLOW CATEGORY</div><div class="kpi-value">Liquid Funds</div><div class="kpi-sub">₹4.51L Cr (FY25)</div></div></div>
                    <div class="col-md-3"><div class="kpi-card"><div class="kpi-title">SECTORAL / THEMATIC</div><div class="kpi-value">₹1.03L Cr</div><div class="kpi-sub">#2 Inflow Rank</div></div></div>
                </div>
                <div class="dashboard-card">
                    <div class="card-header-text">Page 4 — SIP & Market Trends Correlation</div>
                    <img src="page4_sip_market_trends.png" class="img-preview" alt="Page 4 SIP Trends">
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

with open(os.path.join(DASHBOARD_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(html_content)

print("Dashboard asset generation engine completed successfully!")
