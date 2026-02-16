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
)

SELECT
    deployment_id,
    total_minutes,
    total_minutes * (SELECT cost_per_build_minute_usd FROM rate) AS estimated_cost_usd
FROM agg
ORDER BY estimated_cost_usd DESC
LIMIT 10;
"""

result = con.execute(query).fetchall()

print("Top 10 Deployments by Estimated Cost:\n")
for row in result:
    print(row)

con.close()
