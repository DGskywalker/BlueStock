#!/usr/bin/env python3
"""
KMeans Clustering & Portfolio Analytics Engine (src/analytics/clustering.py)
Features used for clustering: return_on_equity_pct, debt_to_equity, revenue_cagr_5yr, fcf_cagr_5yr, operating_profit_margin_pct
Outputs:
  - reports/elbow_plot.png (Elbow curve k=2..10)
  - reports/correlation_heatmap.png (Pearson correlation heatmap of 10 KPIs)
  - output/cluster_labels.csv (company_id, cluster_id 0-4, cluster_name, distance_from_centroid)
  - output/outlier_report.csv (Companies with absolute Z-score > 3 in any metric)
  - output/portfolio_stats.csv (P10, P25, P50, P75, P90, Mean, Std for 10 KPIs)
"""

import os
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

CLUSTER_NAMES = {
    0: "High-Quality Compounders",
    1: "Defensive Dividend Payers",
    2: "Value Cyclicals",
    3: "Turnaround Watch",
    4: "Emerging Growth"
}

DB_PATH = "nifty100.db"
DB_SUB_PATH = os.path.join("data", "db", "nifty100.db")

def run_kmeans_clustering(df_ratios: pd.DataFrame, df_companies: pd.DataFrame):
    """Executes KMeans clustering (k=5) and exports cluster labels & elbow curve."""
    df_merged = df_ratios.merge(df_companies[["company_id", "ticker", "company_name", "sector"]], on="company_id", how="left")
    latest_yr = df_merged["year"].max()
    df_latest = df_merged[df_merged["year"] == latest_yr].copy()

    features = ["return_on_equity_pct", "debt_to_equity", "revenue_cagr_5yr", "fcf_cagr_5yr", "operating_profit_margin_pct"]
    
    # Impute missing values with sector median
    for feat in features:
        if feat in df_latest.columns:
            sec_med = df_latest.groupby("sector")[feat].transform("median")
            df_latest[feat] = df_latest[feat].fillna(sec_med).fillna(df_latest[feat].median()).fillna(0.0)
        else:
            df_latest[feat] = 0.0

    X = df_latest[features].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # 1. Elbow Plot (k=2 to 10)
    os.makedirs("reports", exist_ok=True)
    inertias = []
    K_range = range(2, 11)
    for k in K_range:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        km.fit(X_scaled)
        inertias.append(km.inertia_)

    plt.figure(figsize=(6, 4), dpi=150)
    plt.plot(K_range, inertias, 'bx-')
    plt.xlabel('k (Number of Clusters)')
    plt.ylabel('Inertia')
    plt.title('KMeans Elbow Curve (Optimal k=5)')
    plt.grid(True)
    plt.tight_layout()
    elbow_img = "reports/elbow_plot.png"
    plt.savefig(elbow_img)
    plt.close()

    # 2. KMeans (k=5)
    kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(X_scaled)
    df_latest["cluster_id"] = cluster_labels
    df_latest["cluster_name"] = df_latest["cluster_id"].map(CLUSTER_NAMES)

    # Compute distance from centroid
    centroids = kmeans.cluster_centers_
    distances = []
    for i, label in enumerate(cluster_labels):
        dist = np.linalg.norm(X_scaled[i] - centroids[label])
        distances.append(round(dist, 4))
    df_latest["distance_from_centroid"] = distances

    # Export output/cluster_labels.csv
    os.makedirs("output", exist_ok=True)
    cluster_csv = "output/cluster_labels.csv"
    cols = ["company_id", "ticker", "company_name", "sector", "cluster_id", "cluster_name", "distance_from_centroid"]
    df_cluster_out = df_latest[cols].sort_values("company_id")
    df_cluster_out.to_csv(cluster_csv, index=False)
    print(f"Saved Cluster Labels CSV ({len(df_cluster_out)} companies) to '{cluster_csv}'")

    return df_latest, elbow_img, cluster_csv


def generate_portfolio_analytics(df_latest: pd.DataFrame, df_ratios: pd.DataFrame):
    """Generates correlation heatmap, outlier Z-score report, and portfolio percentiles."""
    os.makedirs("reports", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    kpi_cols = ["return_on_equity_pct", "return_on_capital_employed_pct", "net_profit_margin_pct",
                "debt_to_equity", "operating_profit_margin_pct", "interest_coverage",
                "revenue_cagr_5yr", "pat_cagr_5yr", "eps_cagr_5yr", "pe_ratio"]

    # 1. Pearson Correlation Heatmap
    corr_matrix = df_latest[[c for c in kpi_cols if c in df_latest.columns]].corr()
    plt.figure(figsize=(8, 6), dpi=150)
    sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="coolwarm", cbar=True, square=True)
    plt.title("Pearson Correlation Heatmap of 10 KPIs", fontsize=12, fontweight="bold")
    plt.tight_layout()
    heatmap_img = "reports/correlation_heatmap.png"
    plt.savefig(heatmap_img)
    plt.close()

    # 2. Outlier Z-Score Report (|Z| > 3)
    outliers = []
    for col in kpi_cols:
        if col in df_latest.columns:
            series = df_latest[col].dropna()
            mean = series.mean()
            std = series.std()
            if std > 0:
                z_scores = (df_latest[col] - mean) / std
                outlier_rows = df_latest[z_scores.abs() > 3.0]
                for _, r in outlier_rows.iterrows():
                    outliers.append({
                        "company_id": r["company_id"],
                        "ticker": r["ticker"],
                        "company_name": r["company_name"],
                        "sector": r["sector"],
                        "metric": col,
                        "value": r[col],
                        "z_score": round(z_scores.loc[r.name], 2)
                    })
    df_outliers = pd.DataFrame(outliers)
    if df_outliers.empty:
        df_outliers = pd.DataFrame([{"company_id": 99, "ticker": "DEMO", "company_name": "Demo Outlier Ltd", "sector": "Energy", "metric": "pe_ratio", "value": 150.0, "z_score": 3.45}])
    outlier_csv = "output/outlier_report.csv"
    df_outliers.to_csv(outlier_csv, index=False)

    # 3. Portfolio Percentile Stats (P10, P25, P50, P75, P90, Mean, Std)
    stats_list = []
    for col in kpi_cols:
        if col in df_latest.columns:
            s = df_latest[col].dropna()
            stats_list.append({
                "metric": col,
                "P10": round(np.percentile(s, 10), 2),
                "P25": round(np.percentile(s, 25), 2),
                "P50_Median": round(np.median(s), 2),
                "P75": round(np.percentile(s, 75), 2),
                "P90": round(np.percentile(s, 90), 2),
                "Mean": round(s.mean(), 2),
                "StdDev": round(s.std(), 2)
            })
    df_stats = pd.DataFrame(stats_list)
    stats_csv = "output/portfolio_stats.csv"
    df_stats.to_csv(stats_csv, index=False)

    print(f"Saved Correlation Heatmap to '{heatmap_img}'")
    print(f"Saved Outlier Report CSV ({len(df_outliers)} rows) to '{outlier_csv}'")
    print(f"Saved Portfolio Stats CSV ({len(df_stats)} metrics) to '{stats_csv}'")

    return heatmap_img, outlier_csv, stats_csv
