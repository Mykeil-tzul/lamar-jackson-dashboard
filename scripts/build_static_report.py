# scripts/build_static_report.py
import os
import pathlib
from datetime import datetime

import duckdb
import pandas as pd
import altair as alt

DB_PATH = os.getenv("DUCKDB_PATH", "db/nfl.duckdb")
OUT_DIR = pathlib.Path("docs")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def load_gold(db_path: str) -> pd.DataFrame:
    con = duckdb.connect(db_path)
    return con.execute("""
        SELECT *
        FROM gold.fact_lamar_weekly
        ORDER BY season, week
    """).df()

def build_charts(df: pd.DataFrame) -> str:
    season = int(df["season"].max())
    sdf = df[df["season"] == season].copy()

    # KPI strip
    latest = sdf.sort_values("week").iloc[-1]
    kpi_html = f"""
    <h1>🏈 Lamar Jackson – Weekly Report ({season})</h1>
    <p><b>Last game:</b>
       <span>Total Yards: {int(latest.get('total_yards', 0))}</span> •
       <span>TDs: {int(latest.get('total_tds', 0))}</span> •
       <span>TOs: {int(latest.get('turnovers', 0))}</span>
    </p>
    """

    base = alt.Chart(sdf).encode(x=alt.X("week:O", title="Week"))

    def line(y, title):
        main = base.mark_line(point=True).encode(
            y=alt.Y(f"{y}:Q", title=title),
            tooltip=list(sdf.columns),
        )
        r = f"rolling3_{y}"
        if r in sdf.columns:
            roll = base.mark_line(strokeDash=[4, 4]).encode(y=f"{r}:Q")
            main = alt.layer(main, roll)
        return main.properties(height=260)

    chart = alt.vconcat(
        (line("total_yards", "Total Yards") | line("total_tds", "Total TDs")),
        (line("passing_yards", "Passing Yards") | line("rushing_yards", "Rushing Yards")),
    ).resolve_scale(y="independent").properties(
        title=f"Updated {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    html = (
        "<html><head><meta charset='utf-8'>"
        "<title>Lamar Report</title>"
        "<style>body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Inter,Arial;margin:24px} "
        "h1{margin:0 0 8px} p{margin:4px 0 16px;color:#444}</style>"
        "</head><body>"
        f"{kpi_html}"
        f"{chart.to_html()}</body></html>"
    )
    return html

def main():
    df = load_gold(DB_PATH)
    if df.empty:
        raise SystemExit("Gold is empty. Run the pipeline first (bronze→silver→gold).")

    html = build_charts(df)
    out_path = OUT_DIR / "index.html"
    out_path.write_text(html, encoding="utf-8")
    print(f"[report] wrote {out_path}")

if __name__ == "__main__":
    main()
