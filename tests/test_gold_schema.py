import os, duckdb

def test_gold_not_empty():
    con = duckdb.connect(os.getenv("DUCKDB_PATH", "db/nfl.duckdb"))
    cnt = con.execute("SELECT COUNT(*) FROM gold.fact_lamar_weekly").fetchone()[0]
    assert cnt > 0

def test_unique_season_week():
    con = duckdb.connect(os.getenv("DUCKDB_PATH", "db/nfl.duckdb"))
    dup = con.execute("""
        SELECT COUNT(*) FROM (
          SELECT season, week, COUNT(*) c FROM gold.fact_lamar_weekly GROUP BY season, week HAVING COUNT(*) > 1
        )
    """).fetchone()[0]
    assert dup == 0
