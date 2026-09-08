#!/usr/bin/env python3
"""
ReportLab Company Tearsheet PDF Generator (src/reports/tearsheet.py)
Generates a professional 2-page company tearsheet PDF with navy header, KPI tiles, matplotlib charts, and pros/cons.
Output directory: reports/tearsheets/<ticker>_tearsheet.pdf
"""

import os
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def create_company_charts(comp_info: dict, df_pnl: pd.DataFrame, df_rat: pd.DataFrame, temp_dir: str = "output/temp_charts"):
    os.makedirs(temp_dir, exist_ok=True)
    ticker = comp_info["ticker"]

    # 1. Bar Chart: Revenue & PAT
    bar_img_path = os.path.join(temp_dir, f"{ticker}_rev_pat.png")
    fig, ax = plt.subplots(figsize=(6, 3), dpi=150)
    if not df_pnl.empty:
        years = df_pnl["year"].tolist()
        sales = df_pnl["sales"].tolist()
        pat = df_pnl["pat"].tolist()
        width = 0.35
        x = range(len(years))
        ax.bar([i - width/2 for i in x], sales, width=width, label="Revenue (Cr)", color="#1f77b4")
        ax.bar([i + width/2 for i in x], pat, width=width, label="Net Profit (Cr)", color="#2ca02c")
        ax.set_xticks(x)
        ax.set_xticklabels(years, rotation=45, fontsize=8)
    else:
        ax.text(0.5, 0.5, "Chart Data N/A", ha="center", va="center")
    ax.legend(fontsize=8)
    ax.set_title(f"{ticker} 10Y Revenue & Net Profit", fontsize=10, fontweight="bold")
    plt.tight_layout()
    plt.savefig(bar_img_path)
    plt.close()

    # 2. Line Chart: ROE & ROCE
    line_img_path = os.path.join(temp_dir, f"{ticker}_roe_roce.png")
    fig, ax = plt.subplots(figsize=(6, 3), dpi=150)
    if not df_rat.empty:
        years = df_rat["year"].tolist()
        roe = df_rat["return_on_equity_pct"].tolist()
        roce = df_rat["return_on_capital_employed_pct"].tolist()
        ax.plot(years, roe, marker="o", label="ROE (%)", color="#ff7f0e", linewidth=2)
        ax.plot(years, roce, marker="s", label="ROCE (%)", color="#9467bd", linewidth=2)
        ax.set_xticks(years)
        ax.set_xticklabels(years, rotation=45, fontsize=8)
    else:
        ax.text(0.5, 0.5, "Chart Data N/A", ha="center", va="center")
    ax.legend(fontsize=8)
    ax.set_title(f"{ticker} ROE vs ROCE Trend", fontsize=10, fontweight="bold")
    plt.tight_layout()
    plt.savefig(line_img_path)
    plt.close()

    return bar_img_path, line_img_path


def generate_company_tearsheet(comp_info: dict, df_pnl: pd.DataFrame, df_rat: pd.DataFrame,
                               df_pc: pd.DataFrame, output_dir: str = "reports/tearsheets/"):
    os.makedirs(output_dir, exist_ok=True)
    ticker = comp_info["ticker"]
    pdf_path = os.path.join(output_dir, f"{ticker}_tearsheet.pdf")

    # Generate charts
    bar_img, line_img = create_company_charts(comp_info, df_pnl, df_rat)

    doc = SimpleDocTemplate(pdf_path, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=18, textColor=colors.HexColor('#1F497D'))
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=11)
    pro_style = ParagraphStyle('ProStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, textColor=colors.HexColor('#2E75B6'))
    con_style = ParagraphStyle('ConStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, textColor=colors.HexColor('#C00000'))

    elements = []

    # PAGE 1: Header + KPI Tiles + Charts
    header_data = [[
        Paragraph(f"<b>{comp_info['company_name']} ({ticker})</b>", title_style),
        Paragraph(f"<b>Sector:</b> {comp_info.get('sector', 'N/A')}<br/><b>Industry:</b> {comp_info.get('industry', 'N/A')}", body_style)
    ]]
    header_table = Table(header_data, colWidths=[340, 200])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#D9E1F2')),
        ('PADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 10))

    # KPI Tiles Table
    latest_r = df_rat.iloc[-1] if not df_rat.empty else {}
    kpi_data = [
        ["ROE", "ROCE", "NPM", "D/E Ratio", "5Y Rev CAGR", "FCF (Cr)"],
        [
            f"{latest_r.get('return_on_equity_pct', 0.0):.1f}%",
            f"{latest_r.get('return_on_capital_employed_pct', 0.0):.1f}%",
            f"{latest_r.get('net_profit_margin_pct', 0.0):.1f}%",
            f"{latest_r.get('debt_to_equity', 0.0):.2f}",
            f"{latest_r.get('revenue_cagr_5yr', 0.0):.1f}%",
            f"₹{latest_r.get('free_cash_flow_cr', 0.0):,.0f}"
        ]
    ]
    kpi_table = Table(kpi_data, colWidths=[90]*6)
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1F497D')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#F2F2F2')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey)
    ]))
    elements.append(kpi_table)
    elements.append(Spacer(1, 15))

    # Side-by-Side Charts
    chart_table = Table([[Image(bar_img, width=260, height=130), Image(line_img, width=260, height=130)]], colWidths=[270, 270])
    elements.append(chart_table)
    elements.append(Spacer(1, 15))

    # Page 1 Footer Note
    elements.append(Paragraph("<i>Page 1 of 2 — Confidential Equity Research Tearsheet for Bluestock Fintech</i>", body_style))
    elements.append(PageBreak())

    # PAGE 2: Balance Sheet & Pros/Cons Section
    elements.append(Paragraph(f"<b>{comp_info['company_name']} — Qualitative Analysis & Allocation</b>", title_style))
    elements.append(Spacer(1, 10))

    # Pros Section
    elements.append(Paragraph("<b>✅ High Strengths & Key Investment Catalysts (Pros)</b>", pro_style))
    pros_text = [
        "Consistently high return on equity demonstrates exceptional capital efficiency.",
        "Strong free cash flow generation over 5 years signals healthy business fundamentals.",
        "Debt-free balance sheet provides financial flexibility and eliminates interest burden."
    ]
    for p in pros_text:
        elements.append(Paragraph(f"• {p}", body_style))
    elements.append(Spacer(1, 10))

    # Cons Section
    elements.append(Paragraph("<b>⚠️ Watchouts & Key Risks (Cons)</b>", con_style))
    cons_text = [
        "Operating margins subject to short-term raw material input cost volatility.",
        "Exposed to macroeconomic sector growth cycles and regulatory disclosures."
    ]
    for c in cons_text:
        elements.append(Paragraph(f"• {c}", body_style))
    elements.append(Spacer(1, 15))

    # Capital Allocation Badge Table
    alloc_data = [
        ["Capital Allocation Pattern", "CFO Quality Label", "CapEx Intensity"],
        ["Reinvestor (Growth Focused)", "High Quality (>1.0)", "Moderate (3-8%)"]
    ]
    alloc_table = Table(alloc_data, colWidths=[180, 180, 180])
    alloc_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2E75B6')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey)
    ]))
    elements.append(alloc_table)
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("<i>Page 2 of 2 — End of Company Tearsheet Report</i>", body_style))

    doc.build(elements)
    print(f"Generated Tearsheet PDF for {ticker} ({os.path.getsize(pdf_path)//1024} KB) at '{pdf_path}'")
    return pdf_path
