import duckdb

# ✅ Connect to DuckDB
con = duckdb.connect()

# ✅ Corrected SQL query with real column names
query = """
SELECT
    season,
    week,
    SUM("pass") AS total_pass_yards,
    SUM(pass_touchdown) AS total_pass_tds,
    SUM(rush) AS total_rush_yards,
    SUM(rush_touchdown) AS total_rush_tds
FROM 'data/lamar_jackson_weekly_stats.csv'
GROUP BY season, week
ORDER BY season, week
"""

# ✅ Run query
result_df = con.execute(query).fetchdf()

# ✅ Preview output
print("✅ Preview of weekly stats:")
print(result_df.head())
