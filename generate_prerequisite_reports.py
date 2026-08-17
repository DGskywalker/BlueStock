import os
import shutil
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

PRE_DIR = os.path.join("reports", "prerequisites")
os.makedirs(PRE_DIR, exist_ok=True)

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
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#0288d1"))
        self.drawString(54, 750, "BLUESTOCK FINTECH — PREREQUISITE LEARNING & ANALYTICS REPORT")
        self.setStrokeColor(colors.HexColor("#cccccc"))
        self.setLineWidth(0.5)
        self.line(54, 742, 558, 742)
        
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#666666"))
        self.drawString(54, 36, "Bluestock FinTech Data Analytics Internship Prerequisites")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 36, page_str)
        self.setStrokeColor(colors.HexColor("#cccccc"))
        self.setLineWidth(0.5)
        self.line(54, 46, 558, 46)
        self.restoreState()

styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    "DocTitle",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=22,
    leading=26,
    textColor=colors.HexColor("#0288d1"),
    spaceAfter=10
)

subtitle_style = ParagraphStyle(
    "DocSubTitle",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=12,
    leading=16,
    textColor=colors.HexColor("#333333"),
    spaceAfter=15
)

h1_style = ParagraphStyle(
    "H1",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=14,
    leading=18,
    textColor=colors.HexColor("#0288d1"),
    spaceBefore=14,
    spaceAfter=8,
    keepWithNext=True
)

h2_style = ParagraphStyle(
    "H2",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=11,
    leading=14,
    textColor=colors.HexColor("#1565c0"),
    spaceBefore=10,
    spaceAfter=4,
    keepWithNext=True
)

body_style = ParagraphStyle(
    "Body",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=9,
    leading=13,
    textColor=colors.HexColor("#222222"),
    spaceAfter=6
)

bullet_style = ParagraphStyle(
    "Bullet",
    parent=body_style,
    leftIndent=12,
    bulletIndent=4,
    spaceAfter=4
)

callout_style = ParagraphStyle(
    "Callout",
    parent=styles["Normal"],
    fontName="Helvetica-Oblique",
    fontSize=9,
    leading=13,
    textColor=colors.HexColor("#004085"),
    backColor=colors.HexColor("#cce5ff"),
    borderColor=colors.HexColor("#b8daff"),
    borderWidth=1,
    borderPadding=6,
    spaceBefore=6,
    spaceAfter=10
)

table_header_style = ParagraphStyle(
    "TableHeader",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=8,
    leading=10,
    textColor=colors.white,
    alignment=1
)

table_cell_style = ParagraphStyle(
    "TableCell",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=7.5,
    leading=9.5,
    textColor=colors.HexColor("#222222")
)

# =============================================================================
# 1. STOCK MARKET SUMMARY & FINANCIAL STATEMENT ANALYSIS (PDF & MD)
# =============================================================================
print("Generating Stock Market Summary & Financial Analysis PDF...")

sm_pdf_path = os.path.join(PRE_DIR, "Stock_Market_Summary_and_Financial_Analysis.pdf")
doc1 = SimpleDocTemplate(sm_pdf_path, pagesize=letter, leftMargin=54, rightMargin=54, topMargin=54, bottomMargin=54)

story1 = []
story1.append(Paragraph("Stock Market Fundamentals & Listed Financial Statement Analysis", title_style))
story1.append(Paragraph("Prerequisite Module 1: Domain Knowledge & HDFC Bank Limited Financial Evaluation", subtitle_style))
story1.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#0288d1"), spaceAfter=12))

