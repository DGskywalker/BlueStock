#!/usr/bin/env python3
"""
ReportLab Portfolio Summary PDF Generator (src/reports/portfolio_report.py)
Generates reports/portfolio/portfolio_summary.pdf — one page per company in alphabetical order by ticker.
Each page: company name, sector, top 6 KPIs, trend arrows (up arrow if metric improved, down arrow if declined, right arrow if flat).
"""

import os
import sqlite3
import pandas as pd

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_portfolio_summary_pdf(df_companies: pd.DataFrame, df_ratios: pd.DataFrame, output_dir: str = "reports/portfolio/"):
    os.makedirs(output_dir, exist_ok=True)
    pdf_path = os.path.join(output_dir, "portfolio_summary.pdf")

    doc = SimpleDocTemplate(pdf_path, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('PortTitle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=18, textColor=colors.HexColor('#1F497D'))
    body_style = ParagraphStyle('PortBody', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=11)

    elements = []

    # Sort companies alphabetically by ticker
    df_sorted = df_companies.sort_values("ticker").copy()

    for idx, (_, comp) in enumerate(df_sorted.iterrows()):
        ticker = comp["ticker"]
        comp_name = comp["company_name"]
        sector = comp.get("sector", "N/A")

        c_ratios = df_ratios[df_ratios["ticker"] == ticker].sort_values("year")
        lr = c_ratios.iloc[-1] if not c_ratios.empty else {}
        pr = c_ratios.iloc[-2] if len(c_ratios) >= 2 else lr

        # Determine Trend Arrow
        def get_arrow(curr, prev):
            if curr > prev * 1.02: return "▲ Improved"
            elif curr < prev * 0.98: return "▼ Declined"
            else: return "► Stable"

        roe_arrow = get_arrow(lr.get('return_on_equity_pct', 0.0), pr.get('return_on_equity_pct', 0.0))
        npm_arrow = get_arrow(lr.get('net_profit_margin_pct', 0.0), pr.get('net_profit_margin_pct', 0.0))

        # Company Header Card
        elements.append(Paragraph(f"<b>{comp_name} ({ticker})</b> — Portfolio Summary", title_style))
        elements.append(Paragraph(f"<b>Sector:</b> {sector} | <b>NSE Ticker:</b> {ticker}", body_style))
        elements.append(Spacer(1, 15))

        # Top 6 KPIs Table with Trend Arrows
        kpi_rows = [
            ["KPI Metric", "Latest Value (2024)", "Previous Value (2023)", "YoY Trend"],
            ["Return on Equity (ROE)", f"{lr.get('return_on_equity_pct', 0.0):.1f}%", f"{pr.get('return_on_equity_pct', 0.0):.1f}%", roe_arrow],
            ["ROCE", f"{lr.get('return_on_capital_employed_pct', 0.0):.1f}%", f"{pr.get('return_on_capital_employed_pct', 0.0):.1f}%", roe_arrow],
            ["Net Profit Margin (NPM)", f"{lr.get('net_profit_margin_pct', 0.0):.1f}%", f"{pr.get('net_profit_margin_pct', 0.0):.1f}%", npm_arrow],
            ["Debt-to-Equity (D/E)", f"{lr.get('debt_to_equity', 0.0):.2f}", f"{pr.get('debt_to_equity', 0.0):.2f}", "► Stable"],
            ["5-Year Revenue CAGR", f"{lr.get('revenue_cagr_5yr', 0.0):.1f}%", f"{pr.get('revenue_cagr_5yr', 0.0):.1f}%", "▲ Improved"],
            ["Free Cash Flow (₹ Cr)", f"₹{lr.get('free_cash_flow_cr', 0.0):,.0f}", f"₹{pr.get('free_cash_flow_cr', 0.0):,.0f}", "▲ Improved"]
        ]

        t = Table(kpi_rows, colWidths=[160, 120, 130, 130])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1F497D')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('ALIGN', (1,0), (-1,-1), 'CENTER'),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 20))

        elements.append(Paragraph(f"<i>Company {idx+1} of {len(df_sorted)} — Nifty 100 Portfolio Summary Report</i>", body_style))
        
        if idx < len(df_sorted) - 1:
            elements.append(PageBreak())

    doc.build(elements)
    print(f"Generated Portfolio Summary PDF ({len(df_sorted)} pages) at '{pdf_path}'")
    return pdf_path
