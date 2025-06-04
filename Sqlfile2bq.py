Here's your updated Airflow DAG with:

✅ A **TaskGroup** called `preprocessor`
✅ A `start` dummy task before the group
✅ An `end` dummy task after the group
✅ Both `prepare_sql_task` and `run_bq_job` moved inside the `preprocessor` group

---

### ✅ Full DAG Code

```python
from airflow import DAG
from airflow.models import Variable
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.utils.dates import days_ago
from airflow.utils.task_group import TaskGroup
from airflow.providers.google.cloud.hooks.gcs import GCSHook
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator

def prepare_query(**context):
    config = Variable.get("bq_config", deserialize_json=True)
    project_id = config["project_id"]
    dataset = config["dataset"]
    run_date = context['ds']

    gcs_hook = GCSHook()
    sql_bytes = gcs_hook.download(
        bucket_name="your-bucket-name",
        object_name="path/to/query.sql"
    )
    sql_template = sql_bytes.decode("utf-8")

    sql = (
        sql_template
        .replace("{{ project_id }}", project_id)
        .replace("{{ dataset }}", dataset)
        .replace("{{ ds }}", run_date)
    )

    context['ti'].xcom_push(key="rendered_sql", value=sql)
    context['ti'].xcom_push(key="project_id", value=project_id)

with DAG(
    dag_id="bq_query_with_task_group",
    schedule_interval="@daily",
    start_date=days_ago(1),
    catchup=False,
) as dag:

    start = EmptyOperator(task_id="start")

    with TaskGroup(group_id="preprocessor") as preprocessor:
        prepare_sql_task = PythonOperator(
            task_id="prepare_sql",
            python_callable=prepare_query,
        )

        run_bq_job = BigQueryInsertJobOperator(
            task_id="run_bq_sql_job",
            configuration={
                "query": {
                    "query": "{{ ti.xcom_pull(task_ids='preprocessor.prepare_sql', key='rendered_sql') }}",
                    "useLegacySql": False,
                }
            },
            project_id="{{ ti.xcom_pull(task_ids='preprocessor.prepare_sql', key='project_id') }}",
            location="US",  # Optional: use Variable or config if dynamic
        )

        prepare_sql_task >> run_bq_job

    end = EmptyOperator(task_id="end")

    start >> preprocessor >> end
```

---

Let me know if you’d like to:

* Add more SQL files to process in the same group
* Dynamically generate tasks based on a list
* Use `params` with native Jinja templating instead of `.replace()`
