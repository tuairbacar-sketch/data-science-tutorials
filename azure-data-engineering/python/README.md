# Python for Azure Data Engineering

Python is the de-facto scripting language for Azure Data Engineering tasks — from orchestrating pipelines to processing files and interacting with Azure services via the Azure SDK for Python.

## Key Libraries

| Library | Purpose |
|---|---|
| `azure-storage-blob` | Read / write Blob Storage containers |
| `azure-storage-file-datalake` | Interact with ADLS Gen2 (hierarchical namespace) |
| `azure-identity` | Authentication (Managed Identity, Service Principal, CLI) |
| `azure-mgmt-datafactory` | Manage and trigger ADF pipelines programmatically |
| `azure-synapse-artifacts` | Interact with Synapse Pipelines and Spark pools |
| `pyodbc` / `sqlalchemy` | Connect to Azure SQL / Synapse Dedicated SQL Pool |
| `pandas` | In-memory data manipulation and inspection |
| `pyarrow` | Parquet read/write, columnar data conversion |

## Authentication Best Practices

```python
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential

# DefaultAzureCredential tries: Managed Identity → Env vars → Azure CLI → VS Code
credential = DefaultAzureCredential()

# Explicit Managed Identity (recommended in production on Azure)
credential = ManagedIdentityCredential()
```

**Never** hard-code storage account keys or connection strings. Use Azure Key Vault with `SecretClient` to retrieve secrets at runtime.

## Files in this Module

| File | Description |
|---|---|
| `azure_sdk_demo.py` | Utility scripts covering Blob Storage, Key Vault, and ADF trigger patterns |

## Common Patterns

### Upload a file to Blob Storage
```python
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential

client = BlobServiceClient(
    "https://myaccount.blob.core.windows.net",
    credential=DefaultAzureCredential()
)
client.get_blob_client("mycontainer", "path/to/file.csv").upload_blob(data, overwrite=True)
```

### Trigger an ADF Pipeline
```python
from azure.mgmt.datafactory import DataFactoryManagementClient

adf = DataFactoryManagementClient(credential, subscription_id)
run = adf.pipelines.create_run(rg, factory_name, pipeline_name, parameters={})
print(run.run_id)
```
