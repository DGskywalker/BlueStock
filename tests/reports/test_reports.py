#!/usr/bin/env python3
"""
Report Generation Unit Test Suite (tests/reports/test_reports.py)
Tests ReportLab PDF tearsheet and sector report generators.
"""

import unittest
import sys
import os
import pandas as pd

sys.path.insert(0, os.path.abspath("."))

from src.reports.tearsheet import generate_company_tearsheet
from src.reports.sector_report import generate_sector_report

class TestReportsModule(unittest.TestCase):

    def setUp(self):
        self.comp_info = {
            "company_id": 1,
            "ticker": "TESTPDF",
            "company_name": "Test PDF Ltd",
            "sector": "IT",
            "industry": "Software"
        }
        self.df_pnl = pd.DataFrame([
            {"company_id": 1, "year": 2023, "sales": 1000.0, "pat": 150.0},
            {"company_id": 1, "year": 2024, "sales": 1200.0, "pat": 200.0}
        ])
        self.df_rat = pd.DataFrame([
            {"company_id": 1, "year": 2023, "return_on_equity_pct": 20.0, "return_on_capital_employed_pct": 22.0, "debt_to_equity": 0.1, "net_profit_margin_pct": 15.0, "free_cash_flow_cr": 180.0, "revenue_cagr_5yr": 12.0},
            {"company_id": 1, "year": 2024, "return_on_equity_pct": 22.0, "return_on_capital_employed_pct": 25.0, "debt_to_equity": 0.0, "net_profit_margin_pct": 16.6, "free_cash_flow_cr": 220.0, "revenue_cagr_5yr": 14.0}
        ])
        self.df_pc = pd.DataFrame([
            {"company_id": 1, "type": "pro", "rule_id": "PRO_01", "text": "High ROE", "confidence_pct": 95},
            {"company_id": 1, "type": "con", "rule_id": "CON_01", "text": "Input cost inflation", "confidence_pct": 80}
        ])

    def test_01_tearsheet_pdf_generation(self):
        pdf_p = generate_company_tearsheet(self.comp_info, self.df_pnl, self.df_rat, self.df_pc, output_dir="output/temp_test_reports/")
        self.assertTrue(os.path.exists(pdf_p))
        self.assertGreater(os.path.getsize(pdf_p), 10000)

    def test_02_sector_pdf_generation(self):
        df_sec_companies = pd.DataFrame([self.comp_info])
        pdf_sec = generate_sector_report("IT", df_sec_companies, self.df_rat, output_dir="output/temp_test_reports/")
        self.assertTrue(os.path.exists(pdf_sec))
        self.assertGreater(os.path.getsize(pdf_sec), 1000)


if __name__ == "__main__":
    unittest.main()
