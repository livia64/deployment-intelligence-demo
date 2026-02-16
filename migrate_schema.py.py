import duckdb

con = duckdb.connect("deployment.db")

# --- accounts ---
con.execute("""
CREATE TABLE IF NOT EXISTS accounts (
  account_id VARCHAR PRIMARY KEY,
  plan VARCHAR,
  mrr_usd DOUBLE,
  created_at TIMESTAMP
);
""")

# --- cost rates ---
con.execute("""
CREATE TABLE IF NOT EXISTS cost_rates (
  effective_date DATE,
  runner_type VARCHAR,
  region VARCHAR,
  cost_per_build_minute_usd DOUBLE
);
""")

# --- deployment steps ---
con.execute("""
CREATE TABLE IF NOT EXISTS deployment_steps (
  deployment_id VARCHAR,
  step_name VARCHAR,
  duration_minutes DOUBLE
);
""")

# --- add columns to deployments ---
con.execute("ALTER TABLE deployments ADD COLUMN IF NOT EXISTS runner_type VARCHAR;")
con.execute("ALTER TABLE deployments ADD COLUMN IF NOT EXISTS region VARCHAR;")
con.execute("ALTER TABLE deployments ADD COLUMN IF NOT EXISTS status VARCHAR;")
con.execute("ALTER TABLE deployments ADD COLUMN IF NOT EXISTS commit_sha VARCHAR;")
con.execute("ALTER TABLE deployments ADD COLUMN IF NOT EXISTS changed_files_count INTEGER;")
con.execute("ALTER TABLE deployments ADD COLUMN IF NOT EXISTS artifact_mb DOUBLE;")
con.execute("ALTER TABLE deployments ADD COLUMN IF NOT EXISTS trigger VARCHAR;")

print("Schema migration complete.")
con.close()

