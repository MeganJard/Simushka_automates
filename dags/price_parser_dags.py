from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import os
import sys
import time

sys.path.append('/app')

from main import final_func, collect_and_move_to_gsheets
from wb_parser.main import wb_parser
from ozon_parser.main import ozon_parser
from gallery_parser.main import gallery_parser
from golden_apple_parser.main import ga_parser
from BT_parser.main import bt_parser
from analytics import collect_stats, init_analytics_db

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Инициализация аналитической БД
with DAG(
    'init_analytics',
    default_args=default_args,
    description='Initialize analytics database',
    schedule_interval='@once',
    start_date=datetime(2025, 4, 1),
    catchup=False,
) as dag_init:
    init_db = PythonOperator(
        task_id='init_analytics_db',
        python_callable=init_analytics_db,
    )

with DAG(
    'full_price_parsing',
    default_args=default_args,
    description='Full cycle of price parsing',
    schedule_interval='@daily',
    start_date=datetime(2025, 4, 1),
    catchup=False,
) as dag_full:

    clean_folder = BashOperator(
        task_id='clean_main_folder',
        bash_command='rm -rf /app/main_folder/*'
    )

    def parse_with_stats(platform, parser_func):
        start_time = time.time()
        errors = 0
        try:
            data_df = parser_func()
            if data_df is None:
                data_df = pd.DataFrame()
        except Exception as e:
            errors = 1
            data_df = pd.DataFrame()
        execution_time = time.time() - start_time
        collect_stats(platform, data_df, execution_time, errors)
        return data_df

    parse_wb = PythonOperator(
        task_id='parse_wildberries',
        python_callable=lambda: parse_with_stats('wildberries', wb_parser),
    )

    parse_ozon = PythonOperator(
        task_id='parse_ozon',
        python_callable=lambda: parse_with_stats('ozon', ozon_parser),
    )

    parse_gallery = PythonOperator(
        task_id='parse_gallery',
        python_callable=lambda: parse_with_stats('proficosmetics', gallery_parser),
    )

    parse_ga = PythonOperator(
        task_id='parse_golden_apple',
        python_callable=lambda: parse_with_stats('golden_apple', ga_parser),
    )

    parse_bt = PythonOperator(
        task_id='parse_bt',
        python_callable=lambda: parse_with_stats('ibt', lambda: bt_parser(only_checked=False)),
    )

    process_data = PythonOperator(
        task_id='process_parsed_data',
        python_callable=final_func,
    )

    upload_to_gsheets = PythonOperator(
        task_id='upload_to_gsheets',
        python_callable=collect_and_move_to_gsheets,
    )

    clean_folder >> [parse_wb, parse_ozon, parse_gallery, parse_ga, parse_bt] >> process_data >> upload_to_gsheets

with DAG(
    'bt_checked_parsing',
    default_args=default_args,
    description='Parse only checked BT products',
    schedule_interval='0 * * * *',
    start_date=datetime(2025, 4, 1),
    catchup=False,
) as dag_bt:
    parse_bt_checked = PythonOperator(
        task_id='parse_bt_checked',
        python_callable=lambda: parse_with_stats('ibt_checked', lambda: bt_parser(only_checked=True)),
    )

    process_data_bt = PythonOperator(
        task_id='process_bt_data',
        python_callable=final_func,
    )

    parse_bt_checked >> process_data_bt

with DAG(
    'gsheets_update',
    default_args=default_args,
    description='Update Google Sheets only',
    schedule_interval='*/30 * * * *',
    start_date=datetime(2025, 4, 1),
    catchup=False,
) as dag_gsheets:
    update_gsheets = PythonOperator(
        task_id='update_gsheets',
        python_callable=collect_and_move_to_gsheets,
    )