story1.append(Paragraph("1. Fundamental Stock Market Concepts Summary", h1_style))
concepts = [
    "<b>What is a Stock Market?</b> A centralized marketplace facilitating the issuance, buying, and selling of equity shares of publicly listed companies, enabling corporate capital raising and investor wealth creation.",
    "<b>NSE & BSE:</b> The National Stock Exchange (NSE) and Bombay Stock Exchange (BSE) are India's premier stock exchanges. BSE is Asia's oldest exchange (established 1875), while NSE is the largest derivatives exchange globally.",
    "<b>Nifty & Sensex:</b> NIFTY 50 (NSE benchmark index comprising 50 major large-cap stocks) and SENSEX 30 (BSE benchmark index comprising 30 financially sound blue-chip companies).",
    "<b>IPO & SME IPO:</b> Initial Public Offering (IPO) is when an unlisted company issues new shares to the public for mainboard listing. SME IPO caters to Small and Medium Enterprises with lower paid-up capital requirements (post-issue capital up to ₹25 Cr).",
    "<b>Market Capitalization:</b> Total market value of a company's outstanding equity shares (MCap = Current Price x Outstanding Shares). Categorized into Large Cap (>₹20,000 Cr), Mid Cap (₹5,000 Cr–₹20,000 Cr), and Small Cap (<₹5,000 Cr).",
    "<b>P/E & P/B Ratios:</b> Price-to-Earnings Ratio (P/E = Price / EPS) measures valuation relative to earnings. Price-to-Book Ratio (P/B = Price / Book Value per Share) evaluates stock price against net tangible asset value.",
    "<b>EPS & Dividends:</b> Earnings Per Share (EPS = Net Profit / Total Shares) indicates profitability per share. Dividend is the portion of profit distributed to shareholders; Dividend Yield measures cash return.",
    "<b>Bonus Shares & Stock Splits:</b> Bonus shares are additional free shares issued to existing shareholders from accumulated reserves (e.g. 1:1 bonus). Stock Split reduces face value (e.g. ₹10 to ₹2 face value), increasing liquidity without altering market cap.",
    "<b>Trading Volume:</b> Total number of shares or contracts traded during a specified period, reflecting market liquidity and interest."
]

for c in concepts:
    story1.append(Paragraph(c, bullet_style))

story1.append(Spacer(1, 10))
story1.append(Paragraph("2. Financial Statement Analysis: HDFC Bank Limited (NSE: HDFCBANK / BSE: 500180)", h1_style))
story1.append(Paragraph(
    "HDFC Bank Limited is India's largest private sector bank by assets (post-merger with HDFC Ltd). "
    "Below is the quantitative financial statement analysis spanning Balance Sheet, Profit & Loss (P&L), Cash Flow, and Key Financial Ratios:", body_style
))

hdfc_data = [
    [Paragraph("<b>Financial Metric / Statement Category</b>", table_header_style), Paragraph("<b>FY2023 (Pre-Merger)</b>", table_header_style), Paragraph("<b>FY2024 (Post-Merger)</b>", table_header_style), Paragraph("<b>YoY Growth / Variance</b>", table_header_style)],
    [Paragraph("Balance Sheet: Total Assets", table_cell_style), Paragraph("₹24,66,081 Cr", table_cell_style), Paragraph("₹36,17,623 Cr", table_cell_style), Paragraph("<font color='green'><b>+46.7%</b></font>", table_cell_style)],
    [Paragraph("Balance Sheet: Total Deposits", table_cell_style), Paragraph("₹18,83,395 Cr", table_cell_style), Paragraph("₹23,79,786 Cr", table_cell_style), Paragraph("<font color='green'><b>+26.4%</b></font>", table_cell_style)],
    [Paragraph("Balance Sheet: Gross Advances (Loans)", table_cell_style), Paragraph("₹16,00,586 Cr", table_cell_style), Paragraph("₹24,84,863 Cr", table_cell_style), Paragraph("<font color='green'><b>+55.2%</b></font>", table_cell_style)],
    [Paragraph("P&L: Total Interest Income", table_cell_style), Paragraph("₹1,61,586 Cr", table_cell_style), Paragraph("₹2,14,702 Cr", table_cell_style), Paragraph("<font color='green'><b>+32.9%</b></font>", table_cell_style)],
    [Paragraph("P&L: Net Interest Income (NII)", table_cell_style), Paragraph("₹86,842 Cr", table_cell_style), Paragraph("₹1,08,532 Cr", table_cell_style), Paragraph("<font color='green'><b>+25.0%</b></font>", table_cell_style)],
    [Paragraph("P&L: Net Profit After Tax (PAT)", table_cell_style), Paragraph("₹44,108 Cr", table_cell_style), Paragraph("₹64,060 Cr", table_cell_style), Paragraph("<font color='green'><b>+45.2%</b></font>", table_cell_style)],
    [Paragraph("Key Ratio: Net Interest Margin (NIM)", table_cell_style), Paragraph("4.10%", table_cell_style), Paragraph("3.63%", table_cell_style), Paragraph("-47 bps (Merger Dilution)", table_cell_style)],
    [Paragraph("Key Ratio: Gross NPA %", table_cell_style), Paragraph("1.12%", table_cell_style), Paragraph("1.24%", table_cell_style), Paragraph("+12 bps (Stable Asset Quality)", table_cell_style)],
    [Paragraph("Key Ratio: Net NPA %", table_cell_style), Paragraph("0.27%", table_cell_style), Paragraph("0.33%", table_cell_style), Paragraph("+6 bps (Best-in-Class)", table_cell_style)],
    [Paragraph("Key Ratio: Return on Equity (ROE)", table_cell_style), Paragraph("17.1%", table_cell_style), Paragraph("16.8%", table_cell_style), Paragraph("Robust Capital Efficiency", table_cell_style)],
    [Paragraph("Key Ratio: Capital Adequacy Ratio (CAR)", table_cell_style), Paragraph("19.3%", table_cell_style), Paragraph("18.8%", table_cell_style), Paragraph("Well above 15% Min Regulatory Requirement", table_cell_style)]
]

