#!/usr/bin/env python3
"""
Bonus Challenge B4: Markowitz Efficient Frontier Portfolio Optimization Engine
Performs portfolio optimization across 5 key mutual fund schemes via scipy.optimize.minimize (SLSQP),
computes Maximum Sharpe Ratio and Minimum Volatility portfolio weights, and plots the Efficient Frontier curve.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import minimize

# Setup Directories
CHARTS_DIR = os.path.join("reports", "charts")
PROCESSED_DIR = os.path.join("data", "processed")
os.makedirs(CHARTS_DIR, exist_ok=True)

def find_file(name):
    paths = [os.path.join(PROCESSED_DIR, name), os.path.join("csv", name), name]
    for p in paths:
        if os.path.exists(p): return p
    return name

def run_markowitz_optimization():
    nav_df = pd.read_csv(find_file("02_nav_history.csv"))
    nav_df["date"] = pd.to_datetime(nav_df["date"])
    fm_df = pd.read_csv(find_file("01_fund_master.csv"))

    codes = [119551, 120505, 118634, 120842, 148568]
    names = [fm_df[fm_df["amfi_code"] == c]["scheme_name"].values[0][:20] for c in codes]

    pivot_nav = nav_df[nav_df["amfi_code"].isin(codes)].pivot(index="date", columns="amfi_code", values="nav")
    daily_rets = pivot_nav.pct_change().dropna()

    mean_rets = daily_rets.mean() * 252.0
    cov_matrix = daily_rets.cov() * 252.0
    num_assets = len(codes)
    rf = 0.065

    # 1. Maximum Sharpe Ratio Portfolio Optimization
    def neg_sharpe(weights):
        p_ret = np.sum(mean_rets * weights)
        p_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        return -(p_ret - rf) / p_vol

    constraints = ({ "type": "eq", "fun": lambda x: np.sum(x) - 1.0 })
    bounds = tuple((0.0, 1.0) for _ in range(num_assets))
    init_guess = num_assets * [1.0 / num_assets]

    opt_max_sharpe = minimize(neg_sharpe, init_guess, method="SLSQP", bounds=bounds, constraints=constraints)
    max_s_weights = opt_max_sharpe.x

    max_s_ret = np.sum(mean_rets * max_s_weights)
    max_s_vol = np.sqrt(np.dot(max_s_weights.T, np.dot(cov_matrix, max_s_weights)))
    max_s_sharpe = (max_s_ret - rf) / max_s_vol

    # 2. Minimum Volatility Portfolio Optimization
    def portfolio_vol(weights):
        return np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))

    opt_min_vol = minimize(portfolio_vol, init_guess, method="SLSQP", bounds=bounds, constraints=constraints)
    min_v_weights = opt_min_vol.x

    min_v_ret = np.sum(mean_rets * min_v_weights)
    min_v_vol = opt_min_vol.fun

    # 3. Generate Random Portfolio Cloud for Efficient Frontier Plot
    n_portfolios = 2000
    p_returns = []
    p_volatilities = []

    for _ in range(n_portfolios):
        w = np.random.random(num_assets)
        w /= np.sum(w)
        r = np.sum(mean_rets * w)
        v = np.sqrt(np.dot(w.T, np.dot(cov_matrix, w)))
        p_returns.append(r)
        p_volatilities.append(v)

    p_returns = np.array(p_returns)
    p_volatilities = np.array(p_volatilities)
    p_sharpe = (p_returns - rf) / p_volatilities

    # Plot Efficient Frontier
    plt.figure(figsize=(12, 7))
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")

    scatter = plt.scatter(p_volatilities * 100, p_returns * 100, c=p_sharpe, cmap="viridis", alpha=0.5, s=15)
    cbar = plt.colorbar(scatter)
    cbar.set_label("Sharpe Ratio (Rf = 6.5%)", fontsize=10)

    # Highlight Max Sharpe & Min Volatility Portfolios
    plt.scatter(max_s_vol * 100, max_s_ret * 100, color="red", marker="*", s=300, label=f"Max Sharpe Portfolio (SR: {max_s_sharpe:.2f})")
    plt.scatter(min_v_vol * 100, min_v_ret * 100, color="gold", marker="D", s=150, label=f"Min Volatility Portfolio (Vol: {min_v_vol*100:.2f}%)")

    plt.title("Markowitz Efficient Frontier Portfolio Optimization (5 Selected Schemes)", fontsize=14, fontweight="bold", pad=12)
    plt.xlabel("Annualized Volatility (%)", fontsize=11)
    plt.ylabel("Annualized Expected Return (%)", fontsize=11)
    plt.legend(loc="upper left", frameon=True)
    plt.tight_layout()

    out_path = os.path.join(CHARTS_DIR, "markowitz_efficient_frontier.png")
    plt.savefig(out_path, dpi=300)
    plt.close()

    print("Markowitz Portfolio Optimization Complete:")
    print(f"  Max Sharpe Portfolio -> Return: {max_s_ret*100:.2f}% | Vol: {max_s_vol*100:.2f}% | Sharpe: {max_s_sharpe:.2f}")
    for n, w in zip(names, max_s_weights):
        print(f"    - {n}: {w*100:.2f}%")
    print(f"  Saved chart figure to {out_path}")

    return max_s_weights, min_v_weights

if __name__ == "__main__":
    run_markowitz_optimization()
