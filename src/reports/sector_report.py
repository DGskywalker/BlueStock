#!/usr/bin/env python3
"""
ReportLab Sector PDF Report Generator (src/reports/sector_report.py)
Generates 11 sector PDF reports in reports/sector/<sector>_report.pdf
Includes sector summary page with median KPIs + table of all companies in sector with 8 metrics each.
"""

import os
import sqlite3
import pandas as pd

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_sector_report(sector_name: str, df_sec_companies: pd.DataFrame, df_sec_ratios: pd.DataFrame, output_dir: str = "reports/sector/"):
    os.makedirs(output_dir, exist_ok=True)
    safe_name = sector_name.replace(" ", "_").replace("/", "_")
    pdf_path = os.path.join(output_dir, f"{safe_name}_report.pdf")

    doc = SimpleDocTemplate(pdf_path, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('SecTitle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=18, textColor=colors.HexColor('#1F497D'))
    body_style = ParagraphStyle('SecBody', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=11)

    elements = []

    # Header
    elements.append(Paragraph(f"<b>{sector_name} Sector Report</b>", title_style))
    elements.append(Paragraph(f"Comprehensive sector fundamental scorecard and benchmark analysis for {len(df_sec_companies)} companies.", body_style))
    elements.append(Spacer(1, 15))

    # Sector Summary Medians Table
    med_roe = df_sec_ratios["return_on_equity_pct"].dropna().median() if "return_on_equity_pct" in df_sec_ratios.columns else 0.0
    med_pe = df_sec_ratios["pe_ratio"].dropna().median() if "pe_ratio" in df_sec_ratios.columns else 0.0
    med_de = df_sec_ratios["debt_to_equity"].dropna().median() if "debt_to_equity" in df_sec_ratios.columns else 0.0
    med_cagr = df_sec_ratios["revenue_cagr_5yr"].dropna().median() if "revenue_cagr_5yr" in df_sec_ratios.columns else 0.0

    sum_data = [
        ["Sector Companies", "Median ROE (%)", "Median P/E", "Median D/E", "Median 5Y Rev CAGR"],
        [f"{len(df_sec_companies)}", f"{med_roe:.1f}%", f"{med_pe:.1f}x", f"{med_de:.2f}", f"{med_cagr:.1f}%"]
    ]
    sum_table = Table(sum_data, colWidths=[108]*5)
    sum_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1F497D')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey)
    ]))
    elements.append(sum_table)
    elements.append(Spacer(1, 20))

    # Sector Company List Table (8 metrics each)
    elements.append(Paragraph("<b>Sector Company Breakdown & KPIs</b>", ParagraphStyle('Sub', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=12)))
    elements.append(Spacer(1, 5))

    rows = [["Ticker", "Company Name", "ROE (%)", "ROCE (%)", "D/E", "5Y Rev CAGR", "5Y PAT CAGR", "P/E"]]
    for _, comp in df_sec_companies.iterrows():
        t = comp.get("ticker", "COMP")
        cid = comp.get("company_id")
        
        if "ticker" in df_sec_ratios.columns:
            c_ratios = df_sec_ratios[df_sec_ratios["ticker"] == t]
        elif "company_id" in df_sec_ratios.columns and cid is not None:
            c_ratios = df_sec_ratios[df_sec_ratios["company_id"] == cid]
        else:
            c_ratios = df_sec_ratios
            
        lr = c_ratios.iloc[-1] if not c_ratios.empty else {}
        
        rows.append([
            t,
            comp["company_name"][:20],
            f"{lr.get('return_on_equity_pct', 0.0):.1f}%",
            f"{lr.get('return_on_capital_employed_pct', 0.0):.1f}%",
            f"{lr.get('debt_to_equity', 0.0):.2f}",
            f"{lr.get('revenue_cagr_5yr', 0.0):.1f}%",
            f"{lr.get('pat_cagr_5yr', 0.0):.1f}%",
            f"{lr.get('pe_ratio', 0.0):.1f}x"
        ])

    comp_table = Table(rows, colWidths=[65, 145, 55, 55, 55, 65, 65, 55])
    comp_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#D9E1F2')),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('ALIGN', (2,0), (-1,-1), 'RIGHT'),
    ]))
    elements.append(comp_table)

    doc.build(elements)
    print(f"Generated Sector Report PDF for '{sector_name}' at '{pdf_path}'")
    return pdf_path