t1 = Table(hdfc_data, colWidths=[160, 110, 110, 124])
t1.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0288d1")),
    ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cccccc")),
    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e0e0e0")),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('TOPPADDING', (0,0), (-1,-1), 4),
    ('BOTTOMPADDING', (0,0), (-1,-1), 4),
]))
story1.append(t1)

story1.append(Spacer(1, 10))
story1.append(Paragraph("<b>Analytical Insights on HDFC Bank Financial Performance:</b>", h2_style))
story1.append(Paragraph(
    "1. <b>Scale Expansion & Post-Merger Synergies:</b> Total assets expanded by 46.7% to ₹36.17 Lakh Crores following the mega-merger with HDFC Ltd. Advances grew 55.2% driven by home loan integration.<br/>"
    "2. <b>Prudent Asset Quality Management:</b> Despite structural expansion, Net NPA remained exceptionally low at 0.33%, demonstrating industry-leading credit underwriting standards.<br/>"
    "3. <b>Earnings & Capital Strength:</b> Net profit grew 45.2% to ₹64,060 Crores with a Return on Equity (ROE) of 16.8% and CAR of 18.8%, providing substantial capital buffer for future credit growth.", callout_style
))

doc1.build(story1, canvasmaker=NumberedCanvas)
print("Saved Stock_Market_Summary_and_Financial_Analysis.pdf!")

# Create Markdown version as well
sm_md = """# Stock Market Fundamentals & Listed Company Financial Statement Analysis

## Module 1: Basic Stock Market Concepts Summary

1. **What is a Stock Market?**: Centralized market facilitating buying/selling of equity shares of publicly listed companies.
2. **NSE & BSE**: National Stock Exchange (flagship NIFTY 50) and Bombay Stock Exchange (flagship SENSEX 30).
3. **Nifty & Sensex**: Benchmark indices tracking top 50 (NSE) and top 30 (BSE) companies.
4. **IPO & SME IPO**: Mainboard Initial Public Offering vs Small & Medium Enterprise IPO platform.
5. **Market Capitalization**: Total share value ($MCap = \\text{Price} \\times \\text{Total Shares}$).
6. **PE & PB Ratios**: Price-to-Earnings ($P/E = \\text{Price} / \\text{EPS}$) and Price-to-Book ($P/B = \\text{Price} / \\text{Book Value}$).
7. **EPS & Dividends**: Earnings Per Share and profit distribution to shareholders.
8. **Bonus & Stock Split**: Free bonus share issue vs face value reduction to boost liquidity.
9. **Trading Volume**: Total shares traded on a given day indicating liquidity.

---

## Module 2: Financial Statement Analysis — HDFC Bank Limited (HDFCBANK)

| Metric / Financial Category | FY2023 (Pre-Merger) | FY2024 (Post-Merger) | YoY Growth / Variance |
| :--- | :--- | :--- | :--- |
| **Total Assets** | ₹24,66,081 Cr | ₹36,17,623 Cr | **+46.7%** |
| **Total Deposits** | ₹18,83,395 Cr | ₹23,79,786 Cr | **+26.4%** |
| **Gross Advances (Loans)** | ₹16,00,586 Cr | ₹24,84,863 Cr | **+55.2%** |
| **Net Interest Income (NII)** | ₹86,842 Cr | ₹1,08,532 Cr | **+25.0%** |
| **Net Profit After Tax (PAT)** | ₹44,108 Cr | ₹64,060 Cr | **+45.2%** |
| **Net Interest Margin (NIM)** | 4.10% | 3.63% | -47 bps (Merger Dilution) |
| **Gross NPA %** | 1.12% | 1.24% | +12 bps (Stable Asset Quality) |
| **Net NPA %** | 0.27% | 0.33% | +6 bps (Best-in-Class) |
| **Return on Equity (ROE)** | 17.1% | 16.8% | Robust Capital Efficiency |
| **Capital Adequacy Ratio (CAR)**| 19.3% | 18.8% | Well above 15% Regulatory Min |
"""

