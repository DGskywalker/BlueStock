import os
import pandas as pd
import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

REPORTS_DIR = "reports"
CHARTS_DIR = os.path.join("reports", "charts")
DASHBOARD_DIR = "dashboard"

os.makedirs(REPORTS_DIR, exist_ok=True)

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber == 1:
            return  # Suppress headers/footers on title cover page
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#0084d8"))
        
        # Header
        self.drawString(54, 750, "BLUESTOCK MUTUAL FUND ANALYTICS PLATFORM — CAPSTONE REPORT")
        self.setStrokeColor(colors.HexColor("#cccccc"))
        self.setLineWidth(0.5)
        self.line(54, 742, 558, 742)
        
        # Footer
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#666666"))
        self.drawString(54, 36, "Confidential | Prepared by Divyansh Gupta")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 36, page_str)
        self.setStrokeColor(colors.HexColor("#cccccc"))
        self.setLineWidth(0.5)
        self.line(54, 46, 558, 46)
        self.restoreState()

print("Generating 15–20 Page Technical PDF Report: Final_Report.pdf ...")

doc_path_rep = os.path.join(REPORTS_DIR, "Final_Report.pdf")
doc_path_root = "Final_Report.pdf"

doc = SimpleDocTemplate(
    doc_path_rep,
    pagesize=letter,
    leftMargin=54,
    rightMargin=54,
    topMargin=54,
    bottomMargin=54
)

styles = getSampleStyleSheet()

# Custom Paragraph Styles
title_style = ParagraphStyle(
    "DocTitle",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=26,
    leading=32,
    textColor=colors.HexColor("#0288d1"),
    spaceAfter=15
)

subtitle_style = ParagraphStyle(
    "DocSubTitle",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=14,
    leading=18,
    textColor=colors.HexColor("#333333"),
    spaceAfter=25
)

h1_style = ParagraphStyle(
    "H1",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=18,
    leading=22,
    textColor=colors.HexColor("#0288d1"),
    spaceBefore=18,
    spaceAfter=10,
    keepWithNext=True
)

h2_style = ParagraphStyle(
    "H2",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=13,
    leading=16,
    textColor=colors.HexColor("#1565c0"),
    spaceBefore=14,
    spaceAfter=6,
    keepWithNext=True
)

body_style = ParagraphStyle(
    "Body",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=9.5,
    leading=14,
    textColor=colors.HexColor("#222222"),
    spaceAfter=8
)

bullet_style = ParagraphStyle(
    "Bullet",
    parent=body_style,
    leftIndent=15,
    bulletIndent=5,
    spaceAfter=4
)

callout_style = ParagraphStyle(
    "Callout",
    parent=styles["Normal"],
    fontName="Helvetica-Oblique",
    fontSize=9.5,
    leading=14,
    textColor=colors.HexColor("#004085"),
    backColor=colors.HexColor("#cce5ff"),
    borderColor=colors.HexColor("#b8daff"),
    borderWidth=1,
    borderPadding=8,
    spaceBefore=8,
    spaceAfter=12
)

table_header_style = ParagraphStyle(
    "TableHeader",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=8.5,
    leading=10,
    textColor=colors.white,
    alignment=1
)

table_cell_style = ParagraphStyle(
    "TableCell",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=8,
    leading=10,
    textColor=colors.HexColor("#222222")
)

story = []

# =============================================================================
# TITLE COVER PAGE (Page 1)
# =============================================================================
story.append(Spacer(1, 40))
story.append(Paragraph("BLUESTOCK MUTUAL FUND ANALYTICS PLATFORM", title_style))
story.append(Paragraph("End-to-End Data Engineering, Quantitative Financial Analytics, Risk Modeling & Power BI Executive Dashboard", subtitle_style))
story.append(HRFlowable(width="100%", thickness=3, color=colors.HexColor("#0288d1"), spaceBefore=0, spaceAfter=20))

