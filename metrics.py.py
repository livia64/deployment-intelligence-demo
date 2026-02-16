import duckdb

con = duckdb.connect("deployment.db")

tables = ["accounts", "deployments", "deployment_steps", "cost_rates"]

print("=== DATABASE METRICS ===\n")

for table in tables:
    count = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    print(f"{table}: {count} records")

con.close()

