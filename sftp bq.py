To create a dynamic set of tasks based on the unique joining years extracted from the data file, you'll need to perform the following steps:

1. **Download the file from SFTP.**
2. **Load the file into a raw BigQuery table.**
3. **Read the unique joining years from the raw table.**
4. **Create dynamic tasks based on the unique joining years.**

Here’s how you can modify the Airflow DAG to achieve this:

### DAG Code

```python
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.sensors import SFTPSensor
from airflow.operators.bigquery_operator import BigQueryExecuteQueryOperator
from airflow.utils.dates import days_ago
from airflow.utils.task_group import TaskGroup
from airflow.operators.dummy_operator import DummyOperator
from google.cloud import bigquery
import pandas as pd
import paramiko
import os

# Define constants
SFTP_CONN_ID = 'your_sftp_connection'
BQ_RAW_TABLE = 'your_project.your_dataset.raw_table'
BQ_FINAL_TABLE = 'your_project.your_dataset.final_table'
SFTP_PATH = '/path/to/employee_data.csv'
LOCAL_FILE_PATH = '/tmp/employee_data.csv'

# Helper functions
def download_from_sftp(**kwargs):
    sftp_client = kwargs['sftp_client']
    sftp_client.get(SFTP_PATH, LOCAL_FILE_PATH)

def load_to_bq_raw(**kwargs):
    client = bigquery.Client()
    df = pd.read_csv(LOCAL_FILE_PATH)
    df.to_gbq(destination_table=BQ_RAW_TABLE, if_exists='append')

def get_unique_joining_years(**kwargs):
    client = bigquery.Client()
    query = f"""
        SELECT DISTINCT EXTRACT(YEAR FROM joining_date) AS joining_year
        FROM `{BQ_RAW_TABLE}`
    """
    df = client.query(query).to_dataframe()
    return df['joining_year'].tolist()

def create_processing_task(year):
    return BigQueryExecuteQueryOperator(
        task_id=f'process_data_{year}',
        sql=f"""
            INSERT INTO `{BQ_FINAL_TABLE}` (employee_id, employee_name, joining_year)
            SELECT employee_id, employee_name, EXTRACT(YEAR FROM joining_date) AS joining_year
            FROM `{BQ_RAW_TABLE}`
            WHERE EXTRACT(YEAR FROM joining_date) = {year}
        """,
        use_legacy_sql=False
    )

# Define the DAG
with DAG(
    'sftp_to_bq_processing_dynamic',
    default_args={
        'owner': 'airflow',
        'start_date': days_ago(1),
        'retries': 1
    },
    schedule_interval=None,
    catchup=False
) as dag:

    # Task to sense the presence of the file in SFTP
    sftp_sensor = SFTPSensor(
        task_id='sftp_file_sensor',
        sftp_conn_id=SFTP_CONN_ID,
        path=SFTP_PATH,
        mode='poke',
        timeout=600,
        poke_interval=60
    )

    # Task to download file from SFTP
    download_task = PythonOperator(
        task_id='download_file',
        python_callable=download_from_sftp,
        op_kwargs={'sftp_client': paramiko.SFTPClient.from_transport(paramiko.Transport(('hostname', port)))}
    )

    # Task to load data into raw BigQuery table
    load_raw_bq_task = PythonOperator(
        task_id='load_to_bq_raw',
        python_callable=load_to_bq_raw
    )

    # Task to get unique joining years from BigQuery
    get_years_task = PythonOperator(
        task_id='get_unique_joining_years',
        python_callable=get_unique_joining_years,
        provide_context=True
    )

    # Dynamically generate tasks based on unique joining years
    def generate_processing_tasks(**kwargs):
        unique_years = kwargs['task_instance'].xcom_pull(task_ids='get_unique_joining_years')
        task_group = kwargs['task_group']
        for year in unique_years:
            task = create_processing_task(year)
            task_group.add(task)

    with TaskGroup('process_by_year', group_id='process_by_year') as process_by_year_group:
        generate_tasks = PythonOperator(
            task_id='generate_processing_tasks',
            python_callable=generate_processing_tasks,
            provide_context=True,
            op_kwargs={'task_group': process_by_year_group}
        )

    # Set up task dependencies
    sftp_sensor >> download_task >> load_raw_bq_task >> get_years_task >> generate_tasks
```

### Explanation:

1. **SFTP Sensor**: Monitors the presence of the file on the SFTP server.
2. **Download File**: Downloads the file from SFTP to a local path.
3. **Load to Raw BigQuery Table**: Loads the downloaded file into the BigQuery raw table.
4. **Get Unique Joining Years**: Queries the raw table to get a list of unique joining years.
5. **Generate Processing Tasks**: Dynamically creates and adds BigQuery tasks based on the unique joining years.

### Notes:

- Replace placeholders like `'your_sftp_connection'`, `'/path/to/employee_data.csv'`, and `'your_project.your_dataset.*'` with actual values.
- Ensure that the necessary connections and credentials (SFTP and BigQuery) are properly set up in Airflow.
- This example assumes the presence of Airflow 2.x and uses the Google Cloud BigQuery and SFTP hooks. Adjust paths and connection details as needed for your environment.

This approach dynamically adjusts the number of tasks based on the data content, allowing the DAG to scale according to the unique years found in your dataset.