with open(os.path.join(PRE_DIR, "Stock_Market_Summary_and_Financial_Analysis.md"), "w", encoding="utf-8") as f:
    f.write(sm_md)

# =============================================================================
# 2. SOFTWARE ARCHITECTURE DIAGRAM DOCUMENT (MD)
# =============================================================================
print("Generating Software Architecture Diagram Document...")

arch_md = """# Software Architecture & Data Flow Diagram — Bluestock FinTech Platform

## Overview
This architecture document details the end-to-end data flow in a modern FinTech application, tracing how a user action on a Web/Mobile Client progresses through Client-Server APIs, Authentication gateways, Microservice Backends, Relational Databases, Data Engineering Pipelines, and finally renders on Executive Analytics Dashboards.

---

## 1. System Architecture Components

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                             CLIENT LAYER (Frontend UI)                            │
│   Web App (React/Next.js)  │  Mobile App (Flutter)  │  Streamlit App (Python)    │
└────────────────────────────────────────┬─────────────────────────────────────────┘
                                         │ HTTPS / REST / WebSockets
                                         ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                      API GATEWAY & AUTHENTICATION LAYER                          │
│   Kong / NGINX Gateway  │  OAuth2 / JWT Token Validation  │  Rate Limiting       │
└────────────────────────────────────────┬─────────────────────────────────────────┘
                                         │ JSON Payloads (POST/GET)
                                         ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                            BACKEND SERVICES LAYER                                │
│   Trading Service (FastAPI) │ Order Engine (Node.js) │ User Analytics Service     │
└───────────────────┬──────────────────────────────────────────────┬───────────────┘
                    │ Read/Write Transactions                      │ Change Data Capture
                    ▼                                              ▼
┌──────────────────────────────────────┐        ┌──────────────────────────────────┐
│      RELATIONAL DATABASE LAYER       │        │     DATA ENGINEERING PIPELINE    │
│   PostgreSQL / SQLite Star Schema    │        │  Apache Airflow / Python ETL     │
│   (dim_fund, fact_transactions, etc) │        │  (Ingestion -> Cleaning -> Math) │
└──────────────────────────────────────┘        └────────────────┬─────────────────┘
                                                                 │ Aggregated Data
                                                                 ▼
                                                ┌──────────────────────────────────┐
                                                │        ANALYTICS DASHBOARD       │
                                                │  Power BI (.pbix) / Streamlit    │
                                                └──────────────────────────────────┘
```

---

## 2. End-to-End Data Flow Sequence (User Action to Dashboard)

```mermaid
sequenceDiagram
    autonumber
    actor User as Retail Investor
    participant UI as Client Web App (React)
    participant GW as API Gateway / Auth
    participant API as Backend Service (FastAPI)
    participant DB as SQLite / PostgreSQL DB
    participant ETL as Master Pipeline (Python)
    participant BI as Power BI / Dashboard

    User->>UI: Executes Action (e.g. Submits SIP Order / Searches NAV)
    UI->>GW: REST Request (POST /api/v1/sip_order + Bearer JWT Token)
    GW->>GW: Validates JWT Claims & Rate Limits
    GW->>API: Forwards Sanitized Payload
    API->>DB: Executes SQL Transaction (INSERT INTO fact_transactions)
    DB-->>API: Returns Transaction ID & Success Confirmation
    API-->>UI: 201 Created Response (JSON Payload)
    UI-->>User: Renders Order Confirmation UI

    note over DB,ETL: Automated Data Pipeline & ETL Execution
    ETL->>DB: Queries Raw Transactions & Daily NAV Histories
    ETL->>ETL: Executes Cleaning, NAV Gap Forward-Fill & Risk Calculations (Sharpe, VaR, Scorecards)
    ETL->>DB: Updates Analytics Star Schema (fact_performance, fund_scorecard)
    BI->>DB: Refreshes Data Engine & DirectQueries
    BI-->>User: Renders Updated Analytics Charts & Risk Diagnostics
```

---

## 3. Core Software Engineering Concepts Explained

1. **Client-Server Architecture**: Separation of concerns between user interface presentation (Client) and business logic execution (Server).
2. **REST APIs & JSON**: Representation State Transfer protocol utilizing standard HTTP methods (`GET` for fetching data, `POST` for creating resources, `PUT`/`PATCH` for updates, `DELETE` for removal) transmitting structured JSON key-value payloads.
3. **Database Star Schema**: Multi-dimensional schema comprising Central Fact Tables (`fact_transactions`, `fact_nav`) linked via foreign keys to Dimension Tables (`dim_fund`, `dim_date`) optimized for OLAP analytics queries.
4. **Data Pipelines & Logging**: Automated Python/ETL workflows featuring error logging, transaction rollback, and empirical data validation.
"""

