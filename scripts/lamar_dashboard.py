# scripts/lamar_dashboard.py
import os
import sys
import subprocess
from datetime import datetime

import duckdb
import pandas as pd
import streamlit as st
import altair as alt


DB_PATH = os.getenv("DUCKDB_PATH", "db/nfl.duckdb")


# ---------- Data access ----------
@st.cache_data(ttl=300, show_spinner=False)
def load_gold() -> pd.DataFrame:
    """Load analytics-ready data from Gold."""
    con = duckdb.connect(DB_PATH)
    df = con.execute(
        """
        SELECT *
        FROM gold.fact_lamar_weekly
        ORDER BY season, week
        """
    ).df()
    return df


def pipeline_step(cmd: str) -> subprocess.CompletedProcess:
    """Run a pipeline python step and capture output."""
    return subprocess.run(
        [sys.executable, *cmd.split()],
        capture_output=True,
        text=True,
        cwd=os.getcwd(),
        env=os.environ.copy(),
    )


def refresh_pipeline(years: str = "2024", player: str = "Lamar Jackson"):
    """Run Bronze -> Silver -> Gold sequentially."""
    yield "Bronze ingest…"
    r1 = pipeline_step(f"scripts/bronze_ingest.py --years {years} --player '{player}'")
    yield r1.stdout or r1.stderr

    yield "Silver transform…"
    r2 = pipeline_step("scripts/silver_transform.py")
    yield r2.stdout or r2.stderr

    yield "Gold build…"
    r3 = pipeline_step("scripts/gold_build.py")
    yield r3.stdout or r3.stderr


# ---------- UI ----------
st.set_page_config(page_title="Lamar Jackson Weekly Performance", page_icon="🏈", layout="wide")
st.title("🏈 Lamar Jackson – Weekly Performance Dashboard")

with st.sidebar:
    st.subheader("Pipeline Controls")
    years = st.text_input("Years (comma-sep)", value=os.getenv("YEARS", "2024"))
    player = st.text_input("Player", value=os.getenv("PLAYER_NAME", "Lamar Jackson"))
    if st.button("🔄 Refresh Data (Bronze → Silver → Gold)", use_container_width=True):
        with st.spinner("Rebuilding pipeline…"):
            for msg in refresh_pipeline(years=years, player=player):
                st.write(msg)
        st.success("Gold rebuilt. Reloading data…")
        # clear cache and reload
        load_gold.clear()
        st.rerun()

# Load data
try:
    df = load_gold()
except Exception as e:
    st.error(
        f"Could not read Gold table from {DB_PATH}.\n\n"
        f"Run the pipeline first or check DUCKDB_PATH.\n\nError: {e}"
    )
    st.stop()

if df.empty:
    st.warning("Gold table is empty. Click 'Refresh Data' in the sidebar to build it.")
    st.stop()

# ---------- Filters ----------
left, right = st.columns([2, 1])
with left:
    seasons = sorted(df["season"].unique().tolist())
    season = st.selectbox("Season", seasons, index=len(seasons) - 1)
with right:
    show_rolling = st.checkbox("Show 3-game rolling averages", value=True)

sdf = df[df["season"] == season].copy()

# ---------- KPI cards ----------
def kpi_row():
    latest = sdf.sort_values("week").iloc[-1]
    avg3_yards = sdf["rolling3_total_yards"].iloc[-1] if "rolling3_total_yards" in sdf else None
    avg3_tds = sdf["rolling3_total_tds"].iloc[-1] if "rolling3_total_tds" in sdf else None
    avg3_to = sdf["rolling3_turnovers"].iloc[-1] if "rolling3_turnovers" in sdf else None

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Last Game – Total Yards", f"{int(latest.get('total_yards', 0))}")
    k2.metric("Last Game – TDs", f"{int(latest.get('total_tds', 0))}")
    k3.metric("Last Game – TOs", f"{int(latest.get('turnovers', 0))}")
    k4.metric("Rolling-3 Avg Yards", f"{avg3_yards:.1f}" if avg3_yards is not None else "—")
    k5.metric("Rolling-3 Avg TDs", f"{avg3_tds:.2f}" if avg3_tds is not None else "—")

kpi_row()

st.divider()

# ---------- Charts ----------
def line_chart(value_col: str, title: str):
    base = alt.Chart(sdf).encode(x=alt.X("week:O", title="Week"))
    line = base.mark_line(point=True).encode(y=alt.Y(f"{value_col}:Q", title=title), tooltip=list(sdf.columns))
    if show_rolling and f"rolling3_{value_col}" in sdf.columns:
        roll = base.mark_line(strokeDash=[4, 4]).encode(y=f"rolling3_{value_col}:Q")
        chart = alt.layer(line, roll).resolve_scale(y="independent")
    else:
        chart = line
    st.altair_chart(chart.properties(height=300), use_container_width=True)

c1, c2 = st.columns(2)
with c1:
    line_chart("total_yards", "Total Yards")
    line_chart("passing_yards", "Passing Yards")
with c2:
    line_chart("total_tds", "Total TDs")
    line_chart("rushing_yards", "Rushing Yards")

st.divider()

# ---------- Detail table ----------
with st.expander("See weekly detail"):
    show_cols = [c for c in [
        "season","week","team","opp","opponent_team","passing_yards","rushing_yards",
        "passing_tds","rushing_tds","interceptions","fumbles_lost","total_yards",
        "total_tds","turnovers","rolling3_total_yards","rolling3_total_tds","rolling3_turnovers"
    ] if c in sdf.columns]
    st.dataframe(sdf[show_cols].reset_index(drop=True), use_container_width=True)

# Footer
st.caption(
    f"Gold source: `{DB_PATH}` • Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
)
