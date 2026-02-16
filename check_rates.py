import duckdb
con = duckdb.connect("deployment.db")

print("rates:", con.execute("SELECT COUNT(*) FROM cost_rates").fetchone()[0])
print("sample:", con.execute("SELECT * FROM cost_rates ORDER BY effective_date DESC LIMIT 5").fetchall())

con.close()
