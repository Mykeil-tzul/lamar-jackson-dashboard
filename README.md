# Lamar Jackson Weekly Performance Dashboard

![CI](https://github.com/Mykeil-tzul/lamar-jackson-dashboard/actions/workflows/ci.yml/badge.svg)

This project presents an interactive dashboard that visualizes weekly NFL game performance data for quarterback Lamar Jackson. It simulates a sports analytics product that could be used by internal analysts at a company like FanDuel, PrizePicks, or a professional football organization to track player performance week-by-week.

## Project Overview

The dashboard is built using Streamlit and powered by DuckDB for fast, local querying. Users can select a season and filter by individual week to view detailed stats such as passing yards, rushing attempts, completion percentage, and total touchdowns.

This project demonstrates core skills in:

- Interactive data visualization with Python
- Local SQL-based querying using DuckDB
- Data wrangling with pandas
- Dashboard deployment using Streamlit
- Structuring modular Python projects

## Directory Structure

LAMAR_JACKSON_PIPELINE/
│
├── data/ # Raw or processed data files (if applicable)
├── db/ # DuckDB file with all weekly stats
├── dashboard/ # Reserved for dashboard HTML exports (optional)
├── scripts/ # Core logic scripts
│ ├── fetch_stats.py # Placeholder script to simulate pulling player stats
│ ├── query_duckdb.py # SQL query logic using DuckDB
│ └── lamar_dashboard.py # Streamlit app interface
│
├── .gitignore
├── README.md
├── requirements.txt


## Features

- Season dropdown and week selection
- Weekly game stat breakdown
- Local SQL queries using DuckDB
- Error handling for missing data
- Modularized script structure for scalability

## Tech Stack

- Python 3.10
- pandas
- Streamlit
- DuckDB

## Setup Instructions

Clone the repo:

```bash
git clone https://github.com/Mykeil-tzul/lamar-jackson-dashboard.git
cd lamar-jackson-dashboard

Install dependencies:

pip install -r requirements.txt

Run the dashboard locally:

streamlit run scripts/lamar_dashboard.py

Notes
This version uses static, simulated player data.

Future releases may include real-time player stats using the NFL API or scraped sources.

Can be expanded into a larger NFL data platform with team-level analysis, injury reports, and rolling stat summaries.

