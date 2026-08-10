#!/usr/bin/env python3
"""
Bonus Challenge B3: Monte Carlo NAV Growth Simulation Engine
Projects 5-Year NAV growth (1,260 trading days) with 10th, 50th, and 90th percentile uncertainty bands
using Geometric Brownian Motion across key mutual fund schemes.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Setup Directories
CHARTS_DIR = os.path.join("reports", "charts")
PROCESSED_DIR = os.path.join("data", "processed")
os.makedirs(CHARTS_DIR, exist_ok=True)

def find_file(name):
    paths = [os.path.join(PROCESSED_DIR, name), os.path.join("csv", name), name]
    for p in paths:
        if os.path.exists(p): return p
    return name

def run_monte_carlo_simulation(amfi_code=119551, n_years=5, n_simulations=1000, seed=42):
    np.random.seed(seed)
    nav_df = pd.read_csv(find_file("02_nav_history.csv"))
    nav_df["date"] = pd.to_datetime(nav_df["date"])
    fm_df = pd.read_csv(find_file("01_fund_master.csv"))

    f_info = fm_df[fm_df["amfi_code"] == amfi_code]
    s_name = f_info["scheme_name"].values[0] if len(f_info) > 0 else f"Scheme {amfi_code}"

    f_nav = nav_df[nav_df["amfi_code"] == amfi_code].sort_values("date").set_index("date")["nav"]
    f_ret = f_nav.pct_change().dropna()

    # Annualized Return & Volatility
    mu = f_ret.mean() * 252.0
    sigma = f_ret.std() * np.sqrt(252.0)

    S0 = f_nav.iloc[-1]
    n_days = int(n_years * 252)
    dt = 1.0 / 252.0

    # Geometric Brownian Motion simulation paths
    sim_paths = np.zeros((n_days, n_simulations))
    sim_paths[0] = S0

    for t in range(1, n_days):
        z = np.random.standard_normal(n_simulations)
        sim_paths[t] = sim_paths[t-1] * np.exp((mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * z)

    # Percentiles
    p10 = np.percentile(sim_paths, 10, axis=1)
    p50 = np.percentile(sim_paths, 50, axis=1)
    p90 = np.percentile(sim_paths, 90, axis=1)

    days = np.arange(n_days)

    # Plot
    plt.figure(figsize=(12, 6))
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")

    # Plot sample simulation paths
    for i in range(min(50, n_simulations)):
        plt.plot(days, sim_paths[:, i], color="#00b4d8", alpha=0.08, linewidth=0.8)

    plt.plot(days, p50, color="#1565c0", linewidth=2.5, label=f"Median Projection (50th %ile: ₹{p50[-1]:.2f})")
    plt.plot(days, p90, color="#06d6a0", linewidth=2.0, linestyle="--", label=f"Bull Scenario (90th %ile: ₹{p90[-1]:.2f})")
    plt.plot(days, p10, color="#d32f2f", linewidth=2.0, linestyle="--", label=f"Bear Scenario (10th %ile: ₹{p10[-1]:.2f})")
    plt.fill_between(days, p10, p90, color="#00b4d8", alpha=0.15, label="80% Confidence Band")

    plt.title(f"Monte Carlo 5-Year NAV Growth Simulation: {s_name[:35]}", fontsize=14, fontweight="bold", pad=12)
    plt.xlabel("Trading Days Projected (5 Years = 1,260 Days)", fontsize=11)
    plt.ylabel("Projected NAV (INR)", fontsize=11)
    plt.legend(loc="upper left", frameon=True)
    plt.tight_layout()

    out_path = os.path.join(CHARTS_DIR, "monte_carlo_nav_simulation.png")
    plt.savefig(out_path, dpi=300)
    plt.close()

    print(f"Monte Carlo 5Y NAV Simulation complete for '{s_name}':")
    print(f"  Base NAV: ₹{S0:.2f} | 10th %ile: ₹{p10[-1]:.2f} | Median 50th: ₹{p50[-1]:.2f} | 90th %ile: ₹{p90[-1]:.2f}")
    print(f"  Saved chart figure to {out_path}")

    return p10, p50, p90

if __name__ == "__main__":
    run_monte_carlo_simulation()
