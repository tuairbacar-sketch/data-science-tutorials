"""
azure_sdk_demo.py
~~~~~~~~~~~~~~~~~
Utility scripts demonstrating common Azure SDK for Python patterns used in
Azure Data Engineering workflows.

Patterns covered
----------------
1. Blob Storage: upload, list, download, delete blobs
2. Azure Key Vault: retrieve secrets at runtime
3. Azure Data Factory: trigger a pipeline run and poll status

Prerequisites
-------------
    pip install azure-storage-blob azure-identity azure-keyvault-secrets azure-mgmt-datafactory

Environment variables
---------------------
    AZURE_STORAGE_ACCOUNT       Blob Storage account name
    AZURE_KEYVAULT_URL          e.g. https://mykeyvault.vault.azure.net/
    AZURE_SUBSCRIPTION_ID       Azure subscription ID
    AZURE_RESOURCE_GROUP        Resource group name
    AZURE_DATA_FACTORY_NAME     ADF factory name
    AZURE_ADF_PIPELINE_NAME     Pipeline name to trigger

NOTE: When env vars are absent the script runs in DRY_RUN mode and prints
      the operations it would perform.
"""

import os
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Dry-run detection
# ---------------------------------------------------------------------------
DRY_RUN = not bool(os.getenv("AZURE_STORAGE_ACCOUNT"))

if DRY_RUN:
    print("[DRY RUN] Azure credentials not configured — printing operations only.\n")


def _log(msg: str) -> None:
    print(f"  {msg}")


# ---------------------------------------------------------------------------
# 1. Blob Storage operations
# ---------------------------------------------------------------------------

def demo_blob_storage() -> None:
    """Upload, list, download, and delete a blob."""
    print("=" * 55)
    print("1. Azure Blob Storage")
    print("=" * 55)

    account = os.getenv("AZURE_STORAGE_ACCOUNT", "myaccount")
    container = "demo-container"
    blob_name = "demo/sample.txt"
    content = b"Hello from Azure SDK for Python!"

    if not DRY_RUN:
        from azure.identity import DefaultAzureCredential
        from azure.storage.blob import BlobServiceClient

        credential = DefaultAzureCredential()
        service = BlobServiceClient(
            f"https://{account}.blob.core.windows.net", credential=credential
        )
        # Upload
        blob_client = service.get_blob_client(container, blob_name)
        blob_client.upload_blob(content, overwrite=True)
        _log(f"Uploaded '{blob_name}' ({len(content)} bytes)")

        # List blobs
        _log("Blobs in container:")
        for b in service.get_container_client(container).list_blobs():
            _log(f"  {b.name}  ({b.size} bytes)")

        # Download
        downloaded = blob_client.download_blob().readall()
        _log(f"Downloaded content: {downloaded.decode()}")

        # Delete
        blob_client.delete_blob()
        _log(f"Deleted '{blob_name}'")
    else:
        _log(f"BlobServiceClient('https://{account}.blob.core.windows.net', DefaultAzureCredential())")
        _log(f"upload_blob('{blob_name}', data={content})")
        _log(f"list_blobs('{container}')")
        _log(f"download_blob('{blob_name}')")
        _log(f"delete_blob('{blob_name}')")


# ---------------------------------------------------------------------------
# 2. Azure Key Vault — retrieve a secret
# ---------------------------------------------------------------------------

def demo_key_vault() -> None:
    """Retrieve a secret from Azure Key Vault."""
    print("\n" + "=" * 55)
    print("2. Azure Key Vault")
    print("=" * 55)

    vault_url = os.getenv("AZURE_KEYVAULT_URL", "https://mykeyvault.vault.azure.net/")
    secret_name = "db-password"

    if not DRY_RUN:
        from azure.identity import DefaultAzureCredential
        from azure.keyvault.secrets import SecretClient

        client = SecretClient(vault_url=vault_url, credential=DefaultAzureCredential())
        secret = client.get_secret(secret_name)
        _log(f"Retrieved secret '{secret_name}': {'*' * len(secret.value)}")
    else:
        _log(f"SecretClient(vault_url='{vault_url}').get_secret('{secret_name}')")
        _log("Secret value: *** (masked)")


# ---------------------------------------------------------------------------
# 3. Azure Data Factory — trigger pipeline run and poll status
# ---------------------------------------------------------------------------

def demo_adf_trigger() -> None:
    """Trigger an ADF pipeline and poll until completion."""
    print("\n" + "=" * 55)
    print("3. Azure Data Factory – Trigger Pipeline")
    print("=" * 55)

    subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID", "00000000-0000-0000-0000-000000000000")
    resource_group = os.getenv("AZURE_RESOURCE_GROUP", "my-rg")
    factory_name = os.getenv("AZURE_DATA_FACTORY_NAME", "my-adf")
    pipeline_name = os.getenv("AZURE_ADF_PIPELINE_NAME", "CopySalesData_Pipeline")
    parameters = {"windowStart": "2024-01-15T00:00:00Z", "windowEnd": "2024-01-16T00:00:00Z"}

    if not DRY_RUN:
        from azure.identity import DefaultAzureCredential
        from azure.mgmt.datafactory import DataFactoryManagementClient

        credential = DefaultAzureCredential()
        adf_client = DataFactoryManagementClient(credential, subscription_id)

        run = adf_client.pipelines.create_run(
            resource_group, factory_name, pipeline_name, parameters=parameters
        )
        run_id = run.run_id
        _log(f"Pipeline run triggered. Run ID: {run_id}")

        # Poll status
        while True:
            run_status = adf_client.pipeline_runs.get(resource_group, factory_name, run_id)
            status = run_status.status
            _log(f"Status: {status}")
            if status in ("Succeeded", "Failed", "Cancelled"):
                break
            time.sleep(10)

        _log(f"Final status: {status}")
        if status == "Failed":
            _log(f"Error: {run_status.message}")
    else:
        _log(f"DataFactoryManagementClient(credential, '{subscription_id}')")
        _log(f"pipelines.create_run('{resource_group}', '{factory_name}', '{pipeline_name}', parameters={parameters})")
        _log("Poll run_id every 10s until Succeeded / Failed / Cancelled")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    demo_blob_storage()
    demo_key_vault()
    demo_adf_trigger()
