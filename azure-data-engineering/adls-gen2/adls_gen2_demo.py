"""
adls_gen2_demo.py
~~~~~~~~~~~~~~~~~
Demonstrates common Azure Data Lake Storage Gen2 operations using the
azure-storage-file-datalake SDK.

Operations covered
------------------
1. Create a filesystem (container)
2. Create directories (Bronze / Silver / Gold pattern)
3. Upload a file
4. List files in a directory
5. Read file content
6. Rename / move a file (atomic thanks to Hierarchical Namespace)
7. Set and get ACLs on a directory
8. Delete a file

Prerequisites
-------------
    pip install azure-storage-file-datalake azure-identity

Environment variables (or replace with your own values)
-------------------
    AZURE_STORAGE_ACCOUNT_NAME   e.g. myadlsgen2
    AZURE_CLIENT_ID              Service Principal app ID
    AZURE_TENANT_ID              Azure AD tenant ID
    AZURE_CLIENT_SECRET          Service Principal secret

NOTE: This script uses DefaultAzureCredential which automatically picks up
      Managed Identity when running inside Azure, or a Service Principal /
      environment variables locally.

For a **local demo without Azure**, run with DRY_RUN=true (default when
env vars are not set) to see the operations printed rather than executed.
"""

import csv
import io
import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Dry-run mode — if Azure credentials are not configured we simulate calls
# ---------------------------------------------------------------------------
_ACCOUNT = os.getenv("AZURE_STORAGE_ACCOUNT_NAME", "")
DRY_RUN = not bool(_ACCOUNT)

if DRY_RUN:
    print("[DRY RUN] Azure credentials not set — printing operations only.\n")

FILESYSTEM_NAME = "datalake"
SAMPLE_CSV = Path(__file__).parent / "sample_customers.csv"


# ---------------------------------------------------------------------------
# Helper: pretty-print or execute
# ---------------------------------------------------------------------------

def _log(msg: str) -> None:
    print(f"  {msg}")


# ---------------------------------------------------------------------------
# 1. Initialise client
# ---------------------------------------------------------------------------

def get_client():
    from azure.identity import DefaultAzureCredential
    from azure.storage.filedatalake import DataLakeServiceClient

    credential = DefaultAzureCredential()
    service_client = DataLakeServiceClient(
        account_url=f"https://{_ACCOUNT}.dfs.core.windows.net",
        credential=credential,
    )
    return service_client


# ---------------------------------------------------------------------------
# 2. Demonstrate ADLS Gen2 operations
# ---------------------------------------------------------------------------

def demo_adls_operations() -> None:
    print("=" * 55)
    print("Azure Data Lake Storage Gen2 Operations Demo")
    print("=" * 55)

    # -- Create filesystem ------------------------------------------------
    print("\n[1] Create filesystem (container)")
    if not DRY_RUN:
        svc = get_client()
        fs_client = svc.create_file_system(file_system=FILESYSTEM_NAME)
        _log(f"Created filesystem: {FILESYSTEM_NAME}")
    else:
        _log(f"create_file_system('{FILESYSTEM_NAME}')")

    # -- Create directories -----------------------------------------------
    print("\n[2] Create Medallion directories")
    dirs = ["bronze/customers", "silver/customers", "gold/kpi_summary"]
    for d in dirs:
        if not DRY_RUN:
            fs_client.create_directory(d)
        _log(f"create_directory('{d}')")

    # -- Upload file -------------------------------------------------------
    print("\n[3] Upload sample_customers.csv → bronze/customers/")
    target_path = "bronze/customers/sample_customers.csv"
    if not DRY_RUN:
        file_client = fs_client.get_file_client(target_path)
        with open(SAMPLE_CSV, "rb") as fh:
            data = fh.read()
        file_client.upload_data(data, overwrite=True)
        _log(f"Uploaded {SAMPLE_CSV.name} ({len(data)} bytes) → {target_path}")
    else:
        _log(f"upload_data(src='{SAMPLE_CSV.name}', dst='{target_path}')")

    # -- List files -------------------------------------------------------
    print("\n[4] List files in bronze/customers/")
    if not DRY_RUN:
        dir_client = fs_client.get_directory_client("bronze/customers")
        for path in fs_client.get_paths("bronze/customers"):
            _log(f"  {path.name}  (size={path.content_length} bytes)")
    else:
        _log("get_paths('bronze/customers') → ['bronze/customers/sample_customers.csv']")

    # -- Read file --------------------------------------------------------
    print("\n[5] Read file content")
    if not DRY_RUN:
        file_client = fs_client.get_file_client(target_path)
        download = file_client.download_file()
        content = download.readall().decode("utf-8")
        reader = csv.DictReader(io.StringIO(content))
        rows = list(reader)
        _log(f"Read {len(rows)} rows. First row: {rows[0]}")
    else:
        _log(f"download_file() → read CSV content")

    # -- Rename / move ----------------------------------------------------
    print("\n[6] Move file from bronze → silver (atomic rename)")
    new_path = "silver/customers/sample_customers.csv"
    if not DRY_RUN:
        file_client = fs_client.get_file_client(target_path)
        file_client.rename_file(f"{FILESYSTEM_NAME}/{new_path}")
        _log(f"Moved {target_path} → {new_path}")
    else:
        _log(f"rename_file('{target_path}' → '{new_path}')")

    # -- Set ACL ----------------------------------------------------------
    print("\n[7] Set ACL on silver/customers/ (read-only for group data-readers)")
    acl = "user::rwx,group::r-x,other::---,group:data-readers:r-x"
    if not DRY_RUN:
        dir_client = fs_client.get_directory_client("silver/customers")
        dir_client.set_access_control(acl=acl)
        acl_props = dir_client.get_access_control()
        _log(f"ACL set: {acl_props['acl']}")
    else:
        _log(f"set_access_control(acl='{acl}')")

    # -- Delete file ------------------------------------------------------
    print("\n[8] Delete file")
    if not DRY_RUN:
        file_client = fs_client.get_file_client(new_path)
        file_client.delete_file()
        _log(f"Deleted: {new_path}")
    else:
        _log(f"delete_file('{new_path}')")

    print("\nDemo complete.")


if __name__ == "__main__":
    demo_adls_operations()
