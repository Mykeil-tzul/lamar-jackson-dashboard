import os
import pandas as pd
from nfl_data_py import import_pbp_data

def get_lamar_stats():
    print("📥 Loading play-by-play data from 2018–2023...")
    df = import_pbp_data([2018, 2019, 2020, 2021, 2022, 2023])

    print("🔍 Previewing columns...")
    print(df.columns.tolist())  # <-- Optional: Remove after confirming

    # ✅ Filter for Lamar Jackson passing plays
    lamar_df = df[df['passer'] == 'L.Jackson']

    print(f"✅ Found {len(lamar_df)} Lamar Jackson passing plays")

    # ✅ Group by season + week and aggregate key stats
    weekly = lamar_df.groupby(['season', 'week'], as_index=False).agg({
        'passing_yards': 'sum',
        'pass_touchdown': 'sum',
        'rushing_yards': 'sum',
        'rush_touchdown': 'sum'
    })

    # ✅ Save to CSV
    os.makedirs('data', exist_ok=True)
    file_path = 'data/lamar_jackson_weekly_stats.csv'
    weekly.to_csv(file_path, index=False)

    print(f"✅ Stats saved to {file_path}")

if __name__ == "__main__":
    get_lamar_stats()
