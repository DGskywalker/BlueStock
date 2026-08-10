import os
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

# Setup Output Paths
REPORTS_DIR = "reports"
os.makedirs(REPORTS_DIR, exist_ok=True)

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5) # 16:9 Widescreen Aspect Ratio

# Color Palette (Bluestock Dark Modern Theme)
BG_COLOR = RGBColor(11, 19, 43)        # #0b132b
CARD_COLOR = RGBColor(28, 37, 65)      # #1c2541
ACCENT_BLUE = RGBColor(0, 180, 216)    # #00b4d8
TEXT_WHITE = RGBColor(255, 255, 255)
TEXT_MUTED = RGBColor(160, 170, 178)
ACCENT_GREEN = RGBColor(6, 214, 160)
ACCENT_GOLD = RGBColor(255, 159, 28)

blank_slide_layout = prs.slide_layouts[6]

def set_slide_background(slide):
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = BG_COLOR

def add_header(slide, title_text, category_text="BLUESTOCK MUTUAL FUND ANALYTICS CAPSTONE"):
    set_slide_background(slide)
    
    # Category Text
    txBox = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.4))
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    p.text = category_text.upper()
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    
    # Title Text
    txBox2 = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.7), Inches(0.8))
    tf2 = txBox2.text_frame
    p2 = tf2.paragraphs[0]
    p2.text = title_text
    p2.font.size = Pt(22)
    p2.font.bold = True
    p2.font.color.rgb = TEXT_WHITE

def add_card(slide, left, top, width, height, title, body_bullets, accent_color=ACCENT_BLUE):
    shape = slide.shapes.add_shape(pptx.enum.shapes.MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = CARD_COLOR
    shape.line.color.rgb = accent_color
    shape.line.width = Pt(1.5)
    
    tf = shape.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.25)
    tf.margin_right = Inches(0.25)
    tf.margin_top = Inches(0.25)
    tf.margin_bottom = Inches(0.25)
    
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = accent_color
    p.space_after = Pt(10)
    
    for bullet in body_bullets:
        p_b = tf.add_paragraph()
        p_b.text = "• " + bullet
        p_b.font.size = Pt(11)
        p_b.font.color.rgb = TEXT_WHITE
        p_b.space_after = Pt(6)

print("Generating 12-Slide Presentation: Bluestock_MF_Presentation.pptx ...")

# -----------------------------------------------------------------------------
# SLIDE 1: Title Slide
# -----------------------------------------------------------------------------
slide1 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(slide1)

tb = slide1.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(11.3), Inches(3.0))
tf = tb.text_frame
p = tf.paragraphs[0]
p.text = "BLUESTOCK MUTUAL FUND ANALYTICS"
p.font.size = Pt(36)
p.font.bold = True
p.font.color.rgb = ACCENT_BLUE

p2 = tf.add_paragraph()
p2.text = "End-to-End Data Engineering, Quantitative Risk Analytics & Power BI Dashboard"
p2.font.size = Pt(18)
p2.font.color.rgb = TEXT_WHITE
p2.space_after = Pt(20)

p3 = tf.add_paragraph()
p3.text = "Prepared by: Divyansh Gupta | Repository: github.com/DGskywalker/BlueStock"
p3.font.size = Pt(12)
p3.font.color.rgb = TEXT_MUTED

# -----------------------------------------------------------------------------
# SLIDE 2: Problem Statement & Project Objectives
# -----------------------------------------------------------------------------
slide2 = prs.slides.add_slide(blank_slide_layout)
add_header(slide2, "Problem Statement & Capstone Objectives")

add_card(slide2, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0), "Industry Problem Statement", [
    "Fragmented Mutual Fund Data: Ingestion across disparate sources (AMFI, NAV histories, portfolio disclosures, transaction logs).",
    "Data Quality Gaps: Weekend/holiday NAV gaps, unstandardized transaction types, unverified KYC statuses.",
    "Lack of Integrated Risk Metrics: Need for comprehensive risk-adjusted evaluation (Sharpe, Sortino, Alpha, Beta, VaR, CVaR).",
    "Executive Accessibility: Fragmented datasets hinder real-time executive decision-making."
], ACCENT_BLUE)

add_card(slide2, Inches(6.8), Inches(1.8), Inches(5.6), Inches(5.0), "Core Capstone Objectives", [
    "Build Production ETL Pipeline: Ingest, clean, validate, and load 10 datasets into SQLite Star Schema.",
    "Perform 15+ EDA Visualizations: Uncover AUM growth, SIP inflows, and demographic participation.",
    "Quantitative Risk Modeling: Compute CAGRs, Sharpe/Sortino, OLS Alpha/Beta, 95% VaR & CVaR.",
    "Composite 0-100 Scorecard: Multi-attribute algorithm ranking all 40 schemes.",
    "Power BI Executive Dashboard: Build 4 interactive pages with full slicer & drill-through capability."
], ACCENT_GREEN)

