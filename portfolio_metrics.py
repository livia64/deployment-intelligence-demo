import duckdb
import pandas as pd

con = duckdb.connect("deployment.db")

# Pull scenario results from engine table logic
df = pd.read_csv("outputs/vercel_margin_simulation.csv")

# Ensure numeric
numeric_cols = [
    "cost_usd",
    "revenue_usd",
    "gross_margin_usd",
    "gross_margin_pct"
]
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# -------------------------------
# 1️⃣ Weighted Portfolio Margin
# -------------------------------

portfolio = (
    df.groupby("scenario")
    .agg(
        total_revenue=("revenue_usd", "sum"),
        total_cost=("cost_usd", "sum"),
        total_gross_margin=("gross_margin_usd", "sum")
    )
    .reset_index()
)

portfolio["weighted_margin_pct"] = (
    portfolio["total_gross_margin"] /
    portfolio["total_revenue"] * 100
).round(1)

# -------------------------------
# 2️⃣ Exposure Under Stress
# -------------------------------

base_margin = portfolio.loc[
    portfolio["scenario"] == "Base",
    "weighted_margin_pct"
].values[0]

portfolio["margin_compression_vs_base"] = (
    portfolio["weighted_margin_pct"] - base_margin
).round(1)

# -------------------------------
# 3️⃣ Simulated EBITDA Impact
# -------------------------------

base_gross = portfolio.loc[
    portfolio["scenario"] == "Base",
    "total_gross_margin"
].values[0]

portfolio["ebitda_impact_vs_base_usd"] = (
    portfolio["total_gross_margin"] - base_gross
).round(2)

print("\n=== PORTFOLIO-LEVEL METRICS ===\n")
print(portfolio)

con.close()
