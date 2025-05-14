from airflow import models
from airflow.utils.dates import days_ago
from airflow.providers.google.cloud.operators.dataproc import (
    DataprocCreateClusterOperator,
    DataprocSubmitJobOperator,
    DataprocDeleteClusterOperator,
)
from airflow.utils.trigger_rule import TriggerRule

# Configurations
PROJECT_ID = 'your-project-id'
REGION = 'your-region'  # e.g., 'us-central1'
CLUSTER_NAME = 'example-pyspark-cluster'
BUCKET_NAME = 'your-bucket-name'
PYSPARK_URI = f'gs://{BUCKET_NAME}/pyspark-scripts/print_project.py'

# Cluster settings
CLUSTER_CONFIG = {
    "master_config": {
        "num_instances": 1,
        "machine_type_uri": "n1-standard-2",
    },
    "worker_config": {
        "num_instances": 2,
        "machine_type_uri": "n1-standard-2",
    },
}

# PySpark job definition
PYSPARK_JOB = {
    "reference": {"project_id": PROJECT_ID},
    "placement": {"cluster_name": CLUSTER_NAME},
    "pyspark_job": {
        "main_python_file_uri": PYSPARK_URI,
        "args": ["--project_id", PROJECT_ID],
    },
}

# Define the DAG
with models.DAG(
    dag_id="dataproc_pyspark_with_project_param",
    schedule_interval=None,
    start_date=days_ago(1),
    catchup=False,
    tags=["dataproc", "pyspark"],
) as dag:

    create_cluster = DataprocCreateClusterOperator(
        task_id="create_cluster",
        project_id=PROJECT_ID,
        cluster_config=CLUSTER_CONFIG,
        region=REGION,
        cluster_name=CLUSTER_NAME,
    )

    submit_pyspark_job = DataprocSubmitJobOperator(
        task_id="submit_pyspark_job",
        job=PYSPARK_JOB,
        region=REGION,
        project_id=PROJECT_ID,
    )

    delete_cluster = DataprocDeleteClusterOperator(
        task_id="delete_cluster",
        project_id=PROJECT_ID,
        region=REGION,
        cluster_name=CLUSTER_NAME,
        trigger_rule=TriggerRule.ALL_DONE,
    )

    create_cluster >> submit_pyspark_job >> delete_cluster
