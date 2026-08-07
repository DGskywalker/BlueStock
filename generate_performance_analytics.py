import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
import nbformat as nbf

# Setup Directories
CHARTS_DIR = os.path.join("reports", "charts")
NOTEBOOKS_DIR = "notebooks"
PROCESSED_DIR = os.path.join("data", "processed")

os.makedirs(CHARTS_DIR, exist_ok=True)
os.makedirs(NOTEBOOKS_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

# Helper function to find CSV path
def find_file(name):
    paths = [
        os.path.join(PROCESSED_DIR, name),
        os.path.join("csv", name),
        name,
        os.path.join("data", "raw", name)
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return name

print("Loading cleaned datasets for Performance Analytics...")
nav_df = pd.read_csv(find_file("02_nav_history.csv"))
nav_df["date"] = pd.to_datetime(nav_df["date"])

fm_df = pd.read_csv(find_file("01_fund_master.csv"))
sp_df = pd.read_csv(find_file("07_scheme_performance.csv"))

bi_df = pd.read_csv(find_file("10_benchmark_indices.csv"))
bi_df["date"] = pd.to_datetime(bi_df["date"])

# Extract NIFTY 100 & NIFTY 50 benchmark daily returns
nifty100_df = bi_df[bi_df["index_name"] == "NIFTY100"].sort_values("date").set_index("date")["close_value"]
nifty100_ret = nifty100_df.pct_change().dropna()

nifty50_df = bi_df[bi_df["index_name"] == "NIFTY50"].sort_values("date").set_index("date")["close_value"]
nifty50_ret = nifty50_df.pct_change().dropna()

RF_ANNUAL = 0.065 # 6.5% RBI Repo Rate Proxy
RF_DAILY = RF_ANNUAL / 252.0

# -----------------------------------------------------------------------------
# 1. Compute Daily Returns & Risk-Adjusted Metrics per Fund
# -----------------------------------------------------------------------------
results = []
alpha_beta_list = []

codes = fm_df["amfi_code"].unique()

for code in codes:
    f_info = fm_df[fm_df["amfi_code"] == code].iloc[0]
    f_nav = nav_df[nav_df["amfi_code"] == code].sort_values("date").set_index("date")["nav"]
    f_ret = f_nav.pct_change().dropna()
    
    # 1. CAGR Calculations (1Y, 3Y, 5Y / Max)
    start_date = f_nav.index[0]
    end_date = f_nav.index[-1]
    total_days = (end_date - start_date).days
    total_years = total_days / 365.25
    
    start_nav = f_nav.iloc[0]
    end_nav = f_nav.iloc[-1]
    
    cagr_overall = (end_nav / start_nav) ** (1.0 / total_years) - 1.0
    
    # 1-Year CAGR
    date_1y = end_date - pd.DateOffset(years=1)
    sub_1y = f_nav[f_nav.index >= date_1y]
    cagr_1yr = (sub_1y.iloc[-1] / sub_1y.iloc[0]) ** (1.0 / 1.0) - 1.0 if len(sub_1y) > 1 else cagr_overall
    
    # 3-Year CAGR
    date_3y = end_date - pd.DateOffset(years=3)
    sub_3y = f_nav[f_nav.index >= date_3y]
    cagr_3yr = (sub_3y.iloc[-1] / sub_3y.iloc[0]) ** (1.0 / 3.0) - 1.0 if len(sub_3y) > 1 else cagr_overall

    # 5-Year CAGR (or available duration)
    cagr_5yr = cagr_overall
    
    # 2. Sharpe Ratio
    avg_daily_ret = f_ret.mean()
    std_daily_ret = f_ret.std()
    sharpe = (avg_daily_ret - RF_DAILY) / std_daily_ret * np.sqrt(252) if std_daily_ret > 0 else 0.0
    
    # 3. Sortino Ratio (Downside deviation only)
    neg_rets = f_ret[f_ret < 0]
    downside_std = neg_rets.std()
    sortino = (avg_daily_ret - RF_DAILY) / downside_std * np.sqrt(252) if downside_std > 0 else 0.0
    
    # 4. Alpha & Beta (OLS Regression vs NIFTY 100)
    comb = pd.DataFrame({"fund": f_ret, "nifty100": nifty100_ret}).dropna()
    if len(comb) > 30:
        reg = stats.linregress(comb["nifty100"], comb["fund"])
        beta = reg.slope
        alpha = reg.intercept * 252.0 # Annualized Alpha
        r_squared = reg.rvalue ** 2
        p_value = reg.pvalue
        std_err = reg.stderr
    else:
        beta, alpha, r_squared, p_value, std_err = 1.0, 0.0, 0.0, 1.0, 0.0
        
    # 5. Maximum Drawdown & Date Range
    running_max = f_nav.cummax()
    drawdown = (f_nav / running_max) - 1.0
    max_dd = drawdown.min()
    
    trough_date = drawdown.idxmin()
    peak_date = f_nav.loc[:trough_date].idxmax()
    dd_date_range = f"{peak_date.strftime('%Y-%m-%d')} to {trough_date.strftime('%Y-%m-%d')}"
    
    # Expense Ratio
    exp_ratio = f_info.get("expense_ratio_pct", 1.5)
    if pd.isna(exp_ratio):
        sp_match = sp_df[sp_df["amfi_code"] == code]
        exp_ratio = sp_match["expense_ratio_pct"].values[0] if len(sp_match) > 0 else 1.2
        
    results.append({
        "amfi_code": code,
        "scheme_name": f_info["scheme_name"],
        "fund_house": f_info["fund_house"],
        "category": f_info["category"],
        "sub_category": f_info["sub_category"],
        "cagr_1yr_pct": round(cagr_1yr * 100, 2),
        "cagr_3yr_pct": round(cagr_3yr * 100, 2),
        "cagr_5yr_pct": round(cagr_5yr * 100, 2),
        "sharpe_ratio": round(sharpe, 2),
        "sortino_ratio": round(sortino, 2),
        "alpha_pct": round(alpha * 100, 2),
        "beta": round(beta, 2),
        "max_drawdown_pct": round(max_dd * 100, 2),
        "worst_dd_period": dd_date_range,
        "expense_ratio_pct": round(exp_ratio, 2)
    })
    
    alpha_beta_list.append({
        "amfi_code": code,
        "scheme_name": f_info["scheme_name"],
        "fund_house": f_info["fund_house"],
        "category": f_info["category"],
        "beta": round(beta, 4),
        "annualized_alpha_pct": round(alpha * 100, 4),
        "r_squared": round(r_squared, 4),
        "p_value": round(p_value, 6),
        "std_error": round(std_err, 6)
    })

res_df = pd.DataFrame(results)
ab_df = pd.DataFrame(alpha_beta_list)

# -----------------------------------------------------------------------------
# 2. Composite Fund Scorecard (0 - 100 Scale)
# -----------------------------------------------------------------------------
# Ranks (Higher is better for CAGR, Sharpe, Alpha. Lower is better for Expense Ratio & Max DD)
res_df["rank_3yr"] = res_df["cagr_3yr_pct"].rank(ascending=True, pct=True)
res_df["rank_sharpe"] = res_df["sharpe_ratio"].rank(ascending=True, pct=True)
res_df["rank_alpha"] = res_df["alpha_pct"].rank(ascending=True, pct=True)
res_df["rank_expense_inv"] = res_df["expense_ratio_pct"].rank(ascending=False, pct=True)
res_df["rank_max_dd_inv"] = res_df["max_drawdown_pct"].rank(ascending=False, pct=True) # Max DD is negative, so smaller magnitude = higher value

res_df["scorecard_val"] = (
    0.30 * res_df["rank_3yr"] +
    0.25 * res_df["rank_sharpe"] +
    0.20 * res_df["rank_alpha"] +
    0.15 * res_df["rank_expense_inv"] +
    0.10 * res_df["rank_max_dd_inv"]
) * 100.0

res_df["fund_score"] = res_df["scorecard_val"].round(1)
res_df["overall_rank"] = res_df["fund_score"].rank(ascending=False, method="min").astype(int)
res_df = res_df.sort_values("overall_rank")

# Clean up helper rank columns
scorecard_df = res_df.drop(columns=["rank_3yr", "rank_sharpe", "rank_alpha", "rank_expense_inv", "rank_max_dd_inv", "scorecard_val"])

# Save CSV Deliverables
scorecard_df.to_csv(os.path.join(PROCESSED_DIR, "fund_scorecard.csv"), index=False)
scorecard_df.to_csv("fund_scorecard.csv", index=False)

ab_df.to_csv(os.path.join(PROCESSED_DIR, "alpha_beta.csv"), index=False)
ab_df.to_csv("alpha_beta.csv", index=False)

print("Saved fund_scorecard.csv and alpha_beta.csv deliverables!")

# -----------------------------------------------------------------------------
# 3. Top 5 Funds vs Benchmark Comparison & Tracking Error Plot
# -----------------------------------------------------------------------------
top_5_schemes = scorecard_df.head(5)
top_5_codes = top_5_schemes["amfi_code"].tolist()

# 3-Year NAV progression normalized to 100
start_3y_date = nav_df["date"].max() - pd.DateOffset(years=3)

fig, ax = plt.subplots(figsize=(14, 7))

# Plot NIFTY 50 Benchmark
n50_3y = nifty50_df[nifty50_df.index >= start_3y_date]
n50_norm = n50_3y / n50_3y.iloc[0] * 100.0
ax.plot(n50_norm.index, n50_norm, label="NIFTY 50 Index (Benchmark)", color="black", linestyle="--", linewidth=2.5)

# Plot NIFTY 100 Benchmark
n100_3y = nifty100_df[nifty100_df.index >= start_3y_date]
n100_norm = n100_3y / n100_3y.iloc[0] * 100.0
ax.plot(n100_norm.index, n100_norm, label="NIFTY 100 Index (Benchmark)", color="#444444", linestyle=":", linewidth=2.5)

tracking_errors = []

for code in top_5_codes:
    s_name = fm_df[fm_df["amfi_code"] == code]["scheme_name"].values[0][:25]
    f_sub = nav_df[(nav_df["amfi_code"] == code) & (nav_df["date"] >= start_3y_date)].sort_values("date").set_index("date")["nav"]
    f_norm = f_sub / f_sub.iloc[0] * 100.0
    
    # Calculate Tracking Error vs NIFTY 100
    f_ret_3y = f_sub.pct_change().dropna()
    n100_ret_3y = nifty100_ret[nifty100_ret.index >= start_3y_date]
    comb_te = pd.DataFrame({"f": f_ret_3y, "b": n100_ret_3y}).dropna()
    te = (comb_te["f"] - comb_te["b"]).std() * np.sqrt(252) * 100.0
    tracking_errors.append({"amfi_code": code, "scheme_name": s_name, "tracking_error_pct": round(te, 2)})
    
    ax.plot(f_norm.index, f_norm, label=f"{s_name} (TE: {te:.2f}%)", linewidth=2.0)

ax.set_title("Top 5 Funds vs. Benchmarks (NIFTY 50 & NIFTY 100) — 3-Year Relative Performance", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Date", fontsize=11)
ax.set_ylabel("Normalized NAV / Index Level (Base = 100)", fontsize=11)
ax.legend(loc="upper left", frameon=True)
plt.tight_layout()

chart_path = os.path.join(CHARTS_DIR, "top5_vs_benchmark_comparison.png")
plt.savefig(chart_path, dpi=300)
plt.close()

print(f"Saved benchmark comparison chart PNG to {chart_path}!")

# =============================================================================
# BUILD JUPYTER NOTEBOOK (notebooks/Performance_Analytics.ipynb)
# =============================================================================
print("Building Jupyter Notebook: notebooks/Performance_Analytics.ipynb ...")

nb = nbf.v4.new_notebook()

cells = [
    nbf.v4.new_markdown_cell("""# 📈 BlueStock Mutual Fund Platform — Risk & Performance Analytics

This notebook delivers rigorous financial analytics across all 40 mutual fund schemes. It calculates **Daily Returns**, **Multi-Period CAGRs**, **Risk-Adjusted Ratios (Sharpe & Sortino)**, **OLS Regression Alpha & Beta vs NIFTY 100**, **Maximum Drawdowns with Peak-to-Trough Date Ranges**, a composite **0–100 Fund Scorecard**, and **Benchmark Tracking Error** comparisons.

---
"""),

    nbf.v4.new_code_cell("""import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
from IPython.display import display

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')

PROCESSED_DIR = os.path.join('..', 'data', 'processed') if os.path.exists(os.path.join('..', 'data', 'processed')) else os.path.join('data', 'processed')

def p(name):
    for path in [os.path.join(PROCESSED_DIR, name), os.path.join('csv', name), name]:
        if os.path.exists(path): return path
    return name

print("Loading cleaned dataset and scorecard results...")
scorecard_df = pd.read_csv(p('fund_scorecard.csv'))
alpha_beta_df = pd.read_csv(p('alpha_beta.csv'))
nav_df = pd.read_csv(p('02_nav_history.csv'))
nav_df['date'] = pd.to_datetime(nav_df['date'])

bi_df = pd.read_csv(p('10_benchmark_indices.csv'))
bi_df['date'] = pd.to_datetime(bi_df['date'])

print(f"Loaded metrics for all {len(scorecard_df)} schemes!")
"""),

    nbf.v4.new_markdown_cell("""## 1. Top 10 Composite Fund Scorecard (0–100 Rating Scale)

The composite rating score synthesizes 5 core parameters:
- **30%**: 3-Year CAGR Rank
- **25%**: Risk-Adjusted Sharpe Ratio Rank
- **20%**: Alpha Outperformance Rank
- **15%**: Expense Ratio Rank (Inverse)
- **10%**: Max Drawdown Rank (Inverse)
"""),

    nbf.v4.new_code_cell("""# Display Top 10 Rated Funds
top10_table = scorecard_df[['overall_rank', 'fund_score', 'scheme_name', 'fund_house', 'category', 'cagr_3yr_pct', 'sharpe_ratio', 'sortino_ratio', 'alpha_pct', 'max_drawdown_pct', 'expense_ratio_pct']].head(10)
display(top10_table)
"""),

    nbf.v4.new_markdown_cell("""## 2. Risk-Adjusted Performance (Sharpe vs. Sortino Ratios)

- **Sharpe Ratio**: Uses total volatility in the denominator ($R_f = 6.5\%$).
- **Sortino Ratio**: Uses downside volatility only, punishing only negative return days.
"""),

    nbf.v4.new_code_cell("""# Bar Plot of Top 10 Schemes by Sharpe & Sortino Ratio
top10_ratios = scorecard_df.head(10).melt(id_vars=['scheme_name'], value_vars=['sharpe_ratio', 'sortino_ratio'], var_name='Metric', value_name='Ratio')

plt.figure(figsize=(14, 6))
sns.barplot(data=top10_ratios, x='scheme_name', y='Ratio', hue='Metric', palette='muted')
plt.title("Risk-Adjusted Ratios (Sharpe vs. Sortino) for Top 10 Rated Schemes", fontsize=14, fontweight="bold")
plt.xlabel("Scheme Name", fontsize=11)
plt.ylabel("Ratio Value", fontsize=11)
plt.xticks(rotation=45, ha='right')
plt.legend(title="Risk Metric")
plt.tight_layout()
plt.show()
"""),

    nbf.v4.new_markdown_cell("""## 3. OLS Regression Analysis: Fund Alpha & Beta vs. NIFTY 100 Benchmark

Alpha measures manager stock-picking skill (annualized excess return over market line), while Beta measures systemic market exposure.
"""),

    nbf.v4.new_code_cell("""# Scatter Plot of Alpha vs Beta across Funds
plt.figure(figsize=(12, 6))
sns.scatterplot(data=scorecard_df, x='beta', y='alpha_pct', hue='category', size='cagr_3yr_pct', sizes=(40, 300), palette='deep')
plt.axhline(0, color='red', linestyle='--', linewidth=1, label='Zero Alpha Baseline')
plt.axvline(1, color='gray', linestyle=':', linewidth=1, label='Market Beta = 1.0')

plt.title("Scheme Alpha (%) vs. Beta (Systemic Market Risk)", fontsize=14, fontweight="bold")
plt.xlabel("Beta (Market Sensitivity)", fontsize=11)
plt.ylabel("Annualized Alpha (%)", fontsize=11)
plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left')
plt.tight_layout()
plt.show()
"""),

    nbf.v4.new_markdown_cell("""## 4. Maximum Drawdown & Downside Risk Profile

Maximum Drawdown measures peak-to-trough drop. The table highlights worst drawdown periods across equity and debt categories.
"""),

    nbf.v4.new_code_cell("""# Display Worst Drawdown Risk Table
dd_table = scorecard_df[['scheme_name', 'category', 'max_drawdown_pct', 'worst_dd_period', 'cagr_3yr_pct']].sort_values('max_drawdown_pct', ascending=True).head(10)
display(dd_table)
"""),

    nbf.v4.new_markdown_cell("""## 5. Benchmark Comparison & Tracking Error Analysis

Top 5 ranked funds plotted against NIFTY 50 and NIFTY 100 benchmarks over 3 years.
"""),

    nbf.v4.new_code_cell("""# Plot Normalized Performance of Top 5 Funds vs NIFTY 50 and NIFTY 100
top_5_codes = scorecard_df.head(5)['amfi_code'].tolist()
start_3y_date = nav_df['date'].max() - pd.DateOffset(years=3)

nifty50_df = bi_df[bi_df['index_name'] == 'NIFTY50'].sort_values('date').set_index('date')['close_value']
nifty100_df = bi_df[bi_df['index_name'] == 'NIFTY100'].sort_values('date').set_index('date')['close_value']

plt.figure(figsize=(14, 7))

n50_3y = nifty50_df[nifty50_df.index >= start_3y_date]
plt.plot(n50_3y.index, n50_3y / n50_3y.iloc[0] * 100, label="NIFTY 50 Benchmark", color="black", linestyle="--", linewidth=2.5)

n100_3y = nifty100_df[nifty100_df.index >= start_3y_date]
plt.plot(n100_3y.index, n100_3y / n100_3y.iloc[0] * 100, label="NIFTY 100 Benchmark", color="#444444", linestyle=":", linewidth=2.5)

for code in top_5_codes:
    s_name = scorecard_df[scorecard_df['amfi_code'] == code]['scheme_name'].values[0][:25]
    f_sub = nav_df[(nav_df['amfi_code'] == code) & (nav_df['date'] >= start_3y_date)].sort_values('date').set_index('date')['nav']
    plt.plot(f_sub.index, f_sub / f_sub.iloc[0] * 100, label=s_name, linewidth=2.0)

plt.title("Top 5 Rated Funds vs. NIFTY 50 & NIFTY 100 Benchmarks (3-Year Relative Performance)", fontsize=14, fontweight="bold")
plt.xlabel("Date", fontsize=11)
plt.ylabel("Normalized NAV / Index Level (Base = 100)", fontsize=11)
plt.legend(loc="upper left")
plt.tight_layout()
plt.show()
""")
]

nb["cells"] = cells

# Save Notebooks
nb_path_sub = os.path.join(NOTEBOOKS_DIR, "Performance_Analytics.ipynb")
nb_path_root = "Performance_Analytics.ipynb"

with open(nb_path_sub, "w", encoding="utf-8") as f:
    nbf.write(nb, f)

with open(nb_path_root, "w", encoding="utf-8") as f:
    nbf.write(nb, f)

print(f"Saved Jupyter Notebook to {nb_path_sub} and {nb_path_root}")
print("Performance Analytics pipeline completed successfully!")
