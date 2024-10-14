Below is a complete Apache Airflow DAG that uses both the YAML (for tag template creation) and JSON (for applying tags to BigQuery tables). This DAG has two tasks:

1. **Task 1: Create the Tag Template** using the YAML structure.
2. **Task 2: Apply the Tag to the BigQuery Table** using the values from the JSON configuration.

Before running this, make sure that:
- You have the `google-cloud-datacatalog` package installed (`pip install google-cloud-datacatalog`).
- The Airflow environment has access to Google Cloud with the appropriate permissions.

### Complete Airflow DAG

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from google.cloud import datacatalog_v1
from google.protobuf import field_mask_pb2
from airflow.utils.dates import days_ago
import json

# Path to your JSON and YAML file
JSON_FILE_PATH = '/path/to/your/json/file.json'
YAML_FILE_PATH = '/path/to/your/yaml/file.yaml'

# Define default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1),
}

# Function to load JSON configuration
def load_json_config():
    with open(JSON_FILE_PATH, 'r') as f:
        return json.load(f)

# Function to create a tag template from YAML structure
def create_tag_template():
    project_id = 'your_project_id'
    location = 'your_location'
    template_id = 'table_data_sensitivity'
    
    # YAML structure definition (could be parsed from YAML file using PyYAML)
    client = datacatalog_v1.DataCatalogClient()
    location_path = f"projects/{project_id}/locations/{location}"

    tag_template = datacatalog_v1.TagTemplate()
    tag_template.display_name = "Data Sensitivity Template for tables"

    # Define the has_PII field
    has_pii_field = datacatalog_v1.TagTemplateField()
    has_pii_field.display_name = "Table has PII fields"
    has_pii_field.type.primitive_type = datacatalog_v1.FieldType.PrimitiveType.BOOL
    tag_template.fields["has_PII"] = has_pii_field

    # Define the sensitive_type field
    sensitive_type_field = datacatalog_v1.TagTemplateField()
    sensitive_type_field.display_name = "Sensitive type"
    sensitive_type_field.type.enum_type.allowed_values.extend([
        datacatalog_v1.FieldType.EnumType.EnumValue(display_name="Public"),
        datacatalog_v1.FieldType.EnumType.EnumValue(display_name="Internal"),
        datacatalog_v1.FieldType.EnumType.EnumValue(display_name="Restricted"),
        datacatalog_v1.FieldType.EnumType.EnumValue(display_name="Secret"),
        datacatalog_v1.FieldType.EnumType.EnumValue(display_name="Top_Secret")
    ])
    tag_template.fields["sensitive_type"] = sensitive_type_field

    # Create the tag template
    try:
        response = client.create_tag_template(parent=location_path, tag_template_id=template_id, tag_template=tag_template)
        print(f"Tag template created: {response.name}")
    except Exception as e:
        print(f"Error creating tag template: {str(e)}")

# Function to apply tag to BigQuery table using values from the JSON configuration
def apply_tag_to_table():
    config = load_json_config()[0]  # Load the first entry of the JSON config
    
    project_id = config['projectid']
    dataset_name = config['datasetname']
    table_name = config['tablename']
    tag_template = config['tagtemplate']
    tag_fields = config['tag']

    # Create a Data Catalog client
    client = datacatalog_v1.DataCatalogClient()

    # Build the tag using fields from JSON
    tag = {
        "template": f"projects/{project_id}/locations/YOUR_LOCATION/tagTemplates/{tag_template}",
        "fields": {
            field["key"]: {"bool_value" if isinstance(field["value"], bool) else "string_value": field["value"]}
            for field in tag_fields
        },
    }

    # Create the tag and assign it to the BigQuery table
    table_resource = f'//bigquery.googleapis.com/projects/{project_id}/datasets/{dataset_name}/tables/{table_name}'
    
    try:
        tag_response = client.create_tag(parent=table_resource, tag=tag)
        print(f"Tag applied to table {table_name}: {tag_response.name}")
    except Exception as e:
        print(f"Error applying tag: {str(e)}")

# Define the DAG
with DAG(
    dag_id='tag_bq_tables_with_yaml_json',
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
) as dag:

    # Task 1: Create Tag Template
    create_template_task = PythonOperator(
        task_id='create_tag_template',
        python_callable=create_tag_template,
    )

    # Task 2: Apply Tag to BigQuery Table
    apply_tag_task = PythonOperator(
        task_id='apply_tag_to_table',
        python_callable=apply_tag_to_table,
    )

    # Set task dependencies
    create_template_task >> apply_tag_task
```

### How It Works:

1. **Task 1 (create_tag_template)**: 
   - Uses the YAML definition (which could be read from a YAML file) to create a tag template in Google Cloud Data Catalog.
   - The tag template is created with fields like `has_PII` and `sensitive_type`.

2. **Task 2 (apply_tag_to_table)**:
   - Reads the JSON file containing the tag values.
   - Applies the tag to the BigQuery table using the tag template created in the first task.

### Setup:
1. **YAML File**: The YAML content could be hard-coded in the script or loaded using `pyyaml`. In this example, it is hard-coded as part of the `create_tag_template` function.
2. **JSON File**: This should be a separate file defining the values and target BigQuery table as in your earlier example. Place the JSON file on your system and update the path (`JSON_FILE_PATH`).
   
3. **Permissions**: Ensure that your Airflow environment has access to the Google Cloud project, and your service account has the necessary permissions for:
   - Data Catalog (`roles/datacatalog.tagTemplateOwner`)
   - BigQuery resources.

4. **Google Cloud SDK**: The `google-cloud-datacatalog` package must be installed on the Airflow worker nodes for both tasks to function properly.

### Running the DAG:
1. Deploy this DAG into your Airflow environment.
2. Trigger the DAG via the Airflow UI or CLI.
3. The DAG will first create the tag template, and then apply the tags to the specified BigQuery table.

This solution leverages both YAML and JSON for a complete tagging process in BigQuery using Apache Airflow.
