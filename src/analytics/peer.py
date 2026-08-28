#!/usr/bin/env python3
"""
Peer Analytics & Percentile Ranking Engine (src/analytics/peer.py)
Computes PERCENT_RANK for 10 metrics across 11 peer groups.
Populates peer_percentiles table in SQLite nifty100.db.
Generates 8-axis polar radar charts with peer group average overlay saved to reports/radar_charts/.
"""

import os
import sqlite3
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg") # Non-interactive headless backend
import matplotlib.pyplot as plt

PEER_METRICS = [
    "return_on_equity_pct",
    "return_on_capital_employed_pct",
    "net_profit_margin_pct",
    "debt_to_equity",
    "free_cash_flow_cr",
    "pat_cagr_5yr",
    "revenue_cagr_5yr",
    "eps_cagr_5yr",
    "interest_coverage",
    "asset_turnover"
]

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS peer_percentiles (
    company_id INTEGER NOT NULL,
    peer_group_name TEXT NOT NULL,
    metric TEXT NOT NULL,
    value REAL,
    percentile_rank REAL NOT NULL,
    year INTEGER NOT NULL,
    PRIMARY KEY (company_id, peer_group_name, metric, year)
);
"""

def compute_percent_rank(series: pd.Series, inverse: bool = False) -> pd.Series:
    """Computes percentiles (0.0 to 1.0). If inverse=True (e.g. D/E), lower values get higher percentiles."""
    s_clean = series.fillna(series.median() if not series.dropna().empty else 0.0)
    if len(s_clean) <= 1 or s_clean.nunique() == 1:
        return pd.Series(0.5, index=series.index)
    ranks = s_clean.rank(method="min", ascending=True)
    pct = (ranks - 1.0) / (len(s_clean) - 1.0)
    if inverse:
        pct = 1.0 - pct
    return pct.round(4)


class PeerAnalyticsEngine:
    """Peer Group Percentile & Radar Visualization Engine."""

    def __init__(self, db_path: str = "nifty100.db"):
        self.db_path = db_path

    def compute_all_peer_percentiles(self, df_ratios: pd.DataFrame, df_companies: pd.DataFrame,
                                     df_peers: pd.DataFrame) -> pd.DataFrame:
        """
        Computes PERCENT_RANK across 10 metrics for each of the 11 peer groups.
        Populates peer_percentiles table in SQLite.
        """
        records = []
        
        # Clean overlapping metadata columns from df_ratios to prevent sector_x / sector_y issues
        df_r = df_ratios.copy()
        overlap_cols = [c for c in ["ticker", "company_name", "sector", "industry"] if c in df_r.columns]
        if overlap_cols:
            df_r = df_r.drop(columns=overlap_cols)

        # Merge company info into ratios
        df_merged = df_r.merge(df_companies[["company_id", "ticker", "company_name", "sector"]], on="company_id", how="left")

        # Define 11 Peer Groups based on sector/industry
        sectors = df_merged["sector"].dropna().unique()

        for sec_name in sectors:
            group_df = df_merged[df_merged["sector"] == sec_name].copy()
            if group_df.empty:
                continue
                
            # Latest year data per company in sector
            latest_year = group_df["year"].max()
            sec_latest = group_df[group_df["year"] == latest_year].copy()
            
            for metric in PEER_METRICS:
                if metric not in sec_latest.columns:
                    continue
                
                is_inv = (metric == "debt_to_equity")
                pct_series = compute_percent_rank(sec_latest[metric], inverse=is_inv)
                
                for idx, row in sec_latest.iterrows():
                    records.append({
                        "company_id": row["company_id"],
                        "peer_group_name": f"{sec_name} Group",
                        "metric": metric,
                        "value": row[metric],
                        "percentile_rank": pct_series.loc[idx],
                        "year": row["year"]
                    })

        df_percentiles = pd.DataFrame(records)
        
        # Check unassigned companies
        assigned_ids = set(df_percentiles["company_id"].unique()) if not df_percentiles.empty else set()
        all_comp_ids = set(df_companies["company_id"].unique())
        unassigned_ids = all_comp_ids - assigned_ids
        if unassigned_ids:
            print(f"Info: {len(unassigned_ids)} companies not in any peer group -> 'No peer group assigned'")

        # Populate SQLite
        target_dbs = [self.db_path]
        if self.db_path != ":memory:":
            target_dbs.append(os.path.join("data", "db", self.db_path))

        if not df_percentiles.empty:
            for target_db in target_dbs:
                if target_db == ":memory:" or os.path.exists(os.path.dirname(target_db) or "."):
                    conn = sqlite3.connect(target_db)
                    cur = conn.cursor()
                    cur.execute("PRAGMA foreign_keys = OFF;")
                    cur.execute(CREATE_TABLE_SQL)
                    cur.execute("DELETE FROM peer_percentiles;")
                    df_percentiles.to_sql("peer_percentiles", conn, if_exists="append", index=False)
                    conn.commit()
                    conn.close()

        return df_percentiles

    def generate_radar_charts(self, df_ratios: pd.DataFrame, df_companies: pd.DataFrame,
                              output_dir: str = "reports/radar_charts/"):
        """Generates 8-axis polar radar charts with filled company polygon and peer group average overlay."""
        os.makedirs(output_dir, exist_ok=True)
        
        df_r = df_ratios.copy()
        overlap_cols = [c for c in ["ticker", "company_name", "sector", "industry"] if c in df_r.columns]
        if overlap_cols:
            df_r = df_r.drop(columns=overlap_cols)

        df_merged = df_r.merge(df_companies[["company_id", "ticker", "sector"]], on="company_id", how="left")
        latest_yr = df_merged["year"].max()
        df_latest = df_merged[df_merged["year"] == latest_yr].copy()

        radar_metrics = [
            ("ROE", "return_on_equity_pct"),
            ("ROCE", "return_on_capital_employed_pct"),
            ("NPM", "net_profit_margin_pct"),
            ("D/E", "debt_to_equity"),
            ("FCF", "free_cash_flow_cr"),
            ("PAT CAGR", "pat_cagr_5yr"),
            ("Rev CAGR", "revenue_cagr_5yr"),
            ("Composite", "composite_quality_score")
        ]

        labels = [m[0] for m in radar_metrics]
        num_vars = len(labels)
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
        angles += angles[:1] # Close polygon

        for sec_name, sec_df in df_latest.groupby("sector"):
            # Compute sector averages
            sec_avg_vals = []
            for _, m_col in radar_metrics:
                vals = sec_df[m_col].fillna(0.0)
                sec_avg_vals.append(vals.mean() if not vals.empty else 0.0)
            
            # Scale sector averages 0-100 for radar
            sec_avg_scaled = [min(100.0, max(0.0, float(v))) for v in sec_avg_vals]
            sec_avg_scaled += sec_avg_scaled[:1]

            for _, comp_row in sec_df.iterrows():
                ticker = comp_row["ticker"]
                comp_vals = []
                for _, m_col in radar_metrics:
                    v = comp_row.get(m_col, 0.0)
                    comp_vals.append(min(100.0, max(0.0, float(v if v is not None else 0.0))))
                comp_vals += comp_vals[:1]

                fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
                
                # Company Filled Polygon
                ax.plot(angles, comp_vals, color="#1f77b4", linewidth=2, label=f"{ticker}")
                ax.fill(angles, comp_vals, color="#1f77b4", alpha=0.25)

                # Peer Group Average Dashed Overlay
                ax.plot(angles, sec_avg_scaled, color="#ff7f0e", linestyle="--", linewidth=2, label=f"{sec_name} Avg")

                ax.set_xticks(angles[:-1])
                ax.set_xticklabels(labels, fontsize=10, fontweight="bold")
                ax.set_title(f"{ticker} vs {sec_name} Peer Average", size=13, weight="bold", y=1.1)
                ax.legend(loc="upper right", bbox_to_anchor=(1.2, 1.1))

                png_path = os.path.join(output_dir, f"{ticker}_radar.png")
                plt.tight_layout()
                plt.savefig(png_path, dpi=150)
                plt.close(fig)

        print(f"Generated {len(df_latest)} radar charts saved to '{output_dir}'")
