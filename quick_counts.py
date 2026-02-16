import duckdb

con = duckdb.connect("deployment.db")

for t in ["deployment_steps", "cost_rates", "deployments", "accounts"]:
    n = con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    print(t, n)

con.close()