# -----------------------------------------------------------------------------
# SLIDE 3: Data Sources & Star Schema Architecture
# -----------------------------------------------------------------------------
slide3 = prs.slides.add_slide(blank_slide_layout)
add_header(slide3, "Data Sources & SQLite Star Schema Architecture")

add_card(slide3, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0), "10 Cleaned Datasets Ingested", [
    "01_fund_master.csv (40 Schemes metadata)",
    "02_nav_history.csv (64,320 Daily NAV records)",
    "03_aum_by_fund_house.csv (90 AMC AUM trends)",
    "04_monthly_sip_inflows.csv (48 Monthly SIP records)",
    "05_category_inflows.csv (144 Category Net Flow records)",
    "06_industry_folio_count.csv (21 Folio expansion records)",
    "07_scheme_performance.csv (40 Scheme Return & Risk metrics)",
    "08_investor_transactions.csv (32,778 Investor transactions)",
    "09_portfolio_holdings.csv (322 Stock sector holdings)",
    "10_benchmark_indices.csv (8,050 Market index records)"
], ACCENT_BLUE)

add_card(slide3, Inches(6.8), Inches(1.8), Inches(5.6), Inches(5.0), "Star Schema Database Design (bluestock_mf.db)", [
    "Dimension Tables: dim_fund (AMFI PK), dim_date (Calendar PK).",
    "Fact Tables: fact_nav, fact_transactions, fact_performance, fact_aum, fact_portfolio_holdings, fact_category_inflows, fact_sip_inflows, fact_benchmark_indices, fact_industry_folio_count.",
    "Integrity Constraints: Foreign Keys linking fact tables to dim_fund & dim_date.",
    "Performance Optimization: Composite indexes on (amfi_code, date) for sub-millisecond query execution."
], ACCENT_GOLD)

# -----------------------------------------------------------------------------
# SLIDE 4: Data Pipeline & Data Quality Audit
# -----------------------------------------------------------------------------
slide4 = prs.slides.add_slide(blank_slide_layout)
add_header(slide4, "ETL Data Pipeline & Quality Assurance Audit")

add_card(slide4, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0), "Data Cleaning & Transformation Engine", [
    "NAV Gap Forward-Fill: Reindexed NAV history daily per fund across 1,642 days; expanded history from 46K to 64,320 complete rows.",
    "Transaction Standardization: Standardized transaction types (SIP, Lumpsum, Redemption) & validated net amounts.",
    "Expense Ratio & Return Validation: Ensured expense ratios fall within 0.1%–2.5% bounds (actual: 0.55%–1.64%).",
    "Live API Integration: Configured live NAV fetching module via mfapi.in API."
], ACCENT_BLUE)

add_card(slide4, Inches(6.8), Inches(1.8), Inches(5.6), Inches(5.0), "Database Load Verification (100% Match)", [
    "dim_fund: Source 40 | SQLite 40 (MATCH)",
    "fact_nav: Source 64,320 | SQLite 64,320 (MATCH)",
    "fact_transactions: Source 32,778 | SQLite 32,778 (MATCH)",
    "fact_performance: Source 40 | SQLite 40 (MATCH)",
    "fact_aum: Source 90 | SQLite 90 (MATCH)",
    "fact_portfolio_holdings: Source 322 | SQLite 322 (MATCH)",
    "fact_benchmark_indices: Source 8,050 | SQLite 8,050 (MATCH)",
    "dim_date: Generated 1,642 Calendar Days (MATCH)"
], ACCENT_GREEN)

# -----------------------------------------------------------------------------
# SLIDE 5: EDA Highlights — Market Expansion & AUM Leadership
# -----------------------------------------------------------------------------
slide5 = prs.slides.add_slide(blank_slide_layout)
add_header(slide5, "EDA Highlights: Market Expansion & AMC Leadership")

add_card(slide5, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0), "NAV Trend Analysis (2022–2026)", [
    "2023 Bull Run Phase: Strong market expansion (April–Dec 2023) driving equity NAVs to all-time highs.",
    "2024 Election & Macro Resilience: Brief market pullbacks in June 2024 & Oct 2024 followed by rapid recovery.",
    "Long-Term Growth: Equity schemes delivered 25%+ 3-year CAGRs across mid cap & small cap categories."
], ACCENT_BLUE)

add_card(slide5, Inches(6.8), Inches(1.8), Inches(5.6), Inches(5.0), "AMC Market Share Leadership", [
    "SBI Mutual Fund Dominance: Surpassed ₹12.5 Lakh Crores AUM across reported schemes, maintaining #1 market share.",
    "Top AMC Tier: ICICI Prudential, HDFC Mutual Fund, Kotak Mahindra, Nippon India, and Axis Mutual Fund constitute over 70% of total industry AUM.",
    "Equity Dominance: Equity funds represent over 62% of aggregate sampled AUM."
], ACCENT_GOLD)

