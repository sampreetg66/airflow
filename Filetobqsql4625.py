from airflow import DAG
from airflow.models import Variable
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from airflow.utils.dates import days_ago

with DAG(
    dag_id='bq_query_with_env_variables',
    schedule_interval='@daily',
    start_date=days_ago(1),
    catchup=False,
    params={
        'project_id': Variable.get('project_id'),
        'dataset': Variable.get('bq_dataset')
    }
) as dag:

    run_bq_query = BigQueryInsertJobOperator(
        task_id='run_query',
        configuration={
            "query": {
                "query": "{% include 'sql/query.sql' %}",
                "useLegacySql": False
            }
        },
        location='US',
    )
