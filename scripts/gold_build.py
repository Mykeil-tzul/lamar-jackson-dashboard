import os, pathlib
import duckdb
from dotenv import load_dotenv

def main():
    load_dotenv()
    db_path = os.getenv("DUCKDB_PATH", "db/nfl.duckdb")
    gold_dir = os.getenv("GOLD_DIR", "data/gold")
    pathlib.Path(gold_dir).mkdir(parents=True, exist_ok=True)

    con = duckdb.connect(db_path)
    con.execute("CREATE SCHEMA IF NOT EXISTS gold")

    sql = '''
    CREATE OR REPLACE TABLE gold.fact_lamar_weekly AS
    WITH base AS (
        SELECT
            season,
            week,
            COALESCE(team, '') AS team,
            COALESCE(opponent_team, '') AS opp,
            COALESCE(passing_yards, 0) AS passing_yards,
            COALESCE(rushing_yards, 0) AS rushing_yards,
            COALESCE(passing_tds, 0) AS passing_tds,
            COALESCE(rushing_tds, 0) AS rushing_tds,
            COALESCE(interceptions, 0) AS interceptions,
            COALESCE(fumbles_lost, 0) AS fumbles_lost,
            COALESCE(total_yards, 0) AS total_yards,
            COALESCE(total_tds, 0) AS total_tds,
            COALESCE(turnovers, 0) AS turnovers
        FROM silver.lamar_weekly
    )
    SELECT
        *,
        AVG(total_yards) OVER (PARTITION BY season ORDER BY week ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS rolling3_total_yards,
        AVG(total_tds)   OVER (PARTITION BY season ORDER BY week ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS rolling3_total_tds,
        AVG(turnovers)   OVER (PARTITION BY season ORDER BY week ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS rolling3_turnovers
    FROM base
    ORDER BY season, week;
    '''
    con.execute(sql)

    # Also export a csv for the dashboard to read directly if preferred
    out_csv = pathlib.Path(gold_dir) / "fact_lamar_weekly.csv"
    con.execute(f"COPY (SELECT * FROM gold.fact_lamar_weekly) TO '{out_csv}' (HEADER, DELIMITER ',')")
    print(f"[gold] wrote table gold.fact_lamar_weekly and {out_csv}")

if __name__ == "__main__":
    main()
