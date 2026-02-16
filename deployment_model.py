import duckdb

# conecta ou cria banco local
con = duckdb.connect("deployment.db")

# cria tabela
con.execute("""
CREATE TABLE IF NOT EXISTS deployments (
  deployment_id VARCHAR,
  account_id VARCHAR,
  project_id VARCHAR,
  env VARCHAR,
  created_at TIMESTAMP,
  build_minutes DOUBLE,
  queue_minutes DOUBLE,
  cache_hit_rate DOUBLE,
  rerun_flag BOOLEAN
);
""")

# inserir dados teste
con.execute("""
INSERT INTO deployments VALUES
('d1','a1','p1','preview',CURRENT_TIMESTAMP,12,2,0.4,false),
('d2','a1','p1','prod',CURRENT_TIMESTAMP,9,1,0.8,false),
('d3','a1','p1','preview',CURRENT_TIMESTAMP,14,3,0.3,true),
('d4','a2','p2','prod',CURRENT_TIMESTAMP,7,1,0.9,false);
""")

print("Banco criado e dados inseridos.")
