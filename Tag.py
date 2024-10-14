You're right; there isn't a specific `DataplexTagOperator` in Apache Airflow for tagging in Dataplex. Instead, you can use the `BigQueryInsertJobOperator` to run a custom SQL command for tagging or utilize the Google Cloud REST API through a Python operator.

Here’s how to do it with a combination of Airflow’s capabilities:

### Step 1: Create a Tag Template

Create a tag template in your Google Cloud Console. Use the following structure in YAML:

```yaml
name: "projects/YOUR_PROJECT_ID/locations/YOUR_LOCATION/tagTemplates/YOUR_TAG_TEMPLATE_ID"
displayName: "Your Tag Template"
fields:
  field1:
    displayName: "Field 1"
    type: "STRING"
  field2:
    displayName: "Field 2"
    type: "STRING"
```

### Step 2: Create an Airflow DAG

Here’s an example DAG that creates a tag and applies it to a BigQuery table using the Google Cloud Python client:

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from google.cloud import datacatalog_v1
from google.oauth2 import service_account
from airflow.utils.dates import days_ago

def create_and_tag_table():
    project_id = 'YOUR_PROJECT_ID'
    location = 'YOUR_LOCATION'
    table_id = 'YOUR_TABLE_ID'
    
    # Create a Data Catalog client
    client = datacatalog_v1.DataCatalogClient()

    # Define the tag
    tag_template_name = f'projects/{project_id}/locations/{location}/tagTemplates/YOUR_TAG_TEMPLATE_ID'
    tag = {
        "template": tag_template_name,
        "fields": {
            "field1": {"string_value": "value1"},
            "field2": {"string_value": "value2"},
        },
    }

    # Create the tag
    tag_response = client.create_tag(parent=f'projects/{project_id}/locations/{location}/tags', tag=tag)

    # Assign the tag to the BigQuery table
    table_resource = f'bigquery.googleapis.com/projects/{project_id}/datasets/YOUR_DATASET/tables/{table_id}'
    tag_id = tag_response.name

    # Create a Tag Attachment
    tag_attachment = {
        "tag": tag_id,
        "linked_resource": table_resource,
    }

    client.create_tag_template(tag_attachment)

default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1),
}

with DAG(
    dag_id='tag_bigquery_tables',
    default_args=default_args,
    schedule_interval='@once',
) as dag:

    tag_bigquery_table = PythonOperator(
        task_id='tag_bigquery_table',
        python_callable=create_and_tag_table,
    )

    tag_bigquery_table
```

### Step 3: Deploy and Execute the DAG

1. **Deploy the DAG**: Save this DAG in your Airflow `dags` directory.
2. **Run the DAG**: Trigger it from the Airflow UI or via the command line.

### Notes

- Make sure your environment has the `google-cloud-datacatalog` package installed.
- Update the `YOUR_*` placeholders with your actual values.
- Ensure the Airflow worker has access to the necessary Google Cloud services and permissions to create tags and access BigQuery resources. 

This approach effectively tags your BigQuery tables using Apache Airflow and the Google Cloud client libraries.
