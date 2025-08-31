from datetime import datetime
import os
from airflow import DAG
from airflow.operators.python import PythonOperator

# Each task calls the corresponding module's main() to keep it simple
def run_bronze():
    from scripts.bronze_ingest import main as bronze_main
    bronze_main()

def run_silver():
    from scripts.silver_transform import main as silver_main
    silver_main()

def run_gold():
    from scripts.gold_build import main as gold_main
    gold_main()

def run_validate():
    from scripts.validate_data import main as validate_main
    validate_main()

default_args = {
    "owner": "mykeil",
    "retries": 1,
}

with DAG(
    dag_id="lamar_weekly_pipeline",
    start_date=datetime(2024, 1, 1),
    schedule="@weekly",
    catchup=False,
    default_args=default_args,
    tags=["lamar","nfl","duckdb"],
) as dag:

    bronze = PythonOperator(task_id="bronze_ingest", python_callable=run_bronze)
    silver = PythonOperator(task_id="silver_transform", python_callable=run_silver)
    gold = PythonOperator(task_id="gold_build", python_callable=run_gold)
    validate = PythonOperator(task_id="validate_gold", python_callable=run_validate)

    bronze >> silver >> gold >> validate