with open(os.path.join(PRE_DIR, "Software_Architecture_Diagram.md"), "w", encoding="utf-8") as f:
    f.write(arch_md)

print("Saved Software_Architecture_Diagram.md!")

# =============================================================================
# 3. FINTECH RESEARCH REPORT (PDF & MD)
# =============================================================================
print("Generating FinTech Research Report PDF...")

ft_pdf_path = os.path.join(PRE_DIR, "FinTech_Research_Report.pdf")
doc2 = SimpleDocTemplate(ft_pdf_path, pagesize=letter, leftMargin=54, rightMargin=54, topMargin=54, bottomMargin=54)

story2 = []
story2.append(Paragraph("FinTech Business Ecosystem & Analytics Research Report", title_style))
story2.append(Paragraph("Prerequisite Module 5: Market Ecosystem Infrastructure & Zerodha / Bluestock Analytics Case Study", subtitle_style))
story2.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#0288d1"), spaceAfter=12))

story2.append(Paragraph("1. Indian FinTech Market Infrastructure & Mechanics", h1_style))
ft_concepts = [
    "<b>Brokerage Platforms:</b> Technology platforms enabling retail and institutional investors to execute stock, derivative, mutual fund, and commodity orders. Discount brokers (e.g. Zerodha, Groww, Angel One) offer low-cost flat-fee pricing models.",
    "<b>Demat Accounts:</b> Dematerialized accounts holding securities (equity shares, bonds, mutual fund units, ETFs) in electronic form, eliminating physical share certificate risks.",
    "<b>Depositories (NSDL & CDSL):</b> National Securities Depository Limited (NSDL) and Central Depository Services India Limited (CDSL) are SEBI-regulated national institutions acting as electronic vaults for Demat holdings.",
    "<b>SEBI (Securities and Exchange Board of India):</b> The apex statutory regulatory body governing Indian securities markets, safeguarding investor interests, and enforcing market transparency.",
    "<b>Trading & Settlement Lifecycle (T+1 Cycle):</b> India implemented the T+1 settlement cycle in 2023. When an investor buys shares on Day T, order matching occurs instantly at the exchange, clearing houses process funds/securities, and shares are credited to the investor's Demat account on Day T+1.",
    "<b>Market Participants:</b> Retail Investors, High Net-Worth Individuals (HNIs), Domestic Institutional Investors (DIIs - Mutual Funds/LIC), Foreign Portfolio Investors (FPIs), Brokers, Clearing Members, and Depositories."
]

for ft in ft_concepts:
    story2.append(Paragraph(ft, bullet_style))

story2.append(Spacer(1, 10))
story2.append(Paragraph("2. In-Depth Case Study: How Zerodha / Bluestock Uses Data Analytics", h1_style))
story2.append(Paragraph(
    "Discount brokerages process billions of telemetry events, order entries, and market ticks daily. "
    "Below is an analytical evaluation of how data analytics drives strategic business decisions and enhances customer experience:", body_style
))

