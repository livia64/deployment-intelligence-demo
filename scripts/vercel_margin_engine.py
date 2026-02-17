# vercel_margin_engine.py
import duckdb
import pandas as pd
from pathlib import Path

DB_PATH = "deployment.db"
OUT_DIR = Path("outputs")
OUT_DIR.mkdir(exist_ok=True)
OUT_CSV = OUT_DIR / "vercel_margin_simulation.csv"


def main():
    con = duckdb.connect(DB_PATH)

    # 1) Base rate (latest)
    base_rate_row = con.execute("""
        SELECT cost_per_build_minute_usd
        FROM cost_rates
        ORDER BY effective_date DESC
        LIMIT 1
    """).fetchone()

    if not base_rate_row:
        con.close()
        raise SystemExit("ERROR: cost_rates is empty. Seed at least one row in cost_rates first.")

    base_rate = float(base_rate_row[0])

    # 2) Minutes per deployment
    deployment_minutes = con.execute("""
        SELECT deployment_id, SUM(duration_minutes) AS total_minutes
        FROM deployment_steps
        GROUP BY deployment_id
    """).fetchall()

    # 3) Pricing
    pricing_rows = con.execute("""
        SELECT deployment_id, revenue_usd
        FROM pricing
    """).fetchall()
    pricing = {dep_id: float(rev) for dep_id, rev in pricing_rows}

    # 4) Scenarios (DB-driven)
    scenarios = con.execute("""
        SELECT scenario_name, cost_multiplier, revenue_multiplier
        FROM scenario_assumptions
        ORDER BY created_at ASC, scenario_name ASC
    """).fetchall()

    # --- Debug summary (safe to show in console) ---
    print("\n=== VERCEL MARGIN ENGINE (DB-DRIVEN) ===")
    print(f"DB: {DB_PATH}")
    print(f"Base cost_per_minute_usd: {base_rate:.4f}")
    print(f"deployments with minutes: {len(deployment_minutes)}")
    print(f"pricing rows: {len(pricing)}")
    print(f"scenarios: {len(scenarios)}")

    # Guardrails
    if len(deployment_minutes) == 0:
        con.close()
        raise SystemExit("ERROR: deployment_steps is empty (no minutes to cost). Seed deployment_steps first.")

    if len(pricing) == 0:
        con.close()
        raise SystemExit("ERROR: pricing is empty. Seed pricing first (deployment_id -> revenue_usd).")

    if len(scenarios) == 0:
        con.close()
        raise SystemExit("ERROR: scenario_assumptions is empty. Seed scenarios first.")

    # 5) Compute scenario results
    results = []
    missing_pricing = 0

    for deployment_id, total_minutes in deployment_minutes:
        deployment_id = str(deployment_id)
        total_minutes = float(total_minutes) if total_minutes is not None else 0.0

        revenue_base = pricing.get(deployment_id)
        if revenue_base is None:
            missing_pricing += 1
            continue

        for scenario_name, cost_mult, rev_mult in scenarios:
            cost_mult = float(cost_mult)
            rev_mult = float(rev_mult)

            cost_per_minute = base_rate * cost_mult
            revenue = revenue_base * rev_mult
            cost = total_minutes * cost_per_minute
            margin = revenue - cost
            margin_pct = (margin / revenue * 100.0) if revenue else 0.0

            results.append({
                "deployment_id": deployment_id,
                "scenario": str(scenario_name),
                "total_minutes": round(total_minutes, 2),
                "cost_per_minute_usd": round(cost_per_minute, 4),
                "cost_usd": round(cost, 2),
                "revenue_usd": round(revenue, 2),
                "gross_margin_usd": round(margin, 2),
                "gross_margin_pct": round(margin_pct, 1),
            })

    con.close()

    if missing_pricing > 0:
        print(f"WARNING: {missing_pricing} deployment(s) had no pricing and were skipped.")

    if not results:
        raise SystemExit("ERROR: No results generated. Check that pricing deployment_id matches deployment_steps deployment_id.")

    # 6) Build DataFrame and export
    df = pd.DataFrame(results)
    df = df.sort_values(["deployment_id", "scenario"]).reset_index(drop=True)

    df.to_csv(OUT_CSV, index=False)

    # 7) Print a compact view (best for copy/paste into slide)
    print("\n--- Output Preview (first 30 rows) ---")
    print(df.head(30).to_string(index=False))

    print(f"\n✅ CSV exported: {OUT_CSV}")


if __name__ == "__main__":
    main()