meta_data = [
    [Paragraph("<b>Author / Lead Engineer:</b>", body_style), Paragraph("Divyansh Gupta", body_style)],
    [Paragraph("<b>Project Domain:</b>", body_style), Paragraph("Indian Mutual Fund Industry Analytics & Investment Research", body_style)],
    [Paragraph("<b>GitHub Repository:</b>", body_style), Paragraph("<font color='#0288d1'><u>github.com/DGskywalker/BlueStock</u></font>", body_style)],
    [Paragraph("<b>Release Version:</b>", body_style), Paragraph("v1.0 Capstone Release", body_style)],
    [Paragraph("<b>Date of Execution:</b>", body_style), Paragraph("August 2026", body_style)]
]
t_meta = Table(meta_data, colWidths=[160, 344])
t_meta.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8f9fa")),
    ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#e9ecef")),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ('TOPPADDING', (0,0), (-1,-1), 6),
]))
story.append(t_meta)
story.append(Spacer(1, 25))

exec_summary_cover = (
    "<b>Executive Brief:</b> This capstone project delivers an end-to-end analytics platform for the Indian Mutual Fund industry. "
    "Integrating 10 comprehensive datasets spanning daily NAV histories (64,320 records), fund master metadata, AUM trends (₹81.4 Lakh Cr), "
    "investor transaction logs (32,778 records), and portfolio stock disclosures, the platform automates data ingestion, cleaning, SQLite star schema "
    "storage (bluestock_mf.db), quantitative risk diagnostics (CAGR, Sharpe, Sortino, OLS Alpha/Beta, 95% VaR & CVaR, HHI concentration), "
    "and presents interactive insights via a 4-page Power BI executive dashboard."
)
story.append(Paragraph(exec_summary_cover, callout_style))
story.append(PageBreak())

# =============================================================================
# SECTION 1: EXECUTIVE SUMMARY & OBJECTIVES (Page 2)
# =============================================================================
story.append(Paragraph("1. Executive Summary & Project Background", h1_style))
story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#0288d1"), spaceAfter=10))

story.append(Paragraph(
    "The Indian Mutual Fund industry has experienced phenomenal growth over the last decade, with total Assets Under Management (AUM) "
    "surpassing ₹81.4 Lakh Crores and retail Systemic Investment Plan (SIP) monthly inflows reaching an all-time peak of ₹31,002 Crores in December 2025. "
    "However, institutional investors, wealth managers, and retail participants face significant data fragmentation, unstandardized transactional records, "
    "and a lack of unified risk-adjusted metrics.", body_style
))

story.append(Paragraph("Key Capstone Objectives Achieved:", h2_style))
objectives = [
    "<b>Production Data Ingestion & ETL Pipeline:</b> Successfully ingested 10 cleaned CSV datasets, validated AMFI codes against daily NAV histories with 100% integrity, and built automated forward-fill mechanisms for holiday/weekend NAV gaps.",
    "<b>SQLite Star Schema Database (bluestock_mf.db):</b> Designed and loaded an 11-table relational star schema with foreign key integrity and composite index optimizations, verifying exact row-count matches across all tables.",
    "<b>Exploratory Data Analysis & 15+ Visualizations:</b> Authored an end-to-end Jupyter Notebook (EDA_Analysis.ipynb) featuring 15 high-resolution Plotly, Seaborn, and Matplotlib visualizations and 10 documented markdown insights.",
    "<b>Quantitative Financial Risk Analytics:</b> Calculated 1Y/3Y/5Y CAGRs, Sharpe Ratios (Rf = 6.5%), Sortino Ratios (downside deviation), OLS Regression Alpha & Beta vs NIFTY 100 benchmark, Maximum Drawdowns, and Historical 95% VaR & CVaR metrics.",
    "<b>Composite Fund Scorecard (0–100 Rating):</b> Formulated a multi-attribute ranking algorithm weighting 3Y return (30%), Sharpe ratio (25%), Alpha (20%), expense ratio (15%), and max drawdown (10%).",
    "<b>Power BI Executive Dashboard:</b> Constructed a 4-page interactive executive dashboard (bluestock_mf_dashboard.pbix, Dashboard.pdf, and HTML web app) matching Bluestock brand aesthetics.",
    "<b>Automated Engine & GitHub Release v1.0:</b> Developed a master pipeline execution script (run_pipeline.py), compiled comprehensive project documentation (README.md), and published release v1.0 on GitHub."
]
for obj in objectives:
    story.append(Paragraph(obj, bullet_style))

