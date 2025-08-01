from datetime import datetime, timedelta
from airflow import DAG
#from airflow.providers.standard.operators.python import PythonOperator
from airflow.operators.python import PythonOperator
import logging
import os
import sys

module_path = os.path.abspath("/Users/tienle/Documents/Coding/end-to-end-ETL/end-to-end/src")
sys.path.append(module_path)

from consumer import mongo_to_postgres
from reporting import generate_daily_report

logger = logging.getLogger('dag_logger')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

default_args = {
    "owner": "airflow",
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "start_date": datetime(2025,4,14),
    "catchup": False,
}

dag = DAG(
    dag_id="stocks_dag",
    default_args=default_args,
    schedule='0 9-16 * * 1-5',
    #schedule=None,
    start_date=datetime.now(),
    max_active_runs=1
)

def start_job():
    logging.info("Starting the pipeline.")

def fetch_data_from_mongo():
    try:
        logger.info("Fetching data from MongoDB")
        mongo_to_postgres()
        logger.info("The data has been inserted into Postgresql")

    except Exception as e:
        logger.error(f"An error occured while fetching data {e}")

def daily_report():
    generate_daily_report()
    logger.info("The daily report prepared and saved into CSV files")

def end_job():
    logger.info("All process completed.")


start_task = PythonOperator(
    task_id='start_job',
    python_callable=start_job,
    dag=dag
)

fetching_data_task = PythonOperator(
    task_id='fetch_data_job',
    python_callable=fetch_data_from_mongo,
    dag=dag
)

daily_report_task = PythonOperator(
    task_id='daily_report_job',
    python_callable= daily_report,
    dag = dag
)

end_task = PythonOperator(
    task_id= 'end_job',
    python_callable=end_job,
    dag=dag
)

start_task >> fetching_data_task >> daily_report_task >> end_task