#!/usr/bin/env python3
"""
NLP Module Unit Test Suite (tests/nlp/test_nlp.py)
Tests analysis regex text parser and 24 auto pros/cons rules.
"""

import unittest
import sys
import os
import pandas as pd

sys.path.insert(0, os.path.abspath("."))

from src.nlp.parser import parse_analysis_text
from src.nlp.pros_cons_generator import generate_pros_and_cons

class TestNLPModule(unittest.TestCase):

    def setUp(self):
        self.df_analysis = pd.DataFrame([
            {"company_id": 1, "compounded_sales_growth": "10 Years: 21%  5 Years: 18%", "roe": "5 Years: 24%"}
        ])
        
        self.df_ratios = pd.DataFrame([
            {"company_id": 1, "year": 2024, "return_on_equity_pct": 25.0, "debt_to_equity": 0.0, "free_cash_flow_cr": 500.0, "revenue_cagr_5yr": 18.0, "operating_profit_margin_pct": 28.0, "composite_quality_score": 85.0}
        ])
        
        self.df_companies = pd.DataFrame([
            {"company_id": 1, "ticker": "TESTCO", "company_name": "Test Co Ltd", "sector": "IT"}
        ])

    def test_01_regex_parser(self):
        df_parsed, df_failures = parse_analysis_text(self.df_analysis)
        self.assertFalse(df_parsed.empty)
        self.assertEqual(len(df_parsed), 3)
        row1 = df_parsed.iloc[0]
        self.assertEqual(row1["period_years"], 10)
        self.assertEqual(row1["value_pct"], 21.0)

    def test_02_pros_cons_generator_pro_rules(self):
        df_pc = generate_pros_and_cons(self.df_ratios, self.df_companies)
        self.assertFalse(df_pc.empty)
        pros = df_pc[df_pc["type"] == "pro"]
        self.assertGreater(len(pros), 0)
        rule_ids = pros["rule_id"].tolist()
        self.assertIn("PRO_01", rule_ids) # ROE > 20%
        self.assertIn("PRO_03", rule_ids) # D/E = 0

    def test_03_pros_cons_generator_guarantee_every_company_has_pro_and_con(self):
        df_pc = generate_pros_and_cons(self.df_ratios, self.df_companies)
        comp_ids = df_pc["company_id"].unique()
        self.assertIn(1, comp_ids)
        pros = df_pc[df_pc["company_id"] == 1]["type"].tolist()
        self.assertIn("pro", pros)
        self.assertIn("con", pros)


if __name__ == "__main__":
    unittest.main()