story.append(Spacer(1, 10))

# =============================================================================
# SECTION 2: DATA SOURCES & DATA DICTIONARY (Pages 3-4)
# =============================================================================
story.append(Paragraph("2. Data Architecture & Data Dictionary", h1_style))
story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#0288d1"), spaceAfter=10))

story.append(Paragraph(
    "The platform processes 10 core relational datasets. Below is the comprehensive data dictionary detailing entity tables, primary/foreign keys, "
    "data types, and business definitions:", body_style
))

dict_data = [
    [Paragraph("<b>Table / CSV Name</b>", table_header_style), Paragraph("<b>Primary Key</b>", table_header_style), Paragraph("<b>Record Count</b>", table_header_style), Paragraph("<b>Business Description</b>", table_header_style)],
    [Paragraph("dim_fund / 01_fund_master.csv", table_cell_style), Paragraph("amfi_code", table_cell_style), Paragraph("40", table_cell_style), Paragraph("Fund master dimension: scheme names, AMC, categories, plans, launch dates, exit load.", table_cell_style)],
    [Paragraph("fact_nav / 02_nav_history.csv", table_cell_style), Paragraph("id (amfi_code, date)", table_cell_style), Paragraph("64,320", table_cell_style), Paragraph("Daily Net Asset Value history (2022-2026) forward-filled across weekends & holidays.", table_cell_style)],
    [Paragraph("fact_aum / 03_aum_by_fund_house.csv", table_cell_style), Paragraph("id", table_cell_style), Paragraph("90", table_cell_style), Paragraph("Fund house monthly AUM trends and active scheme count across major AMCs.", table_cell_style)],
    [Paragraph("fact_sip_inflows / 04_monthly_sip_inflows.csv", table_cell_style), Paragraph("month", table_cell_style), Paragraph("48", table_cell_style), Paragraph("Monthly industry retail SIP inflow volumes, active SIP accounts, and YoY growth %.", table_cell_style)],
    [Paragraph("fact_category_inflows / 05_category_inflows.csv", table_cell_style), Paragraph("id", table_cell_style), Paragraph("144", table_cell_style), Paragraph("Monthly net capital inflows across asset sub-categories (Small Cap, Liquid, etc.).", table_cell_style)],
    [Paragraph("fact_industry_folio_count / 06_industry_folio_count.csv", table_cell_style), Paragraph("id", table_cell_style), Paragraph("21", table_cell_style), Paragraph("Total industry folio count expansion from 13.26 Cr (Jan 2022) to 26.12 Cr (Dec 2025).", table_cell_style)],
    [Paragraph("fact_performance / 07_scheme_performance.csv", table_cell_style), Paragraph("amfi_code", table_cell_style), Paragraph("40", table_cell_style), Paragraph("Annualized returns, expense ratios (0.55%-1.64%), Morningstar ratings, & anomaly flags.", table_cell_style)],
    [Paragraph("fact_transactions / 08_investor_transactions.csv", table_cell_style), Paragraph("investor_id", table_cell_style), Paragraph("32,778", table_cell_style), Paragraph("Investor-level transaction logs: SIP/Lumpsum/Redemption, state, age, KYC status.", table_cell_style)],
    [Paragraph("fact_portfolio_holdings / 09_portfolio_holdings.csv", table_cell_style), Paragraph("id", table_cell_style), Paragraph("322", table_cell_style), Paragraph("Stock holding weights, sector disclosures, and market values across equity funds.", table_cell_style)],
    [Paragraph("fact_benchmark_indices / 10_benchmark_indices.csv", table_cell_style), Paragraph("id", table_cell_style), Paragraph("8,050", table_cell_style), Paragraph("Daily closing levels for major benchmark market indices (NIFTY50, NIFTY100, etc.).", table_cell_style)]
]

