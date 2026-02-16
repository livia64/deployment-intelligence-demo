import duckdb

con = duckdb.connect("deployment.db")

COST_PER_BUILD_MINUTE = 0.01  # custo interno simulado (depois você liga em cost_rates)

print("\n=== A) Risk Flags (30d) ===")
rows = con.execute("""
WITH base AS (
  SELECT *
  FROM deployments
  WHERE created_at >= NOW() - INTERVAL 30 DAY
),
acct AS (
  SELECT
    account_id,
    COUNT(*) AS deployments_30d,

    -- preview share
    SUM(CASE WHEN env='preview' THEN 1 ELSE 0 END)::DOUBLE / NULLIF(COUNT(*),0) AS preview_share_count,
    SUM(CASE WHEN env='preview' THEN build_minutes ELSE 0 END) / NULLIF(SUM(build_minutes),0) AS preview_share_minutes,

    AVG(build_minutes) AS avg_build,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY build_minutes) AS p95_build,

    AVG(rerun_count) AS avg_reruns_per_deploy,
    SUM(rerun_count) AS total_reruns_30d,

    AVG(cache_hit_rate) AS avg_cache,
    AVG(queue_minutes) AS avg_queue,

    SUM(CASE WHEN status='fail' THEN 1 ELSE 0 END)::DOUBLE / NULLIF(COUNT(*),0) AS fail_rate
  FROM base
  GROUP BY account_id
)
SELECT
  account_id,
  deployments_30d,
  ROUND(preview_share_minutes, 3) AS preview_share_minutes,
  ROUND(avg_build, 2) AS avg_build,
  ROUND(p95_build, 2) AS p95_build,
  ROUND(avg_cache, 3) AS avg_cache,
  ROUND(avg_queue, 2) AS avg_queue,
  ROUND(fail_rate, 3) AS fail_rate,
  total_reruns_30d,

  CASE WHEN preview_share_minutes >= 0.60 THEN 'FLAG' ELSE 'OK' END AS preview_storm_risk,
  CASE WHEN total_reruns_30d >= 8 OR avg_reruns_per_deploy >= 0.15 THEN 'FLAG' ELSE 'OK' END AS rerun_instability_risk,
  CASE WHEN avg_build >= 10 OR p95_build >= 15 THEN 'FLAG' ELSE 'OK' END AS build_heaviness_risk,
  CASE WHEN avg_cache <= 0.60 THEN 'FLAG' ELSE 'OK' END AS cache_degradation_risk,
  CASE WHEN fail_rate >= 0.06 THEN 'FLAG' ELSE 'OK' END AS failure_risk

FROM acct
ORDER BY deployments_30d DESC;
""").fetchall()
for r in rows:
    print(r)

print("\n=== B) Waste Index (30d, conservative) ===")
rows = con.execute("""
WITH base AS (
  SELECT *
  FROM deployments
  WHERE created_at >= NOW() - INTERVAL 30 DAY
),
agg AS (
  SELECT
    account_id,
    SUM(build_minutes) AS total_build_minutes,
    SUM(queue_minutes) AS total_queue_minutes,
    SUM(COALESCE(rerun_count,0) * build_minutes) AS rerun_minutes_proxy,
    SUM(build_minutes * (1 - cache_hit_rate)) AS cache_opportunity_minutes
  FROM base
  GROUP BY account_id
)
SELECT
  account_id,
  total_build_minutes,
  total_queue_minutes,
  ROUND(rerun_minutes_proxy, 1) AS rerun_minutes_proxy,
  ROUND(cache_opportunity_minutes, 1) AS cache_opportunity_minutes,
  ROUND((rerun_minutes_proxy + 0.5 * cache_opportunity_minutes) / NULLIF(total_build_minutes, 0), 3) AS conservative_waste_index
FROM agg
ORDER BY conservative_waste_index DESC;
""").fetchall()
for r in rows:
    print(r)

print("\n=== C) 30-day Cost Projection by env (last 14 days baseline) ===")
rows = con.execute(f"""
WITH last14 AS (
  SELECT
    account_id,
    env,
    COUNT(*)::DOUBLE / 14.0 AS builds_per_day,
    AVG(build_minutes) AS avg_build_minutes,
    AVG(COALESCE(rerun_count,0)) AS avg_reruns
  FROM deployments
  WHERE created_at >= NOW() - INTERVAL 14 DAY
  GROUP BY account_id, env
)
SELECT
  account_id,
  env,
  ROUND(builds_per_day, 2) AS builds_per_day,
  ROUND(avg_build_minutes, 2) AS avg_build_minutes,
  ROUND(avg_reruns, 2) AS avg_reruns,
  ROUND(builds_per_day * 30 * avg_build_minutes * (1 + avg_reruns), 1) AS projected_minutes_30d,
  ROUND((builds_per_day * 30 * avg_build_minutes * (1 + avg_reruns)) * {COST_PER_BUILD_MINUTE}, 2) AS projected_cost_30d_usd
FROM last14
ORDER BY projected_cost_30d_usd DESC;
""").fetchall()
for r in rows:
    print(r)

print("\n=== D) Root-cause hints from retries (top reasons) ===")
rows = con.execute("""
SELECT
  reason,
  COUNT(*) AS events
FROM deployment_retries
GROUP BY reason
ORDER BY events DESC
LIMIT 10;
""").fetchall()
for r in rows:
    print(r)

con.close()
