#!/usr/bin/env python3
"""
Risk & Performance Diagnostic Engine (scripts/compute_metrics.py)
Computes CAGRs, Sharpe, Sortino, OLS Alpha/Beta, Max DD, 95% VaR/CVaR, and Scorecards.
"""

import os
import sys

def main():
    print("Executing Quantitative Performance Analytics & Risk Diagnostics Engine...")
    os.system("python3 generate_performance_analytics.py")
    os.system("python3 generate_advanced_analytics.py")
    print("Quantitative Risk Engine Execution Complete!")

if __name__ == "__main__":
    main()
