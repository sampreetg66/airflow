To create DAGs dynamically based on the provided code template, we can utilize a configuration-based approach. By storing DAG configuration details in a JSON file, you can use a loop to create multiple DAGs programmatically.

Here’s how you can modify your existing DAG to dynamically generate DAGs from a configuration file:

1. **Create a Configuration File** (e.g., `dags_config.json`):
    ```json
    [
        {
            "dag_id": "sftp_to_bq_processing_1",
            "schedule": "@daily",
            "sftp_conn_id": "your_sftp_connection_1",
            "bq_raw_table": "your_bq_raw_table_1",
            "bq_final_table": "your_bq_final_table_1",
            "gcs_bucket": "your_gcs_bucket_1",
            "teams_webhook_url": "your_teams_webhook_url_1",
            "email_recipients": ["email1@example.com"],
            "gcs_yaml_check_folder": "yaml_check_folder_1"
        },
        {
            "dag_id": "sftp_to_bq_processing_2",
            "schedule": "@hourly",
            "sftp_conn_id": "your_sftp_connection_2",
            "bq_raw_table": "your_bq_raw_table_2",
            "bq_final_table": "your_bq_final_table_2",
            "gcs_bucket": "your_gcs_bucket_2",
            "teams_webhook_url": "your_teams_webhook_url_2",
            "email_recipients": ["email2@example.com"],
            "gcs_yaml_check_folder": "yaml_check_folder_2"
        }
    ]
    ```

2. **Python Code to Generate DAGs Dynamically**:
    In your Airflow DAG folder, you can create a Python file (e.g., `dynamic_dags.py`) to load the configuration and dynamically create DAGs.

    ```python
    import json
    import os
    from airflow import DAG
    from airflow.operators.python_operator import PythonOperator
    from airflow.operators.sensors import SFTPSensor
    from airflow.operators.bigquery_operator import BigQueryExecuteQueryOperator
    from airflow.utils.dates import days_ago
    from airflow.utils.task_group import TaskGroup
    from google.cloud import bigquery, storage, secretmanager
    import requests
    from airflow.utils.email import send_email

    # Load the DAG configuration file
    config_file_path = os.path.join(os.path.dirname(__file__), 'dags_config.json')

    with open(config_file_path) as config_file:
        dags_config = json.load(config_file)

    def get_secret(secret_name):
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/<your_project_id>/secrets/{secret_name}/versions/latest"
        response = client.access_secret_version(name=name)
        return response.payload.data.decode("UTF-8")

    # Helper function for dynamic DAG creation
    def create_dag(dag_config):

        dag_id = dag_config['dag_id']
        default_args = {
            'owner': 'airflow',
            'start_date': days_ago(1),
            'retries': 1,
            'on_failure_callback': notify_failure,
        }

        # Define the DAG
        with DAG(
            dag_id=dag_id,
            default_args=default_args,
            schedule_interval=dag_config['schedule'],
            catchup=False
        ) as dag:

            # Helper functions for DAG tasks
            def download_from_sftp(**kwargs):
                pass  # Implementation here

            def upload_to_gcs_landing(**kwargs):
                pass  # Implementation here

            def data_check(**kwargs):
                pass  # Implementation here

            def load_to_bq_raw(**kwargs):
                pass  # Implementation here

            def validate_data_with_dataplex(**kwargs):
                pass  # Implementation here

            def notify_failure(context):
                pass  # Implementation here

            # Define the tasks using the configuration from the JSON file
            sftp_sensor = SFTPSensor(
                task_id='sftp_file_sensor',
                sftp_conn_id=dag_config['sftp_conn_id'],
                path='/path/to/file',
                mode='poke',
                timeout=600,
                poke_interval=60
            )

            download_task = PythonOperator(
                task_id='download_file',
                python_callable=download_from_sftp
            )

            upload_to_gcs_landing_task = PythonOperator(
                task_id='upload_to_gcs_landing',
                python_callable=upload_to_gcs_landing
            )

            data_check_task = PythonOperator(
                task_id='data_check',
                python_callable=data_check
            )

            load_raw_bq_task = PythonOperator(
                task_id='load_to_bq_raw',
                python_callable=load_to_bq_raw
            )

            validate_data_task = PythonOperator(
                task_id='validate_data_with_dataplex',
                python_callable=validate_data_with_dataplex,
                op_kwargs={'yaml_path': dag_config['gcs_yaml_check_folder']}
            )

            # Set up task dependencies
            sftp_sensor >> download_task >> upload_to_gcs_landing_task >> data_check_task >> load_raw_bq_task >> validate_data_task

        return dag

    # Generate a DAG for each configuration in the JSON file
    for config in dags_config:
        globals()[config['dag_id']] = create_dag(config)
    ```

### Explanation:
- **Configuration File**: Holds all the necessary DAG settings for each DAG (like `dag_id`, `schedule`, `bq_raw_table`, `gcs_bucket`, etc.).
- **Dynamic DAG Creation**: The `create_dag` function is called for each configuration in the JSON file, generating a unique DAG based on that configuration.
- **Task Definitions**: You can expand each of the task functions (`download_from_sftp`, `upload_to_gcs_landing`, etc.) as per your business logic.
- **Task Dependencies**: The task dependencies are established based on the configuration and DAG structure.

By following this approach, you can easily maintain multiple DAGs dynamically and update them simply by modifying the JSON configuration file.
