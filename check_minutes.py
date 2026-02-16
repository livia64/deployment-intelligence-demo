import duckdb
con = duckdb.connect("deployment.db")

print("Rows with minutes not null:",
      con.execute("SELECT COUNT(*) FROM deployment_steps WHERE duration_minutes IS NOT NULL").fetchone()[0])

print("Sample rows:",
      con.execute("SELECT deployment_id, step_name, duration_minutes FROM deployment_steps LIMIT 5").fetchall())

con.close()