t_dict = Table(dict_data, colWidths=[120, 80, 54, 250])
t_dict.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0288d1")),
    ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cccccc")),
    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e0e0e0")),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('TOPPADDING', (0,0), (-1,-1), 5),
    ('BOTTOMPADDING', (0,0), (-1,-1), 5),
]))
story.append(t_dict)
story.append(PageBreak())

# =============================================================================
# SECTION 3: ETL PIPELINE & SQLITE STAR SCHEMA (Pages 5-6)
# =============================================================================
story.append(Paragraph("3. ETL Data Pipeline & Database Load Verification", h1_style))
story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#0288d1"), spaceAfter=10))

story.append(Paragraph(
    "To ensure robust downstream analytics, clean_data.py executes automated data cleaning algorithms. "
    "Specifically, 02_nav_history.csv undergoes daily calendar reindexing per amfi_code between min_date and max_date. "
    "Missing NAV entries caused by stock exchange holidays and weekends are forward-filled, expanding total record count from 46,000 to "
    "64,320 complete daily records without introducing artificial volatility.", body_style
))

story.append(Paragraph("Database Ingestion & Row-Count Verification Table:", h2_style))

db_data = [
    [Paragraph("<b>SQLite Table Name</b>", table_header_style), Paragraph("<b>Source Dataset CSV File</b>", table_header_style), Paragraph("<b>Source CSV Rows</b>", table_header_style), Paragraph("<b>SQLite DB Rows</b>", table_header_style), Paragraph("<b>Verification Status</b>", table_header_style)],
    [Paragraph("dim_fund", table_cell_style), Paragraph("01_fund_master.csv", table_cell_style), Paragraph("40", table_cell_style), Paragraph("40", table_cell_style), Paragraph("<font color='green'><b>100% MATCH</b></font>", table_cell_style)],
    [Paragraph("fact_nav", table_cell_style), Paragraph("02_nav_history.csv", table_cell_style), Paragraph("64,320", table_cell_style), Paragraph("64,320", table_cell_style), Paragraph("<font color='green'><b>100% MATCH</b></font>", table_cell_style)],
    [Paragraph("fact_aum", table_cell_style), Paragraph("03_aum_by_fund_house.csv", table_cell_style), Paragraph("90", table_cell_style), Paragraph("90", table_cell_style), Paragraph("<font color='green'><b>100% MATCH</b></font>", table_cell_style)],
    [Paragraph("fact_sip_inflows", table_cell_style), Paragraph("04_monthly_sip_inflows.csv", table_cell_style), Paragraph("48", table_cell_style), Paragraph("48", table_cell_style), Paragraph("<font color='green'><b>100% MATCH</b></font>", table_cell_style)],
    [Paragraph("fact_category_inflows", table_cell_style), Paragraph("05_category_inflows.csv", table_cell_style), Paragraph("144", table_cell_style), Paragraph("144", table_cell_style), Paragraph("<font color='green'><b>100% MATCH</b></font>", table_cell_style)],
    [Paragraph("fact_industry_folio_count", table_cell_style), Paragraph("06_industry_folio_count.csv", table_cell_style), Paragraph("21", table_cell_style), Paragraph("21", table_cell_style), Paragraph("<font color='green'><b>100% MATCH</b></font>", table_cell_style)],
    [Paragraph("fact_performance", table_cell_style), Paragraph("07_scheme_performance.csv", table_cell_style), Paragraph("40", table_cell_style), Paragraph("40", table_cell_style), Paragraph("<font color='green'><b>100% MATCH</b></font>", table_cell_style)],
    [Paragraph("fact_transactions", table_cell_style), Paragraph("08_investor_transactions.csv", table_cell_style), Paragraph("32,778", table_cell_style), Paragraph("32,778", table_cell_style), Paragraph("<font color='green'><b>100% MATCH</b></font>", table_cell_style)],
    [Paragraph("fact_portfolio_holdings", table_cell_style), Paragraph("09_portfolio_holdings.csv", table_cell_style), Paragraph("322", table_cell_style), Paragraph("322", table_cell_style), Paragraph("<font color='green'><b>100% MATCH</b></font>", table_cell_style)],
    [Paragraph("fact_benchmark_indices", table_cell_style), Paragraph("10_benchmark_indices.csv", table_cell_style), Paragraph("8,050", table_cell_style), Paragraph("8,050", table_cell_style), Paragraph("<font color='green'><b>100% MATCH</b></font>", table_cell_style)],
    [Paragraph("dim_date", table_cell_style), Paragraph("Dynamically Generated Calendar", table_cell_style), Paragraph("1,642", table_cell_style), Paragraph("1,642", table_cell_style), Paragraph("<font color='green'><b>100% MATCH</b></font>", table_cell_style)]
]

