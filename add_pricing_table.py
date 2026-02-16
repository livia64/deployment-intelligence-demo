import duckdb

con = duckdb.connect("deployment.db")

# Create a simple pricing table (idempotent)
con.execute("""
CREATE TABLE IF NOT EXISTS pricing (
  deployment_id VARCHAR,
  revenue_usd DOUBLE,
  pricing_model VARCHAR,
  created_at TIMESTAMP DEFAULT NOW()
)
""")

# Seed example revenues (adjust values freely)
rows = [
    ("d1", 25.0, "flat_fee"),
    ("d2", 35.0, "flat_fee"),
    ("d3", 15.0, "flat_fee"),
    ("d4", 50.0, "flat_fee"),
]

# Upsert-ish (delete then insert for demo simplicity)
con.execute("DELETE FROM pricing")
con.executemany("INSERT INTO pricing (deployment_id, revenue_usd, pricing_model) VALUES (?, ?, ?)", rows)

con.close()
print("pricing table ready.")
