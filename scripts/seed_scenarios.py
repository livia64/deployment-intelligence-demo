import duckdb

con = duckdb.connect("deployment.db")

# cria a tabela se não existir
con.execute("""
CREATE TABLE IF NOT EXISTS scenario_assumptions (
    scenario_name VARCHAR,
    cost_multiplier DOUBLE,
    revenue_multiplier DOUBLE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# limpa para demo (opcional)
con.execute("DELETE FROM scenario_assumptions")

scenarios = [
    ("Base", 1.00, 1.00),
    ("Cost +20%", 1.20, 1.00),
    ("Cost +50%", 1.50, 1.00),
    ("Cost +100%", 2.00, 1.00),
    ("Revenue -10%", 1.00, 0.90),
    ("Revenue -20%", 1.00, 0.80),
    ("Stress Test (Cost +50%, Rev -15%)", 1.50, 0.85),
]

con.executemany("""
INSERT INTO scenario_assumptions (scenario_name, cost_multiplier, revenue_multiplier)
VALUES (?, ?, ?)
""", scenarios)

print("✅ scenario_assumptions seeded:", len(scenarios))

con.close()
