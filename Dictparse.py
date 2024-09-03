Below is an example of an Airflow DAG that reads a dictionary from Airflow environment variables, processes files in specified folders, and inserts the data into BigQuery. The table name in BigQuery corresponds to the folder name.

### Example Dictionary in Environment Variables:
Let's say your environment variable `FOLDER_FILE_DICT` is a JSON string like this:

```json
{
  "folder1": ["file1.csv", "file2.csv"],
  "folder2": ["file3.csv", "file4.csv"]
}
```

### Airflow DAG Code:

```python
import json
import os
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from airflow.providers.google.cloud.hooks.gcs import GCSHook
from airflow.utils.dates import days_ago

# Function to process files and insert into BigQuery
def process_files(**kwargs):
    folder_file_dict = json.loads(os.environ.get('FOLDER_FILE_DICT'))
    gcs_hook = GCSHook(google_cloud_storage_conn_id='google_cloud_default')
    
    for folder, files in folder_file_dict.items():
        for file in files:
            # Assuming files are in GCS, and CSV format. Modify as needed.
            source_uri = f"gs://your-bucket-name/{folder}/{file}"
            destination_table = f"your-project.your_dataset.{folder}"

            # Load data from GCS into BigQuery
            insert_job = BigQueryInsertJobOperator(
                task_id=f'load_{folder}_{file}',
                configuration={
                    "load": {
                        "sourceUris": [source_uri],
                        "destinationTable": {
                            "projectId": "your-project",
                            "datasetId": "your_dataset",
                            "tableId": folder
                        },
                        "sourceFormat": "CSV",
                        "writeDisposition": "WRITE_APPEND"  # or 'WRITE_TRUNCATE' if you want to overwrite the table
                    }
                }
            )
            insert_job.execute(context=kwargs)

# Define the DAG
with DAG(
    dag_id='process_gcs_to_bigquery',
    start_date=days_ago(1),
    schedule_interval=None,
    catchup=False,
) as dag:

    process_files_task = PythonOperator(
        task_id='process_files',
        python_callable=process_files,
        provide_context=True
    )

    process_files_task
```

### Explanation:
1. **Environment Variable (`FOLDER_FILE_DICT`)**: This variable is expected to be a JSON string containing a dictionary where keys are folder names and values are lists of files.
   
2. **PythonOperator (`process_files`)**: This task reads the dictionary from the environment variable, processes each folder and file, and loads the data into BigQuery.

3. **BigQueryInsertJobOperator**: This operator is used within the `process_files` function to load data from GCS into BigQuery.

4. **Folder and File Processing**: The `process_files` function loops through each folder and its associated files, constructs the GCS URI, and loads the data into the corresponding BigQuery table.

5. **DAG Configuration**: The DAG is configured to start 1 day ago, with no schedule interval (`schedule_interval=None`), meaning it will only run when triggered manually.

### Prerequisites:
- Make sure you have the `google_cloud_default` connection configured in Airflow for accessing Google Cloud resources.
- Replace placeholders like `your-project`, `your_dataset`, `your-bucket-name` with your actual project details.

This setup should help you process the files in GCS and load them into BigQuery tables dynamically based on the dictionary defined in your environment variables.
