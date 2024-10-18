To create a dynamically mapped set of tasks in Airflow based on a string list in the format `d--t` (where `d` is the dataset and `t` is the table), you can use the TaskFlow API with dynamic task mapping, which was introduced in Airflow 2.3. Here’s an example code that does this:

```python
from airflow import DAG
from airflow.decorators import task
from airflow.utils.dates import days_ago

# List of dataset-table pairs
data_list = ["dataset1--table1", "dataset2--table2", "dataset3--table3"]

# Define the DAG
with DAG(
    dag_id="dynamic_task_mapping_example",
    start_date=days_ago(1),
    schedule_interval=None,
    catchup=False,
) as dag:

    @task
    def process_dataset_table(dataset_table: str):
        # Split the dataset-table string into dataset and table
        dataset, table = dataset_table.split("--")
        # Print the dataset and table
        print(f"Dataset: {dataset}, Table: {table}")

    # Dynamically map tasks based on the dataset-table list
    process_dataset_table.expand(dataset_table=data_list)

# This DAG will create one task per dataset-table pair and print the values
```

### Explanation:
1. **data_list**: This is your list containing strings in the `d--t` format.
2. **process_dataset_table**: This is a task decorated using Airflow's TaskFlow API. It takes the `dataset_table` string as input, splits it into the `dataset` and `table`, and prints them.
3. **expand**: This is how we dynamically map the task to each entry in the `data_list`. For each entry, a task instance will be created that runs `process_dataset_table` and processes the respective dataset-table pair.

### How It Works:
- When this DAG runs, Airflow will create individual task instances for each item in `data_list` (i.e., one for each dataset-table pair), and each task will print the corresponding dataset and table.

Let me know if you need further modifications!
