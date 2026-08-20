#!/usr/bin/env python3
"""
ETL Validator Module (src/etl/validator.py)
Implements all 16 Data Quality (DQ-01 to DQ-16) Rules with CRITICAL & WARNING Severity levels.
Generates output/validation_failures.csv logging rule violations.
"""

import os
import re
import pandas as pd

class DataQualityValidator:
    def __init__(self):
        self.failures = []

    def log_failure(self, rule_id: str, severity: str, table_name: str, key_info: str, description: str):
        self.failures.append({
            "rule_id": rule_id,
            "severity": severity, # CRITICAL or WARNING
            "table_name": table_name,
            "key_info": str(key_info),
            "description": description
        })

    def validate_all(self, data_dict: dict) -> pd.DataFrame:
        """
        Executes DQ-01 through DQ-16 against loaded datasets dict.
        """
        self.failures = []
        
        df_comp = data_dict.get("companies", pd.DataFrame())
        df_pnl = data_dict.get("profitandloss", pd.DataFrame())
        df_bs = data_dict.get("balancesheet", pd.DataFrame())
        df_cf = data_dict.get("cashflow", pd.DataFrame())
        df_docs = data_dict.get("documents", pd.DataFrame())
        df_prices = data_dict.get("stock_prices", pd.DataFrame())
        df_bse = data_dict.get("bse_balancesheet", pd.DataFrame())

        valid_company_ids = set(df_comp["company_id"]) if not df_comp.empty else set()

        # DQ-01: PK Uniqueness in Companies (CRITICAL)
        if not df_comp.empty:
            dups = df_comp[df_comp.duplicated("company_id", keep=False)]
            for _, r in dups.iterrows():
                self.log_failure("DQ-01", "CRITICAL", "companies", r["company_id"], "Duplicate company_id primary key found")

        # DQ-02: Composite PK Uniqueness (company_id, year) (CRITICAL)
        for tbl_name, df_tbl in [("profitandloss", df_pnl), ("balancesheet", df_bs), ("cashflow", df_cf)]:
            if not df_tbl.empty:
                dups = df_tbl[df_tbl.duplicated(["company_id", "year"], keep=False)]
                for _, r in dups.iterrows():
                    self.log_failure("DQ-02", "CRITICAL", tbl_name, f"company_id={r['company_id']}, year={r['year']}", "Duplicate (company_id, year) composite primary key found")

        # DQ-03: Foreign Key Integrity (CRITICAL)
        for tbl_name, df_tbl in [("profitandloss", df_pnl), ("balancesheet", df_bs), ("cashflow", df_cf), ("documents", df_docs), ("stock_prices", df_prices)]:
            if not df_tbl.empty and valid_company_ids:
                invalid_fk = df_tbl[~df_tbl["company_id"].isin(valid_company_ids)]
                for _, r in invalid_fk.iterrows():
                    self.log_failure("DQ-03", "CRITICAL", tbl_name, f"company_id={r['company_id']}", "Foreign Key violation: company_id does not exist in companies table")

        # DQ-04: Balance Sheet Balance Check (|Total Assets - Total Liabilities| < 1%) (WARNING)
        if not df_bs.empty:
            diff_mask = (abs(df_bs["total_assets"] - df_bs["total_liabilities"]) / df_bs["total_assets"].replace(0, 1)) > 0.01
            for _, r in df_bs[diff_mask].iterrows():
                self.log_failure("DQ-04", "WARNING", "balancesheet", f"company_id={r['company_id']}, year={r['year']}", f"Balance Sheet imbalance > 1%: Assets={r['total_assets']}, Liab={r['total_liabilities']}")

        # DQ-05: OPM Cross-Check (OPM = Operating Profit / Sales * 100) (WARNING)
        if not df_pnl.empty:
            for _, r in df_pnl.iterrows():
                if r["sales"] > 0:
                    calc_opm = (r["operating_profit"] / r["sales"]) * 100.0
                    if abs(calc_opm - r["opm_pct"]) > 2.0: # Allow 2% tolerance rounding
                        self.log_failure("DQ-05", "WARNING", "profitandloss", f"company_id={r['company_id']}, year={r['year']}", f"OPM mismatch: reported={r['opm_pct']}%, calculated={calc_opm:.2f}%")

        # DQ-06: Positive Sales Check (WARNING)
        if not df_pnl.empty:
            neg_sales = df_pnl[df_pnl["sales"] <= 0]
            for _, r in neg_sales.iterrows():
                self.log_failure("DQ-06", "WARNING", "profitandloss", f"company_id={r['company_id']}, year={r['year']}", f"Non-positive sales value: {r['sales']}")

        # DQ-07: Net Cash Flow Cross-Check (CFO + CFI + CFF = Net Cash Flow) (WARNING)
        if not df_cf.empty:
            for _, r in df_cf.iterrows():
                calc_ncf = r["cfo"] + r["cfi"] + r["cff"]
                if abs(calc_ncf - r["net_cash_flow"]) > 1.0:
                    self.log_failure("DQ-07", "WARNING", "cashflow", f"company_id={r['company_id']}, year={r['year']}", f"Net Cash Flow mismatch: reported={r['net_cash_flow']}, calculated sum={calc_ncf}")

        # DQ-08: Tax Rate Bounds (0% <= Tax Rate <= 50%) (WARNING)
        if not df_pnl.empty:
            for _, r in df_pnl.iterrows():
                if r["pbt"] > 0:
                    tax_rate = (r["tax"] / r["pbt"]) * 100.0
                    if tax_rate < 0 or tax_rate > 50:
                        self.log_failure("DQ-08", "WARNING", "profitandloss", f"company_id={r['company_id']}, year={r['year']}", f"Effective Tax Rate out of bounds (0-50%): {tax_rate:.2f}%")

        # DQ-09: Dividend Payout Cap (Dividend <= PAT) (WARNING)
        if not df_pnl.empty:
            for _, r in df_pnl.iterrows():
                if r["pat"] > 0 and r["dividend_payout_pct"] > 100.0:
                    self.log_failure("DQ-09", "WARNING", "profitandloss", f"company_id={r['company_id']}, year={r['year']}", f"Dividend payout ratio > 100% of PAT: {r['dividend_payout_pct']}%")

        # DQ-10: Valid URL Format in Documents (WARNING)
        if not df_docs.empty:
            url_regex = re.compile(r'^https?://', re.IGNORECASE)
            for _, r in df_docs.iterrows():
                if not url_regex.match(str(r["url"])):
                    self.log_failure("DQ-10", "WARNING", "documents", f"doc_id={r.get('doc_id', r['company_id'])}", f"Invalid URL format: {r['url']}")

        # DQ-11: EPS Sign Consistency with PAT (WARNING)
        if not df_pnl.empty:
            for _, r in df_pnl.iterrows():
                if (r["pat"] > 0 and r["eps_inr"] < 0) or (r["pat"] < 0 and r["eps_inr"] > 0):
                    self.log_failure("DQ-11", "WARNING", "profitandloss", f"company_id={r['company_id']}, year={r['year']}", f"EPS sign ({r['eps_inr']}) inconsistent with PAT ({r['pat']})")

        # DQ-12: BSE Balance Sheet Balance Check (WARNING)
        if not df_bse.empty:
            diff_bse = (abs(df_bse["total_assets"] - df_bse["total_liabilities"]) / df_bse["total_assets"].replace(0, 1)) > 0.01
            for _, r in df_bse[diff_bse].iterrows():
                self.log_failure("DQ-12", "WARNING", "bse_balancesheet", f"company_id={r['company_id']}, year={r['year']}", f"BSE Balance Sheet imbalance > 1%")

        # DQ-13: Minimum 5-Year Coverage Check Per Company (WARNING)
        if not df_pnl.empty:
            year_counts = df_pnl.groupby("company_id")["year"].nunique()
            for comp_id, cnt in year_counts.items():
                if cnt < 5:
                    self.log_failure("DQ-13", "WARNING", "profitandloss", f"company_id={comp_id}", f"Company has < 5 years of P&L historical coverage (Actual: {cnt} years)")

        # DQ-14: Duplicate Year Records Check (CRITICAL)
        if not df_pnl.empty:
            dup_years = df_pnl[df_pnl.duplicated(["company_id", "year"])]
            for _, r in dup_years.iterrows():
                self.log_failure("DQ-14", "CRITICAL", "profitandloss", f"company_id={r['company_id']}, year={r['year']}", "Duplicate year record detected")

        # DQ-15: Ticker Format Validation (WARNING)
        if not df_comp.empty:
            ticker_regex = re.compile(r'^[A-Z0-9_-]+$')
            for _, r in df_comp.iterrows():
                if not ticker_regex.match(str(r["ticker"])):
                    self.log_failure("DQ-15", "WARNING", "companies", f"company_id={r['company_id']}", f"Ticker format non-standard: {r['ticker']}")

        # DQ-16: Outlier Stock Prices Check (Price > 0, Volume >= 0) (WARNING)
        if not df_prices.empty:
            invalid_prices = df_prices[(df_prices["close_price"] <= 0) | (df_prices["volume"] < 0)]
            for _, r in invalid_prices.iterrows():
                self.log_failure("DQ-16", "WARNING", "stock_prices", f"company_id={r['company_id']}, date={r['date']}", f"Outlier stock price/volume: close={r['close_price']}, vol={r['volume']}")

        df_failures = pd.DataFrame(self.failures)
        if df_failures.empty:
            df_failures = pd.DataFrame(columns=["rule_id", "severity", "table_name", "key_info", "description"])
            
        return df_failures

if __name__ == "__main__":
    validator = DataQualityValidator()
    print("DataQualityValidator class loaded. All 16 DQ rules implemented.")
