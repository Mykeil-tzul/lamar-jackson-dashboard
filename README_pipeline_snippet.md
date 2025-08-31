# Lamar Weekly Pipeline (Bronze → Silver → Gold)

## Quickstart
```bash
pip install -r requirements.txt
cp .env.example .env  # then edit years/player if you want
mkdir -p data/bronze data/silver data/gold db
python scripts/bronze_ingest.py --years "2024"
python scripts/silver_transform.py
python scripts/gold_build.py
pytest -q
```

The dashboard can query `gold.fact_lamar_weekly` from `db/nfl.duckdb` or read `data/gold/fact_lamar_weekly.csv`.
