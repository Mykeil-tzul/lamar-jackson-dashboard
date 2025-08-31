# scripts/silver_transform.py
import os
import glob
import pathlib
import duckdb
import pandas as pd
from dotenv import load_dotenv


def main():
    load_dotenv()

    bronze_dir = os.getenv("BRONZE_DIR", "data/bronze")
    silver_dir = os.getenv("SILVER_DIR", "data/silver")
    db_path = os.getenv("DUCKDB_PATH", "db/nfl.duckdb")

    pathlib.Path(silver_dir).mkdir(parents=True, exist_ok=True)
    pathlib.Path(os.path.dirname(db_path)).mkdir(parents=True, exist_ok=True)

    # 1) Load Bronze parquet partitions
    files = glob.glob(f"{bronze_dir}/season=*/week=*/lamar_weekly.parquet")
    if not files:
        raise SystemExit("No bronze files found. Run bronze_ingest.py first.")

    pdfs = [pd.read_parquet(f) for f in files]
    df = pd.concat(pdfs, ignore_index=True)

    # 2) Normalize columns expected downstream
    # Map nflfastR 'recent_team' to 'team'
    if "team" not in df.columns:
        if "recent_team" in df.columns:
            df["team"] = df["recent_team"]
        else:
            df["team"] = ""

    # Some exports use 'opponent' instead of 'opponent_team'
    if "opponent_team" not in df.columns and "opponent" in df.columns:
        df["opponent_team"] = df["opponent"]

    # Player name column varies; keep if present
    if "player_display_name" in df.columns:
        name_col = "player_display_name"
    elif "player_name" in df.columns:
        name_col = "player_name"
    else:
        name_col = None

    # 3) Ensure required numeric columns exist (create as zeros if missing)
    REQUIRED_NUMERIC_COLS = [
        "passing_yards",
        "passing_tds",
        "interceptions",
        "rushing_yards",
        "rushing_tds",
        "fumbles_lost",
        "sacks",
        "attempts",
        "completions",
        "games",
        "week",
        "season",
    ]
    for col in REQUIRED_NUMERIC_COLS:
        if col not in df.columns:
            df[col] = 0

    # 4) Coerce dtypes & fill NAs
    for col in REQUIRED_NUMERIC_COLS:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    # 5) Derived features
    df["total_yards"] = df.get("passing_yards", 0) + df.get("rushing_yards", 0)
    df["total_tds"] = df.get("passing_tds", 0) + df.get("rushing_tds", 0)
    df["turnovers"] = df.get("interceptions", 0) + df.get("fumbles_lost", 0)

    # 6) Deterministic dedupe on (season, week)
    df = (
        df.sort_values(["season", "week"])
        .drop_duplicates(subset=["season", "week"], keep="last")
    )

    # 7) Select safe Silver columns
    keep_cols = [
        c
        for c in [
            name_col,
            "player_id",
            "season",
            "week",
            "team",
            "opponent_team",
            "games",
            "attempts",
            "completions",
            "passing_yards",
            "passing_tds",
            "interceptions",
            "carries",
            "rushing_yards",
            "rushing_tds",
            "fumbles_lost",
            "sacks",
            "total_yards",
            "total_tds",
            "turnovers",
        ]
        if c is not None and c in df.columns
    ]
    df = df[keep_cols].reset_index(drop=True)

    # 8) Persist Silver parquet
    silver_fp = pathlib.Path(silver_dir) / "lamar_weekly_clean.parquet"
    df.to_parquet(silver_fp, index=False)

    # 9) Load into DuckDB (schema: silver)
    con = duckdb.connect(db_path)
    con.execute("CREATE SCHEMA IF NOT EXISTS silver")
    con.execute(
        "CREATE OR REPLACE TABLE silver.lamar_weekly AS SELECT * FROM read_parquet(?);",
        [str(silver_fp)],
    )
    print(f"[silver] wrote table silver.lamar_weekly with {len(df)} rows")


if __name__ == "__main__":
    main()