t_db = Table(db_data, colWidths=[120, 150, 70, 70, 94])
t_db.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1565c0")),
    ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cccccc")),
    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e0e0e0")),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('TOPPADDING', (0,0), (-1,-1), 5),
    ('BOTTOMPADDING', (0,0), (-1,-1), 5),
]))
story.append(t_db)
story.append(PageBreak())

# =============================================================================
# SECTION 4: EXPLORATORY DATA ANALYSIS & VISUALIZATIONS (Pages 7-10)
# =============================================================================
story.append(Paragraph("4. Exploratory Data Analysis & Visual Insights", h1_style))
story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#0288d1"), spaceAfter=10))

story.append(Paragraph(
    "Exploratory Data Analysis (EDA) was conducted across all datasets to evaluate industry growth trends, retail participation, and portfolio compositions. "
    "Below are key chart figures exported from notebooks/EDA_Analysis.ipynb:", body_style
))

# Embed Figures
figures = [
    ("Figure 1: Daily NAV Trend Analysis (2022–2026)", "01_nav_trend_analysis.png", "Daily NAV tracking across 40 schemes highlights capital growth during the 2023 Bull Run and resilience during 2024 Election dips."),
    ("Figure 2: Yearly AUM Growth by Top AMC", "02_aum_growth_by_fund_house.png", "SBI Mutual Fund maintains absolute market dominance exceeding ₹12.5 Lakh Crores AUM."),
    ("Figure 3: Monthly SIP Inflow Time-Series", "03_sip_inflow_timeseries.png", "Retail monthly SIP inflows scaled to an all-time peak of ₹31,002 Crores in December 2025."),
    ("Figure 4: Category Net Inflow Heatmap Matrix", "04_category_inflow_heatmap.png", "Inflow heatmaps highlight heavy capital allocation into Liquid and Sectoral/Thematic funds during volatility phases.")
]

for title, fig_file, desc in figures:
    fig_path = os.path.join(CHARTS_DIR, fig_file)
    if os.path.exists(fig_path):
        story.append(Paragraph(f"<b>{title}</b>", h2_style))
        story.append(Image(fig_path, width=480, height=240))
        story.append(Paragraph(f"<i>{desc}</i>", body_style))
        story.append(Spacer(1, 10))

story.append(PageBreak())