# -----------------------------------------------------------------------------
# SLIDE 6: EDA Highlights — Retail SIP & Demographics
# -----------------------------------------------------------------------------
slide6 = prs.slides.add_slide(blank_slide_layout)
add_header(slide6, "EDA Highlights: Retail SIP Inflows & Demographics")

add_card(slide6, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0), "Monthly SIP Inflow Surge", [
    "All-Time Peak Record: Monthly SIP inflows reached ₹31,002 Crores in December 2025.",
    "Growth Rate: 169% expansion from ₹11,517 Cr in January 2022.",
    "Folio Doubling: Total industry folios nearly doubled from 13.26 Cr to 26.12 Cr."
], ACCENT_GREEN)

add_card(slide6, Inches(6.8), Inches(1.8), Inches(5.6), Inches(5.0), "Investor Demographic Insights", [
    "Core Age Bracket: Investors aged 26–50 comprise 69.6% of active transaction accounts.",
    "Senior Ticket Size: Investors aged 51–65 exhibit higher median SIP amounts (₹7,500+) than entry-level cohorts (₹2,500–₹5,000).",
    "Geographic Distribution: Maharashtra, Gujarat, Punjab & Tamil Nadu lead total investment volume, accompanied by rapid B30 tier-2/3 expansion."
], ACCENT_BLUE)

# -----------------------------------------------------------------------------
# SLIDE 7: Performance Analytics & Risk-Adjusted Ratios
# -----------------------------------------------------------------------------
slide7 = prs.slides.add_slide(blank_slide_layout)
add_header(slide7, "Performance Analytics & Composite Scorecard")

add_card(slide7, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0), "Multi-Attribute Scorecard Algorithm (0–100)", [
    "30% Weight: 3-Year CAGR Return Rank",
    "25% Weight: Sharpe Ratio Rank (Risk-Adjusted Return)",
    "20% Weight: Annualized Alpha Rank (Manager Skill)",
    "15% Weight: Expense Ratio Rank (Inverse)",
    "10% Weight: Max Drawdown Rank (Inverse Risk)"
], ACCENT_BLUE)

add_card(slide7, Inches(6.8), Inches(1.8), Inches(5.6), Inches(5.0), "Top 5 Composite Rated Schemes", [
    "#1 ICICI Pru Midcap Fund (Score: 85.1 | 3Y CAGR: 31.78% | Sharpe: 0.88)",
    "#2 Axis Midcap Fund (Score: 82.0 | 3Y CAGR: 35.11% | Sharpe: 0.73)",
    "#3 HDFC Mid-Cap Opportunities (Score: 80.5 | 3Y CAGR: 32.44% | Sharpe: 0.81)",
    "#4 Mirae Asset Large Cap (Score: 80.0 | 3Y CAGR: 34.00% | Sharpe: 1.07)",
    "#5 Nippon India Small Cap (Score: 78.6 | 3Y CAGR: 36.45% | Sharpe: 0.82)"
], ACCENT_GOLD)

# -----------------------------------------------------------------------------
# SLIDE 8: Quantitative Risk Diagnostics (Alpha/Beta & VaR)
# -----------------------------------------------------------------------------
slide8 = prs.slides.add_slide(blank_slide_layout)
add_header(slide8, "Quantitative Risk Diagnostics: Alpha, Beta & Tail Risk")

add_card(slide8, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0), "OLS Regression Alpha & Beta vs NIFTY 100", [
    "Alpha Outperformance: Top mid cap and small cap managers generated annualized Alpha > +25.0% over NIFTY 100.",
    "Systemic Beta: Equity funds range in Beta from 0.85 to 1.15; Debt & Gilt schemes exhibit near-zero Beta (< 0.05).",
    "Statistical Significance: OLS regression models validated via scipy.stats.linregress."
], ACCENT_BLUE)

add_card(slide8, Inches(6.8), Inches(1.8), Inches(5.6), Inches(5.0), "Historical 95% VaR & CVaR Tail Risk", [
    "Small Cap Tail Risk: Small Cap schemes register highest tail loss (95% VaR = -2.39%, 95% CVaR = -3.03%).",
    "Debt Tail Stability: Debt & Gilt funds maintain extreme tail stability (95% VaR > -0.20%).",
    "HHI Concentration: Focused equity funds exhibit HHI > 2,000, indicating high stock concentration risk."
], ACCENT_GREEN)

# -----------------------------------------------------------------------------
# SLIDE 9: Power BI Dashboard — Industry Overview & Performance
# -----------------------------------------------------------------------------
slide9 = prs.slides.add_slide(blank_slide_layout)
add_header(slide9, "Power BI Executive Dashboard: Pages 1 & 2")

