import duckdb

con = duckdb.connect("deployment.db")

query = """
WITH rate AS (
  SELECT cost_per_build_minute_usd
  FROM cost_rates
  ORDER BY effective_date DESC
  LIMIT 1
),
agg AS (
  SELECT
    deployment_id,
    SUM(duration_minutes) AS total_minutes
  FROM deployment_steps
  GROUP BY deployment_id
),
costed AS (
  SELECT
    a.deployment_id,
    a.total_minutes,
    a.total_minutes * (SELECT cost_per_build_minute_usd FROM rate) AS cost_usd
  FROM agg a
)
SELECT
  c.deployment_id,
  c.total_minutes,
  ROUND(c.cost_usd, 2) AS cost_usd,
  ROUND(p.revenue_usd, 2) AS revenue_usd,
  ROUND(p.revenue_usd - c.cost_usd, 2) AS gross_margin_usd,
  ROUND((p.revenue_usd - c.cost_usd) / NULLIF(p.revenue_usd, 0) * 100, 1) AS gross_margin_pct
FROM costed c
JOIN pricing p USING (deployment_id)
ORDER BY gross_margin_usd DESC;
"""

rows = con.execute(query).fetchall()

print("Deployment Margin Simulation:\n")
print("(deployment_id, total_minutes, cost_usd, revenue_usd, gross_margin_usd, gross_margin_pct)")
for r in rows:
    print(r)

con.close()
