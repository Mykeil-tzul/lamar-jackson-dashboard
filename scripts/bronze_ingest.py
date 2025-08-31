import os
import argparse
import pathlib
from dotenv import load_dotenv
import pandas as pd
import nfl_data_py as nfl
from typing import List

def ensure_dirs(path: str):
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)

def parse_years(s: str) -> List[int]:
    return [int(x.strip()) for x in s.split(",") if x.strip()]

def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="Ingest weekly NFL data into Bronze layer (parquet partitions).")
    parser.add_argument("--player", default=os.getenv("PLAYER_NAME", "Lamar Jackson"))
    parser.add_argument("--years", default=os.getenv("YEARS", "2024"))
    parser.add_argument("--bronze_dir", default=os.getenv("BRONZE_DIR", "data/bronze"))
    args = parser.parse_args()

    years = parse_years(args.years)
    ensure_dirs(args.bronze_dir)

    print(f"[bronze] downloading weekly data for years={years}")
    weekly = nfl.import_weekly_data(years=years)  # pulls from public nflfastR data
    # Standardize player name column if needed
    name_col = "player_display_name" if "player_display_name" in weekly.columns else ("player_name" if "player_name" in weekly.columns else None)
    if name_col is None:
        raise RuntimeError("Could not find player name column in weekly dataset.")
    player_df = weekly[weekly[name_col] == args.player].copy()

    # Minimal columns to keep; add more as you wish
    keep = [
        name_col, "player_id", "season", "week", "team", "opponent_team",
        "games", "attempts", "completions", "passing_yards", "passing_tds", "interceptions",
        "carries", "rushing_yards", "rushing_tds", "fumbles_lost", "sacks"
    ]
    existing = [c for c in keep if c in player_df.columns]
    player_df = player_df[existing].reset_index(drop=True)

    # Write partitioned parquet by season/week
    for (season, week), grp in player_df.groupby(["season", "week"]):
        out_dir = pathlib.Path(args.bronze_dir) / f"season={season}" / f"week={int(week)}"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_fp = out_dir / "lamar_weekly.parquet"
        grp.to_parquet(out_fp, index=False)
        print(f"[bronze] wrote {out_fp} ({len(grp)} rows)")

    print("[bronze] done.")

if __name__ == "__main__":
    main()