add_card(slide9, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0), "Page 1: Industry Overview Dashboard", [
    "KPI Cards: Total AUM (₹81.4L Cr), Monthly SIP (₹31K Cr), Folios (26.12 Cr), Schemes (1,908).",
    "Time-Series Visuals: Industry AUM Trend line & Folio Expansion line.",
    "AMC Bar Chart: AUM breakdown highlighting SBI Mutual Fund dominance."
], ACCENT_BLUE)

add_card(slide9, Inches(6.8), Inches(1.8), Inches(5.6), Inches(5.0), "Page 2: Fund Performance Analytics", [
    "Risk vs Return Scatter Plot: 3Y CAGR % (X) vs Volatility % (Y), bubble size = AUM.",
    "Sortable Scorecard Table: Multi-metric financial diagnostics table.",
    "NAV vs Benchmark Line: Normalized performance tracking vs NIFTY 50."
], ACCENT_GOLD)

# -----------------------------------------------------------------------------
# SLIDE 10: Power BI Dashboard — Investor Analytics & Trends
# -----------------------------------------------------------------------------
slide10 = prs.slides.add_slide(blank_slide_layout)
add_header(slide10, "Power BI Executive Dashboard: Pages 3 & 4")

add_card(slide10, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0), "Page 3: Investor Demographics & Behavior", [
    "State Bar Chart: Transaction volume breakdown by state.",
    "Transaction Donut Split: SIP (60.15%), Lumpsum (24.70%), Redemption (15.15%).",
    "Age Ticket Sizes: Bar chart showing average SIP size per age bracket."
], ACCENT_GREEN)

add_card(slide10, Inches(6.8), Inches(1.8), Inches(5.6), Inches(5.0), "Page 4: SIP & Market Trends Correlation", [
    "Dual-Axis Chart: Monthly SIP Inflow (Bar) + NIFTY 50 Close (Line).",
    "Category Heatmap Matrix: Monthly net inflow color intensity across categories.",
    "Top Categories FY25: Liquid & Sectoral/Thematic leading net capital inflows."
], ACCENT_BLUE)

# -----------------------------------------------------------------------------
# SLIDE 11: Key Business Insights & Strategic Recommendations
# -----------------------------------------------------------------------------
slide11 = prs.slides.add_slide(blank_slide_layout)
add_header(slide11, "Strategic Recommendations & Business Roadmap")

add_card(slide11, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0), "Strategic Product & Distribution Recommendations", [
    "Promote High Risk-Adjusted Funds: Focus marketing on schemes with Sharpe > 0.8 and low expense ratios.",
    "Expand B30 Digital Onboarding: Target Tier 2/3 cities to capture growing retail SIP participation.",
    "Standardize SIP Ticket Sizes: Introduce automated SIP step-up features for 26-35 age cohort."
], ACCENT_GOLD)

add_card(slide11, Inches(6.8), Inches(1.8), Inches(5.6), Inches(5.0), "Platform & Risk Management Roadmap", [
    "Automate At-Risk SIP Nudges: Use date gap monitoring (>35 days) to trigger retention alerts.",
    "Real-Time Tail Risk Monitoring: Integrate automated VaR/CVaR alerts during market volatility phases.",
    "HHI Concentration Caps: Flag focused funds exceeding HHI > 2,200 for portfolio rebalancing."
], ACCENT_BLUE)

# -----------------------------------------------------------------------------
# SLIDE 12: Conclusion & Q&A Slide
# -----------------------------------------------------------------------------
slide12 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(slide12)

tb_end = slide12.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(11.3), Inches(3.0))
tf_end = tb_end.text_frame
p_end = tf_end.paragraphs[0]
p_end.text = "THANK YOU!"
p_end.font.size = Pt(40)
p_end.font.bold = True
p_end.font.color.rgb = ACCENT_BLUE

p_end2 = tf_end.add_paragraph()
p_end2.text = "BlueStock Mutual Fund Analytics Capstone Project Complete"
p_end2.font.size = Pt(18)
p_end2.font.color.rgb = TEXT_WHITE
p_end2.space_after = Pt(20)

p_end3 = tf_end.add_paragraph()
p_end3.text = "GitHub Repository: github.com/DGskywalker/BlueStock (Release Tag v1.0)"
p_end3.font.size = Pt(13)
p_end3.font.color.rgb = ACCENT_GREEN

# Save Presentation
pptx_path_rep = os.path.join(REPORTS_DIR, "Bluestock_MF_Presentation.pptx")
pptx_path_root = "Bluestock_MF_Presentation.pptx"

prs.save(pptx_path_rep)
prs.save(pptx_path_root)

print(f"Saved 12-slide presentation to {pptx_path_rep} and {pptx_path_root}!")
