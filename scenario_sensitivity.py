import duckdb

con = duckdb.connect("deployment.db")

# Scenario multipliers
SCENARIOS = [
    ("Base", 1.00),
    ("+20% cost", 1.20),
    ("+50% cost", 1.50),
    ("+100% cost", 2.00),
]

# Get latest cost rate
base_rate = con.execute(
    "SELECT cost_per_build_minute_usd FROM cost_rates ORDER BY effective_date DESC LIMIT 1"
).fetchone()[0]

print("\n=== SCENARIO SENSITIVITY ===")
print(f"Base cost per minute: {base_rate}\n")

# Compute total minutes per deployment
deployment_minutes = con.execute("""
    SELECT deployment_id, SUM(duration_minutes) AS total_minutes
    FROM deployment_steps
    GROUP BY deployment_id
""").fetchall()

# Get pricing data
pricing = dict(con.execute("""
    SELECT deployment_id, revenue_usd
    FROM pricing
""").fetchall())

print("(deployment_id, scenario, cost_usd, revenue_usd, margin_usd, margin_pct)\n")

for deployment_id, total_minutes in deployment_minutes:
    revenue = pricing.get(deployment_id, 0)

    for label, multiplier in SCENARIOS:
        rate = base_rate * multiplier
        cost = total_minutes * rate
        margin = revenue - cost
        margin_pct = (margin / revenue * 100) if revenue != 0 else 0

        print((
            deployment_id,
            label,
            round(cost, 2),
            revenue,
            round(margin, 2),
            round(margin_pct, 1)
        ))

con.close()
