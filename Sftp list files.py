To get a list of all files in an SFTP location in Airflow, you can use the `SFTPOperator` or `SFTPHook` from the Airflow `providers.sftp` package. Below is an example using the `SFTPHook` to list files in an SFTP directory.

```python
from airflow import DAG
from airflow.providers.sftp.hooks.sftp import SFTPHook
from airflow.operators.python import PythonOperator
from datetime import datetime

# Function to list files in an SFTP directory
def list_sftp_files():
    sftp_hook = SFTPHook(ftp_conn_id='my_sftp_conn')  # Replace 'my_sftp_conn' with your SFTP connection ID
    sftp_client = sftp_hook.get_conn()
    
    # Specify the directory in the SFTP server
    remote_dir = '/path/to/sftp/directory'
    
    # List all files in the specified directory
    file_list = sftp_client.listdir(remote_dir)
    
    # Log or return the list of files
    print(f"Files in {remote_dir}: {file_list}")
    return file_list

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 1, 1),
    'retries': 1
}

# Define the DAG
with DAG('sftp_file_listing_dag', 
         default_args=default_args, 
         schedule_interval=None, 
         catchup=False) as dag:

    # PythonOperator to list files
    list_files_task = PythonOperator(
        task_id='list_sftp_files',
        python_callable=list_sftp_files
    )

list_files_task
```

### Key parts:
1. **SFTPHook**: Used to connect to the SFTP server.
2. **`ftp_conn_id`**: Replace it with the connection ID defined in your Airflow Connections UI.
3. **`remote_dir`**: Set the directory path on the SFTP server from which you want to list the files.

Make sure you have your SFTP connection details set up in Airflow (Admin > Connections).