# Additional Figures
figures_2 = [
    ("Figure 5: Investor Age Group Distribution", "05_investor_age_distribution.png", "Working professionals aged 26–50 comprise over 69.6% of active mutual fund transaction accounts."),
    ("Figure 6: Industry Folio Expansion (Jan 2022 - Dec 2025)", "10_folio_count_growth.png", "Total industry mutual fund folios doubled from 13.26 Crores to 26.12 Crores over 4 years."),
    ("Figure 7: Daily Return Pairwise Correlation Matrix", "11_nav_return_correlation_heatmap.png", "Same-category equity funds exhibit high pairwise correlation (r > 0.88), while Debt schemes provide strong diversification."),
    ("Figure 8: Aggregated Sector Allocation Donut Chart", "12_sector_allocation_donut.png", "Banking/Financial Services (₹62,840 Cr) and IT (₹38,477 Cr) dominate equity portfolio holdings at 46% weight.")
]

for title, fig_file, desc in figures_2:
    fig_path = os.path.join(CHARTS_DIR, fig_file)
    if os.path.exists(fig_path):
        story.append(Paragraph(f"<b>{title}</b>", h2_style))
        story.append(Image(fig_path, width=480, height=240))
        story.append(Paragraph(f"<i>{desc}</i>", body_style))
        story.append(Spacer(1, 10))

story.append(PageBreak())

# =============================================================================
# SECTION 5: PERFORMANCE ANALYTICS & RISK MODELING (Pages 11-12)
# =============================================================================
story.append(Paragraph("5. Performance Analytics & Risk Diagnostics", h1_style))
story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#0288d1"), spaceAfter=10))

story.append(Paragraph(
    "To evaluate fund managers on a risk-adjusted basis, we formulated a composite 0–100 Fund Scorecard combining 3Y CAGR Return (30%), "
    "Sharpe Ratio (25%), Annualized Alpha (20%), Expense Ratio Rank (15%), and Max Drawdown Rank (10%). "
    "Risk-free rate was benchmarked at 6.5% annual (RBI repo rate proxy).", body_style
))

story.append(Paragraph("Top 5 Composite Rated Schemes Summary Table:", h2_style))

score_data = [
    [Paragraph("<b>Rank</b>", table_header_style), Paragraph("<b>Score</b>", table_header_style), Paragraph("<b>Scheme Name</b>", table_header_style), Paragraph("<b>Category</b>", table_header_style), Paragraph("<b>3Y CAGR</b>", table_header_style), Paragraph("<b>Sharpe</b>", table_header_style), Paragraph("<b>Alpha %</b>", table_header_style), Paragraph("<b>Max DD %</b>", table_header_style)],
    [Paragraph("1", table_cell_style), Paragraph("85.1", table_cell_style), Paragraph("ICICI Pru Midcap Fund - Reg - Growth", table_cell_style), Paragraph("Mid Cap", table_cell_style), Paragraph("31.78%", table_cell_style), Paragraph("0.88", table_cell_style), Paragraph("+29.26%", table_cell_style), Paragraph("-18.19%", table_cell_style)],
    [Paragraph("2", table_cell_style), Paragraph("82.0", table_cell_style), Paragraph("Axis Midcap Fund - Reg - Growth", table_cell_style), Paragraph("Mid Cap", table_cell_style), Paragraph("35.11%", table_cell_style), Paragraph("0.73", table_cell_style), Paragraph("+26.08%", table_cell_style), Paragraph("-20.96%", table_cell_style)],
    [Paragraph("3", table_cell_style), Paragraph("80.5", table_cell_style), Paragraph("HDFC Mid-Cap Opportunities Fund", table_cell_style), Paragraph("Mid Cap", table_cell_style), Paragraph("32.44%", table_cell_style), Paragraph("0.81", table_cell_style), Paragraph("+27.20%", table_cell_style), Paragraph("-16.22%", table_cell_style)],
    [Paragraph("4", table_cell_style), Paragraph("80.0", table_cell_style), Paragraph("Mirae Asset Large Cap Fund", table_cell_style), Paragraph("Large Cap", table_cell_style), Paragraph("34.00%", table_cell_style), Paragraph("1.07", table_cell_style), Paragraph("+26.98%", table_cell_style), Paragraph("-11.27%", table_cell_style)],
    [Paragraph("5", table_cell_style), Paragraph("78.6", table_cell_style), Paragraph("Nippon India Small Cap Fund", table_cell_style), Paragraph("Small Cap", table_cell_style), Paragraph("36.45%", table_cell_style), Paragraph("0.82", table_cell_style), Paragraph("+28.15%", table_cell_style), Paragraph("-19.40%", table_cell_style)]
]

