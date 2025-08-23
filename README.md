# Lamar Jackson Weekly Performance Dashboard

![CI](https://github.com/Mykeil-tzul/lamar-jackson-dashboard/actions/workflows/ci.yml/badge.svg)

A real-time data pipeline built using Python, DuckDB, and Streamlit to track and visualize Lamar Jackson’s game-by-game stats. This project includes automated testing and CI/CD using GitHub Actions.

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

## Challenges Faced

1. Pandas Version Conflicts in GitHub Actions
While setting up continuous integration with GitHub Actions, I encountered dependency conflicts between fastparquet, nfl-data-py, and pandas.

fastparquet required pandas >=1.5.0

nfl-data-py pinned pandas <2.0

My original code used pandas==2.0.0, which broke the build

✅ Fix: Aligned all packages to use pandas==1.5.3, the latest version compatible with both tools, which allowed CI to pass.

2. CI Workflow Setup for Python Projects
Configuring the .github/workflows/ci.yml file required trial-and-error to:

Properly install dependencies

Cache Python packages

Ensure requirements.txt worked in the GitHub Actions runner environment

✅ Fix: Tweaked the workflow and ensured consistent local vs CI environments. Added clear version pins in requirements.txt to avoid future conflicts.

3. Real-Time Data Reliability
The nfl_data_py package pulls live stats from NFL's Next Gen Stats, which occasionally failed during CI testing due to rate limits or unstable endpoints.

✅ Fix: Wrapped critical API calls with error handling to prevent crashes during CI runs and dashboard refresh.



## Setup Instructions

Clone the repo:

```bash
git clone https://github.com/Mykeil-tzul/lamar-jackson-dashboard.git
cd lamar-jackson-dashboard

Install dependencies:

pip install -r requirements.txt

Run the dashboard locally:

streamlit run scripts/lamar_dashboard.py

----------

Notes
This version uses static, simulated player data.

Future releases may include real-time player stats using the NFL API or scraped sources.

Can be expanded into a larger NFL data platform with team-level analysis, injury reports, and rolling stat summaries.

