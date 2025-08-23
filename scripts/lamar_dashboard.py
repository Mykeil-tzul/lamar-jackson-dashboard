import streamlit as st
import duckdb

# 🎯 Title
st.title("🏈 Lamar Jackson Weekly Performance Dashboard")

# 📥 Connect to DuckDB and run query
con = duckdb.connect()

query = """
SELECT
    season,
    week,
    SUM(passing_yards) AS total_pass_yards,
    SUM(pass_touchdown) AS total_pass_tds,
    SUM(rushing_yards) AS total_rush_yards,
    SUM(rush_touchdown) AS total_rush_tds
FROM 'data/lamar_jackson_weekly_stats.csv'
GROUP BY season, week
ORDER BY season, week
"""

try:
    # ✅ Execute and display result
    result_df = con.execute(query).fetchdf()
    st.success("✅ Data loaded successfully!")
    st.dataframe(result_df)  # Shows the full table

    # 🎛️ Season dropdown
    selected_season = st.selectbox("📅 Select Season", sorted(result_df["season"].unique()))
    filtered_df = result_df[result_df["season"] == selected_season]

    # 📅 Week dropdown
    selected_week = st.selectbox("📆 Select Week", sorted(filtered_df["week"].unique()))
    week_df = filtered_df[filtered_df["week"] == selected_week]

    # 🧾 Display selected week stats
    st.write("📊 Selected Week Stats", week_df)

except Exception as e:
    st.error(f"❌ Failed to load data: {e}")
