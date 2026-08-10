#!/usr/bin/env python3
"""
BlueStock Mutual Fund Platform - Interactive Fund Recommender Module
Usage:
    python3 recommender.py --risk Moderate
    or run interactively: python3 recommender.py
"""

import os
import sys
import argparse
import pandas as pd

def find_file(name):
    paths = [
        os.path.join("data", "processed", name),
        os.path.join("csv", name),
        name,
        os.path.join("data", "raw", name)
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return name

def recommend_funds(risk_appetite="Moderate", top_n=3):
    scorecard_path = find_file("fund_scorecard.csv")
    fm_path = find_file("01_fund_master.csv")
    
    if not os.path.exists(scorecard_path):
        print(f"Error: Could not find {scorecard_path}. Please run performance analytics first.")
        return None

    df = pd.read_csv(scorecard_path)
    
    risk_appetite = risk_appetite.strip().capitalize()
    
    # Map Risk Appetite to Risk Grade / Risk Category
    risk_map = {
        "Low": ["Low", "Very Low", "Low to Moderate", "Debt"],
        "Moderate": ["Moderate", "Moderately High", "Hybrid"],
        "High": ["High", "Very High", "Equity"]
    }

    allowed = risk_map.get(risk_appetite, risk_map["Moderate"])
    
    # Filter matching funds
    mask = df["risk_category"].isin(allowed) if "risk_category" in df.columns else df["category"].isin(allowed)
    filtered = df[mask]
    
    if len(filtered) == 0:
        # Fallback filter based on category
        if risk_appetite == "Low":
            filtered = df[df["category"] == "Debt"]
        elif risk_appetite == "High":
            filtered = df[df["category"] == "Equity"]
        else:
            filtered = df
            
    # Sort by Sharpe Ratio descending
    recommended = filtered.sort_values("sharpe_ratio", ascending=False).head(top_n)
    
    cols_to_show = ["overall_rank", "fund_score", "scheme_name", "fund_house", "category", "cagr_3yr_pct", "sharpe_ratio", "alpha_pct", "expense_ratio_pct"]
    cols_present = [c for c in cols_to_show if c in recommended.columns]
    
    return recommended[cols_present]

def main():
    parser = argparse.ArgumentParser(description="BlueStock Fund Recommender Engine")
    parser.add_argument("--risk", type=str, default=None, choices=["Low", "Moderate", "High", "low", "moderate", "high"],
                        help="Investor Risk Appetite (Low, Moderate, High)")
    args = parser.parse_args()
    
    risk_input = args.risk
    if not risk_input:
        print("\n================================================================================")
        print("WELCOME TO BLUESTOCK MUTUAL FUND RECOMMENDER ENGINE")
        print("================================================================================")
        risk_input = input("Select Investor Risk Appetite (Low / Moderate / High) [Default: Moderate]: ").strip()
        if not risk_input:
            risk_input = "Moderate"
            
    recs = recommend_funds(risk_input)
    
    print("\n" + "=" * 80)
    print(f"TOP 3 FUND RECOMMENDATIONS FOR RISK PROFILE: '{risk_input.upper()}'")
    print("=" * 80)
    if recs is not None and len(recs) > 0:
        print(recs.to_string(index=False))
    else:
        print("No matching funds found.")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()