case_data = [
    [Paragraph("<b>Analytics Domain</b>", table_header_style), Paragraph("<b>Data Infrastructure & Technical Implementation</b>", table_header_style), Paragraph("<b>Business & Customer Value Impact</b>", table_header_style)],
    [Paragraph("1. Real-Time Risk Management System (RMS)", table_cell_style), Paragraph("Stream processing of open positions against portfolio margins using VAR (Value-at-Risk) & SPAN margin calculators.", table_cell_style), Paragraph("Prevents broker insolvency; automates square-off alerts before margin call breaches during extreme market crashes.", table_cell_style)],
    [Paragraph("2. Nudge Behavioral Analytics Engine", table_cell_style), Paragraph("Rule-based predictive classification engine checking user order intents against illiquid penny stock registers, OTC options risk, and dividend eligibility.", table_cell_style), Paragraph("Protects retail investors from market manipulation and common trading traps, reducing customer support tickets by 30%.", table_cell_style)],
    [Paragraph("3. Console Personal Portfolio Analytics", table_cell_style), Paragraph("OLAP query engines computing FIFO-based capital gains tax reports, Sector Exposure Heatmaps, and Trade Journal attribution.", table_cell_style), Paragraph("Empowers investors with institutional-grade portfolio visibility, driving long-term user retention.", table_cell_style)],
    [Paragraph("4. Infrastructure & Order Routing Optimization", table_cell_style), Paragraph("Time-series logging of WebSocket tick latency and exchange gateway execution speeds.", table_cell_style), Paragraph("Ensures sub-millisecond order execution during high-volatility events (e.g. Budget/Election days).", table_cell_style)]
]

t2 = Table(case_data, colWidths=[130, 200, 174])
t2.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0288d1")),
    ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cccccc")),
    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e0e0e0")),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('TOPPADDING', (0,0), (-1,-1), 5),
    ('BOTTOMPADDING', (0,0), (-1,-1), 5),
]))
story2.append(t2)

story2.append(Spacer(1, 15))
story2.append(Paragraph("<b>Strategic Takeaways for Bluestock FinTech:</b>", h2_style))
story2.append(Paragraph(
    "Data Analytics is no longer just a reporting tool in FinTech—it is the core competitive moat. "
    "By integrating automated risk metrics, real-time NAV tracking, and behavioral nudges, Bluestock FinTech "
    "delivers institutional-grade financial decision support to retail mutual fund investors across India.", callout_style
))

doc2.build(story2, canvasmaker=NumberedCanvas)
print("Saved FinTech_Research_Report.pdf!")

# Markdown version
ft_md = """# FinTech Business Ecosystem & Analytics Research Report

## Module 1: Market Ecosystem Infrastructure & Terminology

1. **Brokerage Platforms**: Tech platforms executing stock/derivative/mutual fund orders (Discount vs Full-service).
2. **Demat Accounts**: Electronic accounts holding securities in digital form.
3. **Depositories (NSDL & CDSL)**: National institutions holding electronic securities.
4. **SEBI**: Market regulator safeguarding investor interests.
5. **Trading & Settlement Lifecycle (T+1)**: Orders matched at exchange on Day T; funds/shares settled on Day T+1.
6. **Market Participants**: Retail, HNIs, DIIs, FIIs, Brokers, Depositories.

---

## Module 2: Case Study — How Zerodha & Bluestock Use Data Analytics

| Analytics Domain | Technical Implementation | Business & Customer Impact |
| :--- | :--- | :--- |
| **Real-Time Risk Management (RMS)** | Stream processing of open positions vs VAR/SPAN margin calculators. | Automates square-off alerts, preventing broker & client insolvency. |
| **Nudge Behavioral Analytics** | Rule-based engine checking order intent against penny stock/options risk registers. | Protects retail traders from high-risk traps; cuts support tickets by 30%. |
| **Console Portfolio Analytics** | OLAP queries computing FIFO capital gains tax reports & sector heatmaps. | Empowers investors with institutional portfolio visibility. |
| **Infrastructure Optimization** | Time-series logging of WebSocket tick latency & gateway speed. | Ensures sub-millisecond execution during market volatility peaks. |
"""

with open(os.path.join(PRE_DIR, "FinTech_Research_Report.md"), "w", encoding="utf-8") as f:
    f.write(ft_md)

print("Prerequisite Reports Generation Complete!")
