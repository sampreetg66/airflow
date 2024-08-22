Here’s the updated DAG code where files from the `sam` folder are loaded into the `sam` table, and files from the `mam` folder are loaded into the `mam` table in BigQuery:

```python
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
from airflow.providers.google.cloud.transfers.gcs_to_gcs import GCSToGCSOperator
from airflow.utils.dates import days_ago
from google.cloud import storage

import os

BUCKET_NAME = 'your-bucket-name'
SAM_FOLDER = 'sam/'
MAM_FOLDER = 'mam/'
ARCHIVE_FOLDER = 'archive/'

def list_gcs_files(bucket_name, folder_prefix):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=folder_prefix)
    
    return [blob.name for blob in blobs if not blob.name.endswith('/')]

def combine_file_lists(**context):
    sam_files = list_gcs_files(BUCKET_NAME, SAM_FOLDER)
    mam_files = list_gcs_files(BUCKET_NAME, MAM_FOLDER)
    
    context['ti'].xcom_push(key='sam_files', value=sam_files)
    context['ti'].xcom_push(key='mam_files', value=mam_files)
    
    return sam_files, mam_files

def archive_files(**context):
    sam_files = context['ti'].xcom_pull(key='sam_files')
    mam_files = context['ti'].xcom_pull(key='mam_files')
    
    for file_name in sam_files + mam_files:
        move_file = GCSToGCSOperator(
            task_id=f'move_{file_name}',
            source_bucket=BUCKET_NAME,
            source_object=file_name,
            destination_bucket=BUCKET_NAME,
            destination_object=ARCHIVE_FOLDER + os.path.basename(file_name),
        )
        move_file.execute(context)

default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1),
    'retries': 1,
}

with DAG(
    'gcs_to_bigquery_and_archive',
    default_args=default_args,
    schedule_interval=None,
) as dag:
    
    # Task 1: Combine file lists from both folders
    combine_task = PythonOperator(
        task_id='combine_file_lists',
        python_callable=combine_file_lists,
        provide_context=True,
    )

    # Task 2a: Load files from SAM folder into SAM table
    sam_files = combine_task.output['sam_files']
    load_sam_to_bq_tasks = []
    
    for file_name in sam_files:
        load_to_bq_task = GCSToBigQueryOperator(
            task_id=f'load_{os.path.basename(file_name)}_to_sam_table',
            bucket=BUCKET_NAME,
            source_objects=[file_name],
            destination_project_dataset_table='your-project.your_dataset.sam_table',
            schema_fields=None,  # Define your schema here if needed
            write_disposition='WRITE_APPEND',
        )
        load_sam_to_bq_tasks.append(load_to_bq_task)

    # Task 2b: Load files from MAM folder into MAM table
    mam_files = combine_task.output['mam_files']
    load_mam_to_bq_tasks = []
    
    for file_name in mam_files:
        load_to_bq_task = GCSToBigQueryOperator(
            task_id=f'load_{os.path.basename(file_name)}_to_mam_table',
            bucket=BUCKET_NAME,
            source_objects=[file_name],
            destination_project_dataset_table='your-project.your_dataset.mam_table',
            schema_fields=None,  # Define your schema here if needed
            write_disposition='WRITE_APPEND',
        )
        load_mam_to_bq_tasks.append(load_to_bq_task)
    
    # Task 3: Archive the files after loading to BigQuery
    archive_task = PythonOperator(
        task_id='archive_files',
        python_callable=archive_files,
        provide_context=True,
    )

    # Setting task dependencies
    combine_task >> load_sam_to_bq_tasks >> archive_task
    combine_task >> load_mam_to_bq_tasks >> archive_task
```

### Updates:
1. **`combine_file_lists`**: Now pushes two lists to XCom, one for `sam_files` and another for `mam_files`.

2. **Task 2a**: Files from the `sam` folder are loaded into the `sam_table`.

3. **Task 2b**: Files from the `mam` folder are loaded into the `mam_table`.

4. **Task 3 (Archival)**: Archives all the processed files from both folders.

### Notes:
- Ensure that `your-project.your_dataset.sam_table` and `your-project.your_dataset.mam_table` are replaced with the actual project and table names.
- Adjust the `schema_fields` parameter if your BigQuery tables require a specific schema.
