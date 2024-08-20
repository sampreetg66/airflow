Sure! Below are the steps to create a Dataplex Data Quality Task for a BigQuery table using Terraform, followed by the corresponding Airflow code to trigger this task.

### 1. **Create Dataplex Task Using Terraform**

First, ensure that you have Terraform set up and configured to manage your Google Cloud resources.

Here's the Terraform code to create a Dataplex Data Quality Task named `dp123` for a BigQuery table named `emp_table123`.

#### **Terraform Configuration**

```hcl
# Variables
variable "project" {
  description = "The project ID where resources will be created"
  type        = string
}

variable "location" {
  description = "The location (region) of Dataplex"
  type        = string
}

variable "lake_id" {
  description = "The ID of the Dataplex lake"
  type        = string
}

variable "dataplex_zone_id" {
  description = "The ID of the Dataplex zone"
  type        = string
}

variable "dataplex_task_id" {
  description = "The ID of the Dataplex task"
  type        = string
  default     = "dp123"
}

variable "bigquery_table" {
  description = "The BigQuery table to run the data quality checks on"
  type        = string
  default     = "emp_table123"
}

# Google provider
provider "google" {
  project = var.project
  region  = var.location
}

# Create Dataplex Task
resource "google_dataplex_task" "dp123" {
  project   = var.project
  location  = var.location
  lake      = var.lake_id
  dataplex_zone_id = var.dataplex_zone_id
  dataplex_task_id = var.dataplex_task_id

  data_quality_spec {
    rules {
      non_null_expectation {
        column = "employee_id"
      }
    }
    rules {
      non_null_expectation {
        column = "employee_name"
      }
    }
    rules {
      non_null_expectation {
        column = "department"
      }
    }
    rules {
      sql_expression {
        sql_expression = "LENGTH(employee_id) = 8"
        column = "employee_id"
      }
    }
  }

  execution_spec {
    args = {
      "bigquery_table" = var.bigquery_table
    }
  }
}
```

#### **Steps to Deploy with Terraform**

1. Save the above Terraform code in a file named `main.tf`.
2. Replace the placeholder values in the variables with your project, location, lake ID, zone ID, and other necessary details.
3. Initialize Terraform:
   ```bash
   terraform init
   ```
4. Review the Terraform plan:
   ```bash
   terraform plan
   ```
5. Apply the configuration to create the Dataplex task:
   ```bash
   terraform apply
   ```

This will create a Dataplex task named `dp123` that will run data quality checks on the `emp_table123` BigQuery table.

### 2. **Airflow DAG to Trigger Dataplex Task**

Now, here is an Airflow DAG that triggers the Dataplex task `dp123` created above.

#### **Airflow DAG Code**

```python
from airflow import DAG
from airflow.providers.google.cloud.operators.dataplex import DataplexRunTaskOperator
from airflow.utils.dates import days_ago
from airflow.utils.email import send_email

# Default arguments
default_args = {
    'owner': 'your-name',
    'start_date': days_ago(1),
    'retries': 1,
    'on_failure_callback': notify_failure
}

def notify_failure(context):
    task_id = context.get('task_instance').task_id
    exception = context.get('exception')
    error_message = f'Task {task_id} failed with exception: {exception}'
    
    send_email(
        to=["you@example.com"],
        subject=f'Airflow Task Failed: {task_id}',
        html_content=error_message
    )

# Define the DAG
with DAG(
    dag_id='trigger_dataplex_task_dp123',
    default_args=default_args,
    schedule_interval=None,
    catchup=False
) as dag:

    # Task to trigger the Dataplex task
    run_dataplex_task = DataplexRunTaskOperator(
        task_id='run_dataplex_task',
        project_id='your-project-id',
        region='your-region',
        lake_id='your-lake-id',
        task_id='dp123',
        execution_spec_args={
            'bigquery_table': 'emp_table123'
        },
        wait_for_task_completion=True
    )

    run_dataplex_task
```

#### **Steps to Deploy the Airflow DAG**

1. Save the above Airflow code as a `.py` file, e.g., `trigger_dataplex_task_dp123.py`.
2. Place this file in your Airflow DAGs directory.
3. The DAG will appear in the Airflow UI. You can trigger it manually or set a schedule.

### Summary

- **Terraform** is used to create a Dataplex Data Quality Task for the `emp_table123` BigQuery table, enforcing rules like non-null checks and ensuring `employee_id` is 8 characters long.
- **Airflow DAG** triggers the Dataplex task `dp123`, allowing you to run the data quality checks as part of your data pipeline.

This setup enables you to automate data quality checks on your BigQuery tables using Google Cloud Composer and Dataplex.
