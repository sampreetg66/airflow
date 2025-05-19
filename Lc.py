

### **Step 1: Install dependencies on your Dataproc cluster**

If not already available, install:

```bash
pip install google-cloud-storage pyyaml
```

---

### **Step 2: Update your helper code**

```python
from google.cloud import storage
import yaml
import io

def load_yaml_config(gs_uri):
    if not gs_uri.startswith("gs://"):
        raise ValueError("Expected a GCS URI (gs://...)")

    # Extract bucket and blob name
    parts = gs_uri[5:].split("/", 1)
    bucket_name, blob_name = parts[0], parts[1]

    # Initialize GCS client
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    # Download the blob content
    content = blob.download_as_text()

    # Parse YAML
    return yaml.safe_load(io.StringIO(content))
```

---

### **Step 3: Usage example**

```python
config = load_yaml_config('gs://p/RI/cecl/mcode/common/config.yaml')
print(config)
```

---

This approach will **work from a helper module running inside Dataproc** as long as your environment has authentication set up (which Dataproc usually handles automatically via service account scopes).

Let me know if you want the function to support both local files and GCS URIs.
