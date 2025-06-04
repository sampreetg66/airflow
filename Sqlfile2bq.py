Yes, you **can absolutely pass a dictionary** from Airflow Variables instead of retrieving each variable one by one. This is a clean and scalable approach, especially when you have multiple parameters.

---

## ✅ Step-by-Step: Use a Dictionary from Airflow Variable

### 🔧 1. **Set a dictionary in Airflow Variables**

You can store a JSON-style dictionary in the UI or CLI:

#### Option A: Airflow UI

Go to **Admin → Variables**
Key: `bq_config`
Value:

```json
{
  "project_id": "your-gcp-project-id",
  "dataset": "your_dataset_name",
  "region": "us-west1"
}
```

#### Option B: Airflow CLI

```bash
airflow variables set bq_config '{"project_id": "your-gcp-project-id", "dataset": "your_dataset_name", "region": "us-west1"}'
```

---

### 🛠️ 2. **Update your DAG code**

Here’s how to update your `PythonOperator` to use the whole dict:

```python
from airflow import DAG
from airflow.models import Variable
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from airflow.providers.google.cloud.hooks.gcs import GCSHook

from google.cloud import bigquery
import json

def run_bq_query_from_gcs(**context):
    # Load config dict from Airflow Variables
    config = Variable.get("bq_config", deserialize_json=True)

    project_id = config["project_id"]
    dataset = config["dataset"]

    # Airflow macro value
    run_date = context['ds']  # e.g. '2025-06-04'

    # Read SQL from GCS
    gcs_hook = GCSHook()
    sql_bytes = gcs_hook.download(
        bucket_name="your-bucket-name",
        object_name="path/to/query.sql"
    )
    sql_template = sql_bytes.decode("utf-8")

    # Replace placeholders
    sql = (
        sql_template
        .replace("{{ project_id }}", project_id)
        .replace("{{ dataset }}", dataset)
        .replace("{{ ds }}", run_date)
    )

    # Run SQL using BigQuery client
    client = bigquery.Client(project=project_id)
    query_job = client.query(sql)
    results = query_job.result()

    # Optional: log output
    for row in results:
        print(dict(row))

with DAG(
    dag_id="bq_query_from_gcs_python_op",
    schedule_interval="@daily",
    start_date=days_ago(1),
    catchup=False,
) as dag:

    run_query_task = PythonOperator(
        task_id="run_bq_query",
        python_callable=run_bq_query_from_gcs,
        provide_context=True
    )
```

---

## ✅ Why This Is Better

| Benefit              | Explanation                              |
| -------------------- | ---------------------------------------- |
| Clean and scalable   | Avoids repetitive `Variable.get()` calls |
| Easy config changes  | Update in one place via UI or CLI        |
| Reusable across DAGs | Share `bq_config` in multiple workflows  |
| Supports nesting     | You can structure more complex configs   |

---

Let me know if you'd like to combine this with **Jinja2 template rendering** (instead of manual `.replace()`), which can also be clean for larger SQL templates.
