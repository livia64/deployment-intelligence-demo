import duckdb
from datetime import date

con = duckdb.connect("deployment.db")

# 1) Seed a cost rate (so we can simulate cost)
con.execute("""
INSERT INTO cost_rates (effective_date, runner_type, region, cost_per_build_minute_usd)
VALUES (?, ?, ?, ?)
""", [date.today(), "standard", "us-east-1", 0.08])

# 2) Get existing deployments
deployments = con.execute("SELECT deployment_id FROM deployments").fetchall()

# 3) Seed steps for each deployment
steps = [
    ("build", 12.0),
    ("test", 8.0),
    ("package", 5.0),
    ("deploy", 4.0),
]

for (deployment_id,) in deployments:
    for step_name, minutes in steps:
        con.execute("""
        INSERT INTO deployment_steps (deployment_id, step_name, duration_minutes)
        VALUES (?, ?, ?)
        """, [deployment_id, step_name, minutes])

con.close()
print("Seed complete.")


