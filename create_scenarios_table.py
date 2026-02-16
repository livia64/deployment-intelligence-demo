import duckdb

con = duckdb.connect("deployment.db")

con.execute("""
CREATE TABLE IF NOT EXISTS scenario_assumptions (
    scenario_name VARCHAR,
    cost_multiplier DOUBLE,
    revenue_multiplier DOUBLE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

print("scenario_assumptions table created.")

con.close()