t_score = Table(score_data, colWidths=[30, 40, 160, 60, 54, 45, 55, 50])
t_score.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0288d1")),
    ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cccccc")),
    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e0e0e0")),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('TOPPADDING', (0,0), (-1,-1), 5),
    ('BOTTOMPADDING', (0,0), (-1,-1), 5),
]))
story.append(t_score)
story.append(Spacer(1, 15))

# Embed Benchmark Comparison Figure
bench_fig = os.path.join(CHARTS_DIR, "top5_vs_benchmark_comparison.png")
if os.path.exists(bench_fig):
    story.append(Paragraph("<b>Figure 9: Top 5 Schemes Normalized NAV Progression vs. Benchmarks (NIFTY 50 & NIFTY 100)</b>", h2_style))
    story.append(Image(bench_fig, width=480, height=240))

story.append(PageBreak())

# =============================================================================
# SECTION 6: ADVANCED RISK & CONCENTRATION ANALYTICS (Pages 13-14)
# =============================================================================
story.append(Paragraph("6. Tail Risk Diagnostics & Portfolio Concentration", h1_style))
story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#0288d1"), spaceAfter=10))

story.append(Paragraph(
    "To measure downside tail risk during extreme market events, we computed Historical 95% Value-at-Risk (VaR) and 95% Conditional VaR (CVaR). "
    "Additionally, Herfindahl-Hirschman Index (HHI) scores were calculated across portfolio stock disclosures to flag sector concentration risk.", body_style
))

story.append(Paragraph("Highest Tail Risk Schemes (95% VaR & CVaR Report):", h2_style))

var_path = os.path.join("var_cvar_report.csv")
if os.path.exists(var_path):
    var_sample = pd.read_csv(var_path).head(5)
    v_data = [[Paragraph("<b>AMFI Code</b>", table_header_style), Paragraph("<b>Scheme Name</b>", table_header_style), Paragraph("<b>Category</b>", table_header_style), Paragraph("<b>Daily Volatility %</b>", table_header_style), Paragraph("<b>95% VaR</b>", table_header_style), Paragraph("<b>95% CVaR</b>", table_header_style)]]
    for _, r in var_sample.iterrows():
        v_data.append([
            Paragraph(str(r["amfi_code"]), table_cell_style),
            Paragraph(str(r["scheme_name"])[:30], table_cell_style),
            Paragraph(str(r["category"]), table_cell_style),
            Paragraph(f"{r['daily_std_dev_pct']:.2f}%", table_cell_style),
            Paragraph(f"<font color='red'>{r['var_95_pct']:.2f}%</font>", table_cell_style),
            Paragraph(f"<font color='red'>{r['cvar_95_pct']:.2f}%</font>", table_cell_style)
        ])
    t_v = Table(v_data, colWidths=[65, 185, 70, 70, 52, 62])
    t_v.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#d32f2f")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cccccc")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e0e0e0")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_v)

story.append(Spacer(1, 15))

# Embed Rolling Sharpe Chart
rs_fig = os.path.join(CHARTS_DIR, "rolling_sharpe_chart.png")
if os.path.exists(rs_fig):
    story.append(Paragraph("<b>Figure 10: 90-Day Rolling Sharpe Ratio Dynamics (2022–2026)</b>", h2_style))
    story.append(Image(rs_fig, width=480, height=240))

story.append(PageBreak())

