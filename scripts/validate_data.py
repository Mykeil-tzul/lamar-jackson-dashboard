import os, duckdb, importlib.util
from dotenv import load_dotenv

def basic_assertions(con):
    # Basic schema checks
    res = con.execute("SELECT COUNT(*) FROM gold.fact_lamar_weekly").fetchone()[0]
    assert res > 0, "Gold table is empty"

    # Uniqueness by season+week
    dup = con.execute("""
        SELECT COUNT(*) FROM (
          SELECT season, week, COUNT(*) c FROM gold.fact_lamar_weekly GROUP BY season, week HAVING COUNT(*) > 1
        )
    """).fetchone()[0]
    assert dup == 0, "Duplicate season-week rows in gold"

    # Null checks
    nulls = con.execute("""
        SELECT SUM(CASE WHEN season IS NULL THEN 1 ELSE 0 END) +
               SUM(CASE WHEN week   IS NULL THEN 1 ELSE 0 END)
        FROM gold.fact_lamar_weekly
    """).fetchone()[0]
    assert nulls == 0, "Null season/week found"

def try_great_expectations(con):
    try:
        import great_expectations as ge  # optional
        import pandas as pd
    except Exception as e:
        print("[validate] great_expectations not installed - skipping GE validations.")
        return

    df = con.execute("SELECT * FROM gold.fact_lamar_weekly").df()
    # Minimal ad-hoc expectations
    assert (df["season"] >= 2018).all()
    assert (df["week"].between(1, 22)).all()
    assert (df["total_yards"] >= 0).all()

    print("[validate] basic GE-style expectations passed.")

def main():
    load_dotenv()
    db_path = os.getenv("DUCKDB_PATH", "db/nfl.duckdb")
    con = duckdb.connect(db_path)
    basic_assertions(con)
    try_great_expectations(con)
    print("[validate] all good!")

if __name__ == "__main__":
    main()