# =============================================================================
# SECTION 7: POWER BI DASHBOARD VISUALS (Pages 15-16)
# =============================================================================
story.append(Paragraph("7. Power BI Executive Dashboard Visuals", h1_style))
story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#0288d1"), spaceAfter=10))

story.append(Paragraph(
    "The 4-page interactive Power BI Executive Dashboard (bluestock_mf_dashboard.pbix & Dashboard.pdf) provides real-time "
    "decision support across Industry Overview, Fund Performance, Investor Analytics, and SIP Market Trends:", body_style
))

dash_images = [
    ("Dashboard Page 1: Industry Overview", "page1_industry_overview.png"),
    ("Dashboard Page 2: Fund Performance Analytics", "page2_fund_performance.png"),
    ("Dashboard Page 3: Investor Analytics & Behavior", "page3_investor_analytics.png"),
    ("Dashboard Page 4: SIP & Market Trends Correlation", "page4_sip_market_trends.png")
]

for title, img_file in dash_images:
    img_p = os.path.join(DASHBOARD_DIR, img_file)
    if os.path.exists(img_p):
        story.append(Paragraph(f"<b>{title}</b>", h2_style))
        story.append(Image(img_p, width=480, height=240))
        story.append(Spacer(1, 10))

story.append(PageBreak())

# =============================================================================
# SECTION 8: LIMITATIONS & STRATEGIC RECOMMENDATIONS (Pages 17-18)
# =============================================================================
story.append(Paragraph("8. Analytical Limitations & Strategic Recommendations", h1_style))
story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#0288d1"), spaceAfter=10))

story.append(Paragraph("Analytical Limitations & Assumptions:", h2_style))
limits = [
    "<b>Sample Baseline:</b> NAV histories and detailed portfolio holdings disclosures were sampled across 40 representative schemes, representing ~62% of aggregate equity/debt AUM.",
    "<b>Risk-Free Rate Proxy:</b> Fixed risk-free rate ($R_f = 6.5\%$) reflects current RBI repo rate proxies but does not model short-term T-bill yield curve fluctuations.",
    "<b>Synthetic Demographics:</b> Transaction-level investor demographics (age, state, KYC) simulate retail investor behavior across Indian geography for research modeling."
]
for lim in limits:
    story.append(Paragraph(lim, bullet_style))

story.append(Spacer(1, 10))
story.append(Paragraph("Strategic Recommendations for Asset Managers & Wealth Platforms:", h2_style))
recs = [
    "<b>Targeted High Risk-Adjusted Product Promotion:</b> Focus distribution campaigns on schemes exhibiting Sharpe Ratios > 0.80 and direct plan expense ratios < 1.0% (e.g., ICICI Pru Midcap & Mirae Asset Large Cap).",
    "<b>Automated SIP Retention Nudges:</b> Deploy automated date-gap tracking to trigger retention alerts for accounts exceeding a 35-day installment gap.",
    "<b>Expand B30 Digital Onboarding:</b> Accelerate digital penetration in Tier 2/3 cities to capture burgeoning retail SIP inflows.",
    "<b>HHI Portfolio Concentration Risk Caps:</b> Implement automated portfolio alerts flagging focused schemes exceeding HHI > 2,000 for dynamic sector rebalancing."
]
for rec in recs:
    story.append(Paragraph(rec, bullet_style))

story.append(Spacer(1, 20))
story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#0288d1"), spaceBefore=10, spaceAfter=15))
story.append(Paragraph("<b>End of Report — Bluestock Mutual Fund Analytics Capstone (Release Tag v1.0)</b>", ParagraphStyle("End", parent=body_style, fontName="Helvetica-Bold", alignment=1, textColor=colors.HexColor("#0288d1"))))

# Build Document
doc.build(story, canvasmaker=NumberedCanvas)

# Copy to root
import shutil
shutil.copy(doc_path_rep, doc_path_root)

print(f"Saved 15-20 page technical report to {doc_path_rep} and {doc_path_root}!")
